#!/usr/bin/env python3
"""
update_supporting_files.py

Patches the mechanical fields in index.html, archive.html, and email_copy.html
when a new Market Pulse article is published. Requires no HTML parsing; uses
exact string replacement on known, stable patterns.

Usage:
    python3 docs/skills/update_supporting_files.py \
        --new-file market_pulse_november14_2026.html \
        --old-file market_pulse_november13_2026.html \
        --date "November 14, 2026" \
        --day "Saturday" \
        --headline "Some Headline Text Here."

Arguments:
    --new-file   New article filename (e.g. market_pulse_november14_2026.html)
    --old-file   Previous article filename (the one being displaced from "current")
    --date       Long date, e.g. "November 14, 2026"
    --day        Day of week, e.g. "Saturday"
    --headline   Article headline, verbatim (must match article <h1> exactly)

What it patches:
    index.html
      - Nav Market Pulse link (old-file → new-file)
      - Inserts new post-card at top of Market Pulse column
      - Removes badge-new from previously-newest post-card
      - Hero card href, cap-kicker, cap-title, cap-date

    archive.html
      - Nav Market Pulse link
      - Inserts new post-card at top of Market Pulse column
      - Removes badge-new from previously-newest post-card

    email_copy.html
      - Nav Market Pulse link
      - Subject lines date header
      - Both email templates: <title>, hero kicker, hero headline, all article href occurrences

Before patching, it checks --headline against the article's <h1> and stops if they differ.

What it clears to ${STEP_4_NOT_WRITTEN} (agent writes these fresh each day):
    - Subject line text (A/B/C) and their notes
    - Email preheader, lead paragraph, data snapshot
    - Email bullet text (open-1 through open-5)
"""

import argparse
import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_BASE = "https://totem-challenge-preview.vercel.app"
STEP4_PLACEHOLDER = "${STEP_4_NOT_WRITTEN}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        sys.exit(f"ERROR: could not find pattern in {label}:\n  {old!r}")
    count = text.count(old)
    if count > 1:
        sys.exit(f"ERROR: pattern found {count} times in {label} (expected 1):\n  {old!r}")
    return text.replace(old, new, 1)


