# Angus Member Vault: home base and hired agents

This folder is separate from the Market Pulse routine. It does not change the repo's `CLAUDE.md`, the scripts, or any deploy. It exists so the files survive the cloud session that made them; the working copies belong on your own computer.

## Install on your computer (one command, from the repo root)

```bash
bash angus/install.sh
```

What it does:

- Creates your home base at `~/totem-ai` (a `CLAUDE.md` with your consultant's instructions). Open Claude Code there to ask for advice or get something new set up or built by Angus.
- Installs the setup skill to `~/.claude/skills/sohk-setup`.
- Gives The School of Hard Knocks Closer its own folder at `~/school-of-hard-knocks-closer` with `SETUP.md`, `setup.json`, the `source`, `exports` and `results` folders, and the retention kit.
- Proves the kit on your machine: file hashes, locked dependencies, nine offline tests. No browser download, no sign-in, nothing posted.

Needs Node.js 22 or newer. Existing files are left alone, except the skill copy, which is refreshed from the repo each run.

## What is in here

| Path | Purpose |
|---|---|
| `totem-ai/CLAUDE.md` | Home base instructions: "Totem LC Group AI consultant" |
| `school-of-hard-knocks-closer/SETUP.md` | The agent's status, open decisions, layout, clip record and boundaries |
| `school-of-hard-knocks-closer/setup.json` | Tool bindings, paths, allowed actions and dated evidence |
| `skills/sohk-setup/` | The setup skill, its editor reference, and the retention kit (hash-verified) |
| `install.sh` | The installer above |

## Verified on November 3, 2026 (cloud container, not your computer)

- Retention kit: 11 files hash-verified, dependencies installed from the lock file, 9 of 9 offline tests passed.
- FFmpeg 6.1.1 and Node 22 present in the container.

## Not verified yet

- The five job skills (plan interview, make clips, recut from retention, publish and compare, follow up) were not fetched: the Vault connection in that session had no skill-fetch tool. They load on the first run from a chat with the full Angus MCP connection.
- Nothing on your machine: Premiere or FFmpeg there, Teams or Meet recording, a notetaker transcript, TikTok and Instagram sign-in.
- Which business the interviews serve. That is the first question the agent asks.
