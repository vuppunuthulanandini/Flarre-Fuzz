import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY="#0B1020"; CYAN="#1FB6E8"; GREEN="#2ECC9A"; AMBER="#F5A623"; ROSE="#E8557A"; GREY="#8A93A8"
fig, ax = plt.subplots(figsize=(13, 7.2), dpi=200)
fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
ax.set_xlim(0, 13); ax.set_ylim(0, 7.2); ax.axis("off")

def box(x, y, w, h, title, sub, color, tag=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#151B33", ec=color, lw=2.2))
    ax.text(x+w/2, y+h-0.38, title, ha="center", va="center", color="white", fontsize=13, fontweight="bold")
    ax.text(x+w/2, y+h/2-0.12, sub, ha="center", va="center", color="#C9D1E6", fontsize=9.2, linespacing=1.45)
    if tag:
        ax.text(x+w/2, y+0.22, tag, ha="center", va="center", color=color, fontsize=8.5, fontweight="bold")

def arrow(x1, y1, x2, y2, label=None, color=GREY, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                                 color=color, lw=1.8, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+0.18, label, ha="center", color=color, fontsize=8.2)

ax.text(6.5, 6.85, "Flarre-Fuzz: system architecture", ha="center", color="white", fontsize=18, fontweight="bold")
ax.text(6.5, 6.5, "Adversarial safety layer for AI-written insurance code", ha="center", color=GREY, fontsize=10.5)

box(0.4, 4.0, 2.4, 1.8, "INPUT", "Code under test\n+ business rules\n(plain English spec)", CYAN)
box(3.5, 4.0, 2.7, 1.8, "BULLY", "1. Boundary values\n2. Random fuzzing\n3. LLM-invented rare cases", ROSE, "LLM + code (validated)")
box(6.9, 4.0, 2.7, 1.8, "SANDBOX", "Isolated subprocess\nTimeout + crash capture\n(stand-in for system clone)", AMBER, "Isolated run")
box(10.3, 4.0, 2.4, 1.8, "REFEREE", "Invariants +\nreference calculator\nNo LLM, repeatable", GREEN, "Deterministic code")

box(10.3, 1.0, 2.4, 1.8, "FIXER", "Minimal repros +\nspec clause, then\nproposes patch", ROSE, "LLM")
box(6.9, 1.0, 2.7, 1.8, "RE-VERIFY", "Full suite re-run on\npatched code (max 3\nattempts, then stop)", GREEN, "Deterministic code")
box(3.5, 1.0, 2.7, 1.8, "HUMAN REVIEW", "Sees diff + re-test\nresult. Approve or\nReject", CYAN, "Final decision")
box(0.4, 1.0, 2.4, 1.8, "AUDIT LOG", "Timestamp, bug, fix,\ndecision, re-test\nresult", AMBER, "Traceability")

arrow(2.85, 4.9, 3.45, 4.9, "spec")
arrow(6.25, 4.9, 6.85, 4.9, "profiles")
arrow(9.65, 4.9, 10.25, 4.9, "outputs")
arrow(11.5, 3.95, 11.5, 2.85, "failures", ROSE)
arrow(10.25, 1.9, 9.65, 1.9, "patch")
arrow(6.85, 1.9, 6.25, 1.9, "passes")
arrow(3.45, 1.9, 2.85, 1.9, "decision")
arrow(8.25, 2.85, 8.25, 3.95, "re-run", GREEN, rad=0.0)

ax.text(6.5, 0.4, "Orchestrator (plain Python) controls the loop. LLMs handle creativity and explanation; deterministic code handles correctness. "
        "Delivered as a FastAPI backend with SQLite audit trail and a web UI.", ha="center", color=GREY, fontsize=9)
plt.savefig(str(__import__("pathlib").Path(__file__).resolve().parents[1] / "architecture.png"), facecolor=NAVY, bbox_inches="tight")
