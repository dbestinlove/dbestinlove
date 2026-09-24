# DBest In Love

**A 10-year long-distance love story, told out loud.**

Live at **https://dbestinlove.github.io/dbestinlove/**

A Jekyll site deployed to GitHub Pages by Actions on every push to `main`. Builds take about 50 seconds.

---

## Editing

| To change | Edit |
|---|---|
| A link button — label, sub-label, badge | `_data/links.yml` |
| Hero, story, and footer copy | `index.md` |
| Site name, tagline, SEO description | `_config.yml` |
| Colours, type, spacing | `assets/css/styles.css` |
| Icons | `_includes/icon.html` |
| Page shell — head, fonts, skip link | `_layouts/default.html` |

**Adding a button:** add an entry to `_data/links.yml`. Give it a `url:` and it renders as a live link; leave the `url:` out and it renders as a dashed "Soon" placeholder.

## Run locally

Requires Ruby 3.x. **This machine has no system Ruby and `sudo` is blocked**, so a workspace-local Ruby 3.3.8 lives in the gitignored `.tools/ruby/`. Activate it first:

```bash
source .tools/ruby/env.sh   # puts ruby/gem/bundle on PATH, sets GEM_HOME
bundle install
bundle exec jekyll serve --baseurl ""
```

Then open <http://127.0.0.1:4000>. The empty `--baseurl` is required — without it every asset 404s on localhost.

> `.tools/` is gitignored, so a fresh clone has no toolchain and has to rebuild it — see `DEEPSEEK_REQUIREMENTS.md`. Without `source .tools/ruby/env.sh`, `bundle` and `gem` are simply not on `PATH`.

## Deploy

Push to `main`. The `Deploy to GitHub Pages` workflow builds and publishes. Watch it with:

```bash
gh run watch
```

## House rules

- **Never add an `index.html`.** GitHub Pages serves it *before* `index.md`, which hides the whole site with no error anywhere. This was the original v1 bug.
- **`_config.yml`'s `url` must not include `baseurl`.** `url: https://dbestinlove.github.io` + `baseurl: /dbestinlove`. Doubling the path breaks every canonical tag and share preview.
- **Markdown inside HTML blocks is not parsed.** kramdown defaults to `parse_block_html: false`, so inside `<section>` or `<div>` you must write real `<p>` tags. That's why the story copy in `index.md` looks like HTML.
- **Don't force-push `main`.** It has diverged once already. See `HANDOFF.md` for the safe recovery move.

## Not done yet

Still outstanding: a sitemap (`jekyll-sitemap` plugin) and a `404.md` page.

Shipped since the v3 handoff: the hero photo and the social share card (`og:image` plus `twitter:card: summary_large_image`). The hero is still a stand-in image — ink in water, not a photo of the couple — so swapping in a real photo remains open. Priorities and specifics are in `HANDOFF.md`.

## Note

`HANDOFF.md` is committed to this public repo but excluded from the build, so it is not served on the site.
