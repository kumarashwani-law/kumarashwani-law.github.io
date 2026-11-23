"""Build blog post pages, the Writing archive and the Home page from LinkedIn posts."""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

from PIL import Image

import extras as X

SRC = Path(__file__).parent
OUT = Path(sys.argv[1])

posts = json.load(open(SRC / "posts.json", encoding="utf-8"))
meta = json.load(open(SRC / "meta.json", encoding="utf-8"))

TOPIC = {
    "0": "surveillance", "2": "surveillance", "5": "surveillance", "14": "surveillance",
    "3": "data", "4": "data", "20": "data", "29": "data", "32": "data",
    "6": "ai-courts", "21": "ai-courts", "22": "ai-courts", "25": "ai-courts", "28": "ai-courts", "35": "ai-courts",
    "7": "deepfakes", "8": "deepfakes", "13": "deepfakes", "27": "deepfakes", "33": "deepfakes",
    "9": "platforms", "16": "platforms", "18": "platforms", "19": "platforms",
    "23": "copyright", "30": "copyright", "31": "copyright", "34": "copyright",
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
TOPIC_PAGE = {
    "data": ("Data Protection", "The DPDP Act and Rules, the Data Protection Board, consent, and what businesses must do before May 2027."),
    "surveillance": ("Surveillance & Privacy", "Facial recognition, phone extraction, police AI tools and CCTV, tested against the right to privacy."),
    "ai-courts": ("AI & the Courts", "AI in courts, tribunals and government offices: fake citations, deepfake evidence and disclosure rules."),
    "deepfakes": ("Deepfakes & Personality Rights", "Deepfakes, satire and personality rights: how courts and the IT Rules protect faces and voices."),
    "platforms": ("Platforms & Free Speech", "Account blocks, takedowns, the Grievance Appellate Committee and platform jurisdiction under the IT Act and Rules."),
    "copyright": ("Copyright & AI", "Can AI train on your work? News publishers, licensing and fair dealing in India and abroad."),
    "other": ("More Tech Law", "Online gaming, digital arrest scams, children's online safety, cybersecurity and legal practice."),
}
FILTERS = ["all", "data", "surveillance", "ai-courts", "deepfakes", "platforms", "copyright", "other"]
FILTER_LABEL = {"all": "All", "data": "Data protection", "surveillance": "Surveillance & privacy",
                "ai-courts": "AI & the courts", "deepfakes": "Deepfakes", "platforms": "Platforms & speech",
                "copyright": "Copyright", "other": "Other"}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&amp;display=swap" rel="stylesheet">')
LINKEDIN = "https://www.linkedin.com/in/advashwanikumar"
import hashlib as _hl
CSS_V = _hl.sha1((OUT / "style.css").read_bytes()).hexdigest()[:8]
JS_V = _hl.sha1((OUT / "site.js").read_bytes()).hexdigest()[:8]
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


def nav(prefix, current=""):
    def cur(name):
        return ' aria-current="page"' if current == name else ""
    return f'''<nav class="nav" aria-label="Main">
<a href="{prefix}writing.html"{cur("writing")}>Writing</a>
<a href="{prefix}guides/index.html"{cur("guides")}>Guides</a>
<a href="{prefix}toolkit/index.html"{cur("tools")}>Tools</a>
<a href="{prefix}topics/index.html"{cur("topics")}>Topics</a>
<a href="{prefix}cases.html"{cur("cases")}>Case tracker</a>
<a href="{prefix}index.html#follow">Follow</a>
</nav>'''


def header(prefix, current=""):
    return f'''<header class="site-header">
<div class="wrap">
<a class="brand" href="{prefix}index.html"><b>Ashwani Kumar</b><span>Law · Privacy · AI</span></a>
{nav(prefix, current)}
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
<div class="contact">{extra}<span class="row" style="gap:6px 16px"><a href="{prefix}glossary.html">Glossary</a><a href="{prefix}toolkit/index.html">Tools</a><a href="{prefix}feed.xml">RSS</a></span><span style="color:var(--muted)">© 2026 Ashwani Kumar</span></div>
</div>
</footer>'''


def head(title, desc, prefix, lang="en"):
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{FONTS}
<link rel="stylesheet" href="{prefix}style.css?v={CSS_V}">
<script src="{prefix}gate.js"></script>
<script src="{prefix}site.js?v={JS_V}"></script>
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
    body_html = X.add_glossary("\n".join(render_block(b) for b in r["blocks"]))
    mins = X.reading_minutes(body_html)
    post_url = f"{X.SITE_URL}/posts/{r['slug']}.html"
    pdf_rel = X.slides_pdf(OUT, r["slug"])
    pdf_btn = (f'<a class="btn btn-ghost btn-sm" href="../{pdf_rel}" download>Download slides (PDF)</a>' if pdf_rel else "")
    tags_html = "".join(f'<span class="tag-pill">#{esc(t)}</span>' for t in r["tags"])
    slide_dir = OUT / "images" / "slides" / r["slug"]
    slide_imgs = sorted(slide_dir.glob("*.webp")) if slide_dir.exists() else []
    slides_html = ""
    if slide_imgs:
        n = len(slide_imgs)
        tj = slide_dir / "text.json"
        stexts = json.load(open(tj, encoding="utf-8")) if tj.exists() else []

        def alt(j):
            t = stexts[j] if j < len(stexts) else ""
            if len(t) > 220:
                t = t[:220].rsplit(" ", 1)[0] + "…"
            return esc(f"Slide {j + 1} of {n}" + (f": {t}" if t else ""))
        figs = "\n".join(
            f'<li class="slide"><img src="../images/slides/{r["slug"]}/{p.name}" width="{Image.open(p).width}" height="{Image.open(p).height}" '
            f'loading="{"eager" if j == 0 else "lazy"}" alt="{alt(j)}"></li>'
            for j, p in enumerate(slide_imgs))
        slides_html = f'''<section class="slides" aria-roledescription="carousel" aria-label="Slides for this post">
<div class="slides-head"><h2 class="label" style="margin:0">Slides</h2><span class="slides-count" aria-live="polite">1 / {n}</span></div>
<ol class="slides-track" tabindex="0">
{figs}
</ol>
<div class="slides-nav">
<button type="button" class="btn btn-ghost btn-sm slides-prev" aria-label="Previous slide">← Previous</button>
<button type="button" class="btn btn-ghost btn-sm slides-next" aria-label="Next slide">Next →</button>
</div>
</section>'''
    if slide_imgs:
        slides_note = "This post first appeared on LinkedIn with the slides above. "
    else:
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
{X.crumbs("../", [("Home", "index.html"), ("Writing", "writing.html"), (r["title"], None, "posts/" + r["slug"] + ".html")])}
<span class="kicker">Analysis · {esc(r["kicker"])}</span>
<h1>{esc(r["title"])}</h1>
<div class="byline">
<div style="display:flex;gap:12px;align-items:center">
<div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">Ashwani Kumar</span><span class="meta">Advocate · <time datetime="{r["date"]}">{fmt_date(r["date"])}</time> · <span class="read-time">{mins} min read</span></span></div>
</div>
<div class="row" style="gap:8px">
{li_btn}<button type="button" class="btn btn-ghost btn-sm copy-link">Copy link</button>
</div>
</div>
<div class="prose post-body">
{body_html}
</div>
{slides_html}
<div class="tags">{tags_html}</div>
<p class="origin">{origin}</p>
<div class="article-actions">
{X.share_row(post_url, r["title"])}
<div class="row" style="gap:8px">{pdf_btn}{X.cite_block("cite-" + r["slug"][:20], r["title"], r["date"], post_url)}</div>
</div>
{X.subscribe_box("p-follow")}
{X.comments_html("posts/" + r["slug"])}
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
(function () {
  var track = document.querySelector('.slides-track');
  if (!track) return;
  var slides = track.querySelectorAll('.slide');
  var count = document.querySelector('.slides-count');
  var prev = document.querySelector('.slides-prev');
  var next = document.querySelector('.slides-next');
  function current() { return Math.round(track.scrollLeft / track.clientWidth); }
  function go(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    track.scrollTo({ left: i * track.clientWidth, behavior: 'smooth' });
  }
  function update() {
    var i = current();
    count.textContent = (i + 1) + ' / ' + slides.length;
    prev.disabled = i === 0;
    next.disabled = i === slides.length - 1;
  }
  prev.addEventListener('click', function () { go(current() - 1); });
  next.addEventListener('click', function () { go(current() + 1); });
  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(current() + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(current() - 1); }
  });
  var t; track.addEventListener('scroll', function () { clearTimeout(t); t = setTimeout(update, 60); });
  update();
})();
</script>
</body>
</html>
'''
    (OUT / "posts" / f'{r["slug"]}.html').write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- search index
def plain(r):
    return " ".join([r["title"]] + r["blocks"] + r["tags"])


def slide_text(r):
    tj = OUT / "images" / "slides" / r["slug"] / "text.json"
    return " ".join(json.load(open(tj, encoding="utf-8"))) if tj.exists() else ""


search_index = [{"s": r["slug"], "x": re.sub(r"\s+", " ", plain(r) + " " + slide_text(r)).lower()} for r in records]
(OUT / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
                                       encoding="utf-8")


def item_html(r, prefix=""):
    return (f'<a class="item" data-topic="{r["topic"]}" data-slug="{r["slug"]}" href="{prefix}posts/{r["slug"]}.html">'
            f'<span class="date">{fmt_date(r["date"])}</span>'
            f'<span class="body"><span class="t">{esc(r["title"])}</span><span class="s">{esc(r["summary"])}</span></span>'
            f'<span class="tag">{esc(r["kicker"])}</span></a>')


# ---------------------------------------------------------------- Writing archive (search + filters)
chips = "\n".join(
    f'<button type="button" class="chip" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}">{FILTER_LABEL[f]}</button>'
    for f in FILTERS)
items = "\n".join(item_html(r) for r in records)
writing = head("Writing — Ashwani Kumar",
               "Commentary by advocate Ashwani Kumar on data protection, AI, surveillance, platforms and technology law in India.",
               "") + header("", "writing") + f'''
