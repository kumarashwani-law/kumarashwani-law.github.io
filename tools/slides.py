"""Turn carousel PDFs into slide images for the post pages.

Put each carousel PDF in tools/slides/ named after the post's page, e.g.
  tools/slides/right-to-privacy-in-a-public-place-what-kind-of-pils-are.pdf
then run:  python3 tools/slides.py <site_dir>
and rebuild with tools/build.py and tools/seo.py.

Images go to images/slides/<slug>/01.webp, 02.webp, ... (1080 px wide).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

SITE = Path(sys.argv[1])
SRC = Path(__file__).parent / "slides"
WIDTH = 1080

if not SRC.exists():
    print("No tools/slides folder; nothing to do.")
    sys.exit(0)

done = 0
for pdf in sorted(SRC.glob("*.pdf")):
    slug = pdf.stem
    if not (SITE / "posts" / f"{slug}.html").exists():
        print(f"SKIP {pdf.name}: no post page named posts/{slug}.html")
        continue
    out = SITE / "images" / "slides" / slug
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.webp"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "150", "-png", str(pdf), f"{tmp}/p"], check=True)
        pages = sorted(Path(tmp).glob("p-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        for i, png in enumerate(pages, 1):
            im = Image.open(png).convert("RGB")
            if im.width != WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            im.save(out / f"{i:02d}.webp", "WEBP", quality=82, method=6)
    print(f"{slug}: {len(pages)} slides")
    done += 1
print(f"{done} carousel(s) converted")
