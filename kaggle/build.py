"""Write the Kaggle kernel folder kaggle/push/ with cellblock/sim.py and a run plan embedded.

    python kaggle/build.py --plan calm:2012:36 --hours 5.5
    python kaggle/build.py --plan calm:3000:12 --model allenai/OLMo-2-1124-7B-Instruct --slug cellblock-olmo

Each --plan block is variant:first_seed:number_of_seeds, and every seed runs as coached and
as neutral. Push the folder with kaggle kernels push -p kaggle/push --accelerator NvidiaTeslaT4.
"""
import argparse
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--plan", nargs="+", default=["calm:2012:36"])
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--hours", type=float, default=2.5)
ap.add_argument("--slug", default="cellblock")
ap.add_argument("--max-wave", type=int, default=36)
ap.add_argument("--chunk", type=int, default=24)
ap.add_argument("--try-vllm", action="store_true")
a = ap.parse_args()

plan = []
for b in a.plan:
    v, s0, n = b.split(":")
    assert v in ("calm", "protest"), v
    plan.append(dict(variant=v, seed0=int(s0), n=int(n)))
config = dict(model=a.model, hours=a.hours, plan=plan, max_wave=a.max_wave, chunk=a.chunk, try_vllm=a.try_vllm)

sim = (HERE.parent / "cellblock" / "sim.py").read_bytes()
src = (HERE / "runner.py").read_text()
src = src.replace("__SIM_B64__", base64.b64encode(sim).decode())
src = src.replace("__CONFIG_B64__", base64.b64encode(json.dumps(config).encode()).decode())
push = HERE / "push"
push.mkdir(exist_ok=True)
(push / "cellblock_kaggle.py").write_text(src)
(push / "kernel-metadata.json").write_text(json.dumps({
    "id": f"pragyaangaur/{a.slug}",
    "title": a.slug.replace("-", " ").title(),
    "code_file": "cellblock_kaggle.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": True,
    "enable_internet": True,
    "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": [],
}, indent=1))
print("wrote", push, "with", json.dumps(config))