<main class="wrap">
<section class="page-head">
<h1>Writing</h1>
<p>{len(records)} pieces on privacy, AI and technology law in India, newest first. Each one first appeared on <a href="{LINKEDIN}">LinkedIn</a>.</p>
<form class="search" role="search" onsubmit="return false">
<label for="q" class="label">Search all posts</label>
<input id="q" type="search" placeholder="Try “deepfake”, “DPDP”, “Section 79” or a case name" autocomplete="off">
</form>
<div class="filters" role="group" aria-label="Filter by topic">
{chips}
</div>
<p id="result-count" class="small" aria-live="polite"></p>
</section>
<section class="groups">
<div class="group" id="list">
{items}
</div>
<p id="empty" class="small" hidden>No posts match. Try a different word, or choose “All”.</p>
</section>
</main>
''' + footer("") + '''
<script>
(function () {
  var chips = document.querySelectorAll('.chip');
  var items = document.querySelectorAll('.item');
  var empty = document.getElementById('empty');
  var count = document.getElementById('result-count');
  var input = document.getElementById('q');
  var topic = 'all', index = null, timer;
  function load() {
    if (index) return Promise.resolve(index);
    return fetch('search-index.json').then(function (r) { return r.json(); }).then(function (d) {
      index = {}; d.forEach(function (e) { index[e.s] = e.x; }); return index;
    }).catch(function () { index = {}; return index; });
  }
  function apply() {
    var q = input.value.trim().toLowerCase();
    var words = q ? q.split(/\\s+/) : [];
    var go = function () {
      var shown = 0;
      items.forEach(function (it) {
        var okTopic = topic === 'all' || it.getAttribute('data-topic') === topic;
        var text = (index && index[it.getAttribute('data-slug')]) || it.textContent.toLowerCase();
        var okText = words.every(function (w) { return text.indexOf(w) !== -1; });
        var on = okTopic && okText;
        it.hidden = !on; if (on) shown++;
      });
      empty.hidden = shown > 0;
      count.textContent = (q || topic !== 'all') ? shown + (shown === 1 ? ' post' : ' posts') : '';
    };
    if (words.length) load().then(go); else go();
  }
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      topic = chip.getAttribute('data-filter');
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      apply();
    });
  });
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(apply, 120); });
  var params = new URLSearchParams(location.search);
  if (params.get('q')) { input.value = params.get('q'); apply(); }
})();
</script>
</body>
</html>
'''
(OUT / "writing.html").write_text(writing, encoding="utf-8")

# ---------------------------------------------------------------- Topic pages
(OUT / "topics").mkdir(exist_ok=True)
counts = {t: sum(1 for r in records if r["topic"] == t) for t in TOPIC_PAGE}
topic_cards = "\n".join(
    f'<a class="topic" href="{{prefix}}topics/{t}.html"><h3>{esc(label)}</h3><p>{esc(desc)}</p>'
    f'<span class="meta">{counts[t]} post{"s" if counts[t] != 1 else ""}</span></a>'
    for t, (label, desc) in TOPIC_PAGE.items() if counts[t])

topics_index = head("Topics — Ashwani Kumar",
                    "Browse Ashwani Kumar's writing on Indian technology law by topic.", "../") + header("../", "topics") + f'''
