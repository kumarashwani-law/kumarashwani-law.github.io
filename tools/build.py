"""Build blog post pages, the Writing archive and the Home page from LinkedIn posts."""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).parent
OUT = Path(sys.argv[1])

posts = json.load(open(SRC / "posts.json", encoding="utf-8"))
meta = json.load(open(SRC / "meta.json", encoding="utf-8"))

TOPIC = {
    "0": "surveillance", "2": "surveillance", "5": "surveillance", "14": "surveillance",
    "3": "data", "4": "data", "20": "data", "29": "data", "32": "data",
    "6": "ai-courts", "21": "ai-courts", "22": "ai-courts", "25": "ai-courts", "28": "ai-courts",
    "7": "deepfakes", "8": "deepfakes", "13": "deepfakes", "27": "deepfakes",
    "9": "platforms", "16": "platforms", "18": "platforms", "19": "platforms",
    "23": "copyright", "30": "copyright", "31": "copyright",
    "1": "other", "10": "other", "12": "other", "17": "other", "24": "other", "26": "other",
}
TOPIC_LABEL = {
    "surveillance": "Surveillance & Privacy",
    "data": "Data Protection",
    "ai-courts": "AI & the Courts",
    "deepfakes": "Deepfakes & Personality Rights",
    "platforms": "Platforms & Free Speech",
    "copyright": "Copyright & AI",
    "other": "Tech Law",
}
KICKER = {
    "1": "Weekly Roundup", "10": "Legal Practice", "12": "Gaming Law", "17": "Cyber Fraud",
    "24": "Cybersecurity", "26": "Child Safety Online",
}
FILTERS = ["all", "data", "surveillance", "ai-courts", "deepfakes", "platforms", "copyright", "other"]
FILTER_LABEL = {"all": "All", "data": "Data protection", "surveillance": "Surveillance & privacy",
                "ai-courts": "AI & the courts", "deepfakes": "Deepfakes", "platforms": "Platforms & speech",
                "copyright": "Copyright", "other": "Other"}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;'
         'family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&amp;display=swap" rel="stylesheet">')
LINKEDIN = "https://www.linkedin.com/in/advashwanikumar"
EMAIL = "kumar.ashwani040801@gmail.com"


def esc(s):
    return html.escape(s, quote=True)


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    words = s.split("-")
    out = []
    for w in words:
        if len("-".join(out + [w])) > 60:
            break
        out.append(w)
    return "-".join(out)


def linkify(text):
    parts = re.split(r"(https?://[^\s)]+)", text)
    res = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            res.append(f'<a href="{esc(p)}" rel="noopener">{esc(p)}</a>')
        else:
            res.append(esc(p))
    return "".join(res)


def split_post(body):
    lines = body.split("\n")
    title = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()
    tags = []
    blocks = [b for b in re.split(r"\n\s*\n", rest) if b.strip()]
    if blocks and all(t.startswith("#") for t in blocks[-1].split()):
        tags = [t.lstrip("#") for t in blocks[-1].split()]
        blocks = blocks[:-1]
    return title, blocks, tags


def summary(blocks):
    first = blocks[0].split("\n")[0] if blocks else ""
    if len(first) > 190:
        cut = first[:190].rsplit(" ", 1)[0]
        first = cut.rstrip(",;:") + "…"
    return first


def header(prefix, current=""):
    cur = ' aria-current="page"' if current == "writing" else ""
    return f'''<header class="site-header">
<div class="wrap">
<a class="brand" href="{prefix}index.html"><b>Ashwani Kumar</b><span>Law · Privacy · AI</span></a>
<nav class="nav" aria-label="Main">
<a href="{prefix}writing.html"{cur}>Writing</a>
<a href="{prefix}index.html#topics">Topics</a>
<a href="{prefix}index.html#follow">Follow</a>
</nav>
</div>
</header>'''


