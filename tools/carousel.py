"""Make a LinkedIn carousel PDF (1080 x 1350, lime on charcoal) from a JSON spec.

    python3 tools/carousel.py spec.json [out.pdf]

Default output: tools/slides/<slug>.pdf, which tools/slides.py then turns into
the post page's slide images. The PDF itself is the file to upload to LinkedIn.

Spec (all text plain; keep each slide short; 6-9 slides is the sweet spot):
{
  "title": "Human in the loop, or human rubber stamp?",   # must match the post's first line
  "kicker": "LORD SALES · UK SUPREME COURT · NOV 2026",
  "dek": "One or two sentences under the title.",
  "tags": ["AI in courts", "Automation bias"],            # up to 3
  "key": "38",                                            # post number in posts.json -> short link on the last slide
  "slides": [
    {"type": "points",  "kicker": "WHAT HAPPENED", "heading": "...", "points": ["...", "..."], "numbered": false},
    {"type": "quote",   "kicker": "...", "heading": "...", "quote": "...", "by": "...", "note": "optional line under"},
    {"type": "compare", "kicker": "...", "heading": "...",
                        "left":  {"label": "...", "items": ["..."]},
                        "right": {"label": "...", "items": ["..."]}},
    {"type": "stats",   "kicker": "...", "heading": "...", "stats": [{"n": "2,873", "label": "..."}]},
    {"type": "end",     "heading": "...", "text": "...", "points": ["optional takeaways"]}
  ]
}
The cover slide is made from title/kicker/dek/tags. Every slide after the cover
shows the website address in its footer. The "end" slide adds a "read the full
article" box with the post's short link (kumarashwani-law.github.io/p/<key>), the
"not legal advice" line and a follow line automatically (no calls to hire,
in keeping with BCI Rule 36).
"""
import html
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).parent
FONT = (TOOLS / "fonts" / "SpaceGrotesk.ttf").resolve()
LIME, INK, PAPER = "#B9FF66", "#191A23", "#F3F3F3"
NAME = "Adv. Ashwani Kumar"
ROLE = "Advocate | Data Privacy &amp; Technology Law"
HANDLE = "linkedin.com/in/advashwanikumar"
SITE = "kumarashwani-law.github.io"


def slugify(title):
    """Same rule as build.py, so the PDF name matches the post page."""
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    out = []
    for w in s.split("-"):
        if len("-".join(out + [w])) > 60:
            break
        out.append(w)
    return "-".join(out)


def e(s):
    return html.escape(str(s or ""))


STAR = f'''<svg class="orbit" viewBox="0 0 420 300" aria-hidden="true">
<ellipse cx="210" cy="160" rx="200" ry="70" transform="rotate(-24 210 160)" fill="none" stroke="{LIME}" stroke-width="3"/>
<ellipse cx="210" cy="160" rx="175" ry="52" transform="rotate(-24 210 160)" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="2 12" stroke-linecap="round"/>
<path d="M200 40 C210 120 230 140 300 150 C230 160 210 180 200 260 C190 180 170 160 100 150 C170 140 190 120 200 40Z" fill="{LIME}"/>
<path d="M370 0 C374 30 382 38 410 42 C382 46 374 54 370 84 C366 54 358 46 330 42 C358 38 366 30 370 0Z" fill="#fff"/>
<circle cx="60" cy="275" r="11" fill="{LIME}"/></svg>'''


def foot(i, n, dark):
    who = f"<b>{NAME}</b> · {ROLE}" if i == 1 else f"<b>{NAME}</b> · {SITE}"
    return f'<footer class="{"d" if dark else "l"}"><span>{who}</span><span class="num">{i:02d} / {n:02d}</span></footer>'


def ul(items, numbered=False, box=False):
    tag = "ol" if numbered else "ul"
    cls = "box" if box else ("num" if numbered else "dot")
    return f'<{tag} class="{cls}">' + "".join(f"<li><span>{e(x)}</span></li>" for x in items) + f"</{tag}>"


