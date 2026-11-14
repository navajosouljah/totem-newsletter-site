# Interview clip retention kit

Your AI uses this small local helper to read the retention curves for your own posted interview clips. It opens TikTok Studio in a separate browser, reads the analytics response that the page itself requests, and makes a dated JSON file and a readable HTML report on your computer. It never posts, edits, sends a message, or changes TikTok settings.

This is a portable derivative of TikTok Sync, not the unchanged original collector. It needs no database, Descript account or API key. You can also have your AI read the same analytics through its connected browser; the kit is an option for repeatable collection of the exact ten clips. An existing approved TikTok Accounts API integration is another option; see SOURCES.md.

## What you need

- A local AI agent with access to files and a terminal on your computer. A temporary cloud chat sandbox cannot keep your browser login for next time. Your agent does the setup; you sign in and clear any verification challenge yourself.
- A supported operating system and current Node.js 22.x or 24.x with npm. Playwright's current documentation also lists Node 26.x. This package was tested with Node 24.2.0 on macOS. See https://nodejs.org/en/download and https://playwright.dev/docs/intro for the current installer and OS support.
- Your own TikTok account, at least one posted video, and analytics available for that post. Analytics can be delayed. A next-day check that finds no curve should stay pending, then be checked later; no curve is not zero retention.
- The exact exported clips, their timestamps and their TikTok post URLs. Your editor or agent creates the time map and transcript from those exports. Never identify sibling clips by caption alone.

## First setup — your agent runs these steps

1. Extract the ZIP into a new project folder on your computer and open this README. All commands below run inside the folder containing package.json. Do not put it inside an existing browser profile. Review SOURCE-MANIFEST.json, then run `node verify.js` to check the included file hashes before installing anything.
2. Check `node --version` and `npm --version`. Install or update Node from its official site if needed. Run `npm ci`, then `npx playwright install chromium`. On a supported Linux machine that lacks browser system libraries, follow Playwright's official dependency instructions. macOS and Windows do not need those Linux packages.
3. Run `npm test`. These offline checks prove parsing, joins, unavailable-data handling and changed-input reports. They do not prove that TikTok currently returns analytics to your account.
4. Run `npm run login`. A new, separate Chromium browser opens at TikTok Studio. You sign in normally. Your AI can navigate after sign-in using a browser tool; it must not enter your passwords or verification codes. If the AI cannot control this separate window, your sign-in still works and the later collection command navigates directly to each analytics page itself.
5. Verify the account you signed into is the account that published the clips. Close that separate browser window when finished. The login stays locally in `.profile`. Never upload that folder, cookies or credentials. The collector opens the same profile next time; do not run two copies together.
6. Your agent copies `clips.example.json` to `clips.json` and replaces every example value with your real first post. The example is fictional and must never be collected as if real. Run `npm run check`. Then run `npm run collect` on that one real post.
7. Open the HTML file printed at the end and compare its post ID with the actual post and its curve against Studio. If the curve is unavailable, your agent opens the actual Studio analytics page to diagnose access or a changed response shape; never manufacture a curve. Only call setup ready after one real post has a verified curve, or explicitly say which access is still missing.
8. Add the other nine clips to `clips.json`. Run `npm run check`, then `npm run collect`. Each run handles at most ten videos, one at a time, with 10–18 seconds between reads. It stops new reads on a login/access challenge or two consecutive unavailable curves. No automatic retries, cookie resets, endpoint replays or bypasses are included.

Your agent can run commands with an explicit manifest instead: `node collector.js collect /full/path/to/clips.json`. `node collector.js help` lists all supported commands.

## Build the manifest correctly

One object is one actual exported clip posted to TikTok. Two records with the same TikTok post ID are the same post and must not be duplicated. Keep the ID as a quoted string: JavaScript numbers cannot safely preserve TikTok's long IDs.

- `interview_id`: your own stable name for this interview.
- `clip_id`: the edit version, such as hook-01-v1. A recut is a new version, not an overwrite.
- `post_id` and `post_url`: the actual TikTok video ID and full URL. Resolve shortened links before recording them.
- `published_at`: the actual publishing date and time with timezone, such as 2026-10-30T12:00:00-05:00.
- `export_file`: the exact file that was posted. Keep the master interview separately.
- `time_map`: one entry per edit segment with `clip_start`, `clip_end`, `source_start`, `source_end`, all in seconds. It covers the entire exported clip from zero, without gaps or overlaps. This helper supports normal-speed cuts. If a clip has speed changes, create an exact mapping for them in your editor before using it; do not pretend the normal-speed map fits.
- `transcript`: the actual exported cut's words with start/end times in clip seconds. Silence can have no transcript line. If a timestamp has no words, the report says Unknown. Do not reuse the master interview timestamps as if they were clip times.

Example: the edit opens with source seconds 90–93, followed by source seconds 80–87. Clip second 1.5 maps to source second 91.5; clip second 3 maps to source second 80. This is why the original footage and the exported cut need separate clocks.

## What the files mean

- `.profile/`: local browser login. Private; never include it in a ZIP or share it.
- `clips.json`: your real clips, source mapping and transcript. Private to your project.
- `results/<run-id>.json`: dated observations, each with post ID, source, collection time, availability, observed curve and source mapping. Every run gets a unique filename; prior observations stay intact.
- `results/<run-id>.html`: a readable report with the three largest observed drops per post and the words playing at each interval end. Open it in a browser. The HTML contains your transcript excerpts; share it only when intended.
- `test-results/`: explicitly fictional offline reports generated by tests. Never present them as live TikTok evidence.

Each curve point contains `second` and `retained_fraction`. A fraction of 0.8 means 80% remain. Source timestamps arrive in milliseconds and are divided by 1,000 without rounding. A fall from 0.8 to 0.5 is a 30 percentage-point drop, not a claim that the next line caused it. Review the interval and the stretch immediately before it in the exported video. Missing seconds are not interpolated; missing metrics remain null. Keep the whole answer coherent when recutting.

## Reruns and failures

- Next-day read is empty: keep that clip pending. Confirm analytics are enabled/available and check again later. The documented API says several metrics can lag 24–48 hours; do not require a curve exactly 24 hours after posting.
- Sign-in expired: run `npm run login` and sign in again. No secrets in chat.
- Security check, 401, 403 or 429: collection stops. Use TikTok normally and resolve the account prompt yourself. Do not loop retries or change accounts/proxies to bypass it.
- Studio shows a curve but the kit reports unavailable: an internal response or URL may have changed. Have the agent inspect that page's actual response and adapt the parser against a real sample. Use the agent's connected browser to read observed values while fixing the collector. Never claim an old parser ran successfully.
- Wrong clip: correct the post ID and exact export mapping, then rerun. The new report reflects the changed input; the old report remains evidence of the prior run.
- `.run.lock` remains after a crash: first check the collector process and its separate browser have stopped. Then delete this file. Never delete an active lock to run competing collectors.
- Nothing useful yet: zero collected clips is a valid report. Do the hook/edit work that does not need analytics, and leave retention-dependent decisions pending.

This kit does not schedule itself. If you later request automatic refreshes, your agent must configure a real local scheduler, prevent overlapping jobs, and prove one completed run. No scheduler is needed for this guide's next-day check.

## Included files

README.md, SOURCES.md, package.json, package-lock.json, .gitignore, collector.js, pull.js, manifest.js, verify.js, clips.example.json, test/collector.test.js and SOURCE-MANIFEST.json. No private account, browser profile, database connection, original video or session capture is included.
