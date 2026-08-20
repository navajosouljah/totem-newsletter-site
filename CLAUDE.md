# Totem Newsletter Site - Standing Instructions

## Formatting

**Always use markdown hyperlinks for URLs.** Never output a bare URL in chat replies. Format every link as `[descriptive text](url)` so it is clickable. This applies to live deploy URLs, GitHub links, Vercel inspection links, article URLs, and any other hyperlink.

Examples:
- Correct: [totem-newsletter-site.vercel.app/market_pulse_july30_2026.html](https://totem-newsletter-site.vercel.app/market_pulse_july30_2026.html)
- Wrong: `https://totem-newsletter-site.vercel.app/market_pulse_july30_2026.html`

## Vercel environments

There are three Vercel projects. Never confuse them.

| Project | URL | Purpose |
|---|---|---|
| `totem-challenge-preview` | totem-challenge-preview.vercel.app | **Live site** - what email links point to. Phase 2 deploy target. |
| `totem-editorial-review` | totem-editorial-review.vercel.app | Editorial review - auto-deploys on every `git push origin main`. |
| `totem-newsletter-site` | totem-newsletter-site.vercel.app | **Do not use for live deploys.** This was mistakenly used on 2026-08-03. |

### Phase 2 live deploy sequence (exact commands)

```bash
# 1. Strip editorial nav links from ALL public HTML files (Email Copy + Emergency PO <li> items).
#    Use a Python script — never sed (sed has corrupted files before).
#    Skip email_copy.html and emergency_po.html themselves.
#    Pattern to remove (match by content, ignore leading whitespace):
#      <li><a href="email_copy.html">Email Copy</a></li>
#      <li><a href="emergency_po.html">Emergency PO</a></li>
#    Reference script: scratchpad/strip_nav.py (created 2026-08-04)

# 2. Link CLI to the correct live project
npx vercel link --yes --project totem-challenge-preview
# 3. Deploy
npx vercel --prod --yes
# 4. Restore editorial nav links in ALL files (reverse of step 1)
#    Reference script: scratchpad/restore_nav.py (created 2026-08-04)
# 5. Relink CLI back to the editorial project (keeps .vercel/project.json tidy)
npx vercel link --yes --project totem-newsletter-site
# 6. Commit and push the restored files so the editorial site stays in sync
git add -A && git commit -m "Restore editorial nav links" && git push origin main
```

Always verify the aliased URL in the deploy output reads `totem-challenge-preview.vercel.app` before declaring Phase 2 complete.

**Why all files, not just today's article:** Every page on the site (index, archive, all articles, all challenge issues) shares the same nav. Stripping only the new article leaves Email Copy and Emergency PO visible to readers on every other page.

## Post-card and hero headline length

**Keep post-card and hero cap-title headlines to 2-3 sentences max.** Pick the 2-3 most important data points - the ones that would stop a reader mid-scroll. Do not dump the full article headline into the post-card. The article itself carries the detail.

- Good: "July CPI Matched Consensus at 3.4% - September Hike Odds Fall to 38%. S&P 500 7,748 in Relief Rally. Oil Retreats to WTI $82.11 on Hormuz Deal Signals."
- Too long: "July CPI Matched Consensus at 3.4% - September Hike Odds Fall to 38%. S&P 500 7,748 in Relief Rally. Oil Retreats to WTI $82.11 on Hormuz Deal Signals. USDA Corn Yield 180.7 BPA Misses Estimates. PPI + Jobless Claims at 8:30 AM ET Today. Retail Sales Tomorrow."

This applies to: index.html post-cards, archive.html post-cards, and the hero `cap-title` on index.html.

## Market Pulse Email Format

**Never change the email format without JJ's explicit instruction.** Content updates only - dates, data, links. The structure is locked.

### Schedule
- **Monday - Thursday:** Market Pulse email only. Member and non-member use the same structure (see below). No additions, no extra sections.
- **Friday:** Different format (Challenge lead + Market Pulse). Do not apply Friday's structure to Mon-Thu.

### Structure (Mon-Thu, both member and non-member)

1. **Masthead** - TOTEM LC GROUP + tagline
2. **Navy date bar** - "Day, Month DD, YYYY · Member Edition" (members) or baked into the hero kicker (non-members)
3. **Market Pulse hero block** - navy gradient, linked to today's article on totem-challenge-preview.vercel.app
4. **Hero headline** - article's 2-3 sentence headline, date below it, "Read Today's Market Pulse" CTA button
5. **Lead paragraph** (Spectral 21px bold) - **3-4 sentences max. Teaser/trailer only.** Hook with the biggest data point, add 2-3 supporting facts. Stop. The goal is to make the reader click - not to summarize the briefing. If you would keep reading past sentence 4, cut it.
6. **Data snapshot** (Inter 14px) - quick-reference line: key closes, crypto, energy, upcoming catalysts
7. **Inline link** - one sentence pointing to the most compelling section of the article
8. **Divider**
9. **"Also in Today's Briefing"** - gold-bullet label, then 5 bullets. Each bullet: bold topic sentence + 2-3 sentences of context. Scannable, not exhaustive.
10. **"Read the Full Briefing"** CTA button - links to today's article
11. **Footer** - disclaimer + Totem LC Group sig

### Lead paragraph rule (the most violated rule)

The lead is a movie trailer, not a plot summary. Good test: if someone could skip clicking after reading it because they already know the story, it is too long. Cut until they have to click to find out what happened.

**Too long (7 sentences - do not do this):**
> "July housing starts crashed to 1.239 million SAAR - 11% below the 1.39 million consensus and the biggest miss since mid-2020. Building permits beat at 1.443 million, the one constructive datapoint in Tuesday's report. The 30-year Treasury surged to 5.33%, a 19-year high, as bond markets priced stagflation: a housing-led slowdown with no Fed relief in sight. Chip stocks led Nasdaq down 1.33% to 26,289.71. S&P 500 settled at 7,691.76. Gold fell toward $4,340 as the real yield surge outweighed Brent's inflation support. Brent approached $92 - fourth consecutive session of gains, still no successor MOU."

**Correct (4 sentences - approved format):**
> "July housing starts crashed to 1.239 million SAAR - 11% below the 1.39 million consensus, the biggest miss since mid-2020. The 30-year Treasury hit 5.33%, a 19-year high, as markets priced stagflation. Chip stocks led Nasdaq down 1.33% to 26,289.71. Brent approaching $92 for a fourth straight session."

### Member vs. non-member differences (only these two)

| Element | Member | Non-member |
|---|---|---|
| `<title>` | `Market Pulse - [Date] - Member Edition` | `Market Pulse - [Date]` |
| Hero kicker | `[Day], [Date] · Member Edition` | `[Day], [Date] · [Day] Briefing` |
| Footer disclaimer | "You are receiving this email as a member of Totem LC Group..." | "A free weekly snapshot for the Totem community..." |

Everything else is identical. Do not add member-only sections, greetings, transaction alerts, or Challenge blocks to Mon-Thu emails without explicit authorization.

## Market Pulse — Tracked Assets

### Crypto (always research and include data lines for all of these)

| Asset | Ticker | Notes |
|---|---|---|
| Bitcoin | BTC | Price, ETF inflows (IBIT etc.), rate-path sensitivity |
| Ethereum | ETH | Price, regulatory backdrop (CLARITY Act), support levels |
| XRP | XRP | Price, ETF inflows, CLARITY Act legislative status, on-chain metrics (DAA, network growth), escrow unlocks |

Search for each asset's price every morning. For XRP specifically: check ETF inflows (cumulative and monthly), CLARITY Act Senate status, on-chain metrics (Daily Active Addresses, network growth from Santiment), and Ripple escrow unlock schedule.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `navajosouljah/totem-newsletter-site` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.
