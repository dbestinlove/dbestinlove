# REDESIGN PLAN — DBest In Love (greenfield, 10 stages)

**Author:** lead dev LLM
**Date:** 2026-10-15
**Status:** Approved for implementation. Stages are strictly sequential; each ends with a deploy and a check, never a big-bang cutover.

This is the plan I would follow if I were building this site from scratch today, with one intent: **make the website a machine for converting TikTok arrivals into returning readers**, refined incrementally as the video strategy matures. The current repo (`v3.4`) is my starting assumption of what exists; where the old project made a call I agree with, I keep it and say so; where I'd decide differently, I override it explicitly.

---

## Design philosophy (the through-line)

1. **One job, stated in one line.** The site is a *story hub*: a TikTok viewer clicks the bio link, understands who we are in under 5 seconds, and leaves again toward a platform — or returns when told there's something new. Every stage is judged against that funnel.
2. **Data-driven cadence.** "New videos weekly" is a promise the site must be able to keep truthfully without editing HTML. Everything downstream (episodes collection, `latest` pointer, og refresh, sitemap lastmod) exists to make that promise mechanical instead of manual.
3. **Content is git.** Video metadata lives in `_data/` and a `_episodes/` collection so a non-technical owner edits one YAML file per upload, and CI enforces validity. No CMS, no database, no Node app server — Jekyll on Pages remains the right architecture for this scale. (Decision: **keep the stack**; rewrite the information architecture.)
4. **Progressive enhancement, always.** The site must be fully usable with JS disabled and honor `prefers-reduced-motion`. Keep this from v3.4.
5. **Ship small, verify live.** Each stage lands behind a watched Actions deploy. No stage depends on assets that don't exist yet — blocked work is stubbed with data files, not skipped silently.

### Decisions made as lead dev (overrides & retirements)

| Old state / rule | Decision | Why |
|---|---|---|
| Ruby toolchain rebuilt rootless in `.tools/ruby/` every clone | **Retire.** Move local dev to `jekyll/jekyll:pages` Docker image (or Dev Container). | The entire DEEPSEEK_REQUIREMENTS saga (dpkg-deb extraction, RUBYLIB traps, stale env vars) was a workaround for a hostile sandbox. A container-first workflow deletes that whole class of problem. |
| `Gemfile.lock` gitignored "on purpose, not the agent's call" | **Resolve: commit it** for local dev parity only; CI keeps using `actions/jekyll-build-pages` which ignores it. Documented in one deliberate commit with a watched deploy. | It was left as an open decision for too long. Committing locally pins contributor builds; Pages behavior is unchanged either way, so risk ≈ 0. |
| Docs split across README + HANDOFF + DEEPSEEK_REQUIREMENTS with contradictory environment claims | **Collapse** into README (usage) + `docs/DECISIONS.md` (ADR-style log) + `docs/RUNBOOK.md` (recovery recipes). Gotchas become ADRs, not folklore. | Three overlapping status documents rot. This plan itself becomes DECISIONS entry 001. |
| Single `index.md` with hardcoded TikTok URL in prose and footer | **Replace** with data-driven templates + `_episodes` collection. URLs come from `_config.yml` only. | The v3.4 social-card bug (silent `og:image` failure) happened precisely because config/prose/data were coupled by hand. |
| Deliberate hold: "don't touch story structure until first video posts" | **Override.** Build the episode spine now with empty/seed data. | Holding structure hostage to content is why the site has no chronology workflow at all. Scaffolding with zero episodes deploys safely and unblocks everything else. |
| Keep ink-swirl hero until a real couple photo exists | **Keep the placeholder policy** (Stage 3), but add an explicit `hero:` front-matter slot so swapping photos later is a two-file change. | Correct prior decision; just make the swap cheaper next time. |
| Never add `index.html`; url/baseurl split; kramdown gotcha | **Keep as permanent guardrails**, encoded in CI checks rather than prose warnings. | These cost real outages before. Memory is not a control system. |

---

## The 10 stages

### Stage 1 — Foundation reset & canonical baseline (Day 1)
**Goal:** a boringly reproducible starting point before any feature work.
**Build:**
- Pin the deployed page as the visual/functional reference (save HTML + screenshots to `docs/baseline/`).
- Replace the rootless-Ruby setup with a `.devcontainer/` + `docker-compose.yml` running `jekyll/jekyll:pages`; delete the rebuild recipe.
- Commit `Gemfile.lock` (one deliberate commit; watch the deploy).
- Collapse README/HANDOFF/DEEPSEEK into `README.md` + `docs/DECISIONS.md` (import unresolved gotchas as ADRs 000–009) + `docs/RUNBOOK.md`.
**Data/schema:** none new.
**Verification:** `docker compose up` → `bundle exec jekyll serve --baseurl ""` renders identical page; production deploy byte-comparable to baseline except version strings.
**Exit criteria:** fresh clone → working preview in ≤ 3 commands.
**Kept/overridden:** kills the biggest environmental tax in the project; changes nothing user-visible.

