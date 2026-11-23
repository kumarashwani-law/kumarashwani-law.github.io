"""Add link previews (Open Graph / Twitter), canonical URLs, preview images, sitemap and robots.txt.

Usage: python3 seo.py <site_dir> [base_url]
Safe to re-run: previously inserted tags are replaced.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SITE = Path(sys.argv[1])
BASE = (sys.argv[2] if len(sys.argv) > 2 else "https://kumarashwani-law.github.io").rstrip("/")
TODAY = date.today().isoformat()
COUNTER = ('\n<!-- counter:start -->\n<script data-goatcounter="https://kumarashwani-law.goatcounter.com/count" '
           'async src="https://gc.zgo.at/count.js"></script>\n<!-- counter:end -->')

SERIF = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
SANS_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SANS_REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"

W, H = 1200, 630
BG = (15, 23, 42)          # navy
ACCENT = (165, 180, 252)   # light indigo, readable on navy
INK = (255, 255, 255)
MUTED = (203, 213, 225)
RULE = (46, 59, 174)


def serif(size, weight="SemiBold"):
    f = ImageFont.truetype(SERIF, size)
    f.set_variation_by_name(weight)
    return f


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_image(path, kicker, title):
    title = title.replace("₹", "Rs ")  # Lora has no rupee glyph
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pad = 80
    d.rectangle([0, 0, W, 10], fill=RULE)
    d.text((pad, 72), kicker.upper(), font=ImageFont.truetype(SANS_SEMI, 24), fill=ACCENT)
    # Fit the title: largest size that fits in 4 lines within the box
    box_w, box_h = W - 2 * pad, 330
    for size in range(66, 34, -2):
        f = serif(size)
        lines = wrap(d, title, f, box_w)
        lh = int(size * 1.22)
        if len(lines) <= 4 and lh * len(lines) <= box_h:
            break
    else:
        lines = lines[:4]
        lines[-1] = lines[-1].rstrip(".,;:") + "…"
    y = 130
    for line in lines:
        d.text((pad, y), line, font=f, fill=INK)
        y += lh
    # Footer
    d.line([pad, H - 120, W - pad, H - 120], fill=(51, 65, 85), width=2)
    d.text((pad, H - 92), "Ashwani Kumar", font=serif(32, "Bold"), fill=INK)
    d.text((pad + d.textlength("Ashwani Kumar", font=serif(32, "Bold")) + 20, H - 84),
           "Advocate · Law, Privacy & AI", font=ImageFont.truetype(SANS_REG, 22), fill=MUTED)
    host = BASE.split("://", 1)[1]
    hf = ImageFont.truetype(SANS_REG, 22)
    d.text((W - pad - d.textlength(host, font=hf), H - 84), host, font=hf, fill=MUTED)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def meta_text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def get(pattern, text, default=""):
    m = re.search(pattern, text, re.S)
    return meta_text(m.group(1)) if m else default


pages = []
for f in sorted([p for p in SITE.glob("*.html") if not p.name.startswith("google")] + list(SITE.glob("posts/*.html")) + list(SITE.glob("topics/*.html")) + list(SITE.glob("guides/*.html")) + list(SITE.glob("guides/*/*.html")) + list(SITE.glob("toolkit/*.html")) + list(SITE.glob("cases/*.html")) + list(SITE.glob("updates/*.html")) + list(SITE.glob("law/*.html")) + list(SITE.glob("reviews/*.html"))):
    rel = f.relative_to(SITE).as_posix()
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"\n<!-- seo:start -->.*?<!-- seo:end -->", "", t, flags=re.S)

    url = f"{BASE}/" if rel == "index.html" else f"{BASE}/{rel}"
    title = get(r"<title>(.*?)</title>", t)
    desc = get(r'<meta name="description" content="(.*?)">', t)
    is_post = rel.startswith(("posts/", "updates/")) or (rel.startswith("guides/") and rel != "guides/index.html")
    is_post = is_post and not rel.endswith("/index.html")
    card_page = is_post or (rel.startswith("cases/") and rel.endswith(".html"))
    published = get(r'<time datetime="(.*?)">', t) if is_post else ""

    lang_m = re.match(r"guides/(hi|te)/", rel)
    if lang_m:
        # Translated guide: reuse the English guide's card (the image font has no Devanagari/Telugu glyphs)
        h1 = get(r"<h1>(.*?)</h1>", t)
        img_rel = f"images/og/{f.stem}.png"
        og_title, img_alt = h1, h1
    elif card_page:
        h1 = re.sub(r"<[^>]+>", "", get(r"<h1>(.*?)</h1>", t))
        kicker = get(r'<span class="kicker">(.*?)</span>', t, "Law, Privacy & AI").replace("Analysis · ", "")
        folder = rel.split("/")[0]
        img_rel = f"images/og/{f.stem}.png" if folder in ("posts", "guides") else f"images/og/{folder}-{f.stem}.png"
        make_image(SITE / img_rel, kicker, h1)
        og_title, img_alt = h1, h1
    else:
        img_rel = "images/og/site.png"
        og_title = title
        img_alt = "Ashwani Kumar — writing on privacy, AI and the law in India"
    img_url = f"{BASE}/{img_rel}"

    tags = [
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:site_name" content="Ashwani Kumar">',
        f'<meta property="og:type" content="{"article" if is_post else "website"}">',
        f'<meta property="og:title" content="{html.escape(og_title)}">',
        f'<meta property="og:description" content="{html.escape(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{img_url}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{html.escape(img_alt)}">',
        f'<meta property="og:locale" content="{ {"hi": "hi_IN", "te": "te_IN"}.get(lang_m.group(1) if lang_m else "", "en_IN") }">',
        f'<link rel="alternate" type="application/rss+xml" title="Ashwani Kumar — Law, Privacy & AI" href="{BASE}/feed.xml">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(og_title)}">',
        f'<meta name="twitter:description" content="{html.escape(desc)}">',
        f'<meta name="twitter:image" content="{img_url}">',
    ]
    gslug = re.match(r"guides/(?:(?:hi|te)/)?([^/]+)\.html$", rel)
    if gslug and gslug.group(1) != "index":
        alts = [("en", f"guides/{gslug.group(1)}.html")] + [(l, f"guides/{l}/{gslug.group(1)}.html") for l in ("hi", "te") if (SITE / "guides" / l / f"{gslug.group(1)}.html").exists()]
        if len(alts) > 1:
            tags += [f'<link rel="alternate" hreflang="{l}" href="{BASE}/{u}">' for l, u in alts]
            tags.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/{alts[0][1]}">')
    if is_post and published:
        tags.append(f'<meta property="article:published_time" content="{published}">')
        tags.append('<meta property="article:author" content="Ashwani Kumar">')
    block = "\n<!-- seo:start -->\n" + "\n".join(tags) + "\n<!-- seo:end -->"
    t = t.replace(f'<meta name="description" content=', "\x00", 1)
    if "\x00" in t:
        # insert right after the description tag
        t = t.replace("\x00", '<meta name="description" content=', 1)
        t = re.sub(r'(<meta name="description" content=".*?">)', lambda m: m.group(1) + block, t, count=1)
    else:
        t = t.replace("</title>", "</title>" + block, 1)
    # Privacy-friendly visitor counter (GoatCounter, no cookies)
    t = re.sub(r"\s*<!-- counter:start -->.*?<!-- counter:end -->\s*", "\n", t, flags=re.S)
    t = t.replace("</body>", COUNTER + "\n</body>", 1)
    f.write_text(t, encoding="utf-8")
    pages.append((url, published or TODAY, is_post, rel))

make_image(SITE / "images/og/site.png", "Advocate · Hyderabad", "Writing on privacy, AI and the law in India.")

# sitemap.xml
prio = {"index.html": "1.0", "writing.html": "0.9", "cases.html": "0.9", "topics/index.html": "0.6", "guides/index.html": "0.9"}
entries = []
for url, lastmod, is_post, rel in sorted(pages, key=lambda p: (not p[0].endswith("/"), p[0])):
    entries.append(
        f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n"
        f"    <priority>{prio.get(rel, '0.9' if rel.startswith('guides/') else ('0.7' if is_post else ('0.6' if rel.startswith('topics/') else '0.3')))}</priority>\n  </url>")
(SITE / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n",
    encoding="utf-8")
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\nSitemap: {BASE}/feed.xml\n", encoding="utf-8")
print(f"{len(pages)} pages tagged; sitemap has {len(entries)} URLs")
