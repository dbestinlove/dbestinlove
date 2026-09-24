# HANDOFF — DBest In Love (v3.4)

**Repo:** `dbestinlove/dbestinlove`
**Live URL:** https://dbestinlove.github.io/dbestinlove/
**Stack:** Jekyll → GitHub Pages via Actions (`actions/jekyll-build-pages@v1`)
**v3.4 status:** Every P0 and P1 item from v3 is implemented. What's left is either quick/independent (P2/P3) or genuinely blocked on video content existing. Only TikTok is live; Instagram/YouTube don't exist yet and nothing should reference them until they do.

---

## 1. What shipped since v3

| Item | What happened |
|---|---|
| Dead "Soon" buttons | Instagram and YouTube entries removed from `_data/links.yml`. Only TikTok remains. Re-add entries there (with a `url:`) once those accounts exist — that's the only file that needs touching. |
| Visible handle | Already satisfied — `sub:` on the TikTok button reads `@dbestinlove — new videos weekly`. No action was needed. |
| Hero photo (P0) | Implemented, but with a **stand-in image**, not a photo of the couple — see §2. Full-bleed above the `<h1>`, `srcset` at 700w/1400w, recompressed to 86 KB / 31 KB from a 604 KB original. |
| Social card (P0) | **Was silently broken; now fixed.** `image:` at the top level of `_config.yml` is never read by `jekyll-seo-tag` — see gotcha 6 — so no `og:image` was emitted at all and `twitter:card` fell back to `summary`. Moved into `_config.yml` `defaults:`. Verified live: `og:image` points at the 1200×630 `og.jpg` and `twitter:card` is now `summary_large_image`. |
| Dead code (P3) | The `document.getElementById('year')` block removed from `assets/js/main.js` — the footer already uses `{{ site.time \| date: "%Y" }}` via Liquid, so this never fired. |
| `.gitignore` (P3) | Added: `_site/`, `.jekyll-cache/`, `.sass-cache/`, `Gemfile.lock`. See gotcha 5 for why `Gemfile.lock` is ignored rather than committed. |
| `robots.txt` (P2) | Added: `User-agent: *` / `Allow: /`. No `Sitemap:` line yet — add one when `jekyll-sitemap` goes in. |

---

## 2. Open items, and what's blocking them

### Needs a person's decision or asset (not blocked on video content)

