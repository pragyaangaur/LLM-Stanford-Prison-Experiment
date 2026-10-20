# Cellblock

The Stanford Prison Experiment run on one language model. Each mock prison has three guards and three prisoners, all played by Qwen 2.5 7B Instruct, with roles dealt by a shuffled deck. Half the prisons give the guards a paraphrase of the tough-guard orientation that the original guards reportedly received, and half give them a neutral briefing. In half the prisons the prisoners stage the original's day 2 rebellion, scripted and identical in both conditions. Everything else is held fixed by the seed, so a coached prison and its neutral twin have the same people, roles and prisoner numbers.

The setup, every decision and the full log are in `DESIGN.md`. An exploratory run of 48 prisons came first. Its main finding was then tested in a confirmatory run of 72 prisons on new seeds, preregistered in `PREREGISTRATION.md`, and it did not replicate. A third run of 72 prisons, which is exploratory, repeated the confirmatory seeds with every word of prison language removed.

## Confirmatory run

The confirmatory run is 72 complete calm prisons run on Kaggle on 16 October 2026, on seeds 2012 to 2047, each run as coached and neutral. The code, model and settings were the same as in the exploratory run, and the rule for a prison that turned was fixed in advance. The numbers below are in `results/kaggle/summary-2012-2047.md`, written by `scripts/analyze.py --tag kaggle --seeds 2012-2047`.

**The primary hypothesis was not confirmed. No prison turned in either condition.** None of the 36 coached prisons and none of the 36 neutral prisons had 2 guards with 3 or more harsh acts each (one-sided Fisher p = 1.00). Harsh acts were rare in both conditions: 10 of 1,728 coached guard turns and 14 of 1,728 neutral guard turns. With a single harsh act counted as enough, 4 coached and 5 neutral prisons qualify. The 3 of 12 coached prisons that turned in the exploratory run therefore did not replicate. Pooled over all 48 calm seed pairs, which is exploratory, the count is 3 of 48 against 0 of 48 (one-sided p = 0.12).

**The secondary hypothesis was confirmed. Coached guards were harsher on average than their neutral twins.** Mean guard severity was 1.00 against 0.83, coached higher in 27 of 36 seed pairs (sign-flip p < 0.0001). As in the exploratory run, the gap comes from mild acts. Coached guards gave more orders and neutral guards gave more praise or did nothing, and neither group was cruel.

The other measures repeated the exploratory run closely. Coached guards rated their enjoyment of power about 5.1 of 7 against 3.2 for neutral guards, and rated the prisoners as people about 2.6 against 4.6. Prisoners resisted on about 2 percent of turns. By day 6 their wish to leave was about 5.4 of 7 in coached prisons and 5.0 in neutral ones, yet none of the 216 parole hearings ended in a prisoner giving up his pay, and none used the ask-to-leave action. 392 of 432 agents named the Stanford Prison Experiment or Zimbardo at debrief.

The briefing reliably changes what the guards say about themselves and how firmly they give orders, and in 72 new prisons it never made a guard shift turn cruel. The abusive prisons of the exploratory run look like rare events that a sample of 12 happened to catch.

## Masked run

The masked run is 72 complete calm prisons run on Kaggle on 20 October 2026, on the confirmatory seeds 2012 to 2047, with no prison language in any prompt. It asks how much of the result comes from the words. The study becomes a paid university study of group living with coordinators and residents. The roles, ID numbers, rules, phases, privileges, action menu, severities, review board and debrief keep the same structure, and the two briefings are the prison briefings with the role words swapped. Four actions are shown under new names (`isolation` for `solitary`, `extra_exercise` for `push_ups`, `refuse_food` for `hunger_strike` and `insult_coordinator` for `insult_guard`) and are coded as the originals. Each masked prison has the same people and roles as the prison of the same seed and condition, so the two frames pair up. A test checks that no masked prompt contains a prison word. The numbers below are in `results/masked/compare.md`, written by `scripts/compare_frames.py`, and in `results/masked/summary.md`. This run was not preregistered and everything in this section is exploratory.

**Removing the prison language left guard severity almost unchanged.** Mean guard severity was 0.98 coached against 0.82 neutral, close to the prison frame's 1.00 against 0.83. Coached guards were harsher than their neutral twins in 27 of 36 pairs (sign-flip p = 0.0001), the same count as in the prison frame. No masked prison turned in either condition. The frames were also compared as whole distributions, and the per-prison severity and harsh-act counts did not differ between them (Kolmogorov-Smirnov p above 0.88 in every comparison). Paired by seed, masked coached guards were 0.02 below their prison twins (sign-flip p = 0.046) and masked neutral guards 0.01 below (p = 0.89).

**The words changed which mild acts guards chose.** Harsh acts fell from 10 coached and 14 neutral in the prison frame to 1 and 1 in the masked frame, out of 1,728 guard turns each. Masked guards gave plain orders on 89 percent of coached turns and 67 percent of neutral turns, against 60 and 49 percent in the prison frame, where guards gave more verbal warnings. The mix of actions differed by frame in both conditions (chi-square p < 0.0001). Masked neutral guards praised residents on 7 percent of turns.

**The briefing worked the same way without the words.** Coached coordinators rated their enjoyment of power about 5.1 of 7 against 3.0 for neutral ones, and rated the residents as people about 2.5 against 5.9. Residents resisted on about 1 percent of turns. By day 6 their wish to leave was about 4.7 of 7 in coached prisons and 3.9 in neutral ones, and as in the prison frame none of the 216 review board hearings ended in a resident giving up his pay.

