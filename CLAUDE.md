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
# 1. Strip editorial nav links from today's article (Email Copy + Emergency PO <li> items)
# 2. Link CLI to the correct live project
npx vercel link --yes --project totem-challenge-preview
# 3. Deploy
npx vercel --prod --yes
# 4. Restore editorial nav links in the article file
# 5. Relink CLI back to the editorial project (keeps .vercel/project.json tidy)
npx vercel link --yes --project totem-newsletter-site
```

Always verify the aliased URL in the deploy output reads `totem-challenge-preview.vercel.app` before declaring Phase 2 complete.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `navajosouljah/totem-newsletter-site` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.
