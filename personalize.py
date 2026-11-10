"""Put YOUR name and college into every deliverable.
Usage:  python personalize.py "Your Full Name (as per Aadhaar)" "Your College Name"
Updates: interactive deck, PPTX, and regenerates the proposal PDF (needs: pip install reportlab)."""
import sys, subprocess, zipfile, shutil
from html import escape
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit(__doc__)
name, college = sys.argv[1], sys.argv[2]
docs = Path(__file__).parent / "docs"

# 1) interactive deck
p = docs / "presentation_interactive.html"
t = p.read_text(encoding="utf-8").replace("[Your Full Name] · [Your College Name]", f"{escape(name)} · {escape(college)}")
p.write_text(t, encoding="utf-8"); print("updated", p.name)

# 2) PPTX (replace placeholders inside the slide XML)
src = docs / "FlarreFuzz_Presentation.pptx"; tmp = docs / "_tmp.pptx"
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
            data = data.decode("utf-8").replace("[Your Full Name]", escape(name)).replace("[Your College Name]", escape(college)).encode("utf-8")
        zout.writestr(item, data)
shutil.move(tmp, src); print("updated", src.name)

# 3) proposal PDF
try:
    subprocess.run([sys.executable, str(docs / "source" / "build_proposal.py"), name, college], check=True)
    print("regenerated FlarreFuzz_Proposal.pdf")
except Exception as e:
    print("PDF not regenerated (run: pip install reportlab, then re-run). Reason:", e)
print("Done. Open each file once to confirm your name appears.")
