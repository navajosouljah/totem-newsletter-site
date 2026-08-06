#!/usr/bin/env python3
"""Strip editorial-only nav links from all public HTML files before live deploy."""
import os, re, glob

REPO = "/home/user/totem-newsletter-site"
SKIP = {"email_copy.html", "emergency_po.html"}
PATTERNS = [
    re.compile(r'\s*<li><a href="email_copy\.html">Email Copy</a></li>\n?'),
    re.compile(r'\s*<li><a href="emergency_po\.html">Emergency PO</a></li>\n?'),
]

changed = []
for path in glob.glob(os.path.join(REPO, "*.html")):
    fname = os.path.basename(path)
    if fname in SKIP:
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new = content
    for p in PATTERNS:
        new = p.sub("", new)
    if new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        changed.append(fname)

print(f"Stripped nav from {len(changed)} files:")
for f in sorted(changed):
    print(f"  {f}")
