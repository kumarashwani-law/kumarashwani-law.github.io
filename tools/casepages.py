"""Case pages, case updates, hearing calendar, law (statute) pages, monthly reviews, site search and home-page sections.
Called at the end of build.py with build.py's globals()."""
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import extras as X

IST = timezone(timedelta(hours=5, minutes=30))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Laws a reader may want to follow. Pages are built only for laws that something on the site mentions.
LAWS = [
    ("dpdp-act", "DPDP Act, 2023 and DPDP Rules, 2025", "India's data protection law: duties of data fiduciaries, rights of data principals, children's data and the Data Protection Board.",
     r"\bDPDP\b|Digital Personal Data Protection|Data Protection Board|data fiduciar"),
    ("it-act-section-79", "IT Act, section 79 (safe harbour)", "When platforms and other intermediaries are protected from liability for what users post, and when they lose that protection.",
     r"\b(?:s\.|section|sec\.)\s*79\b|79\(3\)|safe harbour|safe harbor"),
    ("it-act-section-69a", "IT Act, section 69A (blocking)", "The government's power to order online content blocked, and the 2009 Blocking Rules.",
     r"\b69A\b|blocking order|Blocking Rules"),
    ("it-rules-2021", "IT Rules, 2021", "Due-diligence duties of intermediaries: grievance officers, the Grievance Appellate Committee, takedown timelines and reasons for removal.",
     r"IT Rules|Intermediary Guidelines|Rule 3\(|Rule 4\(8\)|Grievance Appellate|\bGAC\b"),
    ("copyright-act", "Copyright Act, 1957", "Ownership of creative work, fair dealing (s. 52), AI training on copyrighted material, and takedowns.",
     r"Copyright Act|fair dealing|\bs\. 52\b|section 52\b|copyright"),
    ("trade-marks", "Trade Marks Act, 1999", "Brand names, well-known marks, keyword advertising and passing off.",
     r"Trade ?Marks Act|trademark|trade mark|passing off|well-known mark"),
    ("article-21-privacy", "Article 21: right to privacy", "Privacy as a fundamental right after Puttaswamy, and how courts test surveillance, data use and state action against it.",
     r"Article 21\b|right to privacy|Puttaswamy"),
    ("article-19-speech", "Article 19: free speech", "Freedom of speech and expression online: satire, takedowns, blocking and reasonable restrictions.",
     r"Article 19\b|free speech|freedom of speech|freedom of expression"),
    ("rti-act", "Right to Information Act, 2005", "Access to government information, and how the DPDP Act changed the personal-information exemption.",
     r"\bRTI\b|Right to Information"),
    ("online-gaming-act", "Online Gaming Act, 2025", "The Promotion and Regulation of Online Gaming Act, 2025 and the ban on online money games.",
     r"Online Gaming Act|Promotion and Regulation of Online Gaming|online money game"),
    ("rbi-customer-liability", "RBI rules on customer liability and cyber fraud", "When banks must bear losses from unauthorised or fraudulent transactions, and the RBI's new cyber-fraud framework.",
     r"\bRBI\b|Reserve Bank"),
]


def fdate(d, fmt_date):
    if len(d) == 4:
        return d
    if len(d) == 7:
        return f"{MONTHS[int(d[5:7]) - 1]} {d[:4]}"
    return fmt_date(d)