def replace_all(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------

def patch_index(args: argparse.Namespace) -> None:
    path = REPO_ROOT / "index.html"
    text = read(path)

    # 1. Nav link
    text = replace_once(
        text,
        f'<a href="{args.old_file}">Market Pulse</a>',
        f'<a href="{args.new_file}">Market Pulse</a>',
        "index.html nav",
    )

    # 2. Remove badge-new from the previously-newest post-card
    old_badge_line = (
        f'<a class="post-card" href="{args.old_file}">\n'
        f'      <div class="post-title">'
    )
    # Find the old post-card's post-title div and strip any badge-new from it
    # The badge-new looks like: <span class="badge-new">New</span>
    text = re.sub(
        r'(<a class="post-card" href="' + re.escape(args.old_file) + r'">\s*'
        r'<div class="post-title">.*?)(\s*<span class="badge-new">New</span>)(.*?</div>)',
        r'\1\3',
        text,
        count=1,
        flags=re.DOTALL,
    )

    # 3. Insert new post-card after the Market Pulse col-rule
    new_post_card = (
        f'\n    <a class="post-card" href="{args.new_file}">\n'
        f'      <div class="post-title">{args.headline} <span class="badge-new">New</span></div>\n'
        f'      <div class="post-date">{args.date}</div>\n'
        f'    </a>'
    )
    # index.html has a "Daily Updates" subline between col-title and col-rule
    anchor = (
        '<div class="col-title">Market Pulse</div>\n'
        '    <div style="font-family:\'Work Sans\',sans-serif;font-size:10px;font-weight:700;'
        'letter-spacing:0.14em;text-transform:uppercase;color:var(--gold);margin-bottom:6px;">'
        'Daily Updates</div>\n'
        '    <hr class="col-rule">'
    )
    text = replace_once(
        text,
        anchor,
        anchor + new_post_card,
        "index.html post-card insertion",
    )

    # 4. Hero card: href
    text = replace_once(
        text,
        f'<a class="hero-card" id="hero-pulse" href="{args.old_file}">',
        f'<a class="hero-card" id="hero-pulse" href="{args.new_file}">',
        "index.html hero href",
    )

    # 5. Hero cap-kicker
    # Pattern: <div class="cap-kicker">November 13, 2026</div>
    # We replace the first (and only) cap-kicker inside hero-pulse.
    # Since the hero block is unique we just find the old date string.
    text = replace_once(
        text,
        f'<div class="cap-kicker">{args.old_date}</div>',
        f'<div class="cap-kicker">{args.date}</div>',
        "index.html cap-kicker",
    )

    # 6. Hero cap-title
    text = replace_once(
        text,
        f'<div class="cap-title">{args.old_headline}</div>',
        f'<div class="cap-title">{args.headline}</div>',
        "index.html cap-title",
    )

    # 7. Hero cap-date  (old: "Friday, November 13, 2026")
    text = replace_once(
        text,
        f'<div class="cap-date">{args.old_day}, {args.old_date}</div>',
        f'<div class="cap-date">{args.day}, {args.date}</div>',
        "index.html cap-date",
    )

    write(path, text)
    print("index.html  ✓")


# ---------------------------------------------------------------------------
# archive.html
# ---------------------------------------------------------------------------

def patch_archive(args: argparse.Namespace) -> None:
    path = REPO_ROOT / "archive.html"
    text = read(path)

    # 1. Nav link
    text = replace_once(
        text,
        f'<a href="{args.old_file}">Market Pulse</a>',
        f'<a href="{args.new_file}">Market Pulse</a>',
        "archive.html nav",
    )

    # 2. Remove badge-new from previously-newest post-card
    text = re.sub(
        r'(<a class="post-card" href="' + re.escape(args.old_file) + r'">\s*'
        r'<div class="post-title">.*?)(\s*<span class="badge-new">New</span>)(.*?</div>)',
        r'\1\3',
        text,
        count=1,
        flags=re.DOTALL,
    )

    # 3. Insert new post-card after Market Pulse col-rule
    new_post_card = (
        f'\n    <a class="post-card" href="{args.new_file}">\n'
        f'      <div class="post-title">{args.headline} <span class="badge-new">New</span></div>\n'
        f'      <div class="post-date">{args.date}</div>\n'
        f'    </a>'
    )
    anchor = '<div class="col-title">Market Pulse</div>\n    <hr class="col-rule">'
    text = replace_once(
        text,
        anchor,
        anchor + new_post_card,
        "archive.html post-card insertion",
    )

    write(path, text)
    print("archive.html  ✓")


# ---------------------------------------------------------------------------
# email_copy.html
# ---------------------------------------------------------------------------

def patch_email(args: argparse.Namespace) -> None:
    path = REPO_ROOT / "email_copy.html"
    text = read(path)

    # 1. Nav link
    text = replace_once(
        text,
        f'<a href="{args.old_file}">Market Pulse</a>',
        f'<a href="{args.new_file}">Market Pulse</a>',
        "email_copy.html nav",
    )

    # 2. Subject lines date header
    text = replace_once(
        text,
        f"Suggested Subject Lines - {args.old_date}",
        f"Suggested Subject Lines - {args.date}",
        "email_copy.html subject header",
    )

    # 3. Member <title>
    text = replace_once(
        text,
        f"<title>Market Pulse - {args.old_date} - Member Edition</title>",
        f"<title>Market Pulse - {args.date} - Member Edition</title>",
        "email_copy.html member title",
    )

    # 4. Non-member <title>
    text = replace_once(
        text,
        f"<title>Market Pulse - {args.old_date}</title>",
        f"<title>Market Pulse - {args.date}</title>",
        "email_copy.html non-member title",
    )

    # 5. Member hero kicker  e.g. "Friday, November 13, 2026 · Member Edition"
    text = replace_once(
        text,
        f"{args.old_day}, {args.old_date} &middot; Member Edition",
        f"{args.day}, {args.date} &middot; Member Edition",
        "email_copy.html member kicker",
    )

    # 6. Non-member hero kicker  e.g. "Friday, November 13, 2026 · Friday Briefing"
    text = replace_once(
        text,
        f"{args.old_day}, {args.old_date} &middot; {args.old_day} Briefing",
        f"{args.day}, {args.date} &middot; {args.day} Briefing",
        "email_copy.html non-member kicker",
    )

    # 7. Hero headline in both templates must equal the article headline word for word
    hero_re = re.compile(
        r'(font-weight: 700; font-size: 18px; line-height: 1\.4; color: #ffffff;">)(.*?)(</p>)',
        re.DOTALL,
    )
    hero_count = len(hero_re.findall(text))
    if hero_count != 2:
        sys.exit(f"ERROR: expected 2 email hero headlines in email_copy.html, found {hero_count}")
    text = hero_re.sub(lambda m: m.group(1) + args.headline + m.group(3), text)

    # 8. Clear yesterday's agent-written copy. The sender blocks any email that still
    #    holds a ${...} placeholder, so an unwritten Step 4 field stops the send instead
    #    of mailing yesterday's words under today's date and links.
    step4_fields = [
        ("subject lines A/B/C", r'(font-size:17px;font-weight:700;color:#16181d;line-height:1\.3;">)(.*?)(</p>)', 3),
        ("subject line notes", r'(<p style="margin:4px 0 0;font-family:\'Work Sans\',sans-serif;font-size:11px;color:#9aa0a8;">)(.*?)(</p>)', 3),
        ("preheader", r'(mso-hide: all; font-size: 1px; line-height: 1px; color: #f7f8fa;">\s*)(.*?)(\s*</div>)', 2),
        ("lead paragraph", r'(font-size: 21px; font-weight: 700; line-height: 1\.35; color: #16181d;">)(.*?)(</p>)', 2),
        ("data snapshot", r'(font-size: 14px; line-height: 1\.65; color: #26292f;">)(.*?)(</p>)', 2),
        ("five bullets", r'(#open-[1-5]" style="color: #16181d; text-decoration: none; font-weight: 700;">)(.*?)(</a>)', 10),
    ]
    for label, pattern, expected in step4_fields:
        rx = re.compile(pattern, re.DOTALL)
        found = len(rx.findall(text))
        if found != expected:
            sys.exit(f"ERROR: expected {expected} {label} in email_copy.html, found {found}")
        text = rx.sub(lambda m: m.group(1) + STEP4_PLACEHOLDER + m.group(3), text)

    # 9. All article href occurrences in both templates
    #    Covers: hero links, open-1 through open-5, bottom CTA
    old_article_url = f"{LIVE_BASE}/{args.old_file}"
    new_article_url = f"{LIVE_BASE}/{args.new_file}"
    if old_article_url not in text:
        sys.exit(f"ERROR: could not find any occurrence of {old_article_url!r} in email_copy.html")
    text = replace_all(text, old_article_url, new_article_url)

    write(path, text)
    print("email_copy.html  ✓")


def normalize(s: str) -> str:
    s = html.unescape(s).replace("’", "'").replace("‘", "'")
    return " ".join(s.split())


def check_headline_matches_article(args: argparse.Namespace) -> None:
    article = REPO_ROOT / args.new_file
    if not article.exists():
        sys.exit(f"ERROR: article {args.new_file} not found; write it before running this script")
    m = re.search(r'<h1 class="headline">(.*?)</h1>', read(article), re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no <h1 class=\"headline\"> in {args.new_file}")
    if normalize(re.sub(r"<[^>]+>", "", m.group(1))) != normalize(args.headline):
        sys.exit(
            "ERROR: --headline does not match the article headline word for word\n"
            f"  article:  {normalize(m.group(1))!r}\n  argument: {normalize(args.headline)!r}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Patch supporting files for a new Market Pulse article.")
    parser.add_argument("--new-file",   required=True, help="New article filename")
    parser.add_argument("--old-file",   required=True, help="Previous article filename")
    parser.add_argument("--date",       required=True, help="Long date, e.g. 'November 14, 2026'")
    parser.add_argument("--day",        required=True, help="Day of week, e.g. 'Saturday'")
    parser.add_argument("--headline",   required=True, help="Article headline verbatim")
    # Old date and old day are derived from old_file by default but can be
    # overridden if the previous article used a different format.
    parser.add_argument("--old-date",   default=None, help="Previous article long date (auto-derived if omitted)")
    parser.add_argument("--old-day",    default=None, help="Previous article day of week (auto-derived if omitted)")
    parser.add_argument("--old-headline", default=None, help="Previous article headline (required for index.html hero)")
    args = parser.parse_args()

    # Derive old-date from old-file if not supplied
    if args.old_date is None or args.old_day is None or args.old_headline is None:
        # Read old date/day/headline from the existing hero card in index.html
        index_text = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        if args.old_date is None:
            m = re.search(r'<div class="cap-kicker">([^<]+)</div>', index_text)
            if not m:
                sys.exit("ERROR: could not auto-derive --old-date from index.html cap-kicker")
            args.old_date = m.group(1).strip()
        if args.old_day is None:
            m = re.search(r'<div class="cap-date">(\w+),', index_text)
            if not m:
                sys.exit("ERROR: could not auto-derive --old-day from index.html cap-date")
            args.old_day = m.group(1).strip()
        if args.old_headline is None:
            m = re.search(r'<div class="cap-title">([^<]+)</div>', index_text)
            if not m:
                sys.exit("ERROR: could not auto-derive --old-headline from index.html cap-title")
            args.old_headline = m.group(1).strip()

    check_headline_matches_article(args)
    patch_index(args)
    patch_archive(args)
    patch_email(args)
    print("\nAll three files patched. Review the diff before committing.")


if __name__ == "__main__":
    main()
