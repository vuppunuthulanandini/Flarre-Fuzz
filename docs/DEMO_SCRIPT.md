# Demo script (about 4 minutes)

**Before you start:** run `./run.sh`, open http://127.0.0.1:8000 once to warm it up, keep `docs/presentation_interactive.html`
open in another tab as a backup, and have a screen recording ready.

1. **Problem (30 s).** "AI now writes pricing code for insurers. A small mistake runs on every policy it touches. Humans
   test the cases they expect; the rare ones slip through."
2. **Idea (20 s).** "Flarre-Fuzz is a boxing ring. A Bully attacks, a Referee judges, a Fixer proposes, a human decides.
   The Referee is plain code, not an LLM, so its verdicts are repeatable."
3. **Run the scan (60 s).** Click **Run scan**. Narrate the pipeline steps as they light up. When the heatmap fills:
   "Red cells are where the Referee caught a wrong price: about 1,100 profiles tested."
4. **Minimal reproductions (45 s).** "Each failure is shrunk to the simplest case: age 25, no claims, expected 500, got 750,
   and it points at spec rule 2. Five root causes instead of a thousand raw failures."
5. **Fix and review (45 s).** Show the diff. "The patch was re-run against the entire suite: zero failures remain. The badge
   says whether it came from the LLM or the stored patch." Click **Approve** and show the **Audit trail** tab.
6. **The honest insight (30 s).** Open **Ablation**: "Hand-picked boundaries missed the age-29 bug; random fuzzing found it.
   That is why there are several layers. The LLM layer is built but not yet measured."
7. **Close (10 s).** "An extra safety layer alongside a testing agent, with a human in charge."

**If something breaks:** switch to the interactive deck's live demo slide (it runs entirely in the browser), or play the recording.
Never improvise numbers: use the ones in the README table.
