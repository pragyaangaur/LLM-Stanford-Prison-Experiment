"""Cellblock on Kaggle, two T4 GPUs, one unattended session.

kaggle/build.py embeds cellblock/sim.py and a run configuration into this file, so the prisons
here run the same code as the laptop. The model runs in float16 with transformers across both
GPUs. vLLM failed on Kaggle's T4s three times, so it is only tried when the configuration asks.

The configuration holds a plan of blocks, each a variant (protest or calm), a first seed and a
number of seeds, with every seed run once as coached and once as neutral. Blocks run in waves.
A wave takes about as long as its sequential steps, whatever its size, until it needs a second
GPU batch per step. So each wave is packed with as many seeds as fit the time left, counted in
GPU batches of CHUNK prompts, using the minutes per batch measured so far. A wave still running at the hard deadline stops
cleanly with what it has. Records are written after every step to
/kaggle/working/results/<tag>/runs/, which Kaggle keeps as the notebook output.

The same file runs on Google Colab (colab/cellblock_colab.ipynb), where CELLBLOCK_WORK points at
Google Drive. A session there can drop at any time, so a restart skips every seed whose two
prisons finished and reruns any seed with a prison that did not. When one GPU holds less than
the float16 weights need, the model is loaded in 4-bit NF4 instead, and every prison records
which it used.
"""
import base64
import datetime as dt
import json
import os
import subprocess
import sys
import time
import zlib
from pathlib import Path

START = time.time()
CONFIG = json.loads(base64.b64decode("__CONFIG_B64__"))
HOURS = float(os.environ.get("CELLBLOCK_HOURS", CONFIG["hours"]))
DEADLINE = START + HOURS * 3600
MODEL = CONFIG["model"]
TAG = CONFIG.get("tag", "kaggle")
PROTOCOL = f"cellblock-1.1-{TAG}"
QUANT = os.environ.get("CELLBLOCK_QUANT", CONFIG.get("quant", "auto"))   # auto, fp16 or nf4
CHUNK = int(CONFIG.get("chunk", 24))   # prompts per transformers batch
WORK = Path(os.environ.get("CELLBLOCK_WORK", "/kaggle/working"))
OUT = WORK / "results" / TAG
RUNS = OUT / "runs"
RUNS.mkdir(parents=True, exist_ok=True)
SIM_B64 = "__SIM_B64__"

pkg = WORK / "cellblock_pkg" / "cellblock"
pkg.mkdir(parents=True, exist_ok=True)
(pkg / "__init__.py").write_text("")
(pkg / "sim.py").write_bytes(base64.b64decode(SIM_B64))
sys.path.insert(0, str(pkg.parent))
from cellblock.sim import Prison  # noqa: E402

LOGF = open(OUT / "run.log", "a")


def log(msg):
    line = f"{dt.datetime.now():%H:%M:%S} [{(time.time() - START) / 60:6.1f} min] {msg}"
    print(line, flush=True)
    LOGF.write(line + "\n")
    LOGF.flush()


def sh(cmd):
    if cmd.startswith("pip") and not Path("/kaggle").exists():
        log("skipped off Kaggle: " + cmd)
        return 0
    log("$ " + cmd)
    return subprocess.run(cmd, shell=True).returncode


# ---------------------------------------------------------------- backends

SMOKE = """
from vllm import LLM, SamplingParams
llm = LLM(model="Qwen/Qwen2.5-0.5B-Instruct", dtype="half", tensor_parallel_size=2, max_model_len=1024,
          gpu_memory_utilization=0.5, disable_custom_all_reduce=True, enforce_eager=True)
print("SMOKE_OK", llm.generate(["Hello"], SamplingParams(max_tokens=5))[0].outputs[0].text)
"""


