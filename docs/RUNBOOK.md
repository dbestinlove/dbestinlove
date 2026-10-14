# Runbook — day-to-day operations

## §1 Local preview (the only supported path)

Requires Docker. Nothing else — no Ruby, no sudo, no toolchain bootstrap.

```bash
git clone https://github.com/dbestinlove/dbestinlove && cd dbestinlove
docker compose up            # first run installs gems into a named volume
open http://localhost:4000   # --baseurl '' is baked into the compose command
```

The image (`jekyll/jekyll:pages`) carries the **same github-pages gem set as
production** (Jekyll 3.10.0, jekyll-seo-tag 2.8.0), so what you see is what
deploys. Regenerate `Gemfile.lock` inside the same image after any `Gemfile`
change, then commit it (ADR-001):

```bash
docker run --rm -v "$PWD:/srv/jekyll" -w /srv/jekyll jekyll/jekyll:pages \
  bundle lockfile update
```

No Docker available? Guardrails still run anywhere with Python:
`python3 scripts/check.py`. The historical rootless-Ruby recipe (obsolete,
kept for emergencies) is in git history: `git show HEAD~:DEEPSEEK_REQUIREMENTS.md`
from any commit before Stage 1 landed.

## §2 Publish

One file changed → one commit → push to `main`:

```bash
git status -sb               # confirm not diverged; NEVER --force-push main
git add <file> && git commit -m "..." && git push
gh run watch                 # Deploy site workflow, ~50s
```

`ci.yml` (guardrails + production-toolchain build) runs on the same push. A CI
failure does not block the Pages deploy by design (ADR-002) — fix forward
immediately when it does.

## §3 Common tasks

| Task | Do this | Never do this |
|---|---|---|
| Add a video | Create `_episodes/<slug>.md` (Stage 2 template) | hand-edit story HTML |
| Add a channel (once real) | Add URL/handle to `_data/site.yml`, entry in `_data/links.yml` referencing it | hardcode URLs in `index.md`; restore "Soon" placeholders (ADR-008) |
| Swap photos | Overwrite `assets/img/{hero-1400,hero-700,og}.jpg` at identical dimensions, `convert -strip -interlace Plane -resize <W>x -quality 78`, update `alt` text | rename files (ADR-007) |
| Change copy | Edit `index.md`; remember ADR-004 (real `<p>` tags inside HTML blocks) | expect `*markdown*` to render inside `<section>` |
| Social card per page | Front matter `image:` or `_config.yml` defaults (ADR-005) | top-level `image:` key in `_config.yml` — silently ignored |

## §4 Recovery

- **Site vanished after adding `index.html`**: delete it, push. Pages precedence
  (R1) explains the silence.
- **Share previews broken / doubled paths**: check `url:` has no `baseurl` (R2).
- **Branch diverged**: `git reset --soft origin/main`, recommit, push normal.
- **Local build ≠ deployed diffs in twitter: meta style**: ADR-006 — cosmetic
  seo-tag version drift; compare against the pages image, not a newer Jekyll.
- **Privacy incident (drafts)**: `drafts/` is gitignored *and* excluded from
  builds; verify with `grep -r drafts _site/ || true` after any odd build. If
  ever committed, treat as a secret: rewrite history immediately.

## §5 Verification checklist (run before risky merges)

```bash
python3 scripts/check.py                       # guardrails
docker compose up --build                      # renders; eyeball hero/links/story/footer
curl -s http://localhost:4000/ | grep og:image # share card tags present
diff <(sed 's/[0-9]\{4\}-[0-9][0-9]-[0-9][0-9]//g' _site/index.html) \
     <(sed 's/[0-9]\{4\}-[0-9][0-9]-[0-9][0-9]//g' docs/baseline/index.html)  # vs pinned baseline
```