def build(ctx):
    head, header, footer, OUT, SRC = ctx["head"], ctx["header"], ctx["footer"], ctx["OUT"], ctx["SRC"]
    esc, fmt_date, records, cases, guides = ctx["esc"], ctx["fmt_date"], ctx["records"], ctx["cases"], ctx["guides"]
    STATUS, TOPIC_LABEL, LINKEDIN = ctx["STATUS"], ctx["TOPIC_LABEL"], ctx["LINKEDIN"]
    today = datetime.now(IST).strftime("%Y-%m-%d")
    fd = lambda d: fdate(d, fmt_date)

    details = json.load(open(SRC / "case_details.json", encoding="utf-8"))
    updates = json.load(open(SRC / "updates.json", encoding="utf-8"))
    allcases = cases["cases"]
    byid = {c["id"]: c for c in allcases}
    for c in allcases:
        c["d"] = details.get(c["id"], {})
        c["short"] = c["d"].get("short", c["name"])
    slug_rec = {r["slug"]: r for r in records}

    # ---------------------------------------------------------- updates
    used = set()
    for u in updates:
        c = byid[u["case"]]
        u["title"] = f'{c["short"]} | {u["headline"]}'
        s = X.slug(f'{c["short"]} {u["headline"]}')[:80].strip("-")
        while s in used:
            s += "-2"
        used.add(s)
        u["slug"] = s
        u["summary"] = re.sub(r"\s+", " ", u["body"][0])[:220].rsplit(" ", 1)[0] + "…" if len(u["body"][0]) > 220 else u["body"][0]
    updates.sort(key=lambda u: u["date"], reverse=True)
    for c in allcases:
        c["updates"] = [u for u in updates if u["case"] == c["id"]]

    # ---------------------------------------------------------- laws: which items mention which law
    def law_hits(text):
        return [l[0] for l in LAWS if re.search(l[3], text, re.I)]

    for r in records:
        r["laws"] = law_hits(" ".join([r["title"]] + r["blocks"] + r["tags"]))
    for g in guides:
        g["laws"] = law_hits(g["title"] + " " + g["body"])
    for c in allcases:
        c["laws"] = law_hits(" ".join([c["name"], c["parties"], c["issue"], c["stands"]] + c["d"].get("issues", [])))
    for u in updates:
        u["laws"] = sorted(set(law_hits(" ".join(u["body"])) + byid[u["case"]]["laws"]))
    LAWD = {l[0]: l for l in LAWS}

    def law_links(ids, prefix):
        if not ids:
            return ""
        return ('<div class="law-tags"><span class="label">Laws</span>' +
                "".join(f'<a class="law-tag" href="{prefix}law/{i}.html">{esc(LAWD[i][1])}</a>' for i in ids) + "</div>")

    def source_list(srcs):
        seen, out = set(), []
        for n, u in srcs:
            if u in seen:
                continue
            seen.add(u)
            out.append(f'<li><a href="{esc(u)}" rel="noopener">{esc(n)}</a></li>')
        return "".join(out)

    def when_text(c):
        if c["status"] == "decided":
            return "Decided", fmt_date(c["decided"])
        if c.get("next") and not c.get("next_note"):
            return "Next hearing", fmt_date(c["next"])
        return "Next hearing", c.get("next_note") or "Not yet listed"

    # ---------------------------------------------------------- case pages
    (OUT / "cases").mkdir(exist_ok=True)
    for c in allcases:
        d = c["d"]
        lab, val = when_text(c)
        rows = [("Court", esc(c["court"]))]
        if d.get("case_no"):
            rows.append(("Case number", esc(d["case_no"])))
        if d.get("bench"):
            rows.append(("Bench", esc(d["bench"])))
        rows.append(("Status", f'<span class="pill pill-{c["status"]}">{STATUS[c["status"]]}</span>'))
        rows.append((lab, f"<b>{esc(val)}</b>"))
        rows.append(("Last updated", fmt_date(cases["updated"])))
        details_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
        issues = d.get("issues") or [c["issue"]]
        issues_html = "".join(f"<li>{esc(i)}</li>" for i in issues)
        tl = sorted(d.get("timeline", []), key=lambda t: t[0], reverse=True)
        tl_html = "".join(f'<li><time datetime="{t[0]}">{fd(t[0])}</time><span>{esc(t[1])}</span></li>' for t in tl)
        upd_html = "".join(
            f'<a class="item" href="../updates/{u["slug"]}.html"><span class="date">{fmt_date(u["date"])}</span>'
            f'<span class="body"><span class="t">{esc(u["headline"])}</span><span class="s">{esc(u["summary"])}</span></span>'
            f'<span class="tag">Case update</span></a>' for u in c["updates"])
        posts = [slug_rec[p] for p in c.get("posts", []) if p in slug_rec]
        posts_html = "".join(
            f'<a class="item" href="../posts/{r["slug"]}.html"><span class="date">{fmt_date(r["date"])}</span>'
            f'<span class="body"><span class="t">{esc(r["title"])}</span><span class="s">{esc(r["summary"])}</span></span>'
            f'<span class="tag">Analysis</span></a>' for r in posts)
        gmap = {"digital-arrest": "digital-arrest", "sarthak": "account-blocked", "haryana24": "account-blocked", "anmol": "account-blocked",
                "blink": "account-blocked", "dpdp-rti": "dpdp-business-checklist", "dpb": "dpdp-business-checklist"}
        rel_guides = [g for g in guides if g["slug"] == gmap.get(c["id"])]
        guides_html = "".join(f'<li><a href="../guides/{g["slug"]}.html">{esc(g["title"])}</a></li>' for g in rel_guides)
        srcs = source_list(list(c.get("sources", [])) + d.get("extra_sources", []))
        url = f"{X.SITE_URL}/cases/{c['id']}.html"
        desc = f'{c["name"]}: {c["issue"]} Status, next hearing date, key issues and timeline.'
        page = head(f'{c["name"]} — Case tracker — Custos', desc[:300], "../") + header("../", "cases") + f'''
<main>
<article class="article case-page">
{X.crumbs("../", [("Home", "index.html"), ("Case tracker", "cases.html"), (c["short"], None, f"cases/{c['id']}.html")])}
<span class="kicker">Case · {esc(c["court"])}</span>
<h1>{esc(c["name"])}</h1>
<p class="dek case-parties-dek">{esc(c["parties"])}</p>
<dl class="case-details">{details_html}</dl>
<section class="case-block">
<h2>Key issues</h2>
<ol class="key-issues">{issues_html}</ol>
</section>
<section class="case-block">
<h2>Where it stands</h2>
<p>{esc(c["stands"])}</p>
</section>
{f"""<section class="case-block"><h2>Timeline</h2><ol class="timeline">{tl_html}</ol></section>""" if tl_html else ""}
{f"""<section class="case-block"><h2>Case updates ({len(c["updates"])})</h2><div class="group">{upd_html}</div></section>""" if upd_html else ""}
{f"""<section class="case-block"><h2>My analysis ({len(posts)})</h2><div class="group">{posts_html}</div></section>""" if posts_html else ""}
{f"""<section class="case-block"><h2>Related guide</h2><ul>{guides_html}</ul></section>""" if guides_html else ""}
{law_links(c["laws"], "../")}
{f"""<section class="case-block sources"><h2>Sources and documents</h2><ul>{srcs}</ul></section>""" if srcs else ""}
<div class="case-foot-page">{X.case_follow(c, "../")}</div>
<p class="origin">Hearing dates change often, so check the court's cause list before relying on a date. For general information only; not legal advice.</p>
<div class="article-actions">{X.share_row(url, c["name"])}</div>
</article>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
        (OUT / "cases" / f'{c["id"]}.html').write_text(page, encoding="utf-8")

    # ---------------------------------------------------------- update pages
    (OUT / "updates").mkdir(exist_ok=True)
    for u in updates:
        c = byid[u["case"]]
        url = f"{X.SITE_URL}/updates/{u['slug']}.html"
        others = [o for o in c["updates"] if o is not u]
        others_html = "".join(f'<li><time datetime="{o["date"]}">{fmt_date(o["date"])}</time> <a href="{o["slug"]}.html">{esc(o["headline"])}</a></li>' for o in others)
        lab, val = when_text(c)
        bench = c["d"].get("bench")
        body = "\n".join(f"<p>{esc(p)}</p>" for p in u["body"])
        page = head(f'{u["title"]} — Custos', u["summary"], "../") + header("../", "cases") + f'''