<main class="wrap">
<section class="page-head">
<h1>Topics</h1>
<p>Browse the writing by subject. For pending cases and hearing dates, see the <a href="../cases.html">case tracker</a>.</p>
</section>
<section class="grid" style="padding-bottom:96px">
{topic_cards.replace("{prefix}topics/", "")}
</section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
(OUT / "topics" / "index.html").write_text(topics_index, encoding="utf-8")

for t, (label, desc) in TOPIC_PAGE.items():
    rs = [r for r in records if r["topic"] == t]
    if not rs:
        continue
    others = " · ".join(f'<a href="{o}.html">{esc(TOPIC_PAGE[o][0])}</a>' for o in TOPIC_PAGE if o != t and counts[o])
    page = head(f"{label} — Ashwani Kumar", f"{desc} Writing by advocate Ashwani Kumar.", "../") + header("../", "topics") + f'''
<main class="wrap">
<section class="page-head">
<a href="index.html" style="font-size:14px;font-weight:500;text-decoration:none">← All topics</a>
<h1>{esc(label)}</h1>
<p>{esc(desc)}</p>
<p class="small">{len(rs)} post{"s" if len(rs) != 1 else ""}, newest first.</p>
</section>
<section class="groups">
<div class="group">
{chr(10).join(item_html(r, "../") for r in rs)}
</div>
<p class="small">Other topics: {others}</p>
</section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
    (OUT / "topics" / f"{t}.html").write_text(page, encoding="utf-8")

# ---------------------------------------------------------------- Case tracker
cases = json.load(open(SRC / "cases.json", encoding="utf-8"))
slug_title = {r["slug"]: r["title"] for r in records}
STATUS = {"pending": "Pending", "watch": "To watch", "decided": "Decided"}


def case_card(c):
    posts_html = "".join(
        f'<li><a href="posts/{p}.html">{esc(slug_title[p])}</a></li>' for p in c.get("posts", []) if p in slug_title)
    src_html = " · ".join(f'<a href="{esc(u)}" rel="noopener">{esc(n)}</a>' for n, u in c.get("sources", []))
    if c["status"] == "decided":
        when = f'<span class="case-when"><span class="label">Decided</span><b>{fmt_date(c["decided"])}</b></span>'
    else:
        nd = fmt_date(c["next"]) if c.get("next") and not c.get("next_note") else (c.get("next_note") or "—")
        when = f'<span class="case-when"><span class="label">Next</span><b>{esc(nd)}</b></span>'
    return f'''<article class="case" id="{c["id"]}" data-status="{c["status"]}">
