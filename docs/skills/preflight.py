#!/usr/bin/env python3
"""
preflight.py - checks a Market Pulse build against the locked CLAUDE.md rules
before it is pushed. Prints one line per check and exits 1 if any check fails.

Usage:
    python3 docs/skills/preflight.py market_pulse_november16_2026.html

Run it after Step 4 (email copy written) and before the editorial push. Fix
every FAIL, then run it again. WARN lines do not block.
"""

import datetime
import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_BASE = "https://totem-challenge-preview.vercel.app"
DISCLAIMER = (
    "This material is provided for informational purposes only and does not constitute legal, "
    "tax, securities, lending, investment, or financial advice. Participation in commercial "
    "transactions involves risk, including possible loss of capital. Historical performance "
    "does not guarantee future outcomes."
)
BAN = ("strikes", "war", "crisis", "collapse", "crash", "fear", "plunge", "panic", "attack", "escalation")

results = []


def check(ok, label, detail=""):
    results.append(("PASS" if ok else "FAIL", label, detail))


def warn(ok, label, detail=""):
    results.append(("PASS" if ok else "WARN", label, detail))


def plain(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("’", "'").replace("‘", "'").replace("\xa0", " ")
    return " ".join(s.split())


def words(s):
    return len(plain(s).split())


def first8(s):
    return [w.strip(".,:;!?'\"()").lower() for w in plain(s).split()[:8]]


def load_sender():
    g = {"__name__": "pulse_preflight", "PULSE_MODE": "send", "PULSE_PREFETCH": True}
    src = (REPO_ROOT / "scripts" / "send_market_pulse.py").read_text(encoding="utf-8")
    exec(compile(src, "send_market_pulse.py", "exec"), g)
    return g


def date_from_filename(name):
    m = re.fullmatch(r"market_pulse_([a-z]+)(\d{1,2})_(\d{4})\.html", name)
    if not m:
        sys.exit(f"ERROR: {name} is not a market_pulse_[month][day]_[year].html file name")
    return datetime.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date()


def column(page, title):
    start = page.find(f'<div class="col-title">{title}</div>')
    end = page.find('<div class="col-title">', start + 1)
    return page[start:end if end != -1 else len(page)] if start != -1 else ""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    name = Path(sys.argv[1]).name
    day = date_from_filename(name)
    art_url = f"{LIVE_BASE}/{name}"
    article_path = REPO_ROOT / name
    if not article_path.exists():
        sys.exit(f"ERROR: {name} not found")
    article = article_path.read_text(encoding="utf-8")
    email_page = (REPO_ROOT / "email_copy.html").read_text(encoding="utf-8")
    index = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
    archive = (REPO_ROOT / "archive.html").read_text(encoding="utf-8")

    # ---- article -------------------------------------------------------------
    m = re.search(r'<h1 class="headline">(.*?)</h1>', article, re.S)
    headline = plain(m.group(1)) if m else ""
    check(bool(headline), "article headline present")
    check(words(headline) <= 12, "headline is 12 words or fewer", f"{words(headline)} words")

    opens = {}
    for n in range(1, 6):
        hits = re.findall(rf'<li id="open-{n}"><b>(.*?)</b>', article, re.S)
        check(len(hits) == 1, f"article anchor open-{n} present once", f"found {len(hits)}")
        opens[n] = plain(hits[0]) if hits else ""

    check(article.count(DISCLAIMER) == 1, "article carries the General Disclaimer verbatim")

    body = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", article, flags=re.S)
    text = plain(body)
    bad_times = re.findall(r"\b\d{1,2}:\d{2}\s?(?:ET|CT|MT|PT|UTC)\b", text)
    check(not bad_times, "every clock time carries AM or PM", ", ".join(bad_times[:3]))
    warn("—" not in text, "no em dashes in the article")

    # ---- email copy ----------------------------------------------------------
    check("STEP_4_NOT_WRITTEN" not in email_page, "every Step 4 email field is written",
          f"{email_page.count('STEP_4_NOT_WRITTEN')} placeholders left")

    try:
        sender = load_sender()
        copy = sender["parse_copy"](email_page)
        sender["check_copy"](copy, day)
        sender["link_rules"](copy["member_html"], art_url)
        check(True, "the 6:15 AM MT sender would accept this email")
    except Exception as e:  # sender raises Blocked; anything else is also a failure
        copy = None
        check(False, "the 6:15 AM MT sender would accept this email", str(e)[:160])

    heroes = [plain(h) for h in re.findall(
        r'font-size: 18px; line-height: 1\.4; color: #ffffff;">(.*?)</p>', email_page, re.S)]
    check(len(heroes) == 2 and all(h == headline for h in heroes),
          "both email heroes match the article headline word for word")

    check(email_page.count(DISCLAIMER) == 2, "both email footers carry the General Disclaimer verbatim")

    templates = {}
    for var in ("memberEmailHTML", "nonMemberEmailHTML"):
        m = re.search(rf"var {var}=`(.*?)`;", email_page, re.S)
        templates[var] = m.group(1) if m else ""

    for var, t in templates.items():
        who = "member" if var == "memberEmailHTML" else "non-member"
        bullets = {int(n): plain(b) for n, b in re.findall(
            r'#open-([1-5])" style="color: #16181d; text-decoration: none; font-weight: 700;">(.*?)</a>', t, re.S)}
        check(sorted(bullets) == [1, 2, 3, 4, 5], f"{who} email has bullets open-1 to open-5")
        for n, b in sorted(bullets.items()):
            check(words(b) <= 15, f"{who} bullet {n} is 15 words or fewer", f"{words(b)} words")
            check(b == opens.get(n), f"{who} bullet {n} matches the article's open-{n} lead verbatim",
                  f"email: {b[:60]!r} | article: {opens.get(n, '')[:60]!r}")
        lead = re.search(r'font-size: 21px; font-weight: 700; line-height: 1\.35; color: #16181d;">(.*?)</p>', t, re.S)
        pre = re.search(r'mso-hide: all; font-size: 1px; line-height: 1px; color: #f7f8fa;">(.*?)</div>', t, re.S)
        snap = re.search(r'font-size: 14px; line-height: 1\.65; color: #26292f;">(.*?)</p>', t, re.S)
        lead, pre, snap = (plain(x.group(1)) if x else "" for x in (lead, pre, snap))
        check(words(lead) <= 25, f"{who} lead is 25 words or fewer", f"{words(lead)} words")
        check(words(pre) <= 12, f"{who} preheader is 12 words or fewer", f"{words(pre)} words")
        items = [s for s in re.split(r"\s·\s", snap) if s.strip()]
        check(len(items) <= 5, f"{who} snapshot has 5 items or fewer", f"{len(items)} items")
        total = words(pre) + words(lead) + words(snap) + sum(words(b) for b in bullets.values())
        check(total <= 120, f"{who} body copy is 120 words or fewer", f"{total} words")
        for label, s in (("preheader", pre), ("lead", lead), ("hero", headline)):
            hit = [w for w in first8(s) if w in BAN]
            check(not hit, f"{who} {label}: no ban-list word in the first 8 words", ", ".join(hit))

    if copy:
        hit = [w for w in first8(copy["subject_A"]) if w in BAN]
        check(not hit, "subject line A: no ban-list word in the first 8 words", ", ".join(hit))

    # ---- index and archive ---------------------------------------------------
    for label, page in (("index.html", index), ("archive.html", archive)):
        col = column(page, "Market Pulse")
        first = re.search(r'<a class="post-card" href="([^"]+)">', col)
        check(bool(first) and first.group(1) == name, f"{label}: today's post-card is first in Market Pulse")
        badges = col.count('class="badge-new"')
        check(badges == 1, f"{label}: exactly one New badge in Market Pulse", f"found {badges}")
        check(f'<a href="{name}">Market Pulse</a>' in page, f"{label}: nav Market Pulse link points to today")
    check(f'id="hero-pulse" href="{name}"' in index, "index.html: hero card links to today's article")
    cap = re.search(r'id="hero-pulse".*?<div class="cap-title">(.*?)</div>', index, re.S)
    check(bool(cap) and plain(cap.group(1)) == headline, "index.html: hero title matches the article headline")

    # ---- report --------------------------------------------------------------
    shown = results
    width = max(len(r[1]) for r in shown)
    for status, label, detail in shown:
        print(f"{status}  {label.ljust(width)}  {detail if status != 'PASS' else ''}".rstrip())
    fails = sum(r[0] == "FAIL" for r in shown)
    warns = sum(r[0] == "WARN" for r in shown)
    print(f"\n{len(shown) - fails - warns} passed, {fails} failed, {warns} warnings")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
