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

### Morning deploy authorization (locked 2026-08-31)

**The site deploys automatically. No approval gate.** After Phase 1 completes (build + push to editorial), proceed immediately to Phase 2 without stopping to ask JJ.

**The one exception:** JJ reviews email copy on his own schedule before sending in Mailchimp. The agent does not send email and does not wait. After Phase 2, send JJ a push notification with the live article URL and the email copy review link — then stop.

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

## The Attention Rules (locked 2026-08-20)

These govern the **opening block** of every article and every email - the first thing the reader sees. They exist because 11,000-word briefings with the correct data still get archived unread when the top of the page fails to earn the scroll. Length was never the real problem; **sequence** was. Each opening unit must earn its place by being different from the one before it.

### The Subject Variety Rule (the one that actually governs attention)

**No two consecutive opening units may lead with the same subject.** The opening units are, in order: headline → dek → Quick Read paragraphs → How Thursday Opens bullets. If unit N is about the buyback, unit N+1 is not. This is not a length rule - a 30-word dek that restates the headline is worse than a 90-word paragraph that opens a second front.

Test: read only the first 8 words of every opening unit in order. If more than one leads with the same subject or keyword, restructure. On Aug 20 the pre-fix count was 5 of 6 opening units framed by Treasury; 42 Treasury mentions before the bullets even started. That is the failure mode.

### The Five Opening Jobs

Each of these appears exactly once. Never in the same unit, never repeated.

1. **Headline** - the 2-3 biggest facts (2-3 sentences, hyphen for asides). Rule below on length.
2. **Dek** - the day's tension, not a summary. Two sentences. It must add the read rather than restate the headline. Test: if it could sit under any headline this week, rewrite it.
3. **Quick Read paragraph 1** - the cause and its full downstream chain, said once. Ends with the mechanism ("that is the whole mechanism") so nothing downstream needs to re-explain it.
4. **Quick Read paragraph 2** - what today actually decides. The scheduled event, the number the market is watching, the stakes.
5. **Quick Read paragraph 3** - what keeps building underneath. The slow pressure the market hasn't priced yet.

Quick Read caps at 250 words across the three paragraphs combined. Section-intro lines that restate the bullets beneath them are forbidden.

### The Bullet Rule

Every "How Thursday Opens" bullet must **add information the Quick Read did not carry**, not retell it in longer form. Good bullet openings: "What the buyback means past this week." "The crypto flows say institutions, not retail." "Why these three dissenters, specifically." Bad bullet openings: "Treasury doubled long-bond buybacks to $4 billion..." (restatement).

Test: strike the Quick Read from the draft and re-read each bullet. If a bullet loses its point, it was a restatement; rewrite it.

### Headline length

Headline: 2-3 sentences, 40-word ceiling. Same discipline as the post-card rule below. The August 20 headline before the fix ran 96 words across 6 sentences. Ship at 30-40.

### Dek length

Dek: 30 words maximum, two sentences. Anything longer is a lead paragraph in the wrong slot.

### Rounding

Use precise figures the first time only. Every subsequent mention rounds: $71,751 becomes $71.8K, 26,331.09 becomes 26,331 or "the Nasdaq." Decimals signal a data dump; round numbers signal a point of view.

### Standing sections only appear when something changed

The 13 deep sections (Stock Market, Interest Rates, Savings & CD, Energy, Commodities, Crop Weather, Real Estate, Household Finance, Crypto, Around the World, This Week's Events) are the product and stay. But a section whose data has not moved since yesterday runs as a two-line "no change" note rather than three paragraphs of restatement. Crop Weather when corn is flat, Around the World when China's number is unchanged - those get compressed, not padded.

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

**LOCKED FORMAT (confirmed Aug 25, 2026 — do not change without JJ's explicit instruction):**

1. **Masthead** - TOTEM LC GROUP + tagline
2. **Gold 1px `<hr>` rule** - between masthead and hero block
3. **Navy hero block** (navy gradient, `border-radius: 4px`) - self-contained, contains ALL of: kicker line, "Market Pulse" logo text, short headline (3 punchy sentences, white Spectral bold), and gold CTA button. Links to today's article on totem-challenge-preview.vercel.app. **No separate white card below the hero.**
4. **Gold CTA button** (`#fcb900` background, dark text `#16181d`, `border-radius: 3px`) - inside the hero block. Label: "Read Today's Briefing". **No second CTA button anywhere else in the email.**
5. **Lead paragraph** (Spectral 21px bold) - **the tension frame, not a teaser of the top story.** Two sentences. It must open a second subject to whatever the hero headline led with. See the Subject Variety Rule.
6. **Data snapshot** (Inter 14px) - one line. Rounded figures. **Gold left border: 3px gold `<td>` + 14px padding-left.** Never restates the lead paragraph in prose.
7. **Divider**
8. **"Five Things Only Totem Will Tell You Today"** - gold-bullet label, then 5 bullets. Each bullet: bold topic sentence + 2-3 sentences of context. Every bullet opens a distinct subject; no bullet may re-tell the hero story. See the Bullet Rule.
9. **Footer** - disclaimer + Totem LC Group sig

**What is NOT in this email (do not add):** inline link row, second CTA button, separate white article card below the hero, navy date bar as a separate element (it is baked into the hero kicker).

### The lead paragraph is the tension frame

The lead in the email is not a teaser of the top story - the hero headline already carries that. Its job is to name **the day's hinge**: the question the day is about to answer, or the tension the market is holding. Two sentences. If the reader could guess what your top story is by the end of sentence one, the lead is not doing its job.

**Correct (tension frame, Aug 20):**
> "Rates fell, crypto ripped, and equities bounced. Walmart opens its books at 6am against a consumer 13.1% behind on credit cards - the number that says whether any of it holds."

**Wrong (retelling the hero story):**
> "Bessent doubled Treasury long-bond buybacks to $4 billion per operation, pulling the 30-year yield from 5.33% to 5.19%. The move triggered a crypto rally with Bitcoin at $71,751 and Ethereum at $2,280..."

### The Subject Variety Rule (applies to the email too)

Read only the first 8 words of each of these opening units in order:
1. Preheader
2. Hero headline
3. Lead paragraph
4. Data snapshot
5. Each of the five bullets

**No two consecutive units may lead with the same subject.** On Aug 20 before the fix, 8 of 9 email units opened with or landed on Treasury. That is the failure mode. If the hero is the buyback, the lead is the consumer, bullet 1 tells the reader something they can't get on CNBC about the buyback's *consequence*, not its facts.

### The Bullet Rule

The bullet label was changed from "Also in Today's Briefing" to **"Five Things Only Totem Will Tell You Today"** to enforce the standard. Every bullet must be an editorial read - the "why," the "so what," or the second-order consequence - not a data restatement.

Bad bullet opening: "Treasury doubles long-bond buybacks to $4B - 30-year falls to 5.19%." (data restatement)
Good bullet opening: "The rate ceiling has an expiration date." (the read)

Test: strike the article's Quick Read from the email and re-read each bullet. If a bullet loses its point, it was a restatement; rewrite it.

### Rounding in the email

Data snapshot uses rounded figures. $71,751 → $71.8K. 7,707.98 → 7,708. 26,331.09 → 26,331. The article carries the decimals; the email is the map, not the terrain.

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
