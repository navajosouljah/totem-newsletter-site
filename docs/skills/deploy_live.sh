#!/usr/bin/env bash
# Phase 2 in one command: strip editorial nav links, deploy to totem-challenge-preview,
# restore the links, relink to editorial, push the restore, then verify the live page.
# Usage: bash docs/skills/deploy_live.sh market_pulse_[date].html
# Prints "LIVE OK <url>" on success. Any other ending is a failure; the editorial
# links are restored either way. VERCEL_TOKEN is only ever passed, never printed.
set -uo pipefail

ART="${1:?usage: deploy_live.sh market_pulse_[date].html}"
LIVE="https://totem-challenge-preview.vercel.app"
cd "$(git rev-parse --show-toplevel)" || exit 1

fail() { echo "FAILED: $*"; exit 1; }
[ -f "$ART" ] || fail "$ART not found"
[ -n "${VERCEL_TOKEN:-}" ] || fail "VERCEL_TOKEN is not set"
[ -z "$(git status --porcelain -- '*.html')" ] || fail "uncommitted page changes; finish and push Phase 1 first"

PRE=$(git rev-parse HEAD)
LOG=$(mktemp)

restore() {
  if ! python3 scripts/nav_links.py restore; then
    echo "nav_links restore failed; restoring pages from $PRE"
    git checkout "$PRE" -- '*.html'
  fi
  npx vercel link --yes --project totem-newsletter-site --token "$VERCEL_TOKEN" >/dev/null 2>&1 \
    || echo "WARNING: could not relink the CLI to totem-newsletter-site"
}

echo "1/5 strip editorial nav links"
python3 scripts/nav_links.py strip || { restore; fail "strip did not finish clean"; }

echo "2/5 deploy to totem-challenge-preview"
if ! npx vercel link --yes --project totem-challenge-preview --token "$VERCEL_TOKEN" >/dev/null 2>&1; then
  restore; fail "could not link the CLI to totem-challenge-preview"
fi
npx vercel --prod --yes --token "$VERCEL_TOKEN" >"$LOG" 2>&1
DEPLOY_RC=$?
grep -E "^\S*\s*(Production|Aliased)\b|Error" "$LOG" | sed 's/^/    /'

echo "3/5 restore editorial nav links and relink to editorial"
restore
[ "$DEPLOY_RC" -eq 0 ] || fail "vercel deploy exited $DEPLOY_RC"
grep -Eq "Aliased:?[[:space:]]+${LIVE}\$" "$LOG" || fail "deploy output does not show the alias ${LIVE}"

echo "4/5 push restored pages"
if [ -n "$(git status --porcelain -- '*.html')" ]; then
  git add -- '*.html' && git commit -q -m "Restore editorial nav links" || fail "restore commit failed"
  for wait in 2 4 8 16; do git push -q origin HEAD:main && break; echo "push retry in ${wait}s"; sleep "$wait"; done
  [ -z "$(git log origin/main..HEAD --oneline 2>/dev/null)" ] || fail "restore commit not pushed to main"
else
  echo "    pages already match main, nothing to commit"
fi

echo "5/5 verify the live page"
PAGE=$(mktemp); INDEX=$(mktemp)
for wait in 0 5 10 20 30; do
  sleep "$wait"
  CODE=$(curl -s -o "$PAGE" -w '%{http_code}' "${LIVE}/${ART}?v=$(date +%s)")
  curl -s -o "$INDEX" "${LIVE}/?v=$(date +%s)"
  python3 - "$ART" "$PAGE" "$INDEX" "$CODE" <<'EOF' && { echo "LIVE OK ${LIVE}/${ART}"; exit 0; }
import html, re, sys
art, page, index, code = sys.argv[1], open(sys.argv[2]).read(), open(sys.argv[3]).read(), sys.argv[4]
plain = lambda s: " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())
want = plain(re.search(r'<h1 class="headline">(.*?)</h1>', open(art).read(), re.S).group(1))
got = re.search(r'<h1 class="headline">(.*?)</h1>', page, re.S)
checks = {
    "HTTP 200": code == "200",
    "headline matches": bool(got) and plain(got.group(1)) == want,
    "no email_copy.html link": "email_copy.html" not in page,
    "anchors open-1 to open-5": all(f'id="open-{n}"' in page for n in range(1, 6)),
    "homepage hero links to today": f'id="hero-pulse" href="{art}"' in index,
}
for k, v in checks.items():
    print(f"    {'ok ' if v else 'NO '} {k}")
sys.exit(0 if all(checks.values()) else 1)
EOF
  echo "    live page not right yet, checking again"
done
fail "live page did not pass verification"