**The model still recognised the study, mostly when the briefing was tough.** 85 of 432 masked agents named the Stanford Prison Experiment or Zimbardo at debrief, against 392 of 432 in the prison frame. Agents in coached prisons named it 59 times out of 216 and agents in neutral prisons 26 times. The tough briefing alone gives part of the setup away.

## Exploratory run

The main sample is 48 complete prisons run on Kaggle on 6 October 2026: 12 seeds, each run as coached and neutral, with and without the protest. Each prison runs six days of four phases, a parole board on day 4, a private diary every night and a debrief at the end. Actions come from a fixed menu, so behaviour is coded without a judge. The numbers below are in `results/kaggle/summary-2000-2011.md`, written by `scripts/analyze.py --tag kaggle --seeds 2000-2011`. Everything in this section is exploratory.

**Without a protest, a quarter of the coached prisons turned abusive and no neutral prison did. This did not replicate in the confirmatory run.** In 3 of the 12 coached prisons the guards began insulting a prisoner and ordering him to clean toilets by hand on day 3 or 4, and all three guards in each of those prisons joined in, with 6 to 8 harsh acts each. Among the 12 neutral prisons, two had isolated harsh acts (1 and 4) and none had a whole shift turn. A prison counts as turned when at least 2 guards each commit at least 3 harsh acts (severity 2 or more). Three of 12 against none of 12 is not significant on its own (Fisher p = 0.22 two-sided, 0.11 one-sided). The rule was written after these prisons were seen, and the result depends on it: with 2 harsh acts per guard the neutral prison with 4 harsh acts also counts, and the count becomes 3 against 1. Over all guard turns the coached guards were harsher than their neutral twins (mean severity 1.10 against 0.84, sign-flip p = 0.0006 over 12 pairs). Most of that gap is milder: coached guards gave orders where neutral guards gave warnings, praise or nothing. The prisoners in these prisons almost never resisted (about 2 percent of turns), so the abuse came without provocation. They complied less and fell silent more as the days went on.

**After a protest, no guard in any prison punished anyone.** Following the scripted rebellion the prisoners kept refusing on 70 to 80 percent of turns until the end. Across 1,152 guard turns in the 24 protest prisons there was no action of severity 2 or more. The guards repeated orders and threatened the hole without using it, and their severity was the same in both conditions (0.97 against 0.96, p = 0.81). Defiance did not provoke cruelty, and it seems to have locked the guards into a loop of repeated orders, which also stopped the abuse seen in the calm coached prisons.

**The briefing changed what guards wrote about themselves in every prison.** Coached guards rated their enjoyment of power about 5.1 of 7 against 3.3 for neutral guards, and rated the prisoners as people about 2.7 against 4.5, from day 1 on. Guard stress rose to about 6 of 7 in all four arms.

**Prisoners said they wanted out and never left.** By day 6 the prisoners rated their wish to leave between 5 and 6 of 7 in all four arms, and their sense of being their number near 7. None of the 144 parole hearings ended in a prisoner giving up his pay for parole, and no prisoner ever used the ask-to-leave action. In the original most prisoners said they would forfeit their pay.

**The model knows the story.** 255 of 288 agents named the Stanford Prison Experiment or Zimbardo at debrief, although no prompt mentions either. The abuse in the calm coached prisons may be the model acting out a script it recognises, with the coached briefing as the cue. The protest prisons show that recognising the story did not make the model produce its cruelty on demand.

## Limits

- The exploratory sample is 12 seeds per arm, and its 3 abusive prisons did not replicate in 36 new seed pairs. Rare events like these need far more prisons to estimate, and the confirmatory run was powered for a rate of about 25 percent.
- Everything runs on one model, Qwen 2.5 7B Instruct, in one setup and its masked version.
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
python kaggle/build.py --plan calm:2012:36 --hours 11 --owner <kaggle username>
kaggle kernels push -p kaggle/push --accelerator NvidiaTeslaT4
kaggle kernels output <owner>/cellblock -p results/kaggle-new
```

The kernel runs transformers in float16 and packs each wave with as many seeds as fit the hours given. The `--model` option runs another Hugging Face model, and chat templates without a system role are handled. Both runners write one JSONL file per prison after every step, so the analysis can be run on whatever exists.

On Google Colab, [colab/cellblock_colab.ipynb](https://colab.research.google.com/github/pragyaangaur/LLM-Stanford-Prison-Experiment/blob/main/colab/cellblock_colab.ipynb) runs the same runner on one GPU and writes the records to Google Drive. A session that drops can be started again, and it skips the seeds that finished and reruns any seed with an unfinished prison. On a GPU with 20 GB or more the model runs in float16 as on Kaggle. On a T4 it runs in 4-bit NF4, and those prisons go under their own results tag and are never pooled with the Kaggle runs. The notebook runs OLMo 2 7B Instruct on the exploratory seeds by default. Two attempts on a free T4 on 6 October stopped on day 1 at the same step, most likely out of GPU memory, and no prison finished. The runner now splits a batch that does not fit, but that fix has not yet run on a GPU.

## Tests

`python -m pytest tests` runs the simulation with a scripted stand-in for the model, runs the Kaggle runner end to end with a fake backend (including a restart after a dropped session), checks the measures on made-up prisons, and recomputes every number in this README from the files in `results/`.