<div class="case-top">
<span class="pill pill-{c["status"]}">{STATUS[c["status"]]}</span>
<span class="case-court">{esc(c["court"])}</span>
</div>
<h3>{esc(c["name"])}</h3>
<p class="case-parties">{esc(c["parties"])}</p>
<p><b>The question:</b> {esc(c["issue"])}</p>
<p><b>Where it stands:</b> {esc(c["stands"])}</p>
<div class="case-foot">
{when}
{f'<div class="case-links"><span class="label">My analysis</span><ul>{posts_html}</ul></div>' if posts_html else ""}
{f'<p class="small">Sources: {src_html}</p>' if src_html else ""}
{X.case_follow(c)}
</div>
</article>'''


def sort_key(c):
    return (c.get("next") or "9999-12-31", c["name"])


pending = sorted([c for c in cases["cases"] if c["status"] in ("pending", "watch")], key=sort_key)
decided = sorted([c for c in cases["cases"] if c["status"] == "decided"], key=lambda c: c["decided"], reverse=True)
case_names = {c["id"]: c["name"] for c in cases["cases"]}
watch = "\n".join(
    f'<li><time datetime="{w["date"]}">{fmt_date(w["date"])}</time><a href="#{w["case"]}">{esc(w["label"])}</a></li>'
    for w in sorted(cases["watch"], key=lambda w: w["date"]) if w["date"] >= cases["updated"])
cases_page = head("Case tracker — Ashwani Kumar",
                  "Pending Indian court cases on privacy, AI and technology law, with status and next hearing dates, tracked by advocate Ashwani Kumar.",
                  "") + header("", "cases") + f'''