def slide_html(s, i, n):
    t = s["type"]
    dark = t in ("cover", "end") or s.get("dark", i % 2 == 1 and t not in ("compare",))
    k = f'<div class="kicker">{e(s.get("kicker"))}</div>' if s.get("kicker") else ""
    h = f'<h2>{e(s.get("heading"))}</h2>' if s.get("heading") else ""
    if t == "cover":
        tags = "".join(f'<span class="tag">{e(x)}</span>' for x in s.get("tags", [])[:3])
        body = f'''{k}<h1>{e(s["title"])}</h1><div class="rule"></div>
<p class="dek">{e(s.get("dek"))}</p><div class="tags">{tags}</div>{STAR}'''
    elif t == "points":
        body = k + h + ul(s["points"], s.get("numbered"))
    elif t == "quote":
        note = f'<p class="note">{e(s["note"])}</p>' if s.get("note") else ""
        body = f'''{k}{h}<figure class="quote"><blockquote>“{e(s["quote"].strip("“”\""))}”</blockquote>
<figcaption>{e(s.get("by"))}</figcaption></figure>{note}'''
    elif t == "compare":
        L, R = s["left"], s["right"]
        body = f'''{k}{h}<div class="cols"><div class="col lime"><div class="lab">{e(L["label"])}</div>{ul(L["items"], box=True)}</div>
<div class="col ink"><div class="lab">{e(R["label"])}</div>{ul(R["items"], box=True)}</div></div>'''
    elif t == "stats":
        cells = "".join(f'<div class="stat"><div class="n">{e(x["n"])}</div><div class="sl">{e(x["label"])}</div></div>' for x in s["stats"])
        note = f'<p class="note">{e(s["note"])}</p>' if s.get("note") else ""
        body = f'{k}{h}<div class="stats">{cells}</div>{note}'
    elif t == "end":
        pts = ul(s["points"], numbered=True) if s.get("points") else ""
        txt = f'<p class="dek">{e(s.get("text"))}</p>' if s.get("text") else ""
        body = f'''<div class="kicker">{e(s.get("kicker") or "THE TAKEAWAY")}</div>{h}{txt}{pts}
{f'<div class="web-cta"><span>Full article, sources and case updates</span><b>{SITE}/p/{e(s["key"])}</b></div>' if s.get("key") else f'<div class="web-cta"><span>Full article, sources and case updates</span><b>{SITE}</b></div>'}
<div class="sign"><div class="follow">Follow for daily notes on AI, privacy and Indian tech law</div>
<div class="handle">{HANDLE} · {SITE}</div>
<div class="nla">General information, not legal advice.</div></div>'''
    else:
        raise SystemExit(f"Unknown slide type: {t}")
    return f'<section class="slide {"dark" if dark else "light"} t-{t}"><div class="content">{body}</div>{foot(i, n, dark)}</section>'