### Stage 2 — Content model: `_episodes` collection + single source of truth
**Goal:** every fact about the couple and their channels exists in exactly one place.
**Build:**
- New collection `_episodes/` with front matter: `title`, `video_id`, `tiktok_url`, `posted`, `chapter`, `summary`, `duration`, `featured`, `og_image?`. Permalink: `/watch/:title/` (a redirect shell page that shows summary + CTA, then forwards — see Stage 8 for UTMs).
- `_data/chapters.yml`: `{ id, label, years, blurb }` — e.g. *"Met (2015)"*, *"The pandemic years"*, *"Not yet, but not never"*, *"Closing the distance"*.
- `_data/site.yml` for handles/URLs; `index.md`'s hardcoded TikTok links replaced with `site.tiktok` lookups.
- Seed with the promised-but-unposted series as `draft: true` episodes so structure is exercised without publishing dead links (rendered only with `JEKYLL_ENV=development`).
**Verification:** build passes with 0 episodes published; `links.yml` still drives the nav; unit-ish check script asserts every episode's required keys exist.
**Exit criteria:** adding a video = creating one markdown file + optionally one chapter. No template edits ever.
**Rationale:** this is the keystone of the whole strategy; everything after consumes it.

### Stage 3 — First-impression layer: hero, hook, identity
**Goal:** a TikTok arrival recognizes the video within 5 seconds.
**Build:**
- Hero gets a `hero:` front-matter slot (image path + alt), defaulting to the current ink photo via `defaults:` — swap later = overwrite files, same filenames (keep v3.4 rule #7).
- Add handle lockup (`@dbestinlove`) adjacent to the H1 so site ↔ account identity is unmistakable; the sub-label stops carrying that alone.
- Hook copy moves to `_data/copy.yml` (all prose strings keyed), enabling owner edits without touching HTML — respects the kramdown gotcha by keeping blocks pure HTML.
- Compress budget enforced: hero pair stays ≤ 90 KB total; add AVIF/WebP sources with JPEG fallback.
**Verification:** Lighthouse Performance ≥ 95 mobile; CLS = 0 (width/height attrs retained); reduced-motion path visually checked.
**Exit criteria:** photo swap is a documented 3-file operation.

### Stage 4 — Story spine: chapters render from data
**Goal:** the "start here" chronology exists structurally, populated when videos land.
**Build:**
- Rebuild `.story` as a loop over `_data/chapters.yml`, each chapter rendering its episodes (title, year marker, "Watch on TikTok →" deep link). Empty chapters render a quiet dashed placeholder ("Filming now") — the same visual language as the retired "Soon" buttons, applied honestly.
- Voice constraint codified in `docs/DECISIONS.md`: EB Garamond first-person plural, no bullet lists, no marketing register. Prose blurbs live in `chapters.yml`, not templates.
- "Start here" pin: `featured: true` on one episode renders a persistent "Begin with Episode 1" card above the list.
**Verification:** with 0 published episodes the section degrades to the current prose story (feature-flag via chapter count); with seeded drafts it renders correctly.
**Exit criteria:** the v3.4 blocker ("waiting for first video") is dissolved — posting video #1 requires only un-drafting a file.

### Stage 5 — Conversion surfaces & shareability
**Goal:** every exit from the site is measured and every share looks intentional.
**Build:**
- All outbound links get UTM parameters via a Liquid include (`utm_source=web&utm_medium=hub&utm_campaign=<slot>`): button, story links, footer. Slot-level attribution answers "which section sends the taps?"
- Per-episode og images: episode front matter can carry `og_image`; falls back to site `og.jpg`. Card copy generated from title + chapter.
- End-to-end share test executed once and recorded (paste URL into a chat client, screenshot result into `docs/`) — closes the one checkbox v3.4 never managed.
- Optional: `rel="me"` link to TikTok for profile cross-verification.
**Verification:** deployed HTML contains utm params on every external href; og tags verified per episode page; the v3.4 "not done" item flips to done with evidence.
**Exit criteria:** a new episode automatically produces a correct share card with zero template work.

### Stage 6 — Workflow automation: CI quality gates + owner publish flow
**Goal:** mistakes become impossible, publishing becomes trivial.
**Build:**
- Expand Actions: PR workflow runs `jekyll build` + html-proofer (internal links, missing assets) + a custom guard script encoding the house rules: *no `index.html` committed*, *`url` does not contain `baseurl`*, *every episode has required front matter*, *`links.yml` entries with no `url` fail the build* (enforcing delete-until-real mechanically).
- Publish flow doc'd in README: drop `_episodes/my-video.md`, set `posted`, PR merges → auto-deploy. Optionally a `workflow_dispatch` "refresh social cards" job that pings u.a/, Twitter bot, and Google indexing for the latest episode URL.
- Branch protection on `main`; the diverged-history incident becomes a RUNBOOK recovery recipe (`git reset --soft origin/main`), never a rule written in blood prose.
**Verification:** deliberately broken PR (missing front matter / added index.html) fails with a human-readable annotation.
**Exit criteria:** owner-side publish = one file, one PR, one merge. Guardrail regressions caught pre-merge, not post-outage.

### Stage 7 — Discoverability & SEO completion
**Goal:** the site is findable and cache-correct.
**Build:**
- Enable `jekyll-sitemap`; add `Sitemap:` line to robots.txt (v3.4's deferred half-step).
- `404.md` — quiet, in-voice page pointing to featured episode (the other v3.4 straggler).
- Canonical handling already safe via `url`+`baseurl` separation; add breadcrumbs-free minimal JSON-LD (`Person`/`WebSite` + episode `VideoObject` with upload date) from episode data.
- Lastmod surfaced through the sitemap plugin (free, once episodes exist).
**Verification:** sitemap.xml lists home + episode pages with sane lastmod; 404 returns status 404 on Pages; Rich Results test passes on an episode URL.
**Exit criteria:** both unchecked v3.4 boxes closed with proof, plus structured data the TikTok-link audience's platforms can consume.

### Stage 8 — Feedback loop: measurement that informs the video strategy
**Goal:** the site tells us what the strategy should do next.
**Build:**
- Self-hosted, cookieless counter (plausible-style snippet or a tiny GoatCounter install) — privacy posture matches a love story, not an ad product. Events: `outbound_click` per UTM slot, `episode_view`.
- A monthly `metrics/YYYY-MM.md` note committed to the repo (owner pastes numbers or a scheduled Action pulls API stats) so decisions have a paper trail: Which chapter's episodes get tapped most? Does "Begin with Episode 1" beat mid-list deep links?
- Explicit non-goal: no A/B infrastructure, no personalization. Sample sizes don't justify it; the ledger approach fits the voice.
**Verification:** counters fire on click (devtools network tab), nothing loads on consent-less load beyond one <2 KB script.
**Exit criteria:** Stage 9's roadmap is generated from ≥ 2 months of this ledger, not vibes.

### Stage 9 — Iteration engine: backlog driven by data + strategy
**Goal:** institutionalize "incremental changes aligned with the strategy."
**Build (candidate queue, ordered by expected funnel impact):**
1. Real couple photo / video-still hero swap (asset-blocked since v3.4 — now a 3-file op thanks to Stage 3).
2. Instagram/YouTube surfaces re-added to `links.yml` **only when accounts exist** (guard script enforces); per-platform og variants.
3. Countdown/"next upload" element fed by `chapters.yml` schedule — only if metrics show return-visit intent.
4. Wedding-date announcement page as a standalone collection item with its own share card — the story's natural climax and the campaign's peak-share moment.
5. Multi-language pass (the three-country, two-flag reality) if analytics show a second language's traffic.
Each candidate enters as a one-page spec in `docs/specs/`, ships as its own stage-sized PR, and cites the metric or strategy note that justified it.
**Exit criteria:** a standing rhythm: monthly metrics note → pick one queue item → ship → measure.

### Stage 10 — Hardening & handoff-as-code
**Goal:** the project survives its authors (and its agents).
**Build:**
- Renovate/Dependabot for gems + actions; quarterly rebuild drill (delete `.devcontainer` volume, rebuild from docs alone, time it).
- Turn down unused surface: if a stage's experiment didn't earn its bytes, delete it in a visible commit (the newsletter precedent — deletion is a maintained decision).
- Final docs pass: README = usage only; DECISIONS.md complete (this plan folded in as ADR-001..N); RUNBOOK holds deploy-failure, diverged-main, and image-swap recipes. Delete HANDOFF.md and DEEPSEEK_REQUIREMENTS.md once their contents are absorbed.
- Definition-of-done audit against the funnel: click-through from bio link measurable end-to-end, publish flow ≤ 15 min, cold-start contribution ≤ 30 min.
**Exit criteria:** repo passes the "new agent, blank memory" test: reads docs, ships a change, verifies, recovers from a simulated failure — without asking a human anything the docs don't answer.

---

## Sequencing & dependencies

```
1 ──► 2 ──► 3 ──┐
                ├─► 5 ──► 6 ──► 7 ──► 8 ──► 9 ──► 10
            4 ──┘
```
Stages 3 and 4 are parallelizable after 2. Nothing waits on real video content: Stage 2's draft seeds exercise every code path video posts will use. Total realistic span: ~6 weeks part-time, or 10 focused working days.

## Global risks

- **Actions runner drift** (Jekyll 3.10 vs local 4.x): mitigated by Stage 1's pinned Docker matching the Pages gem set; re-diff deployed vs local HTML at Stages 5 and 7.
- **Owner adoption**: the whole workflow thesis fails if publishing isn't easier than the old edit-HTML way; Stage 6's PR-based flow must be tested by the actual owner before sign-off.
- **Scope creep toward a blog/CMS**: rejected repeatedly by design — this is a hub, not a publication. Queue items that violate the one-line job die in `docs/specs/`.
