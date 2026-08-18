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
