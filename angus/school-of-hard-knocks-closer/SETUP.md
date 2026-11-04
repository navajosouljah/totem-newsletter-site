# The School of Hard Knocks Closer - setup notes

Turns interviews into improved clips and client conversations. Ask it to plan a guest interview, make ten clips, improve them from retention, and follow up about your actual service.

This folder is the agent's own place. Open Claude Code here and say **set up my interview clip system**; the consultant calls Angus MCP's hire_agent for this agent and follows it. Later jobs: **plan an interview**, **make clips**, **check retention**, **follow up with the guest**. Nothing here posts, sends or pays; every public step is a draft you review first.

## Status as of November 3, 2026

Each item is at one of four states: reachable, signed in, set up, tested.

| Item | State | Notes |
|---|---|---|
| Setup skill (`sohk-setup`) | tested | Installed in `~/.claude/skills/sohk-setup`. Kit hashes verified, locked dependencies installed, 9 of 9 offline tests passed. Run in a cloud container on November 3, 2026, not yet on your own computer. `angus/install.sh` repeats the same proof on your machine. |
| Plan, make clips, recut, publish and compare, follow up (five skills) | not fetched | The Vault connection in the chat that did this setup had no skill-fetch tool. They load automatically the first time you run the agent from a chat with the full Angus MCP connection (Claude desktop or web chat, or Claude Code on your computer). |
| Recording | unbound | Your stack has no Zoom. Microsoft Teams or Google Meet with local recording covers it; a phone or camera works for in-person. Decide before the first interview. |
| Transcription | unbound | You have four notetakers (Otter, Read.ai, Granola, Spinach). Pick one as the source of truth. It must give a timestamped transcript of the actual recording file; the clip skill maps edited seconds back to source seconds. |
| Editor | unbound | Pack default is Adobe Premiere Pro plus its local MCP bridge (paid, desktop, Node on the same computer; steps in `editor-setup.md`). Free alternative: FFmpeg (no visual timeline, the agent does the cuts). Descript is the transcript-editor option. |
| TikTok account | unknown | Test platform. You post the clips yourself; the agent reads your own analytics. |
| Instagram account | unknown | Distribution for reviewed recuts. |
| Analytics | kit verified offline | The retention kit lives in `tiktok-retention-kit/`. Before the first real read on your machine: `npx playwright install chromium`, then `npm run login` (you sign in; the agent never types passwords or codes). Setup is only "ready" once one real post shows a verified curve. The other route is Claude in Chrome reading TikTok Studio directly. |

## Decisions still open, in order

1. Which business the interviews serve, what it sells, and who a useful client or guest is. The pack fits the clips to one offer; candidates are listed in `setup.json`.
2. Recording route and which notetaker is the transcript source.
3. Editor: Premiere (if you have it) or FFmpeg.
4. TikTok and Instagram accounts to use.

The consultant asks these one at a time and records the answers in `setup.json`.

## Working layout

```
~/school-of-hard-knocks-closer/
  SETUP.md                 these notes
  setup.json               business, audience, timezone, tool bindings, paths, allowed actions, evidence
  source/                  original recordings (read-only once placed)
  exports/                 exported clips, one file per clip version
  results/                 retention reads and reports
  tiktok-retention-kit/    the analytics helper; clips.json and .profile stay private and untracked
```

## Clip record

One record per clip version. Unchanged source, answer window, hook and edit is the same version; a recut gets a new `clip_id`. Missing values are `null`.

`interview_id`, `clip_id`, `parent_clip_id`, `hook_id`, `source_file`, `answer_window`, `export_file`, `editor_id`, `transcript`, `time_map`, `review_status`, `tiktok_id`, `tiktok_url`, `tiktok_published_at`, `instagram_url`, `instagram_published_at`, `status`.

Status flow: planned → edited → reviewed → TikTok posted → measured → recut → Instagram posted → closed.

The kit's `clips.json` takes the posted subset of these fields in its own exact shape (`clips.example.json` shows it; the example is fictional and must never be collected as real).

## Boundaries

- Drafts only. No post, message, purchase or deletion without your review of that item.
- Footage, transcripts, clip lists, browser profiles and sign-ins stay on your computer. Nothing of that goes to the Vault.
- Use the released, measured figure. A missing retention curve is "pending", never zero.
- This agent is separate from the Market Pulse routine and must never touch the newsletter repo's own CLAUDE.md or deploys.
