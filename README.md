# DBest In Love

**A 10-year long-distance love story, told out loud.**

Live at **https://dbestinlove.github.io/dbestinlove/** — Jekyll on GitHub
Pages, deployed by Actions on every push to `main` (~50 s).

This repo is mid-redesign: a 10-stage plan lives in `REDESIGN_PLAN.md`.
Stage 1 (foundation reset) established the rules below.

## Quickstart

```bash
docker compose up      # http://localhost:4000 — same gem set as production
python3 scripts/check.py   # house-rule guardrails (needs only Python + PyYAML)
```

No Ruby installation exists or is needed; the container *is* the toolchain
(ADR-000). Full operations guide: **`docs/RUNBOOK.md`**.

## Where things live

| To change | Edit |
|---|---|
| A link button — label, sub-label, badge | `_data/links.yml` |
| Social handles / channel URLs | `_data/site.yml` (single source of truth) |
| Hero, story, and footer copy | `index.md` |
| Site name, tagline, SEO description | `_config.yml` |
| Colours, type, spacing | `assets/css/styles.css` |
| Icons | `_includes/icon.html` |
| Page shell — head, fonts, skip link | `_layouts/default.html` |
| Photos | overwrite `assets/img/{hero-1400,hero-700,og}.jpg` in place (ADR-007) |
| An episode/video (from Stage 2) | one file in `_episodes/` |

## Docs

- `docs/DECISIONS.md` — why the project is shaped like this (ADRs 000–009 plus
  inherited invariants: never add `index.html`, keep `url:` free of `baseurl`,
  kramdown HTML-block caveat, seo-tag image gotcha, delete-until-real links…).
- `docs/RUNBOOK.md` — preview, publish, common tasks, recovery, verification.
- `docs/baseline/` — pinned capture of the deployed page before redesign work.
- `REDESIGN_PLAN.md` — the 10-stage strategy.
- Retired: `HANDOFF.md` v3.4 and `DEEPSEEK_REQUIREMENTS.md` (content absorbed
  into the two docs above; originals recoverable from git history).

## House rules are code

`scripts/check.py` runs on every PR/push (`.github/workflows/ci.yml`) and
builds with the production toolchain inside `jekyll/jekyll:pages`. If it's
green locally, it deploys green. The deploy workflow itself is unchanged and
remains the publisher (ADR-002).
