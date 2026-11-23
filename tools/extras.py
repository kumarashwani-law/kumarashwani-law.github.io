"""Reader features shared by build.py: glossary pop-ups, share/cite/follow blocks, comments,
per-case feeds, slide PDFs, the glossary page, translated guides and the interactive tools."""
import hashlib
import html
import json
import math
import re
from pathlib import Path

SRC = Path(__file__).parent
SITE_URL = "https://kumarashwani-law.github.io"
FEED_URL = SITE_URL + "/feed.xml"

# Comments use giscus (GitHub Discussions). Fill these two IDs from https://giscus.app once
# Discussions are enabled on the repository and the giscus app is installed. Until then no
# comment box is shown.
GISCUS = {"repo": "kumarashwani-law/kumarashwani-law.github.io", "repo_id": "", "category": "Comments", "category_id": ""}

GLOSSARY = json.load(open(SRC / "glossary.json", encoding="utf-8"))


def esc(s):
    return html.escape(s, quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ------------------------------------------------------------------ reading time
def reading_minutes(text):
    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", text)))
    return max(1, math.ceil(words / 200))


# ------------------------------------------------------------------ glossary pop-ups
_TERMS = []
for g in GLOSSARY:
    for m in g["match"]:
        _TERMS.append((m, g))
_TERMS.sort(key=lambda x: -len(x[0]))
_TERM_RE = re.compile(r"(?<![\w-])(" + "|".join(re.escape(m) for m, _ in _TERMS) + r")(?![\w-])", re.I)
_LOOKUP = {m.lower(): g for m, g in _TERMS}


def add_glossary(body_html, limit=8):
    """Mark the first use of each glossary term in text outside links, headings and code."""
    seen = set()
    out = []
    skip = 0  # depth inside tags we must not touch
    for part in re.split(r"(<[^>]+>)", body_html):
        if part.startswith("<"):
            m = re.match(r"<(/?)(a|h1|h2|h3|th|code|button|summary)\b", part, re.I)
            if m:
                skip += -1 if m.group(1) else 1
                skip = max(skip, 0)
            out.append(part)
            continue
        if skip or len(seen) >= limit:
            out.append(part)
            continue

        def repl(mo):
            g = _LOOKUP[mo.group(1).lower()]
            if g["term"] in seen or len(seen) >= limit:
                return mo.group(0)
            seen.add(g["term"])
            return (f'<span class="gloss" tabindex="0" role="button" aria-label="{esc(mo.group(0))}: definition" '
                    f'data-def="{esc(g["def"])}">{mo.group(0)}</span>')
        out.append(_TERM_RE.sub(repl, part))
    return "".join(out)


# ------------------------------------------------------------------ blocks
def share_row(url, title):
    from urllib.parse import quote
    u, t = quote(url, safe=""), quote(title, safe="")
    return (f'<div class="share-row"><span class="label">Share</span>'
            f'<a class="btn btn-ghost btn-sm" href="https://wa.me/?text={t}%20{u}" rel="noopener" target="_blank">WhatsApp</a>'
            f'<a class="btn btn-ghost btn-sm" href="https://www.linkedin.com/sharing/share-offsite/?url={u}" rel="noopener" target="_blank">LinkedIn</a>'
            f'<a class="btn btn-ghost btn-sm" href="https://x.com/intent/post?text={t}&amp;url={u}" rel="noopener" target="_blank">X</a>'
            f'<a class="btn btn-ghost btn-sm" href="mailto:?subject={t}&amp;body={u}">Email</a>'
            f'</div>')


def citation(title, iso_date, url, kind="post"):
    from datetime import date
    d = date.fromisoformat(iso_date)
    when = f"{d.day} {d.strftime('%B %Y')}"
    return f'Ashwani Kumar, "{title}" ({when}) <{url}>'


def cite_block(cid, title, iso_date, url):
    c = citation(title, iso_date, url)
    return (f'<button type="button" class="btn btn-ghost btn-sm cite-toggle" aria-expanded="false" aria-controls="{cid}">Cite this</button>'
            f'<div class="cite-box" id="{cid}" hidden><span class="label">Cite this {"guide" if "/guides/" in url else "article"}</span>'
            f'<code>{esc(c)}</code>'
            f'<div class="row"><button type="button" class="btn btn-ghost btn-sm" data-copy="{esc(c)}" data-done="Citation copied">Copy citation</button></div></div>')


def follow_panel(pid, feed_url=FEED_URL, what="new posts"):
    from urllib.parse import quote
    q = quote(feed_url, safe="")
    return f'''<div class="follow-panel" id="{pid}" hidden>
<b>Get {what} by email</b>
<ol>
<li>Copy this feed address: <code>{esc(feed_url)}</code> <button type="button" class="btn btn-ghost btn-sm" data-copy="{esc(feed_url)}" data-done="Address copied">Copy</button></li>
<li>Open <a href="https://blogtrottr.com/" rel="noopener" target="_blank">Blogtrottr</a> (free; no account needed), paste the address, add your email and choose how often you want updates.</li>
</ol>
<p class="small" style="margin:0">Blogtrottr is an independent service; your email goes to it, not to me. You can unsubscribe from any email it sends.</p>
<p style="margin:0">Prefer a feed reader? <a href="https://feedly.com/i/subscription/feed/{q}" rel="noopener" target="_blank">Feedly</a> · <a href="https://www.inoreader.com/?add_feed={q}" rel="noopener" target="_blank">Inoreader</a> · <a href="{esc(feed_url)}">RSS</a></p>
</div>'''


def subscribe_box(pid, prefix="../"):
    return f'''<div class="subscribe-box no-print">
<h2>Get new posts by email</h2>
<p>New pieces on privacy, AI and technology law in India, about three a week. Free, and you can stop any time.</p>
<div class="row"><button type="button" class="btn btn-primary follow-toggle" aria-expanded="false" aria-controls="{pid}">Get updates by email</button><a class="btn btn-ghost" href="{prefix}feed.xml">RSS feed</a></div>
{follow_panel(pid)}
</div>'''


def comments_html(term):
    if not (GISCUS["repo_id"] and GISCUS["category_id"]):
        return ""
    return f'''<section class="comments no-print" aria-label="Comments">
<h2 class="label" style="margin:0">Discussion</h2>
<p class="small" style="margin:0">Comments are public and need a GitHub account. Please don't share details of your own case; nothing here is legal advice.</p>
<script src="https://giscus.app/client.js" data-repo="{GISCUS["repo"]}" data-repo-id="{GISCUS["repo_id"]}" data-category="{GISCUS["category"]}" data-category-id="{GISCUS["category_id"]}" data-mapping="specific" data-term="{esc(term)}" data-strict="1" data-reactions-enabled="1" data-emit-metadata="0" data-input-position="top" data-theme="preferred_color_scheme" data-lang="en" data-loading="lazy" crossorigin="anonymous" async></script>
</section>'''


# ------------------------------------------------------------------ slide PDFs
def slides_pdf(out, slug_):
    """Make downloads/<slug>.pdf from the post's slide images (once)."""
    from PIL import Image
    d = out / "images" / "slides" / slug_
    imgs = sorted(d.glob("*.webp")) if d.exists() else []
    if not imgs:
        return None
    pdf = out / "downloads" / f"{slug_}.pdf"
    if not pdf.exists():
        pdf.parent.mkdir(exist_ok=True)
        pages = [Image.open(p).convert("RGB") for p in imgs]
        pages[0].save(pdf, "PDF", save_all=True, append_images=pages[1:], resolution=144.0, quality=70, optimize=True)
    return f"downloads/{slug_}.pdf"


# ------------------------------------------------------------------ case feeds
def _rfc822(iso):
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime
    return format_datetime(datetime.strptime(iso, "%Y-%m-%d").replace(hour=9, tzinfo=timezone(timedelta(hours=5, minutes=30))))


def case_item(c, updated):
    h = hashlib.sha1((c["stands"] + str(c.get("next")) + str(c.get("decided"))).encode()).hexdigest()[:10]
    link = f"{SITE_URL}/cases.html#{c['id']}"
    nxt = c.get("decided") and f"Decided {c['decided']}" or (c.get("next") and f"Next listed {c['next']}") or c.get("next_note") or "Next date awaited"
    body = f"<p><b>{esc(c['parties'])}</b> ({esc(c['court'])})</p><p><b>The question:</b> {esc(c['issue'])}</p><p><b>Where it stands:</b> {esc(c['stands'])}</p><p><b>{esc(nxt)}</b></p>"
    return f"""<item>
<title>{esc(c['name'])}: update</title>
<link>{link}</link>
<guid isPermaLink="false">{c['id']}-{h}</guid>
<pubDate>{_rfc822(updated)}</pubDate>
<description><![CDATA[{body}]]></description>
</item>"""


def case_feed(title, desc, link, self_url, items):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>{esc(title)}</title>
<link>{link}</link>
<atom:link href="{self_url}" rel="self" type="application/rss+xml"/>
<description>{esc(desc)}</description>
<language>en-in</language>
{chr(10).join(items)}
</channel>
</rss>
"""


def build_case_feeds(out, cases):
    """cases/feed.xml for all cases, cases/<id>.xml for each. A new item appears whenever a case's status changes."""
    (out / "cases").mkdir(exist_ok=True)
    upd = cases["updated"]
    allc = [c for c in cases["cases"]]
    (out / "cases" / "feed.xml").write_text(case_feed(
        "Case tracker — Ashwani Kumar", "Status updates on Indian technology-law cases tracked by Adv. Ashwani Kumar.",
        f"{SITE_URL}/cases.html", f"{SITE_URL}/cases/feed.xml", [case_item(c, upd) for c in allc]), encoding="utf-8")
    for c in allc:
        (out / "cases" / f"{c['id']}.xml").write_text(case_feed(
            f"{c['name']} — case tracker", f"Updates on {c['parties']}.", f"{SITE_URL}/cases.html#{c['id']}",
            f"{SITE_URL}/cases/{c['id']}.xml", [case_item(c, upd)]), encoding="utf-8")


def case_follow(c, prefix=""):
    feed = f"{SITE_URL}/cases/{c['id']}.xml"
    pid = f"cf-{c['id']}"
    return (f'<div class="case-follow"><span class="label">Follow this case</span>'
            f'<a href="{prefix}cases/{c["id"]}.xml">RSS</a>'
            f'<button type="button" class="btn btn-ghost btn-sm follow-toggle" aria-expanded="false" aria-controls="{pid}">By email</button></div>'
            + follow_panel(pid, feed, "updates on this case"))


# ------------------------------------------------------------------ glossary page
def build_glossary(ctx):
    head, header, footer, OUT = ctx["head"], ctx["header"], ctx["footer"], ctx["OUT"]
    items = sorted(GLOSSARY, key=lambda g: g["term"].lower())
    letters = sorted({g["term"][0].upper() for g in items})
    az = "".join(f'<a href="#letter-{L}">{L}</a>' for L in letters)
    rows, seen_letters = [], set()
    for g in items:
        L = g["term"][0].upper()
        anchor = f' id="letter-{L}"' if L not in seen_letters else ""
        seen_letters.add(L)
        more = f'<span class="small" style="display:block"><a href="{g["link"]}">Read more</a></span>' if g.get("link") else ""
        rows.append(f'<dt id="{slug(g["term"])}"><span{anchor}></span>{esc(g["term"])}</dt><dd>{esc(g["def"])}{more}</dd>')
    page = head("Glossary — Ashwani Kumar",
                "Plain-language definitions of Indian technology-law terms: data fiduciary, safe harbour, personality rights, blocking orders, digital arrest and more.",
                "") + header("") + f'''
<main class="wrap" style="max-width:820px">
<section class="page-head">
{crumbs("", [("Home", "index.html"), ("Glossary", None, "glossary.html")])}
<h1>Glossary</h1>
<p>Short, plain-language definitions of the legal terms that come up in my writing. On articles and guides, terms in this list are underlined with dots: tap or hover to see the definition.</p>
</section>
<nav class="az" aria-label="Jump to letter">{az}</nav>
<dl class="glossary-list" style="padding-bottom:96px">
{chr(10).join(rows)}
</dl>
</main>
''' + footer("") + "\n</body>\n</html>\n"
    (OUT / "glossary.html").write_text(page, encoding="utf-8")


# ------------------------------------------------------------------ translated guides
LANGS = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
L10N = {
    "hi": {"all": "सभी गाइड", "guide": "गाइड", "reviewed": "अंतिम समीक्षा", "min": "मिनट", "print": "प्रिंट / PDF सेव करें",
           "toc": "इस पेज पर", "read_in": "इस गाइड को पढ़ें:",
           "note": "यह अंग्रेज़ी गाइड का अनुवाद है, आम पाठकों की सुविधा के लिए। किसी भी अंतर की स्थिति में <a href=\"../{slug}.html\">अंग्रेज़ी संस्करण</a> मान्य होगा।",
           "origin": "<b>सामान्य जानकारी, क़ानूनी सलाह नहीं।</b> क़ानून, नियम और अदालती फ़ैसले बदलते रहते हैं। अपनी स्थिति पर सलाह के लिए किसी वकील से बात करें।"},
    "te": {"all": "అన్ని గైడ్‌లు", "guide": "గైడ్", "reviewed": "చివరి సమీక్ష", "min": "నిమిషాలు", "print": "ప్రింట్ / PDF సేవ్",
           "toc": "ఈ పేజీలో", "read_in": "ఈ గైడ్‌ను చదవండి:",
           "note": "ఇది ఆంగ్ల గైడ్‌కు అనువాదం, సాధారణ పాఠకుల సౌలభ్యం కోసం. ఏదైనా తేడా ఉంటే <a href=\"../{slug}.html\">ఆంగ్ల వెర్షన్</a> ప్రామాణికం.",
           "origin": "<b>సాధారణ సమాచారం, న్యాయ సలహా కాదు.</b> చట్టాలు, నియమాలు, కోర్టు తీర్పులు మారుతుంటాయి. మీ పరిస్థితిపై సలహా కోసం న్యాయవాదిని సంప్రదించండి."},
}


def guide_languages(slug_):
    langs = ["en"] + [l for l in ("hi", "te") if (SRC / "guides" / l / f"{slug_}.md").exists()]
    return langs if len(langs) > 1 else []


def lang_switch(slug_, current, langs, prefix=""):
    if not langs:
        return ""
    links = []
    for l in langs:
        if current == "en":
            href = f"{l}/{slug_}.html"
        else:
            href = f"../{slug_}.html" if l == "en" else f"../{l}/{slug_}.html"
        if l == current:
            links.append(f'<span aria-current="page" lang="{l}">{LANGS[l]}</span>')
        else:
            links.append(f'<a href="{href}" lang="{l}" hreflang="{l}">{LANGS[l]}</a>')
    label = "Read this guide in:" if current == "en" else L10N[current]["read_in"]
    return f'<nav class="lang-switch" aria-label="Language"><span class="label">{label}</span>{"".join(links)}</nav>'


def _guide_md(body):
    import markdown as _md
    from markdown.extensions.toc import slugify_unicode
    body = body.replace("- [ ] ", "- ☐ ")
    md = _md.Markdown(extensions=["tables", "toc", "sane_lists"],
                      extension_configs={"toc": {"toc_depth": "2", "slugify": slugify_unicode}})
    out = md.convert(body)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out, toc


def build_translations(ctx):
    head, header, footer, OUT, read_guide, fmt_date = (ctx[k] for k in ("head", "header", "footer", "OUT", "read_guide", "fmt_date"))
    n = 0
    for l in ("hi", "te"):
        d = SRC / "guides" / l
        if not d.exists():
            continue
        (OUT / "guides" / l).mkdir(parents=True, exist_ok=True)
        t = L10N[l]
        for p in sorted(d.glob("*.md")):
            g = read_guide(p)
            body, toc = _guide_md(g["body"])
            mins = reading_minutes(body)
            url = f"{SITE_URL}/guides/{l}/{g['slug']}.html"
            toc_html = "".join(f'<li><a href="#{i}">{esc(html.unescape(nm))}</a></li>' for i, nm in toc)
            sw = lang_switch(g["slug"], l, guide_languages(g["slug"]))
            page = head(f'{g["title"]} — Ashwani Kumar', g["description"], "../../", lang=l) + header("../../", "guides") + f'''
<main>
<article class="article guide" lang="{l}">
{crumbs("../../", [("Home", "index.html"), (t["all"], "guides/index.html"), (g["short"], None, f"guides/{l}/{g['slug']}.html")])}
<span class="kicker">{t["guide"]} · {esc(g["kicker"])}</span>
<h1>{esc(g["title"])}</h1>
<p class="dek">{esc(g["description"])}</p>
<div class="byline">
<div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">Ashwani Kumar</span><span class="meta">{t["reviewed"]}: <time datetime="{g["updated"]}">{fmt_date(g["updated"])}</time> · <span class="read-time">{mins} {t["min"]}</span></span></div>
<div class="row" style="gap:8px"><button type="button" class="btn btn-ghost btn-sm print-btn">{t["print"]}</button></div>
</div>
{sw}
<p class="translation-note">{t["note"].format(slug=g["slug"])}</p>
<nav class="toc" aria-label="{t["toc"]}"><span class="label">{t["toc"]}</span><ol>{toc_html}</ol></nav>
<div class="prose guide-body">
{body}
</div>
<div class="origin">{t["origin"]}</div>
<div class="article-actions">
{share_row(url, g["title"])}
</div>
</article>
</main>
''' + footer("../../") + "\n</body>\n</html>\n"
            fam = {"hi": "Noto+Sans+Devanagari", "te": "Noto+Sans+Telugu"}[l]
            page = page.replace("</head>", f'<link href="https://fonts.googleapis.com/css2?family={fam}:wght@400;600;700&display=swap" rel="stylesheet">\n'
                                f'<style>.article[lang={l}],.article[lang={l}] h1,.article[lang={l}] h2,.article[lang={l}] h3,.article[lang={l}] .dek,.article[lang={l}] .prose{{font-family:"{fam.replace("+", " ")}",var(--sans)}}</style>\n</head>', 1)
            (OUT / "guides" / l / f'{g["slug"]}.html').write_text(page, encoding="utf-8")
            n += 1
    print(n, "translated guides built")


# ------------------------------------------------------------------ interactive tools
def build_toolkit(ctx):
    from toolkit import PAGES
    head, header, footer, OUT = ctx["head"], ctx["header"], ctx["footer"], ctx["OUT"]
    (OUT / "toolkit").mkdir(exist_ok=True)
    for name, (title, desc, body) in PAGES.items():
        trail = [("Home", "index.html"), ("Tools", None, "toolkit/index.html")] if name == "index" else [("Home", "index.html"), ("Tools", "toolkit/index.html"), (title, None, f"toolkit/{name}.html")]
        body = body.replace('<a href="index.html" style="font-size:14px;font-weight:500;text-decoration:none" class="no-print">← All tools</a>', crumbs("../", trail), 1)
        if name == "index":
            body = body.replace('<section class="page-head">', '<section class="page-head">\n' + crumbs("../", trail), 1)
        page = head(f"{title} — Ashwani Kumar", desc, "../") + header("../", "tools") + body + footer("../") + "\n</body>\n</html>\n"
        (OUT / "toolkit" / f"{name}.html").write_text(page, encoding="utf-8")
    print(len(PAGES), "toolkit pages built")


# ------------------------------------------------------------------ breadcrumbs
def crumbs(prefix, items):
    """items: [(label, root-relative path or None for the current page, absolute path for JSON-LD)]"""
    parts, ld = [], []
    for i, it in enumerate(items):
        label, path = it[0], it[1]
        last = i == len(items) - 1
        if last:
            parts.append(f'<li aria-current="page">{esc(label)}</li>')
        else:
            parts.append(f'<li><a href="{prefix}{path}">{esc(label)}</a></li>')
        url = f"{SITE_URL}/{path}" if path is not None else (f"{SITE_URL}/{it[2]}" if len(it) > 2 else None)
        e = {"@type": "ListItem", "position": i + 1, "name": html.unescape(label)}
        if url:
            e["item"] = url.replace("/index.html", "/") if url.endswith("/index.html") and url.count("/") > 3 else url
        ld.append(e)
    data = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld}, ensure_ascii=False)
    return (f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>\n'
            f'<script type="application/ld+json">{data}</script>')