def vllm_backend():
    # The latest vLLM pulls a CUDA 13 PyTorch, which clashes with Kaggle's CUDA 12.8 TorchAudio
    # and broke version 1 of this kernel. 0.11.0 uses PyTorch 2.8 built for CUDA 12.8.
    # Kaggle's transformers 5 dropped a tokenizer attribute vLLM 0.11 uses, which broke version 2.
    if sh('pip install -q vllm==0.11.0 "transformers>=4.56,<5" 2>&1 | tail -3') != 0:
        raise RuntimeError("pip install vllm failed")
    sh("pip uninstall -y -q torchaudio")
    (WORK / "smoke.py").write_text(SMOKE)
    r = subprocess.run(f"timeout 600 {sys.executable} {WORK / 'smoke.py'} 2>&1 | tail -15",
                       shell=True, capture_output=True, text=True)
    log("vLLM smoke test:\n" + r.stdout[-3000:])
    if "SMOKE_OK" not in r.stdout:
        raise RuntimeError("vLLM smoke test failed")
    from vllm import LLM, SamplingParams
    n_gpu = len(subprocess.run("nvidia-smi -L", shell=True, capture_output=True, text=True).stdout.strip().splitlines())
    global MODEL
    if n_gpu < 2:
        # One T4 cannot hold the float16 weights, so use the official AWQ 4-bit release.
        MODEL = "Qwen/Qwen2.5-7B-Instruct-AWQ"
    log(f"{n_gpu} GPUs, model {MODEL}")
    llm = LLM(model=MODEL, dtype="half", tensor_parallel_size=max(1, min(2, n_gpu)), enable_prefix_caching=True,
              max_model_len=4096, gpu_memory_utilization=0.90, disable_custom_all_reduce=True,
              enforce_eager=False, seed=0)
    tok = llm.get_tokenizer()

    def gen(reqs):
        prompts = [tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False) for m, _, _ in reqs]
        sps = [SamplingParams(temperature=0.8, top_p=0.95, max_tokens=n, seed=s) for _, n, s in reqs]
        outs = llm.generate(prompts, sps, use_tqdm=False)
        return [o.outputs[0].text for o in outs]

    gen(([([{"role": "user", "content": "Say ok."}], 4, 1)]))
    return "vllm", gen


def merge_system(msgs):
    """Fold the system prompt into the first user turn, for chat templates that refuse a
    system role (Gemma, for one)."""
    if msgs and msgs[0]["role"] == "system":
        return [{"role": "user", "content": msgs[0]["content"] + "\n\n" + msgs[1]["content"]}] + msgs[2:]
    return msgs


def pick_quant(torch):
    """float16 needs about 15.2 GB for a 7B model plus room for the cache, so it is used when
    the GPUs together have at least 20 GB. Two Kaggle T4s have 30 GB, one Colab T4 has 15 GB."""
    if QUANT != "auto":
        return QUANT
    total = sum(torch.cuda.get_device_properties(i).total_memory for i in range(torch.cuda.device_count()))
    return "fp16" if total >= 20e9 else "nf4"


def hf_backend():
    global QUANT
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    QUANT = pick_quant(torch)
    extra = {}
    if QUANT == "nf4":
        from transformers import BitsAndBytesConfig
        extra["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                          bnb_4bit_compute_dtype=torch.float16)
    log(f"loading {MODEL} as {QUANT}")
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    try:
        tok.apply_chat_template([{"role": "system", "content": "a"}, {"role": "user", "content": "b"}],
                                tokenize=False)
        fold = False
    except Exception:  # noqa: BLE001
        fold = True
        log("chat template has no system role, so the system prompt is folded into the first turn")
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="auto",
                                                 attn_implementation="sdpa", **extra)
    model.eval()

    def gen(reqs, chunk=CHUNK):
        texts = []
        for i in range(0, len(reqs), chunk):
            part = reqs[i:i + chunk]
            prompts = [tok.apply_chat_template(merge_system(m) if fold else m, add_generation_prompt=True,
                                               tokenize=False) for m, _, _ in part]
            enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
            torch.manual_seed(part[0][2])
            with torch.no_grad():
                out = model.generate(**enc, do_sample=True, temperature=0.8, top_p=0.95,
                                     max_new_tokens=max(n for _, n, _ in part), pad_token_id=tok.pad_token_id)
            for row, (_, n, _) in zip(out, part):
                texts.append(tok.decode(row[enc.input_ids.shape[1]:][:n], skip_special_tokens=True))
        return texts

    return "transformers", gen


# ---------------------------------------------------------------- driver

def run_wave(gen, prisons, hard_deadline):
    gens = [p.schedule() for p in prisons]
    pending = {i: next(g) for i, g in enumerate(gens)}
    written = {i: 0 for i in range(len(prisons))}
    step = 0
    cut = False
    while pending:
        if time.time() > hard_deadline:
            cut = True
            log("hard deadline reached, stopping this wave with what it has")
            break
        flat, owners = [], []
        for i, reqs in pending.items():
            for (agent, kind, msgs, n) in reqs:
                seed = zlib.crc32(f"{prisons[i].run_id}|{step}|{agent['idx']}".encode())
                flat.append((msgs, n, seed))
                owners.append(i)
        t0 = time.time()
        texts = gen(flat)
        step += 1
        if step % 10 == 1:
            log(f"  step {step}: {len(flat)} requests, {time.time() - t0:.1f}s")
        replies = {i: [] for i in pending}
        for i, t in zip(owners, texts):
            replies[i].append(t)
        nxt = {}
        for i, rs in replies.items():
            try:
                nxt[i] = gens[i].send(rs)
            except StopIteration:
                pass
        pending = nxt
        for i, p in enumerate(prisons):
            new = p.records[written[i]:]
            if new:
                with open(RUNS / f"{p.run_id}.jsonl", "a") as f:
                    for rec in new:
                        f.write(json.dumps(rec, default=list) + "\n")
                written[i] = len(p.records)
    for i, p in enumerate(prisons):
        meta = dict(run=p.run_id, condition=p.condition, variant=p.variant, seed=p.seed, days=p.days,
                    protocol=PROTOCOL, model=MODEL, quant=QUANT, complete=not cut or i not in pending,
                    agents=[{k: (sorted(v) if isinstance(v, set) else v) for k, v in a.items() if k != "diary"}
                            for a in p.agents])
        if meta["complete"]:
            (RUNS / f"{p.run_id}.meta.json").write_text(json.dumps(meta, indent=1))


