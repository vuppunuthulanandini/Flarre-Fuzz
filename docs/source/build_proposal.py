import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

DOCS = Path(__file__).resolve().parents[1]
NAME = sys.argv[1] if len(sys.argv) > 1 else "[Your Full Name as per Aadhaar]"
COLLEGE = sys.argv[2] if len(sys.argv) > 2 else "[Your College Name]"
NAVY = colors.HexColor("#0B1020"); CYAN = colors.HexColor("#1480A8")
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, alignment=0, spaceAfter=4)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=11, textColor=colors.HexColor("#555B6E"), spaceAfter=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13.5, textColor=CYAN, spaceBefore=12, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["Normal"], fontSize=10.3, leading=15, spaceAfter=5)
BL = ParagraphStyle("BL", parent=B, leftIndent=14, bulletIndent=2, spaceAfter=2)
SM = ParagraphStyle("SM", parent=B, fontSize=9, textColor=colors.HexColor("#555B6E"))

def bullets(items): return [Paragraph(i, BL, bulletText="•") for i in items]
def tbl(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9.3),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#C5CAD8")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F5FA")]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return t
def P(x): return Paragraph(x, ParagraphStyle("c", parent=B, fontSize=9.3, leading=12.5, spaceAfter=0))
def PW(x): return Paragraph(x, ParagraphStyle("cw", parent=B, fontSize=9.3, leading=12.5, spaceAfter=0, textColor=colors.white, fontName="Helvetica-Bold"))

doc = SimpleDocTemplate(str(DOCS / "FlarreFuzz_Proposal.pdf"), pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
    title="Flarre-Fuzz: Project Proposal", author=NAME)
s = []
s += [Paragraph("Flarre-Fuzz", H1),
      Paragraph("An adversarial safety layer that attacks AI-written insurance code before it reaches a carrier's systems", SUB),
      Paragraph("<b>Submitted for:</b> Flarre AI Innovation Challenge 2026 &nbsp;|&nbsp; <b>Name:</b> " + NAME + " &nbsp;|&nbsp; <b>College:</b> " + COLLEGE + "", SM)]

s += [Paragraph("1. Problem statement", H2),
      Paragraph("AI agents now write production code for insurance platforms, including premium and rating calculations. A small mistake in this code, such as a wrong age boundary, a missing cap or a rounding error, can quietly misprice thousands of policies, causing financial loss and regulatory exposure. Today, such code is validated mainly through human-written test cases. This is slow, and it tends to cover the cases people already expect, while the failures that matter most hide in rare and extreme inputs.", B)]

s += [Paragraph("2. Impact and relevance", H2)] + bullets([
    "<b>Financial:</b> pricing errors scale with every policy the code touches.",
    "<b>Regulatory:</b> insurers must apply approved rates and rules correctly; errors invite audit findings.",
    "<b>Delivery speed:</b> manual validation is a bottleneck for teams shipping AI-generated code.",
    "<b>Trust:</b> enterprise buyers need evidence of safety and auditability before adopting AI-written code. This matches Flarre's stated focus on governance, auditability and safety."])

s += [Paragraph("3. Proposed solution", H2),
      Paragraph("Flarre-Fuzz is an automated testing pipeline in which different components play different roles, with a human making the final decision:", B)]
s.append(tbl([[PW("Component"),PW("Type"),PW("Role")],
  [P("<b>Bully</b>"),P("LLM + code"),P("Generates attack inputs in three layers: boundary values, random fuzzing, and rare customer profiles invented by an LLM. Every LLM-generated profile is validated by code before use.")],
  [P("<b>Sandbox</b>"),P("Code"),P("Runs the code under test in an isolated subprocess with a timeout, capturing crashes. Stand-in for a system clone.")],
  [P("<b>Referee</b>"),P("Deterministic code"),P("Judges every result using (a) invariants that must always hold and (b) comparison with a trusted reference calculation. Deliberately not an LLM, so verdicts are repeatable.")],
  [P("<b>Fixer</b>"),P("LLM"),P("Explains failures and proposes a patch.")],
  [P("<b>Re-verify</b>"),P("Deterministic code"),P("Re-runs the full suite on the patched code (max 3 attempts) to confirm the bugs are gone and nothing new broke.")],
  [P("<b>Human + audit log</b>"),P("Person + code"),P("Reviewer approves or rejects the fix; each step is logged with a timestamp.")]],
  [3.2*cm, 3.0*cm, 10.8*cm]))
s += [Spacer(1,6), Paragraph("<b>Design principle:</b> LLMs handle creativity and explanation; deterministic code handles correctness. This avoids relying on a language model to judge its own work.", B)]

