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

GROTESK = str(Path(__file__).parent / "fonts" / "SpaceGrotesk.ttf")  # OFL, from Google Fonts

W, H = 1200, 630
BG = (25, 26, 35)          # charcoal #191A23
LIME = (185, 255, 102)     # #B9FF66
INK = (255, 255, 255)
MUTED = (201, 202, 208)


def grotesk(size, weight=500):
    f = ImageFont.truetype(GROTESK, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def star(d, cx, cy, r, fill):
    """Four-point sparkle, the site's mark."""
    import math
    pts = []
    for i in range(96):
        t = i / 96 * 2 * math.pi
        x, y = math.cos(t), math.sin(t)
        pts.append((cx + r * math.copysign(abs(x) ** 3, x), cy + r * math.copysign(abs(y) ** 3, y)))
    d.polygon(pts, fill=fill)


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
    title = title.replace("₹", "Rs ")  # the font has no rupee glyph
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pad = 80
    # decoration: lime orbit and sparkles, top right
    orbit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(orbit)
    od.ellipse([860, -40, 1260, 170], outline=LIME + (255,), width=3)
    orbit = orbit.rotate(-12, center=(1060, 65))
    img.paste(orbit, (0, 0), orbit)
    star(d, 1080, 70, 46, LIME)
    star(d, 985, 150, 16, INK)
    d.ellipse([1150, 160, 1164, 174], fill=LIME)
    # kicker as a lime tag
    kf = grotesk(22, 700)
    k = kicker.upper()
    tw = d.textlength(k, font=kf)
    d.rounded_rectangle([pad, 64, pad + tw + 28, 64 + 42], radius=9, fill=LIME)
    d.text((pad + 14, 73), k, font=kf, fill=BG)
    # title: largest size that fits in 4 lines
    box_w, box_h = W - 2 * pad - 120, 340
    for size in range(68, 34, -2):
        f = grotesk(size, 500)
        lines = wrap(d, title, f, box_w)
        lh = int(size * 1.16)
        if len(lines) <= 4 and lh * len(lines) <= box_h:
            break
    else:
        lines = lines[:4]
        lines[-1] = lines[-1].rstrip(".,;:") + "…"
    y = 140
    for line in lines:
        d.text((pad, y), line, font=f, fill=INK)
        y += lh
    # footer
    d.line([pad, H - 118, W - pad, H - 118], fill=(58, 59, 69), width=2)
    star(d, pad + 14, H - 70, 14, LIME)
    nf = grotesk(30, 700)
    d.text((pad + 40, H - 90), "Ashwani Kumar", font=nf, fill=INK)
    sf = grotesk(22, 400)
    d.text((pad + 40 + d.textlength("Ashwani Kumar", font=nf) + 18, H - 82), "Advocate · Law, Privacy & AI", font=sf, fill=MUTED)
    host = BASE.split("://", 1)[1]
    d.text((W - pad - d.textlength(host, font=sf), H - 82), host, font=sf, fill=LIME)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def meta_text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def get(pattern, text, default=""):
    m = re.search(pattern, text, re.S)
    return meta_text(m.group(1)) if m else default


pages = []
for f in sorted([p for p in SITE.glob("*.html") if not p.name.startswith("google") and p.name != "offline.html"] + list(SITE.glob("posts/*.html")) + list(SITE.glob("topics/*.html")) + list(SITE.glob("guides/*.html")) + list(SITE.glob("guides/*/*.html")) + list(SITE.glob("toolkit/*.html")) + list(SITE.glob("cases/*.html")) + list(SITE.glob("updates/*.html")) + list(SITE.glob("law/*.html")) + list(SITE.glob("reviews/*.html"))):
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
    tags += [
        '<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#121319" media="(prefers-color-scheme: dark)">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="format-detection" content="telephone=no, date=no, address=no, email=no">',
        '<meta name="apple-mobile-web-app-title" content="Ashwani Kumar">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" href="/icons/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
    ]
    t = t.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
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