<main>
<article class="article update">
{X.crumbs("../", [("Home", "index.html"), ("Case tracker", "cases.html"), (c["short"], f"cases/{c['id']}.html"), ("Update", None, f"updates/{u['slug']}.html")])}
<span class="kicker">Case update · {esc(c["court"])}</span>
<h1><a class="case-link" href="../cases/{c["id"]}.html">{esc(c["short"])}</a> <span class="sep">|</span> {esc(u["headline"])}</h1>
<div class="byline">
<div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">Ashwani Kumar</span><span class="meta">Advocate · <time datetime="{u["date"]}">{fmt_date(u["date"])}</time>{f" · Bench: {esc(bench)}" if bench else ""}</span></div>
</div>
<div class="prose update-body">
{body}
</div>
<div class="next-box"><span class="label">{lab}</span><b>{esc(val)}</b><a href="../cases/{c["id"]}.html">Full case page →</a></div>
{law_links(u["laws"], "../")}
<div class="sources"><h2 class="label" style="margin:0">Sources</h2><ul>{source_list(u.get("sources", []))}</ul></div>
{f'<div class="other-guides"><span class="label">Earlier updates in this case</span><ul>{others_html}</ul></div>' if others_html else ""}
<p class="origin">A factual note on the hearing, written from the sources above; my comment on the case is in the analysis linked from the case page. For general information only; not legal advice.</p>
<div class="article-actions">
{X.share_row(url, u["title"])}
<div class="row" style="gap:8px">{X.cite_block("cite-" + u["slug"][:20], u["title"], u["date"], url)}</div>
</div>
{X.subscribe_box("u-follow")}
</article>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
        (OUT / "updates" / f'{u["slug"]}.html').write_text(page, encoding="utf-8")

    upd_items = "".join(
        f'<a class="item" href="{u["slug"]}.html"><span class="date">{fmt_date(u["date"])}</span>'
        f'<span class="body"><span class="t">{esc(u["title"])}</span><span class="s">{esc(u["summary"])}</span></span>'
        f'<span class="tag">{esc(byid[u["case"]]["court"])}</span></a>' for u in updates)
    page = head("Case updates — Custos", "Short, factual notes on hearings and orders in Indian technology-law cases, newest first.", "../") + header("../", "cases") + f'''
<main class="wrap">
<section class="page-head">
{X.crumbs("../", [("Home", "index.html"), ("Case tracker", "cases.html"), ("Updates", None, "updates/index.html")])}
<h1>Case updates</h1>
<p>Short, factual notes on what happened at a hearing and when the case is next listed. My views are in the <a href="../writing.html">analysis posts</a>.</p>
</section>
<section class="groups" style="padding-bottom:96px"><div class="group">{upd_items}</div></section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
    (OUT / "updates" / "index.html").write_text(page, encoding="utf-8")

    # ---------------------------------------------------------- case feeds: status + updates, linking to case pages
    def upd_item(u):
        link = f"{X.SITE_URL}/updates/{u['slug']}.html"
        body = "".join(f"<p>{esc(p)}</p>" for p in u["body"])
        return (f"<item>\n<title>{esc(u['title'])}</title>\n<link>{link}</link>\n<guid isPermaLink=\"true\">{link}</guid>\n"
                f"<pubDate>{ctx['rfc822'](u['date'])}</pubDate>\n<description>{esc(u['summary'])}</description>\n"
                f"<content:encoded>{ctx['cdata'](body)}</content:encoded>\n</item>")
    upd = cases["updated"]
    (OUT / "cases" / "feed.xml").write_text(X.case_feed(
        "Case tracker — Custos", "Status changes and hearing updates on Indian technology-law cases tracked by Adv. Ashwani Kumar.",
        f"{X.SITE_URL}/cases.html", f"{X.SITE_URL}/cases/feed.xml",
        [upd_item(u) for u in updates] + [X.case_item(c, upd) for c in allcases]), encoding="utf-8")
    for c in allcases:
        (OUT / "cases" / f"{c['id']}.xml").write_text(X.case_feed(
            f"{c['name']} — case tracker", f"Updates on {c['parties']}.", f"{X.SITE_URL}/cases/{c['id']}.html",
            f"{X.SITE_URL}/cases/{c['id']}.xml", [upd_item(u) for u in c["updates"]] + [X.case_item(c, upd)]), encoding="utf-8")

    # ---------------------------------------------------------- calendar
    events, seen = [], set()
    for w in cases["watch"]:
        events.append({"date": w["date"], "label": w["label"], "case": w.get("case")})
        seen.add((w["date"], w.get("case")))
    for c in allcases:
        if c["status"] != "decided" and c.get("next") and not c.get("next_note") and (c["next"], c["id"]) not in seen:
            events.append({"date": c["next"], "label": f'{c["court"]}: {c["short"]}', "case": c["id"]})
    events = sorted([e for e in events if e["date"] >= today], key=lambda e: e["date"])
    undated = [c for c in allcases if c["status"] != "decided" and (c.get("next_note") or not c.get("next"))]

    def gcal(e):
        d0 = e["date"].replace("-", "")
        d1 = (datetime.strptime(e["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d")
        details_ = f"Hearing dates change; check the court's cause list. {X.SITE_URL}/cases/{e['case']}.html" if e.get("case") else ""
        return ("https://calendar.google.com/calendar/render?action=TEMPLATE"
                f"&text={quote(e['label'])}&dates={d0}/{d1}&details={quote(details_)}")

    by_month = {}
    for e in events:
        by_month.setdefault(e["date"][:7], []).append(e)
    cal_html = ""
    for ym, es in by_month.items():
        lis = "".join(
            f'<li><time datetime="{e["date"]}"><b>{int(e["date"][8:])}</b><span>{datetime.strptime(e["date"], "%Y-%m-%d").strftime("%a")}</span></time>'
            f'<div><a href="{"cases/" + e["case"] + ".html" if e.get("case") else "cases.html"}">{esc(e["label"])}</a>'
            f'<a class="small" href="{esc(gcal(e))}" rel="noopener" target="_blank">Add to Google Calendar</a></div></li>' for e in es)
        cal_html += f'<section class="cal-month"><h2 class="h2" style="font-size:24px">{fd(ym)}</h2><ol class="cal-list">{lis}</ol></section>'
    und_html = "".join(f'<li><a href="cases/{c["id"]}.html">{esc(c["name"])}</a> <span class="small">({esc(c["court"])}): {esc(c.get("next_note") or "not yet listed")}</span></li>' for c in undated)
    page = head("Case calendar — Custos", "Upcoming hearing dates in Indian technology-law cases: data protection, AI, platforms, deepfakes and cyber fraud.", "") + header("", "cases") + f'''