<main class="wrap">
<section class="page-head">
<h1>Case tracker</h1>
<p>The technology-law cases I'm following in Indian courts: what each one is about, where it stands, and when it's next listed.</p>
<p class="small">Follow every case update by <a href="cases/feed.xml">RSS</a>, or follow a single case from its card below.</p>
<p class="small">Updated <time datetime="{cases["updated"]}">{fmt_date(cases["updated"])}</time>. Hearing dates change often, so check the court's cause list before relying on a date. For general information only; not legal advice.</p>
</section>
<section class="watch">
<h2 class="h2" style="font-size:26px">Dates to watch</h2>
<ol class="watch-list">
{watch}
</ol>
</section>
<section class="cases-section">
<h2 class="h2" style="font-size:26px">Pending</h2>
<div class="cases">
{chr(10).join(case_card(c) for c in pending)}
</div>
</section>
<section class="cases-section" style="padding-bottom:96px">
<h2 class="h2" style="font-size:26px">Recently decided</h2>
<div class="cases">
{chr(10).join(case_card(c) for c in decided)}
</div>
</section>
</main>
''' + footer("") + "\n</body>\n</html>\n"
(OUT / "cases.html").write_text(cases_page, encoding="utf-8")
X.build_case_feeds(OUT, cases)

# ---------------------------------------------------------------- Home page
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
    f'<a class="card" href="posts/{r["slug"]}.html"><span class="kicker">Analysis · {esc(r["kicker"])}</span>'
    f'<h3>{esc(r["title"])}</h3><p>{esc(r["summary"])}</p><span class="meta">{fmt_date(r["date"])}</span></a>'
    for r in records[1:7])
latest = f'''<section class="wrap section">
<div class="section-head">
<h2 class="h2">Recent analysis</h2>
<a href="writing.html" style="font-size:15px;font-weight:600;padding:12px 0">View all {len(records)}</a>
</div>
<div class="grid">
{cards}
</div>
</section>'''
next_up = [w for w in sorted(cases["watch"], key=lambda w: w["date"]) if w["date"] >= cases["updated"]][:3]
tracker_teaser = f'''<section class="wrap section">
<div class="tracker-teaser">
<div style="flex:1 1 320px;min-width:0">
<span class="kicker">Case tracker</span>
<h2 class="h2" style="font-size:28px;margin-top:8px">Coming up in court</h2>
<p class="small" style="margin-top:8px">Pending tech-law cases, their status and next dates.</p>
</div>
<ol class="watch-list" style="flex:2 1 420px;min-width:0">
{chr(10).join(f'<li><time datetime="{w["date"]}">{fmt_date(w["date"])}</time><a href="cases.html#{w["case"]}">{esc(w["label"])}</a></li>' for w in next_up)}
</ol>
<a class="btn btn-ghost" href="cases.html">Open the tracker</a>
</div>
</section>'''
topics_sec = f'''<section id="topics" class="band">
<div class="wrap">
<div class="section-head" style="padding-bottom:0">
<h2 class="h2">What I write about</h2>
<a href="topics/index.html" style="font-size:15px;font-weight:600;padding:12px 0">All topics</a>
</div>
<div class="grid">
{topic_cards.replace("{prefix}", "")}
</div>
</div>
</section>'''
start = idx.index('<section class="wrap section">\n<a class="featured"')
end = idx.index('<section id="topics"')
idx = idx[:start] + featured + "\n\n" + latest + "\n\n" + tracker_teaser + "\n\n" + idx[end:]
t0 = idx.index('<section id="topics"')
t1 = idx.index('<section id="follow"')
idx = idx[:t0] + topics_sec + "\n\n" + idx[t1:]
idx = re.sub(r'href="[^"]*">Read the latest', f'href="posts/{f["slug"]}.html">Read the latest', idx, count=1)
idx = re.sub(r'<nav class="nav" aria-label="Main">.*?</nav>', lambda m: nav(""), idx, count=1, flags=re.S)
index_path.write_text(idx, encoding="utf-8")

# Keep the static pages' menus and stylesheet version in step
for static in ["disclaimer.html", "index.html"]:
    p = OUT / static
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'href="style\.css(\?v=[0-9a-f]+)?"', f'href="style.css?v={CSS_V}"', t)
    t = re.sub(r'\n?<script src="site\.js(\?v=[0-9a-f]+)?"></script>', "", t)
    t = t.replace('<script src="gate.js"></script>', f'<script src="gate.js"></script>\n<script src="site.js?v={JS_V}"></script>', 1)
    t = re.sub(r'<nav class="nav" aria-label="Main">.*?</nav>', lambda m: nav(""), t, count=1, flags=re.S)
    p.write_text(t, encoding="utf-8")

# ---------------------------------------------------------------- RSS feed
from email.utils import format_datetime
from datetime import datetime, timezone, timedelta
SITE_URL = "https://kumarashwani-law.github.io"
IST = timezone(timedelta(hours=5, minutes=30))

def rfc822(d):
    return format_datetime(datetime.strptime(d, "%Y-%m-%d").replace(hour=9, tzinfo=IST))

def cdata(x):
    return "<![CDATA[" + x.replace("]]>", "]]]]><![CDATA[>") + "]]>"

feed_items = []
for r in records[:25]:
    link = f'{SITE_URL}/posts/{r["slug"]}.html'
    body = "\n".join(render_block(b) for b in r["blocks"])
    if r["url"]:
        body += f'\n<p><a href="{esc(r["url"])}">See the original post on LinkedIn</a>.</p>'
    cats = f'<category>{esc(TOPIC_LABEL[r["topic"]])}</category>'
    feed_items.append(f"""<item>
<title>{esc(r["title"])}</title>
<link>{link}</link>
<guid isPermaLink="true">{link}</guid>
<pubDate>{rfc822(r["date"])}</pubDate>
{cats}
<description>{esc(r["summary"])}</description>
<content:encoded>{cdata(body)}</content:encoded>
</item>""")

feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Ashwani Kumar — Law, Privacy &amp; AI</title>
<link>{SITE_URL}/</link>
<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
<description>Commentary on data protection, AI governance, platform regulation and digital free speech in India, by Adv. Ashwani Kumar. For information only; not legal advice.</description>
<language>en-in</language>
<copyright>© 2026 Ashwani Kumar</copyright>
<lastBuildDate>{rfc822(records[0]["date"])}</lastBuildDate>
{chr(10).join(feed_items)}
</channel>
</rss>
"""
(OUT / "feed.xml").write_text(feed_xml, encoding="utf-8")

print(len(records), "posts built; latest:", records[0]["slug"])
print("topics:", {t: counts[t] for t in counts}, "| cases:", len(pending), "pending,", len(decided), "decided")

# ---------------------------------------------------------------- Guides
import markdown as _md

GUIDES_DIR = SRC / "guides"


def read_guide(path):
    text = path.read_text(encoding="utf-8")
    _, fm, body = text.split("---", 2)
    meta_g = {}
    for line in fm.strip().splitlines():
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") or v.startswith("{"):
            v = json.loads(v)
        elif len(v) >= 2 and v[0] == v[-1] == '"':
            v = v[1:-1]
        meta_g[k.strip()] = v
    meta_g["slug"] = path.stem
    meta_g["body"] = body.strip()
    return meta_g


def guide_html(body):
    body = body.replace("- [ ] ", "- ☐ ")
    md = _md.Markdown(extensions=["tables", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2"}})
    out = md.convert(body)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out, toc


guides = [read_guide(p) for p in sorted(GUIDES_DIR.glob("*.md"))] if GUIDES_DIR.exists() else []
GUIDE_ORDER = ["account-blocked", "digital-arrest", "neighbour-cctv", "dpdp-business-checklist"]
guides.sort(key=lambda g: GUIDE_ORDER.index(g["slug"]) if g["slug"] in GUIDE_ORDER else 99)
(OUT / "guides").mkdir(exist_ok=True)

for g in guides:
    body, toc = guide_html(g["body"])
    body = X.add_glossary(body)
    gmins = X.reading_minutes(body)
    guide_url = f"{X.SITE_URL}/guides/{g['slug']}.html"
    langs = X.guide_languages(g["slug"])
    lang_html = X.lang_switch(g["slug"], "en", langs, "")
    toc_html = "".join(f'<li><a href="#{i}">{esc(html.unescape(n))}</a></li>' for i, n in toc)
    rel = [r for s in g.get("related", []) for r in records if r["slug"] == s]
    rel_html = "\n".join(
        f'<a class="card" href="../posts/{x["slug"]}.html"><span class="kicker">{esc(x["kicker"])}</span>'
        f'<h3>{esc(x["title"])}</h3><span class="meta">{fmt_date(x["date"])}</span></a>' for x in rel[:3])
    src_html = "".join(f'<li><a href="{esc(u)}" rel="noopener">{esc(n)}</a></li>' for n, u in g.get("sources", []))
    others = [o for o in guides if o is not g]
    other_html = "".join(f'<li><a href="{o["slug"]}.html">{esc(o["short"])}</a></li>' for o in others)
    page = head(f'{g["title"]} — Ashwani Kumar', g["description"], "../") + header("../", "guides") + f'''