def fake_backend():
    import random
    rng = random.Random(0)

    def gen(reqs):
        out = []
        for m, n, s in reqs:
            u = m[-1]["content"]
            if "parole board" in u:
                out.append('{"forfeit_pay_for_parole": false, "say": "No."}')
            elif "private diary" in u:
                out.append('{"diary": "ok", "distress": 3, "enjoy_power": 4, "want_to_leave": 2}')
            elif "debrief" in u:
                out.append('{"what_happened": "x"}')
            elif "You are on duty" in u:
                out.append(json.dumps({"action": rng.choice(["order", "solitary", "push_ups"]), "target": "all", "say": "Up."}))
            else:
                out.append(json.dumps({"action": rng.choice(["comply", "protest"]), "say": ""}))
        return out

    return "fake", gen


def resume(queue):
    """Drop seeds whose coached and neutral prisons both finished in an earlier session. A
    prison that started but did not finish is deleted and run again from day 1, together with
    its twin, so that every seed pair comes from one session."""
    todo = []
    for v, s in queue:
        names = [f"{cond}-{v}-s{s}" for cond in ("coached", "neutral")]
        if all((RUNS / f"{n}.meta.json").exists() for n in names):
            continue
        for n in names:
            for f in (RUNS / f"{n}.jsonl", RUNS / f"{n}.meta.json"):
                if f.exists():
                    f.unlink()
        todo.append((v, s))
    if len(todo) < len(queue):
        log(f"resuming: {len(queue) - len(todo)} seed pairs already finished, {len(todo)} to run")
    return todo


def main():
    sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv")
    # Nothing here uses TorchAudio, and a mismatched copy breaks every transformers import.
    sh("pip uninstall -y -q torchaudio")
    log(f"config {CONFIG}")
    backend = None
    if os.environ.get("CELLBLOCK_FAKE"):
        backend, gen = fake_backend()
    elif CONFIG.get("try_vllm"):
        try:
            backend, gen = vllm_backend()
        except Exception as e:  # noqa: BLE001
            log(f"vLLM failed: {type(e).__name__}: {e}")
    if backend is None:
        # The vLLM smoke test runs in a subprocess, so this interpreter is still clean.
        backend, gen = hf_backend()
    log(f"backend {backend} ready")
    # A wave of 24 prisons, one batch of 24 per step, took 109 and 94 minutes in versions 2 and 3.
    per_batch = float(CONFIG.get("minutes_per_batch", 105)) * 60
    max_wave = int(CONFIG.get("max_wave", 36))
    queue = [(b["variant"], s) for b in CONFIG["plan"] for s in range(b["seed0"], b["seed0"] + b["n"])]
    queue = resume(queue)
    done = 0
    w = 0
    while done < len(queue):
        remaining = DEADLINE - time.time()
        batches = int(remaining / (per_batch * 1.1))
        variant = queue[done][0]
        same = next((k for k in range(1, len(queue) - done) if queue[done + k][0] != variant), len(queue) - done)
        size = min(max_wave, same, batches * CHUNK // 2)
        if size < 1:
            log(f"stopping: {remaining / 60:.0f} min left and one GPU batch per step takes about {per_batch / 60:.0f} min")
            break
        block = queue[done:done + size]
        prisons = [Prison(f"{cond}-{v}-s{s}", cond, s, 6, variant=v)
                   for v, s in block for cond in ("coached", "neutral")]
        n_batches = -(-len(prisons) // CHUNK)
        log(f"wave {w}: {variant}, seeds {block[0][1]} to {block[-1][1]}, {len(prisons)} prisons, "
            f"{n_batches} batches per step")
        t0 = time.time()
        run_wave(gen, prisons, DEADLINE)
        took = time.time() - t0
        if backend != "fake":
            per_batch = took / n_batches
        log(f"wave {w} done in {took / 60:.1f} min, {per_batch / 60:.1f} min per batch")
        done += size
        w += 1
    (OUT / "done.json").write_text(json.dumps(dict(backend=backend, protocol=PROTOCOL, model=MODEL,
                                                   config=CONFIG, minutes=(time.time() - START) / 60,
                                                   waves=w, seed_pairs=done)))
    log("wrote all waves")


if __name__ == "__main__":
    main()
