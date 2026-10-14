# Decision Log (ADRs)

One entry per decision that constrains future work. Newest first within
sections. These absorbed the gotchas from the retired `HANDOFF.md` v3.4 and
`DEEPSEEK_REQUIREMENTS.md` (both live in git history; see Stage 1 of
`REDESIGN_PLAN.md`). ADR numbers are stable — CI rules cite them.

## Environment & toolchain

### ADR-000 — Docker is the dev environment; the rootless-Ruby saga is dead
The old sandbox had no system Ruby, blocked `sudo`, and a read-only `$HOME`,
which produced a 790 MB gitignored `.tools/ruby/` rebuilt by hand from Debian
debs (`dpkg-deb -x`, `RUBYLIB` traps, shebang rewrites). **Retired.** Local
preview now runs `jekyll/jekyll:pages` via `docker compose up` (see
`docs/RUNBOOK.md`). The container image matches production's gem set, which
also ends ADR-006's version drift as a daily annoyance. If a future sandbox
truly lacks Docker, the full historical rebuild recipe is preserved in git
history under `DEEPSEEK_REQUIREMENTS.md` (2026-09-24 revision).

### ADR-001 — `Gemfile.lock` is committed
It was previously gitignored "because the local toolchain drifted from
production". With the lockfile generated *inside* the pages image (RUNBOOK §1),
local and production resolve identically, so committing it makes builds
reproducible instead of aspirational. One deliberate commit; watch the deploy.

### ADR-002 — Production build is owned by `actions/jekyll-build-pages@v1`
The deploy workflow stays exactly as-is. Do not swap in a custom Jekyll 4
build to "modernize": Pages infrastructure is the boring, working choice.
Guardrails run in a separate `ci.yml` so a failing check never blocks a hotfix
deploy (they share the same code path being tested).

## Content model

### ADR-003 — `_data/site.yml` is the single source of truth for channel URLs
Handles/URLs appear once, in `_data/site.yml`; `index.md` and `_data/links.yml`
reference them via `site.data.site.*`. CI fails on hardcoded `tiktok.com/@…`
outside the data file. When Stage 2 adds episodes, per-video URLs go in
`_episodes/` front matter, never inline in prose.

### ADR-004 — kramdown does not parse markdown inside HTML blocks
`parse_block_html: false` is the default. Copy inside `<section>`/`<div>` must
be real `<p>`/`<em>` tags. This is why story copy in `index.md` looks like
HTML. Keep it that way rather than flipping the config globally.

### ADR-005 — Social share image comes from page front matter, not a site key
`jekyll-seo-tag`'s `ImageDrop` reads only `page["image"]` (and its documented
sub-keys). A top-level `image:` in `_config.yml` is silently ignored — no
error, no `og:image`, degraded card. Set it via `_config.yml` `defaults:`
(current setup) or per-page front matter. Per-episode cards (Stage 5) will use
the episode's own `image:` front matter. Cost one full P0 cycle to learn.

### ADR-006 — Accepted cosmetic drift: Actions seo-tag 2.8.0 vs newer locally
Actions' pages environment pins jekyll 3.10.0 / jekyll-seo-tag 2.8.0; newer
seo-tag emits an extra `twitter:description` and writes `name="twitter:image"`
instead of `property=`. Harmless; don't chase diffs that exist only outside
the pinned image. The Docker/pages-image workflow means local previews now
run *the same* versions, shrinking this gap to zero in practice.

### ADR-007 — Image-swap contract: stable filenames
`assets/img/hero-1400.jpg` (1400×764), `hero-700.jpg`, `og.jpg` (1200×630) are
referenced by templates. Swapping a photo = overwrite those files at the same
dimensions (`convert -strip -interlace Plane -resize <W>x -quality 78`);
never rename, never touch `index.md`/`_config.yml` for an image change. CI
enforces existence + og dimensions.

### ADR-008 — Dead channels are deleted, not placeholdered
Instagram/YouTube "Soon" buttons were removed deliberately; nothing may
reference accounts that don't exist. Re-add entries to `_data/links.yml` (with
real `url:`s pointing into `_data/site.yml`) only when the account is live.
CI flags link entries whose URL doesn't resolve to `http…`.

### ADR-009 — Story chronology is data-driven and unblocked by draft seeds
The v3.4 hold ("don't touch `.story` until the first video posts") existed to
prevent publishing dead links. Stage 2 supersedes it structurally: the
chronology renders from `_episodes/`, and promised-but-unposted videos live
there as `draft: true` — invisible in production, so the structure can be
built and exercised without any dead-link risk. Owner-provided titles/dates
populate the drafts as they arrive.

## Site integrity (invariants, inherited)

- **Never add `index.html`** — Pages serves it before `index.md` and hides the
  site with no error anywhere (the original v1 bug). CI-enforced (R1).
- **`url:` must not include `baseurl`** — doubling breaks canonicals and
  share previews; this went live broken once. CI-enforced (R2).
- **Check `git status -sb` before pushing; never force-push `main`** — it has
  diverged once. Safe recovery: `git reset --soft origin/main`, recommit.
- Footer year via `{{ site.time | date: "%Y" }}`, never JS. CI-enforced.
- Type pairing (EB Garamond story / Jost interface) is brand identity.
  CI-enforced (R-type).
- No newsletter section (removed in v2, deliberately).
- Do not rename the repo or change `baseurl`.
- `drafts/` is gitignored *and* excluded from the build: raw scripts contain
  private facts (dates, cities, ages) that must never ship. Never `git add -f`
  anything in there.

## Open decisions (not yet made)

- Real couple photo replacing the ink-swirl stand-in — owner asset pending
  (swap procedure: ADR-007).
- Sitemap + 404 page + VideoObject JSON-LD — scheduled Stage 7.
- End-to-end social-card test in a real chat client — scheduled Stage 5.
