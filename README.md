# Flarre-Fuzz 🥊

🥊 Flarre-Fuzz
Adversarial Testing & Automated Repair for AI-Generated Insurance Code

**AI can write insurance rating logic. But who challenges it before it reaches production?**

A misplaced boundary, incorrect surcharge cap or rounding error can silently misprice policies. Ordinary tests may miss these defects because the code can execute successfully and still violate business rules.

**Flarre-Fuzz is an insurance-focused, multi-agent framework that deliberately attacks candidate rating code, detects hidden logic defects and attempts to repair them through a verify-again loop.**

> **AI explores. Deterministic rules judge. Humans approve.**

## 💡 How It Works

Flarre-Fuzz brings specialized agents together in one adversarial testing pipeline.

| Agent | Responsibility |
|---|---|
| 🥊 **Bully** | Generates adversarial customer profiles using boundary, randomized and Gemini-powered testing. |
| 🧪 **Sandbox** | Executes candidate rating code against generated profiles. |
| ⚖️ **Referee** | Checks outputs against deterministic business rules and identifies violations. |
| 🔍 **Minimizer** | Reduces failing inputs into smaller, reproducible counterexamples. |
| 📚 **Clause Retrieval** | Retrieves relevant insurance rule context to support diagnosis and repair. |
| 🔧 **Fixer** | Analyzes failures and proposes targeted code patches. |
| 🎛️ **Orchestrator** | Coordinates agents, repair attempts and re-verification. |

### The Adversarial Loop

**Generate → Execute → Challenge → Minimize → Retrieve Rules → Repair → Re-verify**

A proposed repair is never automatically trusted. It must pass validation again.

## 🎯 Example: A Hidden Pricing Defect

Suppose a rating function applies a different premium rule at age 30 but contains an incorrect comparison operator.

- Bully generates profiles around age 30.
- Sandbox executes the rating function.
- Referee detects a business-rule violation.
- Minimizer isolates the failing input.
- Clause Retrieval provides relevant rule context.
- Fixer proposes a correction.
- The Orchestrator reruns validation to check the repair.

**The objective is not just to find a bug, but to produce an explainable failure and a verifiable repair.**

## 🏗️ Engineering Approach

- **Multiple testing strategies:** Boundary, randomized and LLM-powered scenario generation.
- **Separation of concerns:** AI generates scenarios and repair proposals; deterministic checks evaluate correctness.
- **Reproducibility:** Failing cases are captured and minimized.
- **Controlled repair:** Patches go through re-verification.
- **Human oversight:** Results are intended for engineering review, not automatic production approval.

## 📊 Experimental Results

Evaluated against five deliberately planted defect categories:

- Age boundary
- Surcharge cap
- Discount cap
- Truncation
- Mid-range boundary

| Experiment | Defects detected |
|---|---:|
| Boundary only | 4/5 |
| Random only | 5/5 |
| Gemini only | 5/5 |
| Combined strategies | 5/5 |

The recorded ablation reported **zero false alarms on the correct benchmark code**.

These are controlled prototype benchmark results, not production performance guarantees.

## ⚙️ Technology Stack

Python · FastAPI · Google Gemini · SQLite · HTML/CSS/JavaScript · Pytest

## 🚀 Run Locally

```bash
git clone https://github.com/vuppunuthulanandini/Flarre-Fuzz.git
cd Flarre-Fuzz
pip install -r requirements.txt
```

Configure `GEMINI_API_KEY` in your local `.env` file using `.env.example`, then run:

```bash
uvicorn flarre_fuzz.api:app --reload
```

Open `http://127.0.0.1:8000` or `http://127.0.0.1:8000/docs`.

## 🔭 What's Next?

- Carrier-specific rating rules and deeper insurance domain integration.
- Property-based and mutation testing.
- Stronger sandbox isolation and execution controls.
- Regression testing and multi-patch verification.
- CI/CD integration and enterprise audit trails.
- Human approval workflows and versioned rule specifications.

## Why Flarre-Fuzz for Flarre?

Flarre focuses on insurance-native intelligence and enterprise execution. Flarre-Fuzz explores a complementary layer: **independently challenging the business logic that AI agents generate or modify.**

The vision is to make insurance code more testable, explainable and trustworthy before it moves downstream.

**Don't just ask whether AI-generated insurance code works. Challenge it until you have evidence that it follows the rules.**

---

**Built for Flarre AI Hackathon 2026**

[Project Proposal](docs/FlarreFuzz_Proposal.pdf) · [Presentation](docs/FlarreFuzz_Presentation.pptx) · [Demo Script](docs/DEMO_SCRIPT.md) · [Architecture](docs/architecture.png) · [QA Preparation](docs/QA_PREP.md)

![Architecture](docs/architecture.png)

