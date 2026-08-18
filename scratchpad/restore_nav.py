#!/usr/bin/env python3
"""Restore editorial-only nav links to all public HTML files after live deploy."""
import os, re, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root, works on any machine
SKIP = {"email_copy.html", "emergency_po.html"}

EMAIL_COPY_LI = '      <li><a href="email_copy.html">Email Copy</a></li>'
EMERGENCY_PO_LI = '      <li><a href="emergency_po.html">Emergency PO</a></li>'

# Insert before </ul> inside the nav block (first occurrence)
# [^>]* tolerates class="live" on archive.html's own nav (missed archive.html on Aug 15 without it)
ANCHOR = re.compile(r'(<li><a href="archive\.html"[^>]*>Archive</a></li>)(.*?)(</ul>)', re.DOTALL)

changed = []
for path in glob.glob(os.path.join(REPO, "*.html")):
    fname = os.path.basename(path)
    if fname in SKIP:
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if 'href="email_copy.html"' in content:
        continue  # already restored
    # Find the nav </ul> and insert before it, after Archive li
    def inserter(m):
        return (m.group(1) + m.group(2) +
                "\n" + EMAIL_COPY_LI +
                "\n" + EMERGENCY_PO_LI +
                "\n      " + m.group(3))
    new, count = ANCHOR.subn(inserter, content, count=1)
    if count and new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        changed.append(fname)

print(f"Restored nav in {len(changed)} files:")
for f in sorted(changed):
    print(f"  {f}")