def footer(prefix, contact=False):
    extra = ""
    if contact:
        extra = (f'<span>Hyderabad, Telangana</span><a href="mailto:{EMAIL}">{EMAIL}</a>'
                 f'<a href="{LINKEDIN}">LinkedIn</a>')
    return f'''<footer class="site-footer">
<div class="wrap">
<p>This website is for information only. It is not legal advice and is not intended to solicit work, in keeping with the Bar Council of India Rules. <a href="{prefix}disclaimer.html">Read the full disclaimer</a>.</p>
<div class="contact">{extra}<span style="color:var(--muted)">© 2026 Ashwani Kumar</span></div>
</div>
</footer>'''


def head(title, desc, prefix):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{FONTS}
<link rel="stylesheet" href="{prefix}style.css">
<script src="{prefix}gate.js"></script>
</head>
<body>
'''


def render_block(block):
    lines = block.split("\n")
    inner = "<br>\n".join(linkify(l) for l in lines)
    return f"<p>{inner}</p>"


# Build records, newest first (keys are in LinkedIn order already)
order = sorted(posts.keys(), key=lambda k: (meta[k]["date"], -int(k)), reverse=True)
records = []
used = set()
for k in order:
    title, blocks, tags = split_post(posts[k])
    slug = slugify(title)
    while slug in used:
        slug += "-2"
    used.add(slug)
    topic = TOPIC[k]
    records.append({
        "k": k, "title": title, "blocks": blocks, "tags": tags, "slug": slug,
        "topic": topic, "kicker": KICKER.get(k, TOPIC_LABEL[topic]),
        "date": meta[k]["date"],
        "url": (f"https://www.linkedin.com/feed/update/urn:li:activity:{meta[k]['id']}/" if meta[k].get("id") else None),
        "summary": summary(blocks),
        "slides": bool(re.search(r"\bslides?\b", posts[k], re.I)),
    })

(OUT / "posts").mkdir(parents=True, exist_ok=True)

for i, r in enumerate(records):
    li_btn = (f'<a class="btn btn-ghost btn-sm" href="{esc(r["url"])}">View on LinkedIn</a>\n' if r["url"] else "")
    body_html = "\n".join(render_block(b) for b in r["blocks"])
    tags_html = "".join(f'<span class="tag-pill">#{esc(t)}</span>' for t in r["tags"])
    slides_note = ("This post first appeared on LinkedIn with a slide deck. "
                   if r["slides"] else "This post first appeared on LinkedIn. ")
    origin = (f'{slides_note}<a href="{esc(r["url"])}">See the original post on LinkedIn</a>.' if r["url"]
              else f'This post also appears on <a href="{LINKEDIN}">LinkedIn</a>.')
    related = [x for x in records if x["topic"] == r["topic"] and x is not r][:3]
    if len(related) < 3:
        related += [x for x in records if x is not r and x not in related][: 3 - len(related)]
    rel_html = "\n".join(
        f'<a class="card" href="{x["slug"]}.html"><span class="kicker">{esc(x["kicker"])}</span>'
        f'<h3>{esc(x["title"])}</h3><span class="meta">{fmt_date(x["date"])}</span></a>' for x in related)
    page = head(f'{r["title"]} — Ashwani Kumar', r["summary"], "../") + header("../") + f'''