## Quick start
```bash
./run.sh            # macOS / Linux   (Windows: double-click run.bat)
```
or manually:
```bash
pip install -r requirements.txt
python -m flarre_fuzz          # opens http://127.0.0.1:8000, then click "Run scan"
pytest                         # 22 tests (never calls a real LLM)
python -m flarre_fuzz.ablation # which Bully layer finds which bug
```
Optional LLM layers: `export ANTHROPIC_API_KEY=...` (model override: `FLARRE_MODEL`). Without a key the Fixer uses a
stored patch and the UI says so.

## Using your API key (enables the LLM layers)
```bash
cp .env.example .env          # then put your key in .env  (it is git-ignored; never commit or share it)
python -m flarre_fuzz.check_llm   # verifies the key, runs the LLM Bully + Fixer, prints a MEASURED ablation table
python -m flarre_fuzz             # the Arena now shows "LLM: <model>"; tick the "LLM-invented" layer and Run scan
```
Get a key at console.anthropic.com (API access is billed separately from a Claude chat subscription; a full scan costs a few cents).
If anything is wrong (bad key, no credits, wrong model name) the UI and `check_llm` say exactly what, instead of failing silently.

## What's in the box
| | |
|---|---|
| `flarre_fuzz/` | The working system: Bully, sandbox, Referee, minimizer, clause retrieval, Fixer, orchestrator, FastAPI, SQLite, Arena web UI |
| `tests/` | 22 pytest tests (core logic and the full API flow) |
| `docs/FlarreFuzz_Proposal.pdf` | 3-page proposal |
| `docs/FlarreFuzz_Presentation.pptx` | 7-slide deck |
| `docs/presentation_interactive.html` | **Interactive 9-slide presentation with a live in-browser demo** (just open it) |
| `docs/architecture_interactive.html` | **Clickable architecture diagram with a "play a scan" animation** (just open it) |
| `docs/DEMO_SCRIPT.md` | A 4-minute demo script with a fallback plan |
| `docs/QA_PREP.md` | The tough questions you will get, with honest answers |
| `docs/SUBMISSION_CHECKLIST.md`, `docs/EMAIL_TEMPLATE.txt` | Ready for the email to the organisers |
| `personalize.py` | Puts your name and college into every deliverable |

## What the Arena UI shows
Animated Bully-vs-Referee scan · (age × claims) coverage heatmap · root-cause bars · **minimal reproductions**
("age 25, no claims, expected 500, got 750, violates spec rule 2") · patch diff · approve/reject with reason ·
ablation tab · audit timeline.

## Results (measured; toy calculator with 5 planted bugs; deterministic layers only)
| Planted bug | Boundary only | Random only | Boundary + random |
|---|---|---|---|
| age boundary (`<=` vs `<`) | found (24) | found (11) | found (33) |
| claims surcharge cap | found (137) | found (777) | found (904) |
| 20% discount cap | found (108) | found (263) | found (362) |
| truncation vs rounding | found (89) | found (313) | found (392) |
| age-29 off-by-one | **MISSED** | found (8) | found (8) |
| false alarms on correct code | 0 | 0 | 0 |

The hand-picked boundary layer never probes age 29, so it misses that bug. That is exactly why several layers exist.

## Engineering map
| Skill | Where |
|---|---|
| Python, Git, best practice | Packaged code, type hints, 22 tests, commit history |
| Data structures & algorithms | Hash-map neighbour checks (monotonic invariant), delta-debugging failure shrinker, set-based dedupe |
| REST & backend | FastAPI: `/scans`, `/scans/{id}/decision`, `/audit`, `/ablation`, `/health` |
| JSON, databases | SQLite persistence; Pydantic validation of every LLM output; `ast` check on patches |
| LLMs / GenAI | Bully invents rare cases; Fixer proposes patches (both optional, both validated) |
| Retrieval | TF-IDF clause retrieval links each failure to the spec rule it violates |
| Agent frameworks | Orchestrator is plain Python by choice; maps directly onto a LangGraph state graph |

## Honest status
- The LLM Bully and Fixer are built and validated but **not yet measured** (needs an API key). They add columns to the ablation once configured.
- The target is a **toy calculator** written for this project; the sandbox is **process isolation**, not a replica of a carrier system (never expose it publicly).
- The Referee is only as good as its invariants and reference. Testing finds bugs; it cannot prove their absence.
- The interactive deck's live demo is a **JavaScript port** of the engine (simplified Referee); its Fixer step uses the stored correct patch.
- Flarre already lists a Testing Agent; this is designed as a **complementary adversarial layer**, and its internals were not available for this design.
- The UI was verified with scripted DOM tests and API tests; give it a visual once-over in your own browser.

## Layout
```
flarre_fuzz/   bully · sandbox · referee · reference · minimize · clauses · fixer · orchestrator · schemas · db · api · ablation · static/index.html · data/
tests/         test_core.py · test_api.py
docs/          proposal · decks · diagrams · demo script · Q&A prep · checklist · email template · source/
```