<main>
<article class="article guide">
{X.crumbs("../", [("Home", "index.html"), ("Guides", "guides/index.html"), (g["short"], None, "guides/" + g["slug"] + ".html")])}
<span class="kicker">Guide · {esc(g["kicker"])}</span>
<h1>{esc(g["title"])}</h1>
<p class="dek">{esc(g["description"])}</p>
<div class="byline">
<div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">Ashwani Kumar</span><span class="meta">Advocate · Last reviewed <time datetime="{g["updated"]}">{fmt_date(g["updated"])}</time> · <span class="read-time">{gmins} min read</span></span></div>
<div class="row" style="gap:8px"><button type="button" class="btn btn-ghost btn-sm print-btn">Print / save PDF</button><button type="button" class="btn btn-ghost btn-sm copy-link">Copy link</button></div>
</div>
{lang_html}
<nav class="toc" aria-label="On this page"><span class="label">On this page</span><ol>{toc_html}</ol></nav>
<div class="prose guide-body">
{body}
</div>
{f'<div class="sources"><h2 class="label" style="margin:0">Sources and further reading</h2><ul>{src_html}</ul></div>' if src_html else ""}
<div class="origin"><b>General information, not legal advice.</b> Laws, rules and court decisions change; this guide was last reviewed on {fmt_date(g["updated"])}. For advice on your own situation, speak to a lawyer.</div>
<div class="article-actions">
{X.share_row(guide_url, g["title"])}
<div class="row" style="gap:8px">{X.cite_block("cite-" + g["slug"][:20], g["title"], g["updated"], guide_url)}</div>
</div>
{f'<div class="other-guides"><span class="label">More guides</span><ul>{other_html}</ul></div>' if other_html else ""}
{X.subscribe_box("g-follow")}
{X.comments_html("guides/" + g["slug"])}
</article>
{f"""<section class="band">
<div class="wrap" style="padding-top:64px;padding-bottom:64px;gap:24px">
<h2 class="h2" style="font-size:28px">Related posts</h2>
<div class="grid">
{rel_html}
</div>
</div>
</section>""" if rel_html else ""}
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
    (OUT / "guides" / f'{g["slug"]}.html').write_text(page, encoding="utf-8")


