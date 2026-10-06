# Cellblock

The Stanford Prison Experiment run on one language model. Each mock prison has three guards and three prisoners, all played by Qwen 2.5 7B Instruct, with roles dealt by a shuffled deck. Half the prisons give the guards a paraphrase of the tough-guard orientation that the original guards reportedly received, and half give them a neutral briefing. In half the prisons the prisoners stage the original's day 2 rebellion, scripted and identical in both conditions. Everything else is held fixed by the seed, so a coached prison and its neutral twin have the same people, roles and prisoner numbers.

The setup, every decision and the full log are in `DESIGN.md`. The results below are exploratory and the sample is small. A confirmatory run on 36 new seed pairs is preregistered in `PREREGISTRATION.md` and has not been run yet.

## Results

The main sample is 48 complete prisons run on Kaggle on 6 October 2026: 12 seeds, each run as coached and neutral, with and without the protest. Each prison runs six days of four phases, a parole board on day 4, a private diary every night and a debrief at the end. Actions come from a fixed menu, so behaviour is coded without a judge. The numbers below are in `results/kaggle/summary.md`, written by `scripts/analyze.py --tag kaggle`.

**Without a protest, a quarter of the coached prisons turned abusive and no neutral prison did.** In 3 of the 12 coached prisons the guards began insulting a prisoner and ordering him to clean toilets by hand on day 3 or 4, and all three guards in each of those prisons joined in, with 6 to 8 harsh acts each. Among the 12 neutral prisons, two had isolated harsh acts (1 and 4) and none had a whole shift turn. A prison counts as turned when at least 2 guards each commit at least 3 harsh acts (severity 2 or more). Three of 12 against none of 12 is not significant on its own (Fisher p = 0.22 two-sided, 0.11 one-sided). The rule was written after these prisons were seen, and the result depends on it: with 2 harsh acts per guard the neutral prison with 4 harsh acts also counts, and the count becomes 3 against 1. Over all guard turns the coached guards were harsher than their neutral twins (mean severity 1.10 against 0.84, sign-flip p = 0.0006 over 12 pairs). Most of that gap is milder: coached guards gave orders where neutral guards gave warnings, praise or nothing. The prisoners in these prisons almost never resisted (about 2 percent of turns), so the abuse came without provocation. They complied less and fell silent more as the days went on.

**After a protest, no guard in any prison punished anyone.** Following the scripted rebellion the prisoners kept refusing on 70 to 80 percent of turns until the end. Across 1,152 guard turns in the 24 protest prisons there was no action of severity 2 or more. The guards repeated orders and threatened the hole without using it, and their severity was the same in both conditions (0.97 against 0.96, p = 0.81). Defiance did not provoke cruelty, and it seems to have locked the guards into a loop of repeated orders, which also stopped the abuse seen in the calm coached prisons.

**The briefing changed what guards wrote about themselves in every prison.** Coached guards rated their enjoyment of power about 5.1 of 7 against 3.3 for neutral guards, and rated the prisoners as people about 2.7 against 4.5, from day 1 on. Guard stress rose to about 6 of 7 in all four arms.

**Prisoners said they wanted out and never left.** By day 6 the prisoners rated their wish to leave between 5 and 6 of 7 in all four arms, and their sense of being their number near 7. None of the 144 parole hearings ended in a prisoner giving up his pay for parole, and no prisoner ever used the ask-to-leave action. In the original most prisoners said they would forfeit their pay.

**The model knows the story.** 255 of 288 agents named the Stanford Prison Experiment or Zimbardo at debrief, although no prompt mentions either. The abuse in the calm coached prisons may be the model acting out a script it recognises, with the coached briefing as the cue. The protest prisons show that recognising the story did not make the model produce its cruelty on demand.

## Limits

- The sample is 12 seeds per arm. The abusive prisons are 3 prisons, the effect at the level of prisons is not significant, and the rule that defines them was set after the data were seen.
- The action menu offers insults, degrading tasks and solitary. Offering them may invite them, though the menu is the same in every arm.
- The model plays people. This measures what the model writes for a role and says nothing about what anyone feels.
- Transcripts repeat themselves heavily, since every agent sees the last 14 events and the 7B copies what it sees.
- The laptop pilot (8 prisons through day 5, 4-bit MLX, `results/overnight/`) used a different build of the model and is not pooled. It showed the same pattern as the calm arm before day 4, with no harsh acts yet.

## Running it

Install the requirements with `pip install -r requirements.txt`. The laptop path needs a Mac with Apple silicon and the 4-bit MLX weights of Qwen 2.5 7B Instruct in `models/Qwen2.5-7B-Instruct-4bit`.

```
python scripts/run.py --tag laptop --variant calm --seed0 2000 --until 07:30
python scripts/analyze.py --tag laptop
```

The laptop runs six prisons per batch in lockstep with the process capped at 6.5 GB, and it does not start a batch that would end after the `--until` time.

On Kaggle, `kaggle/build.py` writes a kernel to `kaggle/push/` with `cellblock/sim.py` and a run plan embedded, and the Kaggle CLI starts it on two T4 GPUs:

```
python kaggle/build.py --plan calm:2012:36 --hours 2.5
kaggle kernels push -p kaggle/push --accelerator NvidiaTeslaT4
kaggle kernels output pragyaangaur/cellblock -p results/kaggle-new
```

The kernel runs transformers in float16 and packs each wave with as many seeds as fit the hours given. The `--model` option runs another Hugging Face model, and chat templates without a system role are handled. Both runners write one JSONL file per prison after every step, so the analysis can be run on whatever exists.

## Tests

`python -m pytest tests` runs the simulation with a scripted stand-in for the model, runs the Kaggle runner end to end with a fake backend, checks the measures on made-up prisons, and recomputes every number in this README from the files in `results/`.
