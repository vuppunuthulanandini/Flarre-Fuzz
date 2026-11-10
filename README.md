# 🥊 Flarre-Fuzz
### Adversarial Testing for AI-Generated Insurance Code

**AI writes the code. Flarre-Fuzz challenges it.**

A misplaced boundary. An incorrect surcharge cap. A rounding error.

In insurance, small coding mistakes can create costly premium miscalculations.

**Flarre-Fuzz is a multi-agent verification framework that attacks insurance rating logic with adversarial inputs, detects business-rule violations, minimizes failures, and proposes fixes with re-verification.**

### ⚙️ The Agentic Arena

| Agent | Responsibility |
|---|---|
| 🥊 Bully | Generates adversarial test profiles |
| 🏟️ Sandbox | Executes candidate code |
| ⚖️ Referee | Validates deterministic business rules |
| 🔍 Minimizer | Isolates minimal failing inputs |
| 📚 Clause Retrieval | Retrieves relevant rule context |
| 🛠️ Fixer | Proposes targeted repairs |
| 🎯 Orchestrator | Coordinates the entire lifecycle |

### 🔄 How It Works

```mermaid
flowchart LR
 A["Rating Code"] --> B["Bully"]
 B --> C["Sandbox"]
 C --> D["Referee"]
 D -->|Violation| E["Minimizer"]
 E --> F["Clause Retrieval"]
 F --> G["Fixer"]
 G --> H["Re-verify"]
 H --> D
 D -->|Pass| I["Human Review"]
```

### 📊 Prototype Benchmark

**Five planted defects. All five detected by the combined strategy.**

| Strategy | Detection |
|---|---:|
| Boundary | 4/5 |
| Random | 5/5 |
| Boundary + Random + Gemini | **5/5** |

40 Gemini-generated profiles · 0 false alarms on the tested correct-code benchmark.

*Controlled prototype results, not production guarantees.*

### 🧠 Engineering Stack

`Python` · `FastAPI` · `Google Gemini` · `SQLite` · `JavaScript` · `Pytest`
<img width="1280" height="605" alt="Screenshot (638)(1)" src="https://github.com/user-attachments/assets/2680ec53-e6d4-4494-8499-f7af4a677ddc" />
<img width="1280" height="612" alt="Screenshot (639)(2)" src="https://github.com/user-attachments/assets/8baed8c8-2deb-4ade-9260-d8eb27f643ba" />
<img width="1280" height="620" alt="Screenshot (637)(1)" src="https://github.com/user-attachments/assets/5ba2f10f-b862-4d31-869a-dce3cdad7909" />
<img width="1280" height="581" alt="Screenshot (641)(1)" src="https://github.com/user-attachments/assets/a71433f5-354b-4dfb-be32-dafe154174b8" />





### 🚀 Run Locally

```bash
git clone https://github.com/vuppunuthulanandini/Flarre-Fuzz.git
cd Flarre-Fuzz
pip install -r requirements.txt
```

Configure `GEMINI_API_KEY` in `.env` using `.env.example`, then:

```bash
uvicorn flarre_fuzz.api:app --reload
```

Open `http://127.0.0.1:8000`

### 🛡️ Our Design Philosophy

**AI explores. Deterministic rules judge. Humans approve.**

Flarre-Fuzz aims to complement insurance-native AI platforms with an adversarial verification layer — challenging generated logic before it can be trusted.

---

**🥊 Don't just test the happy path. Fight for the edge cases.**

[GitHub Repository](https://github.com/vuppunuthulanandini/Flarre-Fuzz)