- **Hero photo is a placeholder.** The current hero/og image is a photo of red and blue ink merging in water — chosen deliberately for the moment (it echoes the site's flag-merge palette) but it is **not a photo of the two people in the story**. The original P0 problem HANDOFF v3 raised — "the site has no faces" — is still technically true. Swap in a real photo of the couple when one is ready: replace `assets/img/hero-1400.jpg`, `hero-700.jpg`, and `og.jpg` (same filenames, same dimensions — 1400×764, 700×382, 1200×630 — keeps `index.md` and `_config.yml` untouched), recompress the same way (`convert -strip -interlace Plane -resize <W>x -quality 78`), and update the `alt` text in `index.md` to describe the actual photo instead of the ink swirl.
- **Hero-photo crop: RESOLVED — it was never broken.** Measured the deployed page with headless Chromium at 400 / 768 / 900 / 1400 / 1920px (setup in `DEEPSEEK_REQUIREMENTS.md` §1). At every width the `.hero__photo` container spans the full viewport (`x: 0`, `width == innerWidth`), horizontal overflow is **0**, and `document.scrollWidth == innerWidth`, so there is no horizontal scrollbar either. `object-fit: cover` overflows on the **vertical** axis only — 18px at 400w rising to 668px at 1920w — which is exactly the intended behaviour: full width, trimmed top and bottom. The full-bleed margin box also equals the wrap's content width at every breakpoint, so it centres correctly. **The deployed site renders as intended.** The screenshot that prompted this was stale cache or taken before the push; a "narrow vertical strip losing the sides" is not producible by this CSS, since only a container narrower than the viewport would crop horizontally. Note the `46vw → 34vw` hedge was a no-op for that symptom — both values clamp to the 380px max at ≥1118px — and merely shortens the image between ~826–1118px. Screenshots are in `.tools/shots/` for a human to eyeball; the agent cannot view images (see gotcha 5).
- **Social card: verified at the tag level, not yet in a real client.** `og:image` and `twitter:card: summary_large_image` are confirmed in the deployed HTML, and the image returns HTTP 200 as a 1200×630 JPEG — which is everything a crawler needs. One end-to-end test is still worth doing: paste the live URL into a chat client, since that exercises the crawler rather than the markup.
- **Old unused `assets/img/hero.jpg`** (604 KB, the original untouched upload) is superseded by `hero-1400.jpg`/`hero-700.jpg` and should be deleted from the repo.
- **Sitemap** (`jekyll-sitemap` plugin) and a **404.md** page — independent, no blockers, just not done yet.

### Blocked on video content existing

- **Story "start here" chronology.** Deliberately held per the site owner's call: don't touch the `.story` section's structure until at least the first video is posted. See §3 — this is the main thing a future agent should pick up once that happens.
- **Re-evaluating the hero/social-card photo choice** once real footage exists to pull a still from, if a dedicated photo of the couple still isn't available by then.

---

## 3. For whoever picks this up once videos and scripts are ready

This is the trigger condition the site owner set: once the first few videos are drafted/posted, the story section should be updated to reflect them. When that happens:

1. **Get the video order and titles/topics** from the owner — the story section needs to tell a new TikTok arrival "start with this one."
2. **Add a short chronology to the `.story` section in `index.md`** — years or "chapter" markers, per the original HANDOFF ask. Keep it consistent with the existing prose style (EB Garamond, first-person plural, understated) rather than turning it into a bullet list; this site's whole voice is quiet and literary, not marketing copy.
3. **Check whether the hero/social-card photo should change too** — if by then there's a real photo of the couple (from a video still or otherwise), replace the ink-swirl stand-in per §2's instructions.
4. **Re-test the social card** after any image swap — paste the live URL into a chat client and confirm the preview renders.
5. **Leave Instagram/YouTube alone** unless those accounts now exist. If they do, re-add entries to `_data/links.yml` with real `url:` values — don't restore the dashed "Soon" placeholders.

---

## 4. Gotchas (carried forward, still true)

1. **kramdown does not parse markdown inside HTML blocks.** `parse_block_html: false` is the default. Text inside `<section>` or `<div>` needs real `<p>`/`<em>` tags, not `*markdown*` syntax.
2. **`url` in `_config.yml` must not include `baseurl`.** `url: "https://dbestinlove.github.io"` + `baseurl: "/dbestinlove"`. Doubling the path breaks every canonical tag and share preview. This was live once.
3. **Never add an `index.html`.** GitHub Pages serves it before `index.md`, silently hiding the whole site. This was the original v1 bug.
4. **Check `git status -sb` before pushing.** `main` has diverged before. `git reset --soft origin/main` then commit is the safe recovery — never `git push --force`.
5. **The agent environment has Ruby, Jekyll, a headless browser, ImageMagick, and now *vision*.** Build and preview with the repo's own documented commands (`bundle install`, then `bundle exec jekyll serve --baseurl ""`) — both work with no env vars or workarounds. It can also measure or screenshot the deployed page at any width and *see* the result through the `vision-skills` toolkit. Full setup and the rebuild recipe are in `DEEPSEEK_REQUIREMENTS.md`. Visual judgement no longer has to route through a human — but for pixel-exact facts (colours, offsets, small diffs) use `vision_dominant_colors` / `vision_trace` / `vision_pixel_diff`, never a model's prose description.
6. **Title and description come from `_config.yml`. The share image does NOT.** `jekyll-seo-tag` resolves `image` through its `ImageDrop`, which reads `page["image"]` and only that — its four documented sources are `image`, `image.path`, `image.facebook`, `image.twitter`, all page-level. There is **no `site.image` fallback**. A top-level `image:` key in `_config.yml` is silently ignored: no error, no `og:image`, and `twitter:card` degrades from `summary_large_image` to `summary`. Set it via `_config.yml` `defaults:` (which populates front matter) or in the page's own front matter. This cost a full P0 cycle.
7. **New:** when changing anything in `assets/img/`, keep filenames stable (`hero-1400.jpg`, `hero-700.jpg`, `og.jpg`) so `index.md` and `_config.yml` never need touching for an image swap — just overwrite the files.

---

## 5. What not to do

- Don't re-add the newsletter section (removed deliberately in v2).
- Don't add an `index.html`.
- Don't hardcode the footer year — `{{ site.time | date: "%Y" }}` is correct.
- Don't rename the repo or `baseurl`.
- Don't commit `_site/`.
- Don't swap the type pairing back (EB Garamond for story / Jost for interface).
- Don't restore Instagram/YouTube "Soon" placeholders — delete-until-real was the explicit decision this round.
- Don't touch the story section's structure before a video is actually posted — that's a deliberate hold, not an oversight.

---

## 6. Definition of done for v3.4's remaining scope

- [x] Hero photo crop confirmed correct — measured at five viewport widths: full width, vertical-only crop, no horizontal overflow
- [x] Social card live — `og:image` emitted and `twitter:card` is `summary_large_image` (verified in the deployed HTML)
- [ ] Social card confirmed end-to-end in a real link-preview test
- [ ] Old unused `assets/img/hero.jpg` removed from the repo
- [ ] Sitemap and 404 page in place
- [ ] Story chronology added once the first video is live
- [ ] Real photo of the couple in place, if/when available, replacing the ink-swirl stand-in
