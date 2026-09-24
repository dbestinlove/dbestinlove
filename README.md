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

Requires Ruby 3.x.

```bash
bundle install
bundle exec jekyll serve --baseurl ""
```

Then open <http://127.0.0.1:4000>. The empty `--baseurl` is required — without it every asset 404s on localhost.

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

No social share image, no photo above the fold, no sitemap, no 404 page. All of it, with priorities and specifics, is in `HANDOFF.md`.

## Note

`HANDOFF.md` is committed to this public repo but excluded from the build, so it is not served on the site.
