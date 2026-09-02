#!/usr/bin/env python3
"""Strip or restore the editorial nav links in every public HTML file.

Phase 2 live deploy uses this. Never sed (sed has corrupted files before).

  python3 scripts/nav_links.py strip     # before `vercel --prod`
  python3 scripts/nav_links.py restore   # after the deploy, before the commit
  python3 scripts/nav_links.py check     # prints how many files carry the links

Skips email_copy.html and emergency_po.html themselves. Strip matches the
two <li> items by content, ignoring leading whitespace. Restore inserts
them just before the nav's closing </ul>, so it works even in the older
files where the Archive link shares a line with The Challenge link.
"""
import re, sys, glob, os

SKIP = {"email_copy.html", "emergency_po.html"}
EMAIL = '<li><a href="email_copy.html">Email Copy</a></li>'
PO = '<li><a href="emergency_po.html">Emergency PO</a></li>'
STRIP_RE = re.compile(
    r'[ \t]*<li><a href="(?:email_copy|emergency_po)\.html">(?:Email Copy|Emergency PO)</a></li>[ \t]*\n?'
)
NAV_CLOSE_RE = re.compile(r'(<(?:nav|div) class="nav"[^>]*>.*?)(\n?)([ \t]*)(</ul>)', re.S)
SITE_NAV_MARK = 'href="archive.html"'   # only real site navs carry the editorial links


def files():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    return [p for p in sorted(glob.glob("*.html")) if p not in SKIP]


def has_links(src):
    return EMAIL in src and PO in src


def strip(src):
    return STRIP_RE.sub("", src)


def restore(src):
    if has_links(src):
        return src
    if SITE_NAV_MARK not in src:
        return src  # standalone page with no site nav (e.g. challenge_issue_01_original.html)
    m = NAV_CLOSE_RE.search(src)
    if not m:
        return None
    indent = m.group(3) or "      "
    add = ""
    if EMAIL not in src:
        add += f"{indent}{EMAIL}\n"
    if PO not in src:
        add += f"{indent}{PO}\n"
    head = src[: m.start(2)]
    if not head.endswith("\n"):
        head += "\n"
    return head + add + m.group(3) + m.group(4) + src[m.end(4):]


def main(mode):
    changed, skipped = 0, []
    for path in files():
        src = open(path, encoding="utf-8").read()
        if mode == "check":
            continue
        new = strip(src) if mode == "strip" else restore(src)
        if new is None:
            skipped.append(path)
            continue
        if new != src:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    site_pages = [p for p in files() if SITE_NAV_MARK in open(p, encoding="utf-8").read()]
    total = len(site_pages)
    with_links = sum(has_links(open(p, encoding="utf-8").read()) for p in site_pages)
    if mode != "check":
        print(f"{mode}: {changed} files changed")
    print(f"{with_links} of {total} public files carry the editorial links")
    if skipped:
        print("NO NAV FOUND (fix by hand):", *skipped, sep="\n  ")
        sys.exit(1)
    if mode == "strip" and with_links:
        sys.exit(1)
    if mode == "restore" and with_links != total:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("strip", "restore", "check"):
        sys.exit(__doc__)
    main(sys.argv[1])