<main>
<article class="article">
<a href="../writing.html" style="font-size:14px;font-weight:500;text-decoration:none">← All writing</a>
<span class="kicker">{esc(r["kicker"])}</span>
<h1>{esc(r["title"])}</h1>
<div class="byline">
<div style="display:flex;gap:12px;align-items:center">
<div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">Ashwani Kumar</span><span class="meta">Advocate · <time datetime="{r["date"]}">{fmt_date(r["date"])}</time></span></div>
</div>
<div class="row" style="gap:8px">
{li_btn}<button type="button" class="btn btn-ghost btn-sm copy-link">Copy link</button>
</div>
</div>
<div class="prose post-body">
{body_html}
</div>
<div class="tags">{tags_html}</div>
<p class="origin">{origin}</p>
</article>
<section class="band">
<div class="wrap" style="padding-top:64px;padding-bottom:64px;gap:24px">
<h2 class="h2" style="font-size:28px">Keep reading</h2>
<div class="grid">
{rel_html}
</div>
</div>
</section>
</main>
''' + footer("../") + '''
<script>
(function () {
  var btn = document.querySelector('.copy-link');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var url = location.href.split('#')[0];
    try {
      navigator.clipboard.writeText(url).then(function () {
        btn.textContent = 'Link copied';
        setTimeout(function () { btn.textContent = 'Copy link'; }, 2000);
      }, function () { btn.textContent = 'Copy failed'; });
    } catch (e) { btn.textContent = 'Copy failed'; }
  });
})();
</script>
</body>
</html>
'''
    (OUT / "posts" / f'{r["slug"]}.html').write_text(page, encoding="utf-8")

# Writing archive
chips = "\n".join(
    f'<button type="button" class="chip" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}">{FILTER_LABEL[f]}</button>'
    for f in FILTERS)
items = "\n".join(
    f'<a class="item" data-topic="{r["topic"]}" href="posts/{r["slug"]}.html"><span class="date">{fmt_date(r["date"])}</span>'
    f'<span class="body"><span class="t">{esc(r["title"])}</span><span class="s">{esc(r["summary"])}</span></span>'
    f'<span class="tag">{esc(r["kicker"])}</span></a>' for r in records)
writing = head("Writing — Ashwani Kumar",
               "Commentary by advocate Ashwani Kumar on data protection, AI, surveillance, platforms and technology law in India.",
               "") + header("", "writing") + f'''
<main class="wrap">
<section class="page-head">
<h1>Writing</h1>
<p>{len(records)} pieces on privacy, AI and technology law in India, newest first. Each one first appeared on <a href="{LINKEDIN}">LinkedIn</a>.</p>
<div class="filters" role="group" aria-label="Filter by topic">
{chips}
</div>
</section>
<section class="groups">
<div class="group" id="list">
{items}
</div>
<p id="empty" class="small" hidden>No posts on this topic yet.</p>
</section>
</main>
''' + footer("") + '''
<script>
(function () {
  var chips = document.querySelectorAll('.chip');
  var items = document.querySelectorAll('.item');
  var empty = document.getElementById('empty');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var f = chip.getAttribute('data-filter');
      var shown = 0;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      items.forEach(function (it) {
        var on = f === 'all' || it.getAttribute('data-topic') === f;
        it.hidden = !on; if (on) shown++;
      });
      empty.hidden = shown > 0;
    });
  });
})();
</script>
</body>
</html>
'''
(OUT / "writing.html").write_text(writing, encoding="utf-8")

# Home page: replace featured + latest sections
index_path = OUT / "index.html"
idx = index_path.read_text(encoding="utf-8")
f = records[0]
featured = f'''<section class="wrap section">
<a class="featured" href="posts/{f["slug"]}.html">
<div class="text">
<span class="kicker">Latest · {esc(f["kicker"])}</span>
<h2>{esc(f["title"])}</h2>
<p>{esc(f["summary"])}</p>
<span class="meta">{fmt_date(f["date"])}</span>
</div>
</a>
</section>'''
cards = "\n".join(
    f'<a class="card" href="posts/{r["slug"]}.html"><span class="kicker">{esc(r["kicker"])}</span>'
    f'<h3>{esc(r["title"])}</h3><p>{esc(r["summary"])}</p><span class="meta">{fmt_date(r["date"])}</span></a>'
    for r in records[1:7])
latest = f'''<section class="wrap section">
<div class="section-head">
<h2 class="h2">Recent writing</h2>
<a href="writing.html" style="font-size:15px;font-weight:600;padding:12px 0">View all {len(records)}</a>
</div>
<div class="grid">
{cards}
</div>
</section>'''
start = idx.index('<section class="wrap section">\n<a class="featured"')
end = idx.index('<section id="topics"')
idx = idx[:start] + featured + "\n\n" + latest + "\n\n" + idx[end:]
idx = idx.replace('href="consent-managers-ai.html">Read the latest', f'href="posts/{f["slug"]}.html">Read the latest')
index_path.write_text(idx, encoding="utf-8")

print(len(records), "posts built; latest:", records[0]["slug"])
for r in records:
    print(r["date"], r["topic"], r["slug"])