def guide_card(g, prefix):
    return (f'<a class="card guide-card" href="{prefix}{g["slug"]}.html"><span class="kicker">Guide · {esc(g["kicker"])}</span>'
            f'<h3>{esc(g["short"])}</h3><p>{esc(g["description"])}</p></a>')


if guides:
    gi = head("Guides — Ashwani Kumar",
              "Plain-language guides to Indian technology law: blocked accounts, digital arrest scams, CCTV and privacy, and the DPDP Act for businesses.",
              "../") + header("../", "guides") + f'''
<main class="wrap">
<section class="page-head">
<h1>Guides</h1>
<p>Plain-language, step-by-step guides to common problems in Indian technology law. Each one is kept up to date and links to the posts behind it.</p>
</section>
<section class="grid" style="padding-bottom:96px">
{chr(10).join(guide_card(g, "") for g in guides)}
</section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
    (OUT / "guides" / "index.html").write_text(gi, encoding="utf-8")

    # Home: guides section before the case tracker teaser
    idx = index_path.read_text(encoding="utf-8")
    idx = re.sub(r'\n<section class="wrap section" id="guides">.*?</section>\n', "\n", idx, flags=re.S)
    gsec = f'''
<section class="wrap section" id="guides">
<div class="section-head">
<h2 class="h2">Practical guides</h2>
<a href="guides/index.html" style="font-size:15px;font-weight:600;padding:12px 0">All guides</a>
</div>
<div class="grid">
{chr(10).join(guide_card(g, "guides/") for g in guides)}
</div>
</section>
'''
    anchor = '<section class="wrap section">\n<div class="tracker-teaser">'
    idx = idx.replace(anchor, gsec.strip() + "\n\n" + anchor, 1)
    index_path.write_text(idx, encoding="utf-8")
    print(len(guides), "guides built")

# ---------------------------------------------------------------- Glossary, tools, translations
X.build_glossary(globals())
X.build_toolkit(globals())
X.build_translations(globals())

# ---------------------------------------------------------------- Case pages, updates, calendar, laws, reviews, search, home
import casepages
casepages.build(globals())