s += [PageBreak(), Paragraph("4. Architecture", H2),
      Image(str(DOCS / "architecture.png"), width=17*cm, height=17*cm*7.2/13*0.92), Spacer(1,4),
      Paragraph("Figure 1. Flarre-Fuzz architecture. A plain-Python orchestrator controls the loop and the retry limit.", SM)]

s += [Paragraph("5. AI utilisation", H2)] + bullets([
    "<b>Generative AI (Bully):</b> invents rare, adversarial customer profiles from the written business rules.",
    "<b>Generative AI (Fixer):</b> diagnoses failures and drafts patches with plain-English explanations.",
    "<b>Orchestrated multi-component workflow:</b> structured JSON hand-offs, retry limits, and a human approval gate.",
    "<b>Guardrails:</b> LLM output is validated by code, and all correctness decisions are deterministic."])

s += [Paragraph("6. Prototype and results", H2),
      Paragraph("A working prototype was built as a FastAPI backend with a web dashboard and a 17-test pytest suite. The code under test is a simplified personal-auto premium calculator written for this project, with <b>five deliberately planted bugs</b>: an age-boundary error, a missing claims surcharge cap, a missing discount cap, truncation instead of rounding, and an off-by-one at age 29 in a mid-range surcharge rule.", B)]
s.append(tbl([[PW("Planted bug"),PW("Boundary only"),PW("Random only"),PW("Boundary + random")],
  [P("Age boundary (&lt;= instead of &lt;)"),P("found (24)"),P("found (11)"),P("found (33)")],
  [P("Missing claims surcharge cap"),P("found (137)"),P("found (777)"),P("found (904)")],
  [P("Missing 20% discount cap"),P("found (108)"),P("found (263)"),P("found (362)")],
  [P("Truncation instead of rounding"),P("found (89)"),P("found (313)"),P("found (392)")],
  [P("Age 29 off-by-one (mid-range rule)"),P("<b>MISSED</b>"),P("found (8)"),P("found (8)")],
  [P("False alarms on correct code"),P("0"),P("0"),P("0")],
  [P("Profiles generated"),P("216"),P("935"),P("1,126")]],
  [6.0*cm, 3.4*cm, 3.4*cm, 4.2*cm]))
s += [Spacer(1,4), Paragraph("All five bugs are detected by the combined deterministic layers, and the corrected implementation produces no failures. The ablation shows why several layers are needed: the hand-picked boundary layer never probes age 29 and misses that bug, while random fuzzing finds it. The LLM layers are built and validated but have <b>not yet been measured</b>. Figures are from a toy calculator, not a production system.", B)]

s += [Paragraph("7. Implementation approach", H2)] + bullets([
    "<b>Stack:</b> Python, FastAPI, Pydantic, SQLite (audit trail), a web UI served by the API, subprocess isolation, optional LLM API.",
    "<b>Algorithms:</b> hash-map neighbour checks for the monotonic invariant, delta-debugging shrinker for minimal reproductions, TF-IDF retrieval linking each failure to the spec clause it violates.",
    "<b>Phase 1 (done):</b> calculator with planted bugs, reference, Referee, Bully (boundary + random), sandbox, re-verification.",
    "<b>Phase 2:</b> LLM-based Bully and Fixer evaluated across multiple runs; patch quality measured.",
    "<b>Phase 3:</b> support multiple rule sets and languages; connect to a real rating engine's test environment."])

s += [Paragraph("8. Scalability and next steps", H2)] + bullets([
    "Add new rule sets by supplying a spec and a reference implementation, with no change to the pipeline.",
    "Swap the subprocess sandbox for container isolation in production.",
    "Use workflow tooling for durable retries, and connectors to plug into an existing testing agent."])

s += [Paragraph("9. Limitations (stated honestly)", H2)] + bullets([
    "Testing can find bugs but cannot prove their absence; the system reduces risk, it does not guarantee safety.",
    "The Referee is only as good as its invariants and reference; a wrong reference gives wrong verdicts.",
    "LLM-proposed patches can be wrong; hence full re-verification and human approval before acceptance.",
    "The prototype uses a simplified calculator and a subprocess sandbox. It is not a replica of a carrier's core system.",
    "Flarre's platform already includes a Testing Agent. Flarre-Fuzz is designed as a complementary adversarial layer, and its internals were not available for this design."])

s += [Paragraph("10. Expected benefits", H2)] + bullets([
    "Broader edge-case coverage than hand-written tests, in minutes instead of days.",
    "Each failure is traced to a specific business rule, which makes review faster.",
    "A full audit trail for every automated decision and human approval.",
    "Human engineers are freed to review fixes instead of hunting for edge cases."])
doc.build(s)
