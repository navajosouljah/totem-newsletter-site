# Morning Market Pulse Skill

**Source of truth:** `CLAUDE.md` in the repo root. This file extracts only the steps relevant to the daily build-and-deploy routine so an audit framework has a discrete path to point at. Nothing here overrides CLAUDE.md; if the two ever conflict, CLAUDE.md wins.

---

## Overview

The morning routine produces one article, updates three supporting files, pushes to editorial, deploys live, and notifies JJ. It runs in two phases. No approval gate between them (locked 2026-08-31; reaffirmed 2026-09-02).

**Hard deadline:** Live deploy must finish before 6:15 AM MT (12:15 UTC) on weekdays. The cloud routine "Totem Market Pulse - Member Email Send" checks for HTTP 200 on the live article at that time and blocks if it is missing.

---

## Phase 1 — Build

### Step 1 · Research today's data

Fetch current figures for all 11 sections before writing a single word. Required assets:

| Section | Key figures to fetch |
|---|---|
| Stock Market | S&P 500, Nasdaq, Dow — prior close |
| Interest Rates | Fed funds target, 2-year yield, 10-year yield |
| Savings & CD | Top 1-yr CD rate, top HYSA rate, national avg 1-yr CD |
| Energy | Brent crude, WTI crude, AAA national gas average |
| Commodities | Gold, Silver, Copper |
| Crop Weather | USDA Corn G/E %, Soybeans G/E %, Corn futures |
| Real Estate | Freddie Mac 30-yr mortgage (PMMS), 10-year yield, Canada lumber tariff status |
| Household Finance | Layoffs or real wages reading, card delinquency 90+, AAA gas |
| Crypto | BTC, ETH, XRP — prices, ETF inflows, CLARITY Act status for XRP |
| Around the World | Nikkei, Hang Seng, Yen (swap in the day's biggest mover) |
| The Week Ahead | Next three dated catalysts with times and time zones |

**Data accuracy rule (the ADP lesson):** Use released figures, never forecasts. If a figure is not yet released, write "due at [time] ET" and leave the strip cell empty. If a figure cannot be found, write "not available" or carry the last reading with its date. Mark estimates as estimated. Every figure needs a source that will appear in that section's "Curated from" line.

---

### Step 2 · Write the article

**File naming:** `market_pulse_[monthname][day]_[year].html`  
**Template:** Copy the full `<style>` block and section markup from the most recent article file. The `.sec-v2` CSS rules are the format.

#### Opening block

1. **Kicker** — `Market Pulse • [Day], [Month D, YYYY]`. Centered.
2. **Headline** — 12 words max, two sentences. Spectral 800. Must be word-for-word identical to the email hero headline. Opportunity Frame: lead with what is available for the reader, not with the conflict or threat.
3. **No dek.** Retired 2026-09-02.
4. **Quick Read** — three paragraphs, 250-word hard cap, Work Sans title, drop cap on paragraph 1.
   - Paragraph 1: the tension, then the cause and its mechanism, ending on the mechanism.
   - Paragraph 2: what today (or Friday) decides, with the thresholds.
   - Paragraph 3: what keeps building underneath.
   - Closes with a `Curated from` sources line.
5. **How [Day] Opens** — exactly five bullets. Each `<li>` has `id="open-1"` through `id="open-5"`. Each opens with the email bullet's text verbatim in bold, gives the answer in 40–50 words, ends with `<a class="more" href="#section">Section name →</a>`. The email bullets deep-link to `#open-1` through `#open-5`. This handoff is not optional.

#### Subject Variety Rule (opening block)

Read only the first 8 words of each opening unit in order: headline → Quick Read paragraphs → How [Day] Opens bullets. No two consecutive units may lead with the same subject. If unit N is about the buyback, unit N+1 is not.

#### Bullet Rule (How [Day] Opens)

Every bullet must add information the Quick Read did not carry. Test: strike the Quick Read and re-read each bullet. If a bullet loses its point, it was a restatement; rewrite it.

#### 11 topic sections — in this order

1. Stock Market
2. Interest Rates
3. Savings & CD Rates
4. Energy & Gas Prices
5. Commodities
6. Crop Weather
7. Real Estate
8. Household Finance
9. Crypto
10. Around the World
11. The Week Ahead

Each section is wrapped in `<div class="sec-v2">` and contains:

1. `h2.section-title` — Work Sans 800, 24px.
2. `div.strip` — three cells. Each cell: `k` (label) / `v` (rounded figure, tabular numerals) / `d` (direction: `up`, `down`, or `flat` with ▲ ▼ and the change, or "Unchanged"). Strip cells per section:

| Section | Strip cells |
|---|---|
| Stock Market | S&P 500 · Nasdaq · Dow |
| Interest Rates | Fed funds · 2-year · 10-year |
| Savings & CD | Top 1-yr CD · Top HYSA · Nat'l avg 1-yr CD |
| Energy | Brent · WTI · Gas (AAA) |
| Commodities | Gold · Silver · Copper |
| Crop Weather | Corn G/E · Soybeans G/E · Corn futures (or drought share) |
| Real Estate | 30-yr mortgage (Freddie Mac) · 10-year · Canada lumber tariff day |
| Household Finance | Layoffs or real wages · Card delinquency 90+ · Gas (AAA) |
| Crypto | Bitcoin · Ethereum · XRP |
| Around the World | Nikkei · Hang Seng · Yen (swap in the day's mover) |
| The Week Ahead | Next three dated catalysts |

3. `p.setup` — italic (CSS does it), 40–70 words, one or two bold phrases max. What moved and why, once. Never a list of the numbers that follow.
4. `div.lines > div.line` — gold dot bullet, then `span.lb` (label with date in parentheses), `span.num` (precise figure to the decimal), `span.d` (direction), then `span.why` on its own line: one to three plain sentences, regular weight, body color, saying why it moved and what it means. Never chain clauses with semicolons. Never restate the setup.
5. `div.bottom` — gold left rule, `span.lbl` label, one `<p>` of one to three sentences. The call, not a summary.
6. `div.src` — `<b>Curated from</b> Source · Source · Source`. Only sources actually used.

#### Word budget

| Unit | Cap |
|---|---|
| Headline | 12 words |
| Quick Read | 250 |
| How [Day] Opens | 5 × 65 (bold lead + answer + link) |
| Each topic section | 200 to 380 |
| Whole article | 3,000 to 3,600 |

Under 3,000 means data lines were dropped. Over 3,600 means something is being said twice.

#### Disclaimer (end of article)

Exactly two paragraphs in `.disclaimer`, nothing else:

1. General Disclaimer verbatim: "This material is provided for informational purposes only and does not constitute legal, tax, securities, lending, investment, or financial advice. Participation in commercial transactions involves risk, including possible loss of capital. Historical performance does not guarantee future outcomes."
2. As-of line: "Figures reflect the latest readings available as of [Day, Month D, YYYY], before the US market open. Sources are listed at the end of each section."

Never append a data recitation to the disclaimer.

#### Typography rules

- Bold: labels, numbers, and at most two key phrases per section.
- Muted gray (`--muted`): metadata only (dates, strip labels, sources). Never for a content sentence.
- Colored text: direction markers only (`.up` green, `.down` red). Never color a sentence.
- Times: always AM/PM plus zone (e.g., "8:30 AM ET"). Never "8:30 ET" or "10am".
- Hyphens for asides, never em dashes.
- Rounding: precise figures the first time only; every subsequent mention rounds.

---

### Step 3 · Update index.html

- Update the nav Market Pulse link to today's article.
- Add a new post-card at the top of the grid with `badge-new`.
- Remove `badge-new` from the previous article's post-card.
- Update the hero card: `href`, `cap-kicker`, `cap-title`, `cap-date`.
- **Friday rule:** Never touch Challenge cards on index.html on Friday builds.
- Post-card headlines: 2–3 sentences max. Pick the 2–3 most important data points.

---

### Step 4 · Update archive.html

- Update the nav Market Pulse link to today's article.
- Add a new post-card at the top of the Market Pulse section with `badge-new`.
- Remove `badge-new` from the previous post-card.
- **Friday rule:** Never touch Challenge entries on archive.html on Friday builds.

---

### Step 5 · Update email_copy.html

- Update the nav Market Pulse link.
- Update subject lines to today's date with three A/B/C options following the Click Rule and Opportunity Frame.
- Update the `memberEmailHTML` JS variable:
  - `<title>`: `Market Pulse - [Month D, YYYY] - Member Edition`
  - Hero kicker: `[Day], [Date] · Member Edition`
  - Hero link: `totem-challenge-preview.vercel.app/[article-filename].html`
  - Hero headline: word-for-word identical to the article headline
  - Lead paragraph: the day's hinge (tension frame), 25 words max, opens a second subject to the hero
  - Data snapshot: 5 items max, rounded figures, gold left border
  - 5 bullets: each ONE bold sentence, 15 words max, linked to `#open-1` through `#open-5` on today's article
  - Bottom CTA: links to today's article
  - Footer: "You are receiving this email as a member of Totem LC Group." + General Disclaimer verbatim
- Update the `nonMemberEmailHTML` JS variable — same as member except:
  - `<title>`: `Market Pulse - [Month D, YYYY]`
  - Hero kicker: `[Day], [Date] · [Day] Briefing`
  - Footer: "A free weekly snapshot for the Totem community." + General Disclaimer verbatim

**Email word caps (not targets — count before pushing):**

| Unit | Cap |
|---|---|
| Preheader | 12 words |
| Hero headline | 20 words, 2 sentences |
| Lead paragraph | 25 words, 1–2 sentences |
| Data snapshot | 5 items |
| Each bullet | 15 words, 1 bold sentence, NO context sentence |
| Total body copy | 120 words |

**Curiosity Gap Test:** Read each bullet alone. Does it make the reader ask "why?" or "what?" — and is the answer only on the website? If the bullet contains its own answer, cut the answer, keep the question.

**Subject Variety Rule (email):** Read the first 8 words of preheader → hero headline → lead → data snapshot → each bullet in order. No two consecutive units may lead with the same subject.

**Opportunity Frame:** Lead with what is available for the reader, not what is happening to them. First-eight-words ban list for subject line, preheader, hero headline, and lead: strikes, war, crisis, collapse, crash, fear, plunge, panic, attack, escalation. At least three of the five bullets point at something the reader can use or act on.

---

### Step 6 · Push to editorial (Phase 1 complete)

```bash
git add market_pulse_[date].html index.html archive.html email_copy.html
git commit -m "Market Pulse [Month D, YYYY]"
git push origin main
```

The `totem-editorial-review` project auto-deploys on every push to main. After this push, editorial review is live at [totem-editorial-review.vercel.app](https://totem-editorial-review.vercel.app).

---

## Phase 2 — Live Deploy

No approval gate. Proceed immediately after Phase 1.

### Step 7 · Strip editorial nav links

```bash
python3 scripts/nav_links.py strip
```

This removes the Email Copy and Emergency PO `<li>` items from ALL public HTML files. It exits non-zero if any file still carries a link. Never use `sed` (sed has corrupted files before). Never strip only the new article — every page on the site shares the same nav.

---

### Step 8 · Link CLI to live project and deploy

```bash
npx vercel link --yes --project totem-challenge-preview --token "$VERCEL_TOKEN"
npx vercel --prod --yes --token "$VERCEL_TOKEN"
```

**Always verify** the aliased URL in the deploy output reads `totem-challenge-preview.vercel.app` before proceeding. If it reads anything else, do not declare Phase 2 complete.

Vercel project table (never confuse these):

| Project | URL | Purpose |
|---|---|---|
| `totem-challenge-preview` | totem-challenge-preview.vercel.app | **Live site.** Phase 2 target. |
| `totem-editorial-review` | totem-editorial-review.vercel.app | Editorial review — auto-deploys on push to main. |
| `totem-newsletter-site` | totem-newsletter-site.vercel.app | **Do not use for live deploys.** |

---

### Step 9 · Restore editorial nav links

```bash
python3 scripts/nav_links.py restore
```

Exits non-zero unless every public file carries both links again. If it fails, restore from git:

```bash
git checkout <pre-strip commit> -- *.html
```

Do not replace the repo script with a one-off. The lesson from 2026-09-02: 58 older files have the Archive `<li>` on the same line as The Challenge link; the repo script handles this correctly.

---

### Step 10 · Relink CLI back to editorial project

```bash
npx vercel link --yes --project totem-newsletter-site --token "$VERCEL_TOKEN"
```

Keeps `.vercel/project.json` tidy for the next editorial push.

---

### Step 11 · Commit and push restored files

```bash
git add -A && git commit -m "Restore editorial nav links" && git push origin main
```

If the restore brought files back to exactly their committed state (working tree clean), no commit is needed — that is correct behavior, not an error.

---

### Step 12 · Verify the live article

```bash
curl -sI https://totem-challenge-preview.vercel.app/market_pulse_[date].html | head -5
```

Confirm all of:
- HTTP 200
- Today's headline is present in the page body
- No `email_copy.html` link visible (editorial nav stripped)
- Anchors `open-1` through `open-5` present

---

### Step 13 · Notify JJ

Send a push notification with the live article URL. Then stop. Do not ask JJ to review or send the email — the member email sends itself via the cloud routine at 6:15 AM MT (12:15 UTC).

---

## Crypto tracked assets (always include all three)

| Asset | Ticker | What to research |
|---|---|---|
| Bitcoin | BTC | Price, ETF inflows (IBIT etc.), rate-path sensitivity |
| Ethereum | ETH | Price, regulatory backdrop (CLARITY Act), support levels |
| XRP | XRP | Price, ETF inflows, CLARITY Act Senate status, on-chain metrics (DAA, network growth from Santiment), Ripple escrow unlock schedule |

---

## Security

`VERCEL_TOKEN` must never be echoed, printed, logged, or pasted — in a command, a commit message, a notification, or any output. Reference it only as `"$VERCEL_TOKEN"`.