CSS = f'''
@font-face {{ font-family: SG; src: url("file://{FONT}") format("truetype"); font-weight: 300 700; }}
@page {{ size: 1080px 1350px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ font-family: SG, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.slide {{ width: 1080px; height: 1350px; position: relative; overflow: hidden; page-break-after: always;
  padding: 92px 90px 0; font-size: 34px; }}
.dark {{ background: {INK}; color: #fff; }} .light {{ background: #fff; color: {INK}; }}
.content {{ height: 1090px; display: flex; flex-direction: column; gap: 38px; }}
.kicker {{ align-self: flex-start; background: {LIME}; color: {INK}; font-weight: 700; font-size: 22px;
  letter-spacing: .08em; padding: 9px 16px; border-radius: 8px; text-transform: uppercase; }}
h1 {{ font-size: 92px; line-height: 1.04; font-weight: 500; letter-spacing: -.02em; }}
h2 {{ font-size: 64px; line-height: 1.1; font-weight: 500; letter-spacing: -.015em; }}
.rule {{ width: 120px; height: 8px; border-radius: 4px; background: {LIME}; }}
.dek {{ font-size: 36px; line-height: 1.45; opacity: .92; }}
.tags {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.tag {{ border: 2px solid {LIME}; border-radius: 12px; padding: 12px 22px; font-size: 25px; }}
.orbit {{ position: absolute; right: -40px; bottom: 210px; width: 430px; }}
ul, ol {{ list-style: none; display: flex; flex-direction: column; gap: 26px; }}
li {{ display: flex; gap: 22px; line-height: 1.38; }}
ul.dot li::before {{ content: ""; flex: 0 0 16px; height: 16px; margin-top: 15px; border-radius: 4px; background: {LIME}; }}
.light ul.dot li::before {{ background: {INK}; box-shadow: inset 0 0 0 4px {LIME}; }}
ol.num {{ counter-reset: n; }}
ol.num li::before {{ counter-increment: n; content: counter(n); flex: 0 0 54px; height: 54px; border-radius: 14px;
  background: {LIME}; color: {INK}; font-weight: 700; font-size: 28px; display: grid; place-items: center; margin-top: -2px; }}
ul.box {{ gap: 18px; }} ul.box li {{ font-size: 30px; }}
ul.box li::before {{ content: ""; flex: 0 0 28px; height: 28px; margin-top: 6px; border: 3px solid currentColor; border-radius: 7px; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }}
.col {{ border-radius: 26px; padding: 36px 32px; border: 3px solid {INK}; box-shadow: 0 8px 0 {INK}; }}
.col.lime {{ background: {LIME}; color: {INK}; }} .col.ink {{ background: {INK}; color: #fff; }}
.col.ink ul.box li::before {{ border-color: {LIME}; }}
.lab {{ font-weight: 700; font-size: 22px; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 24px; }}
.quote {{ background: {INK}; color: #fff; border-radius: 26px; padding: 44px 40px; box-shadow: 0 8px 0 {LIME}; }}
.dark .quote {{ background: #262733; }}
blockquote {{ font-size: 40px; line-height: 1.35; font-weight: 500; }}
figcaption {{ color: {LIME}; font-size: 25px; margin-top: 22px; }}
.note {{ font-size: 28px; line-height: 1.45; opacity: .8; }}
.stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.stat {{ border-radius: 24px; padding: 32px; background: {PAPER}; }}
.dark .stat {{ background: #262733; }}
.stat .n {{ font-size: 76px; font-weight: 700; line-height: 1; color: {INK}; }}
.dark .stat .n {{ color: {LIME}; }}
.stat .sl {{ font-size: 26px; line-height: 1.35; margin-top: 14px; }}
.sign {{ margin-top: auto; border-top: 2px solid rgba(255,255,255,.18); padding-top: 30px; }}
.follow {{ font-size: 32px; font-weight: 600; color: {LIME}; }}
.handle {{ font-size: 25px; opacity: .85; margin-top: 10px; }}
.nla {{ font-size: 22px; opacity: .6; margin-top: 14px; }}
.web-cta {{ margin-top: auto; display: flex; flex-direction: column; gap: 6px; background: {LIME}; color: {INK};
  border-radius: 22px; padding: 26px 30px; box-shadow: 0 8px 0 #fff; }}
.web-cta span {{ font-size: 24px; font-weight: 600; letter-spacing: .02em; }}
.web-cta b {{ font-size: 38px; font-weight: 700; letter-spacing: -.01em; }}
.web-cta + .sign {{ margin-top: 0; }}
footer {{ position: absolute; left: 90px; right: 90px; bottom: 56px; height: 90px; display: flex; align-items: flex-end;
  justify-content: space-between; font-size: 24px; padding-top: 26px; }}
footer.d {{ border-top: 2px solid rgba(255,255,255,.25); }} footer.l {{ border-top: 2px solid {INK}; }}
footer .num {{ background: {LIME}; color: {INK}; font-weight: 700; padding: 8px 14px; border-radius: 8px; border: 2px solid {INK}; }}
'''

FIT = """() => {
  const bad = [];
  document.querySelectorAll('.slide').forEach((s, i) => {
    const c = s.querySelector('.content');
    let f = 34, guard = 0;
    while (c.scrollHeight > c.clientHeight + 1 && guard++ < 12) { f *= 0.95; s.style.zoom = ''; c.style.fontSize = f + 'px';
      c.querySelectorAll('h1,h2,.dek,li,blockquote,.stat .n').forEach(el => {
        const cur = parseFloat(getComputedStyle(el).fontSize); el.style.fontSize = (cur * 0.95) + 'px'; }); }
    if (c.scrollHeight > c.clientHeight + 1) bad.push(i + 1);
  });
  return bad;
}"""


def build(spec, out):
    cover = {"type": "cover", **{k: spec.get(k) for k in ("title", "kicker", "dek", "tags")}}
    slides = [cover] + [dict(x, key=spec.get("key")) if x.get("type") == "end" else x for x in spec["slides"]]
    n = len(slides)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            + "".join(slide_html(s, i, n) for i, s in enumerate(slides, 1)) + "</body></html>")
    from playwright.sync_api import sync_playwright
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".html")
    tmp.write_text(page, encoding="utf-8")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(tmp.resolve().as_uri())
            pg.evaluate("document.fonts.ready")
            bad = pg.evaluate(FIT)
            pg.pdf(path=str(out), width="1080px", height="1350px", print_background=True, prefer_css_page_size=True)
            b.close()
    finally:
        tmp.unlink(missing_ok=True)
    if bad:
        print(f"WARNING: text still overflows on slide(s) {bad}; shorten them.")
    print(f"{out}  ({n} slides)")
    return bad


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else TOOLS / "slides" / f"{spec.get('slug') or slugify(spec['title'])}.pdf"
    sys.exit(1 if build(spec, out) else 0)