<main class="wrap" style="max-width:860px">
<section class="page-head">
{X.crumbs("", [("Home", "index.html"), ("Case tracker", "cases.html"), ("Calendar", None, "calendar.html")])}
<h1>Case calendar</h1>
<p>Upcoming hearings in the cases I track, in date order.</p>
<div class="row" style="gap:8px;flex-wrap:wrap"><a class="btn btn-primary" href="calendar.ics" download>Add all dates to your calendar (.ics)</a><a class="btn btn-ghost" href="cases.html">Open the case tracker</a></div>
<p class="small">Hearing dates change often and cases are not always taken up on the listed day. Check the court's cause list before relying on a date. Updated {fmt_date(cases["updated"])}.</p>
</section>
{cal_html or '<p>No upcoming dates.</p>'}
{f'<section class="cal-month" style="padding-bottom:96px"><h2 class="h2" style="font-size:24px">Date not yet fixed</h2><ul class="undated">{und_html}</ul></section>' if und_html else ""}
</main>
''' + footer("") + "\n</body>\n</html>\n"
    (OUT / "calendar.html").write_text(page, encoding="utf-8")

    def ics_esc(s):
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    vev = []
    for e in events:
        d0 = e["date"].replace("-", "")
        d1 = (datetime.strptime(e["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d")
        link = f"{X.SITE_URL}/cases/{e['case']}.html" if e.get("case") else f"{X.SITE_URL}/calendar.html"
        vev.append("\r\n".join([
            "BEGIN:VEVENT", f"UID:{e.get('case') or 'date'}-{d0}@kumarashwani-law.github.io", f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d0}", f"DTEND;VALUE=DATE:{d1}", f"SUMMARY:{ics_esc(e['label'])}",
            f"DESCRIPTION:{ics_esc('Hearing dates change; check the court cause list. ' + link)}", f"URL:{link}",
            "TRANSP:TRANSPARENT", "END:VEVENT"]))
    ics = "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Custos//Case calendar//EN", "CALSCALE:GREGORIAN",
                       "METHOD:PUBLISH", "X-WR-CALNAME:Tech-law hearings (Custos)", "X-WR-TIMEZONE:Asia/Kolkata"] + vev + ["END:VCALENDAR"]) + "\r\n"
    (OUT / "calendar.ics").write_text(ics, encoding="utf-8", newline="")

    # ---------------------------------------------------------- law pages
    (OUT / "law").mkdir(exist_ok=True)
    law_cards = []
    for lid, name, desc, _ in LAWS:
        cs = [c for c in allcases if lid in c["laws"]]
        ps = [r for r in records if lid in r["laws"]]
        gs = [g for g in guides if lid in g["laws"]]
        us = [u for u in updates if lid in u["laws"]]
        n = len(cs) + len(ps) + len(gs) + len(us)
        if not n:
            continue
        law_cards.append(f'<a class="topic" href="{lid}.html"><h3>{esc(name)}</h3><p>{esc(desc)}</p><span class="meta">{n} item{"s" if n != 1 else ""}</span></a>')
        sec = ""
        if cs:
            sec += '<section class="case-block"><h2>Cases</h2><div class="group">' + "".join(
                f'<a class="item" href="../cases/{c["id"]}.html"><span class="date">{STATUS[c["status"]]}</span><span class="body"><span class="t">{esc(c["name"])}</span>'
                f'<span class="s">{esc(c["issue"])}</span></span><span class="tag">{esc(c["court"])}</span></a>' for c in cs) + "</div></section>"
        if gs:
            sec += '<section class="case-block"><h2>Guides</h2><div class="group">' + "".join(
                f'<a class="item" href="../guides/{g["slug"]}.html"><span class="date">Guide</span><span class="body"><span class="t">{esc(g["title"])}</span>'
                f'<span class="s">{esc(g["description"])}</span></span><span class="tag">Guide</span></a>' for g in gs) + "</div></section>"
        if us:
            sec += '<section class="case-block"><h2>Case updates</h2><div class="group">' + "".join(
                f'<a class="item" href="../updates/{u["slug"]}.html"><span class="date">{fmt_date(u["date"])}</span><span class="body"><span class="t">{esc(u["title"])}</span>'
                f'<span class="s">{esc(u["summary"])}</span></span><span class="tag">Case update</span></a>' for u in us) + "</div></section>"
        if ps:
            sec += '<section class="case-block"><h2>Analysis</h2><div class="group">' + "".join(
                f'<a class="item" href="../posts/{r["slug"]}.html"><span class="date">{fmt_date(r["date"])}</span><span class="body"><span class="t">{esc(r["title"])}</span>'
                f'<span class="s">{esc(r["summary"])}</span></span><span class="tag">{esc(r["kicker"])}</span></a>' for r in ps) + "</div></section>"
        page = head(f"{name} — Custos", f"{desc} Cases, guides and analysis by advocate Ashwani Kumar.", "../") + header("../", "topics") + f'''
