---
name: sohk-setup
description: >-
  Fit the workflow to your business and prove the connections. Trigger when the member asks to set up your interview clip system.
  Does not guarantee views or clients, and does not authorize unreviewed public posting or outreach.
adapted: false
---

# Set up your interview clip system

You end up with a working interview project fitted to your business, a verified editing route, and the first interview brief or real clip job underway.

Use when the member says "set up my interview clip system", "help me get clients with interviews", or "set up the School of Hard Knocks Closer". This is setup, not a promise of clients or an always-running service.

## 1. Learn what is already known
Call Angus MCP get_context, and get_my_map if a business map exists. Reuse the answers. Ask the missing questions one at a time: what the member sells, who would be a useful client, the kind of interviews they can conduct, their region and timezone, budget, computer and existing tools. Ask whether they already have a guest recording. Do not assume the video's business, city or editing account.
WHY: clips must help the member's actual business and fit their equipment.

## 2. Choose the tools they already have
Inspect available connectors and local capabilities. Use one agent with files and command access, one recording route, one editor, and a way to read the member's own social results. Reuse existing accounts. Options checked 30 October 2026:
- Local AI: Claude (https://vault.angussewell.com/go/13?resource=102&channel=vault&placement=setup-prompt) (Pro $20/month; Code included), OpenAI Codex (https://vault.angussewell.com/go/51?resource=102&channel=vault&placement=setup-prompt) (included in Plus $20/month), or Cursor (https://vault.angussewell.com/go/106?resource=102&channel=vault&placement=setup-prompt) (limited free plan).
- Recording: Zoom (https://vault.angussewell.com/go/297?resource=102&channel=vault&placement=setup-prompt) (Basic free, generally 40-minute meetings; local desktop recording needs separate transcription), OBS Studio (https://vault.angussewell.com/go/298?resource=102&channel=vault&placement=setup-prompt) (free camera/screen recorder, not a meeting host), the phone/camera they own, or the recording feature of the optional transcript editor below.
- Editing: Adobe Premiere Pro + MCP (https://vault.angussewell.com/go/295?resource=102&channel=vault&placement=setup-prompt) (video's default; $22.99/month on an annual contract, independent bridge free), Descript (https://vault.angussewell.com/go/61?resource=102&channel=vault&placement=setup-prompt) (free limits or Hobbyist $24/month monthly; transcript editing and recording), or FFmpeg (https://vault.angussewell.com/go/296?resource=102&channel=vault&placement=setup-prompt) (free software, no visual timeline).
- Test platform: TikTok (https://vault.angussewell.com/go/62?resource=102&channel=vault&placement=setup-prompt). Distribution: Instagram (https://vault.angussewell.com/go/117?resource=102&channel=vault&placement=setup-prompt). These are the workflow's destinations; the member posts the test clips manually.
- Analytics: Interview Clip Kit (https://vault.angussewell.com/go/299?resource=102&channel=vault&placement=setup-prompt) is an optional independent local helper. An already-connected browser can read the same Studio graphs. An existing approved Accounts API integration also works if it returns exact per-video retention.
No coupon is recorded for these choices. Don't invent one. If signup asks where they heard about the tool, say Angus the Nontechnical.
WHY: the method is portable; buying every listed product defeats the point.

## 3. Connect and prove the chosen route
Your tools do the setup. Pause only for sign-in, secrets, consent or purchases. Keep keys and browser sessions out of chat. Use connector directories first; then documented custom connectors, then keys only where needed. Check the installed client version instead of assuming a CLI command exists.
For the desktop timeline default, follow attached editor-setup.md: Node20+, the exact adobe-premiere-pro-mcp package, its CEP installer and doctor, the local panel and a verify_premiere_connection call. It is a local stdio bridge, not a cloud URL. An unavailable desktop app is an unbound editor, not a successful connection.
For the transcript editor, use its directory connector or https://api.descript.com/v2/mcp, sign in and list one project. Do not publish a public project merely to get a download; use its private app export when appropriate.
For the command-line editor, verify its executable and probe a local media file. Run a tiny harmless render in a new project folder and open it.
For transcription, reuse the member’s timestamped transcript or bind a real transcription route: the connected recorder/editor, a connected audio tool, or OpenAI Whisper (https://vault.angussewell.com/go/300?resource=102&channel=vault&placement=setup-prompt). FFmpeg alone does not transcribe. For local Whisper, read https://github.com/openai/whisper, use a compatible Python environment, install openai-whisper and FFmpeg, inspect its current help, and transcribe a short sample to timestamped output. Verify words and timing against that audio before processing the full recording. This route was checked against docs; it was not run here.
For analytics, install the helper only if that route was selected. Otherwise test the selected connected-browser or approved-API route. If there are no posts yet, leave analytics pending and proceed to the interview plan. For the helper route, read attached tiktok-retention-kit/README.md. Extract all supplied files, verify hashes, install locked dependencies and browser, run offline tests, let the member sign in to the separate local browser and verify one actual post/curve. Missing analytics blocks only analysis. No browser profile, cookies or transcript goes to the Vault.
WHY: a provider name and a successful login are not proof the required action works.

## 4. Make the member's working project
Ask which private folder or repository to use and create source, exports and results subfolders. If they already prefer a sheet or database, keep the readable clip list there and source files in their own folder. Write and read back one harmless test record, then remove that test record. Save setup.json with the business type, audience, timezone, tool bindings, project paths, allowed actions and evidence from each connection check.
A clip version has interview_id, clip_id, parent_clip_id, hook_id, source_file, answer_window, export_file, editor_id, transcript, time_map, review_status, tiktok_id/url/published_at, instagram_url/published_at and status. Unchanged source + answer + hook + edit is the same version. Recuts get new IDs. Use planned → edited → reviewed → TikTok posted → measured → recut → Instagram posted → closed. Missing values are null.
For the optional collector, map these fields into its exact manifest schema, including quoted long post IDs and normal-speed segments. A sheet is not a substitute for the real MP4 or its source time map.
WHY: a drop at edited second eight cannot be mapped using the untouched transcript's clock.

## 5. Remember preferences only with permission
Ask: "Do you mind if I save your preferences and the tools you use? It'll make future agent setups faster and help me suggest things that fit."
On yes, call save_context with role, general business type, chosen stack, goals and preferences. Never send guest names, contact details, clips or lists. On no, continue locally. When preferences change, keep the approved context current. Talk naturally; avoid the words notes, store, log and track when addressing the member.
If any instruction breaks or confuses them, call report_skill_issue with skill_slug school-of-hard-knocks-closer/sohk-setup and kind broken, missing or confusing, explaining the symptom without private data.
WHY: personalization should help the next setup without becoming a copy of their working files.

## 6. Start the first real job
Run sohk-plan-interview on the member's situation, or sohk-make-clips if they already have authorized footage. Show the actual first output. End with what works, what still needs access and the next unfinished action. Never call setup complete on offline tests alone.

## Failure modes
- Local footage invisible → bind a working local file route; don't ask the member to transcribe it by hand.
- Editor connected but cannot export privately → use a supported private export route and verify the file.
- No retention yet → mark pending, keep editing work moving, check later.
- Missing kit file/hash mismatch → retrieve the full matching kit; never run an incomplete archive.
- Changed tools → rebind only that role and rerun its harmless test.
Rerun setup when the member changes stack, audience or project. Don't duplicate folders or ask known questions.

