# Totem Newsletter Site - Standing Instructions

## Formatting

**Always use markdown hyperlinks for URLs.** Never output a bare URL in chat replies. Format every link as `[descriptive text](url)` so it is clickable. This applies to live deploy URLs, GitHub links, Vercel inspection links, article URLs, and any other hyperlink.

Examples:
- Correct: [totem-newsletter-site.vercel.app/market_pulse_july30_2026.html](https://totem-newsletter-site.vercel.app/market_pulse_july30_2026.html)
- Wrong: `https://totem-newsletter-site.vercel.app/market_pulse_july30_2026.html`

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `navajosouljah/totem-newsletter-site` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.