<main class="wrap" style="max-width:960px">
<section class="page-head">
{X.crumbs("../", [("Home", "index.html"), ("Laws", "law/index.html"), (name, None, f"law/{lid}.html")])}
<span class="kicker">Law</span>
<h1>{esc(name)}</h1>
<p>{esc(desc)}</p>
<p class="small">Everything on this site that deals with this law: {len(cs)} case{"s" if len(cs) != 1 else ""}, {len(gs)} guide{"s" if len(gs) != 1 else ""}, {len(us)} update{"s" if len(us) != 1 else ""} and {len(ps)} post{"s" if len(ps) != 1 else ""}. Pages are matched by the law's name, so a few may only mention it in passing.</p>
</section>
<div style="padding-bottom:96px;display:flex;flex-direction:column;gap:8px">{sec}</div>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
        (OUT / "law" / f"{lid}.html").write_text(page, encoding="utf-8")
    built_laws = {re.search(r'href="([^"]+)\.html"', h).group(1) for h in law_cards}
    for coll in (records, guides, allcases, updates):
        for it in coll:
            it["laws"] = [l for l in it["laws"] if l in built_laws]
    page = head("Laws — Custos", "Browse cases, guides and analysis by the law involved: DPDP Act, IT Act, IT Rules, Copyright Act, Article 21 and more.", "../") + header("../", "topics") + f'''
<main class="wrap">
<section class="page-head">
{X.crumbs("../", [("Home", "index.html"), ("Laws", None, "law/index.html")])}
<h1>Laws</h1>
<p>Follow a single law: every case, update, guide and post on this site that deals with it. To browse by subject instead, see <a href="../topics/index.html">Topics</a>.</p>
</section>
<section class="grid" style="padding-bottom:96px">{"".join(law_cards)}</section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
    (OUT / "law" / "index.html").write_text(page, encoding="utf-8")

    # law tags on post and guide pages
    for r in records:
        p = OUT / "posts" / f'{r["slug"]}.html'
        t = p.read_text(encoding="utf-8")
        t = re.sub(r'\n?<div class="law-tags">.*?</div>(?=\n<p class="origin">)', "", t, flags=re.S)
        if r["laws"]:
            t = t.replace('\n<p class="origin">', "\n" + law_links(r["laws"], "../") + '\n<p class="origin">', 1)
        p.write_text(t, encoding="utf-8")
    for g in guides:
        p = OUT / "guides" / f'{g["slug"]}.html'
        t = p.read_text(encoding="utf-8")
        t = re.sub(r'\n?<div class="law-tags">.*?</div>(?=\n<div class="origin">)', "", t, flags=re.S)
        if g["laws"]:
            t = t.replace('\n<div class="origin">', "\n" + law_links(g["laws"], "../") + '\n<div class="origin">', 1)
        p.write_text(t, encoding="utf-8")

    # ---------------------------------------------------------- monthly reviews
    (OUT / "reviews").mkdir(exist_ok=True)
    months = sorted({r["date"][:7] for r in records} | {u["date"][:7] for u in updates}, reverse=True)
    months = [m for m in months if m <= today[:7]]
    rev_cards = []
    for ym in months:
        ps = [r for r in records if r["date"][:7] == ym]
        us = [u for u in updates if u["date"][:7] == ym]
        dec = [c for c in allcases if c["status"] == "decided" and c.get("decided", "")[:7] == ym]
        ev = sorted([(t[0], c, t[1]) for c in allcases for t in c["d"].get("timeline", []) if t[0][:7] == ym and len(t[0]) == 10 and t[0] <= today], key=lambda x: x[0])
        nxt = [e for e in events if e["date"] > today][:6] if ym == today[:7] else []
        so_far = ym == today[:7]
        title = f"{fd(ym)} in tech law" + (" (so far)" if so_far else "")
        intro_p = SRC / "reviews" / f"{ym}.md"
        intro = ""
        if intro_p.exists():
            intro = "".join(f"<p>{esc(x.strip())}</p>" for x in intro_p.read_text(encoding="utf-8").split("\n\n") if x.strip())
        stats = (f'<div class="stats"><div><b>{len(ev)}</b><span>court developments</span></div><div><b>{len(dec)}</b><span>cases decided</span></div>'
                 f'<div><b>{len(ps)}</b><span>analysis posts</span></div><div><b>{len(us)}</b><span>case updates</span></div></div>')
        ev_html = "".join(f'<li><time datetime="{d_}">{fmt_date(d_)}</time><span><a href="../cases/{c["id"]}.html">{esc(c["short"])}</a> ({esc(c["court"])}): {esc(txt)}</span></li>' for d_, c, txt in ev)
        ps_html = "".join(f'<a class="item" href="../posts/{r["slug"]}.html"><span class="date">{fmt_date(r["date"])}</span><span class="body"><span class="t">{esc(r["title"])}</span><span class="s">{esc(r["summary"])}</span></span><span class="tag">{esc(r["kicker"])}</span></a>' for r in sorted(ps, key=lambda r: r["date"]))
        nxt_html = "".join(f'<li><time datetime="{e["date"]}">{fmt_date(e["date"])}</time><a href="../{"cases/" + e["case"] + ".html" if e.get("case") else "calendar.html"}">{esc(e["label"])}</a></li>' for e in nxt)
        page = head(f"{title} — Custos", f"What happened in Indian technology law in {fd(ym)}: court developments, decided cases and analysis.", "../") + header("../", "writing") + f'''
