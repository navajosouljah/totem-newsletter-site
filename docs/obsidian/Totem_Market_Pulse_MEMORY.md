---
title: Totem Market Pulse - Standing Memory
vault_path: ~/Vaults/BOLT/20_Businesses/Totem/MEMORY.md
owner: JJ Gilmore
updated: 2026-09-02
source_of_truth: CLAUDE.md in navajosouljah/totem-newsletter-site (this note mirrors it)
tags: [totem, market-pulse, newsletter, standing-decisions]
---

# Totem Market Pulse - Standing Memory

One-page memory for any agent or person touching Market Pulse. `CLAUDE.md` in the repo is the enforced version; this note is the human-readable mirror for the vault. When they disagree, `CLAUDE.md` wins and this note gets updated.

## Decisions locked 2026-09-02 (JJ)

### 1. The site goes live without review
> "You can always go live after you build the site. I don't need to review this before we go live anymore." - JJ, 2026-09-02

Morning run: build article + email, push to editorial, run Phase 2 to `totem-challenge-preview`, verify the live page, send one push notification with the live article link and the email copy link. Do not stop to ask. JJ reviews the **email** on his own schedule before sending in Mailchimp; the agent never sends email.

### 2. The email's only job is the click
90-day Mailchimp baseline (Jun-Aug 2026): 32.5% open, **2.0% click**. Best send 16.4% click; a dozen sends at 0.0% with 30%+ opens. The failure mode is an email that answers its own questions.

Hard caps: preheader 12 words · hero 20 words / 2 sentences · lead 25 words · snapshot 5 items · each of the Five Things **15 words, one bold sentence, no context sentence, linked to the article** · body total 120 words. Every bullet must pass the Curiosity Gap Test: the answer is only on the website.

### 3. Less war, less fear: the Opportunity Frame
Lead with what is available *for* the reader, not what is happening *to* them. First-eight-words ban list for subject, preheader, hero, lead: strikes, war, crisis, collapse, crash, fear, plunge, panic, attack, escalation. At least three of five bullets point at something the reader can use; at most one leads with conflict. Not spin: the reality check stays in the snapshot line and the article. Compliance stays on: "66% likely to get a raise" passes; "will get a raise" does not.

### 4. Article Format v2
- Centered headline, **12 words max**, identical to the email hero. No dek.
- The Quick Read: 3 paragraphs, 250 words, Work Sans title, drop cap.
- How [Day] Opens: the five answers to the five email bullets, ids `open-1..5`, each linking to its section. Email bullets deep-link to these anchors.
- Eleven sections, same skeleton: Work Sans title · 3-figure stat strip · italic setup paragraph · precise data lines (label, number to the decimal, direction, one plain-weight reason) · gold-rule bottom line · "Curated from" sources line.
- Bold = labels, numbers, two phrases max. Muted gray = metadata only, never content. Gold 5px dot bullets.
- Whole article 3,000 to 3,600 words. Under means data dropped; over means something said twice.
- Reference implementation: `market_pulse_september2_2026.html` (closing edition).

### 5. Data: released figure, never the forecast
The 2026-09-02 morning article carried ADP at 47K (the consensus). The release was 38K. Use the actual print. If not yet released, say "due at [time]" with no number. Mark estimates (WTI). Never carry a stale number as today's.

### 6. Disclaimers, verbatim from the compliance manual
Article ends with exactly two paragraphs: the General Disclaimer word for word, then one as-of line. Never a recitation of the article's figures (the old block re-stated every number in 600 words). Site footer carries the Website Disclaimer verbatim. Both email footers carry the General Disclaimer verbatim after the audience line. Never the "general information only, not investment advice" paraphrase.

### 7. Every clock time carries AM/PM and the zone
"8:30 AM ET," never "8:30 ET." Article, email, post-cards, chat.

### 8. Phase 2 deploy script lives in the repo
`scripts/nav_links.py strip | restore | check`. On 2026-09-02 a scratchpad restore script put the editorial links back on only 18 of 76 pages because 58 older files have the Archive link sharing a line with The Challenge link. The repo script inserts before the nav's `</ul>` and refuses to exit clean unless every page is restored. Do not replace it with a one-off.

## Open items
- **Mailchimp fragment links.** The five bullets link to `#open-1..5` on one URL. Confirm on the first send whether Mailchimp counts them as five tracked links or one, so the 2.0% click baseline stays comparable.
- **Subject-line A/B.** Run the opportunity subject against the second option on each send for two weeks; ten sends decide it with data.
- **Research note.** Only Axios and Semafor produced verifiable documentation for the headline-then-summary pattern; deep-link click data is principle-level (Nielsen Norman "a link is a promise"), not measured. Our own sends are the evidence that matters.

## Where things live
| Thing | Where |
|---|---|
| Live site | totem-challenge-preview.vercel.app |
| Editorial (auto-deploys on push to main) | totem-editorial-review.vercel.app |
| Do not deploy live here | totem-newsletter-site.vercel.app |
| Rules the agent enforces | `CLAUDE.md` |
| Deploy script | `scripts/nav_links.py` |
| Email copy for Mailchimp | `email_copy.html` on editorial |

## Related
- [[Totem LC Group]]
- [[Market Pulse]]
- [[Totem Compliance Manual]]
