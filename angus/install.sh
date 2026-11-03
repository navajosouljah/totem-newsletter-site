#!/usr/bin/env bash
# One-time install on your own computer (macOS or Linux). From the repo root:
#   bash angus/install.sh
# It copies the home base to ~/totem-ai, the setup skill to ~/.claude/skills,
# and gives The School of Hard Knocks Closer its own folder at
# ~/school-of-hard-knocks-closer. Nothing here signs in, posts or sends.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOME_BASE="$HOME/totem-ai"
AGENT_DIR="$HOME/school-of-hard-knocks-closer"
SKILLS_DIR="$HOME/.claude/skills"

command -v node >/dev/null || { echo "Node.js 22 or newer is needed. Install it from https://nodejs.org/en/download and rerun."; exit 1; }
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
[ "$NODE_MAJOR" -ge 22 ] || { echo "Node $(node --version) found; the retention kit needs 22 or newer."; exit 1; }

# 1. Home base (never overwrites one that already exists)
mkdir -p "$HOME_BASE"
if [ -e "$HOME_BASE/CLAUDE.md" ]; then
  echo "Home base already exists, left untouched: $HOME_BASE/CLAUDE.md"
else
  cp "$HERE/totem-ai/CLAUDE.md" "$HOME_BASE/CLAUDE.md"
  echo "Home base created: $HOME_BASE"
fi

# 2. The setup skill (replaced on every run so it tracks the repo copy)
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/sohk-setup"
cp -R "$HERE/skills/sohk-setup" "$SKILLS_DIR/sohk-setup"
echo "Skill installed: $SKILLS_DIR/sohk-setup"

# 3. The agent's own place (setup notes are copied only if absent, so your edits survive)
mkdir -p "$AGENT_DIR/source" "$AGENT_DIR/exports" "$AGENT_DIR/results"
for f in SETUP.md setup.json; do
  [ -e "$AGENT_DIR/$f" ] || cp "$HERE/school-of-hard-knocks-closer/$f" "$AGENT_DIR/$f"
done
if [ ! -e "$AGENT_DIR/tiktok-retention-kit/package.json" ]; then
  cp -R "$HERE/skills/sohk-setup/tiktok-retention-kit" "$AGENT_DIR/tiktok-retention-kit"
fi
echo "Agent folder: $AGENT_DIR"

# 4. Prove the retention kit on this machine: file hashes, locked dependencies, offline tests.
#    The browser download is skipped here; it is only needed if you choose the kit for analytics
#    (then run: npx playwright install chromium, inside the kit folder).
cd "$AGENT_DIR/tiktok-retention-kit"
node verify.js
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci --no-audit --no-fund
npm test
rm -rf test-results

echo
echo "Done."
echo "  Consultant: open Claude Code in $HOME_BASE"
echo "  The Closer: open Claude Code in $AGENT_DIR and say: set up my interview clip system"