<main>
<article class="article review">
{X.crumbs("../", [("Home", "index.html"), ("Month in review", "reviews/index.html"), (fd(ym), None, f"reviews/{ym}.html")])}
<span class="kicker">Review</span>
<h1>{esc(title)}</h1>
<p class="dek">The month's court developments in the cases I track, and what I wrote about them.</p>
{stats}
{f'<div class="prose">{intro}</div>' if intro else ""}
{f'<section class="case-block"><h2>In court</h2><ol class="timeline">{ev_html}</ol></section>' if ev_html else ""}
{f'<section class="case-block"><h2>Analysis this month</h2><div class="group">{ps_html}</div></section>' if ps_html else ""}
{f'<section class="case-block"><h2>Coming up</h2><ol class="watch-list">{nxt_html}</ol><p class="small"><a href="../calendar.html">Full calendar</a></p></section>' if nxt_html else ""}
<p class="origin">Compiled from the case tracker and posts on this site. For general information only; not legal advice.</p>
</article>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
        (OUT / "reviews" / f"{ym}.html").write_text(page, encoding="utf-8")
        rev_cards.append(f'<a class="card" href="{ym}.html"><span class="kicker">Review</span><h3>{esc(title)}</h3><p>{len(ev)} court developments, {len(dec)} decided, {len(ps)} posts.</p></a>')
    page = head("Month in review — Custos", "Monthly round-ups of Indian technology law: court developments, decided cases and analysis.", "../") + header("../", "writing") + f'''
<main class="wrap">
<section class="page-head">
{X.crumbs("../", [("Home", "index.html"), ("Month in review", None, "reviews/index.html")])}
<h1>Month in review</h1>
<p>Each month's developments in the cases I track, the cases decided, and what I wrote.</p>
</section>
<section class="grid" style="padding-bottom:96px">{"".join(rev_cards)}</section>
</main>
''' + footer("../") + "\n</body>\n</html>\n"
    (OUT / "reviews" / "index.html").write_text(page, encoding="utf-8")

    # ---------------------------------------------------------- site search
    ent = []
    for r in records:
        ent.append({"t": r["title"], "u": f'posts/{r["slug"]}.html', "k": "Analysis", "d": r["date"], "s": r["summary"],
                    "x": " ".join([r["title"]] + r["blocks"] + r["tags"])})
    for u in updates:
        ent.append({"t": u["title"], "u": f'updates/{u["slug"]}.html', "k": "Case update", "d": u["date"], "s": u["summary"], "x": " ".join(u["body"])})
    for c in allcases:
        ent.append({"t": c["name"], "u": f'cases/{c["id"]}.html', "k": "Case", "d": "", "s": c["issue"],
                    "x": " ".join([c["name"], c["parties"], c["issue"], c["stands"], c["court"]] + c["d"].get("issues", []))})
    for g in guides:
        ent.append({"t": g["title"], "u": f'guides/{g["slug"]}.html', "k": "Guide", "d": g["updated"], "s": g["description"], "x": g["body"]})
    for gl in X.GLOSSARY:
        ent.append({"t": gl["term"], "u": f'glossary.html#{X.slug(gl["term"])}', "k": "Glossary", "d": "", "s": gl["def"], "x": gl["def"]})
    for lid, name, desc, _ in LAWS:
        if lid in built_laws:
            ent.append({"t": name, "u": f"law/{lid}.html", "k": "Law", "d": "", "s": desc, "x": desc})
    for nm, u, s in [("Cyber fraud: what to do right now", "toolkit/cyber-fraud.html", "Steps after a scam call, lost money, hacked account or sextortion: 1930, cybercrime.gov.in, your bank."),
                     ("DPDP readiness checker", "toolkit/dpdp-checker.html", "A checklist of DPDP Act duties for your business."),
                     ("Case calendar", "calendar.html", "Upcoming hearing dates in technology-law cases.")]:
        ent.append({"t": nm, "u": u, "k": "Tool", "d": "", "s": s, "x": s})
    for e in ent:
        e["x"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|[#*_>\[\]()|]", " ", e["x"])).lower()
    (OUT / "site-search.json").write_text(json.dumps(ent, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    kinds = ["All", "Analysis", "Case", "Case update", "Guide", "Law", "Glossary", "Tool"]
    chips = "".join(f'<button type="button" class="chip" data-k="{k}" aria-pressed="{"true" if k == "All" else "false"}">{k}</button>' for k in kinds)
    page = head("Search — Custos", "Search posts, cases, case updates, guides, laws and the glossary.", "") + header("") + f'''
<main class="wrap" style="max-width:860px">
<section class="page-head">
{X.crumbs("", [("Home", "index.html"), ("Search", None, "search.html")])}
<h1>Search</h1>
<form class="search" role="search" onsubmit="return false">
<label for="sq" class="label">Search the whole site</label>
<input id="sq" type="search" placeholder="Try “safe harbour”, “1930”, “Amazon” or “Article 21”" autocomplete="off" autofocus>
</form>
<div class="filters" role="group" aria-label="Filter by type">{chips}</div>
<p id="sc" class="small" aria-live="polite"></p>
</section>
<section class="groups" style="padding-bottom:96px"><div class="group" id="sr"></div></section>
</main>
''' + footer("") + '''
<script>
(function () {
  var input = document.getElementById('sq'), out = document.getElementById('sr'), cnt = document.getElementById('sc');
  var chips = document.querySelectorAll('.chip'), kind = 'All', data = null, t;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function fmt(d) { if (!d) return ''; var m = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; return +d.slice(8) + ' ' + m[+d.slice(5, 7) - 1] + ' ' + d.slice(0, 4); }
  function run() {
    if (!data) return;
    var q = input.value.trim().toLowerCase(), words = q ? q.split(/\\s+/) : [];
    if (!words.length) { out.innerHTML = ''; cnt.textContent = 'Type to search ' + data.length + ' pages.'; return; }
    var res = data.filter(function (e) {
      if (kind !== 'All' && e.k !== kind) return false;
      var hay = e.t.toLowerCase() + ' ' + e.x;
      return words.every(function (w) { return hay.indexOf(w) !== -1; });
    }).map(function (e) {
      var tl = e.t.toLowerCase(), sc = 0;
      words.forEach(function (w) { if (tl.indexOf(w) !== -1) sc += 5; sc += Math.min(5, e.x.split(w).length - 1); });
      return [sc, e];
    }).sort(function (a, b) { return b[0] - a[0] || (b[1].d || '').localeCompare(a[1].d || ''); });
    cnt.textContent = res.length + (res.length === 1 ? ' result' : ' results');
    out.innerHTML = res.slice(0, 60).map(function (r) {
      var e = r[1];
      return '<a class="item" href="' + esc(e.u) + '"><span class="date">' + (fmt(e.d) || esc(e.k)) + '</span><span class="body"><span class="t">' + esc(e.t) +
        '</span><span class="s">' + esc(e.s) + '</span></span><span class="tag">' + esc(e.k) + '</span></a>';
    }).join('');
    try { history.replaceState(null, '', '?q=' + encodeURIComponent(input.value.trim())); } catch (err) {}
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { kind = c.getAttribute('data-k'); chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); }); run(); }); });
  input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 120); });
  var q = new URLSearchParams(location.search).get('q'); if (q) input.value = q;
  fetch('site-search.json').then(function (r) { return r.json(); }).then(function (d) { data = d; run(); }).catch(function () { cnt.textContent = 'Search could not load. Try again later.'; });
})();
</script>
</body>
</html>
'''
    (OUT / "search.html").write_text(page, encoding="utf-8")

    # ---------------------------------------------------------- tracker page: link cards to case pages
    p = OUT / "cases.html"
    t = p.read_text(encoding="utf-8")
    for c in allcases:
        t = re.sub(rf'(<article class="case" id="{re.escape(c["id"])}".*?)<h3>(.*?)</h3>',
                   lambda m: f'{m.group(1)}<h3><a href="cases/{c["id"]}.html">{m.group(2)}</a></h3>', t, count=1, flags=re.S)
        t = re.sub(rf'(<article class="case" id="{re.escape(c["id"])}".*?)(<div class="case-foot">)',
                   lambda m: f'{m.group(1)}{m.group(2)}\n<a class="case-more" href="cases/{c["id"]}.html">Case page: timeline, key issues{", updates" if c["updates"] else ""} →</a>',
                   t, count=1, flags=re.S)
    t = t.replace('<p class="small">Follow every case update by <a href="cases/feed.xml">RSS</a>',
                  '<p class="small"><a href="calendar.html">Hearing calendar</a> · <a href="updates/index.html">Case updates</a> · Follow every case update by <a href="cases/feed.xml">RSS</a>', 1)
    t = re.sub(r'<li><time datetime="([^"]+)">([^<]+)</time><a href="#([^"]+)">', r'<li><time datetime="\1">\2</time><a href="cases/\3.html">', t)
    p.write_text(t, encoding="utf-8")

    # ---------------------------------------------------------- home page sections
    p = OUT / "index.html"
    t = p.read_text(encoding="utf-8")
    # Updates strip after the lead story
    up_cards = "".join(
        f'<a class="card update-card" href="updates/{u["slug"]}.html"><span class="kicker">Case update · {esc(byid[u["case"]]["court"])}</span>'
        f'<h3><span class="case-name">{esc(byid[u["case"]]["short"])}</span> | {esc(u["headline"])}</h3><span class="meta">{fmt_date(u["date"])}</span></a>' for u in updates[:3])
    strip = f'''<section class="wrap section" id="updates-strip">
<div class="section-head">
<h2 class="h2">Latest case updates</h2>
<a href="updates/index.html" style="font-size:15px;font-weight:600;padding:12px 0">All updates</a>
</div>
<div class="grid">
{up_cards}
</div>
</section>'''
    # Case Watch + Case Calendar replace the old tracker teaser
    watch_cases = sorted([c for c in allcases if c["status"] == "pending"], key=lambda c: (c.get("next") or "9999", c["name"]))
    watch_cases = [c for c in watch_cases if (c.get("next") or "") >= today][:3] or watch_cases[:3]
    wc = "".join(
        f'<a class="watch-card" href="cases/{c["id"]}.html"><span class="case-top"><span class="pill pill-{c["status"]}">{STATUS[c["status"]]}</span>'
        f'<span class="case-court">{esc(c["court"])}</span></span><b>{esc(c["name"])}</b><span class="small">{esc(c["issue"])}</span>'
        f'<span class="meta">{when_text(c)[0]}: {esc(when_text(c)[1])}</span></a>' for c in watch_cases)
    ce = "".join(
        f'<li><time datetime="{e["date"]}">{fmt_date(e["date"])}</time><a href="{"cases/" + e["case"] + ".html" if e.get("case") else "calendar.html"}">{esc(e["label"])}</a></li>'
        for e in events[:5])
    court = f'''<section class="wrap section" id="court">
<div class="court-grid">
<div class="court-col">
<div class="section-head" style="padding-bottom:0"><h2 class="h2" style="font-size:28px">Case watch</h2><a href="cases.html" style="font-size:15px;font-weight:600;padding:12px 0">All {len(allcases)} cases</a></div>
<div class="watch-cards">{wc}</div>
</div>
<div class="court-col">
<div class="section-head" style="padding-bottom:0"><h2 class="h2" style="font-size:28px">Case calendar</h2><a href="calendar.html" style="font-size:15px;font-weight:600;padding:12px 0">Full calendar</a></div>
<ol class="watch-list">{ce}</ol>
<a class="small" href="calendar.ics" download>Add these dates to your calendar (.ics)</a>
</div>
</div>
</section>'''
    tools_strip = f'''<section class="wrap section" id="tools-strip">
<div class="section-head">
<h2 class="h2">Tools and references</h2>
<a href="toolkit/index.html" style="font-size:15px;font-weight:600;padding:12px 0">All tools</a>
</div>
<div class="grid">
<a class="card" href="toolkit/cyber-fraud.html"><span class="kicker">Tool</span><h3>Cyber fraud: what to do right now</h3><p>Scam call, money lost, hacked account or sextortion: the steps in order.</p></a>
<a class="card" href="toolkit/dpdp-checker.html"><span class="kicker">Tool</span><h3>DPDP readiness checker</h3><p>A tailored checklist of what the DPDP Act expects from your business.</p></a>
<a class="card" href="reviews/{months[0]}.html"><span class="kicker">Review</span><h3>{fd(months[0])} in tech law</h3><p>The month's court developments and analysis in one place.</p></a>
<a class="card" href="law/index.html"><span class="kicker">Laws</span><h3>Follow a law</h3><p>Every case, guide and post on the DPDP Act, IT Act, IT Rules, Copyright Act and more.</p></a>
</div>
</section>'''
    i0 = t.index('<section class="wrap section">\n<div class="tracker-teaser">')
    i1 = t.index("</section>", i0) + len("</section>")
    t = t[:i0] + tools_strip + t[i1:]
    f0 = t.index('<section class="wrap section">\n<a class="featured"')
    f1 = t.index("</section>", f0) + len("</section>")
    t = t[:f1] + "\n\n" + strip + "\n\n" + court + t[f1:]
    t = t.replace('<span class="kicker">Latest · ', '<span class="kicker">Latest analysis · ', 1)
    p.write_text(t, encoding="utf-8")

    print(len(allcases), "case pages;", len(updates), "updates;", len(events), "calendar dates;", len(built_laws), "law pages;", len(months), "reviews;", len(ent), "search entries")
