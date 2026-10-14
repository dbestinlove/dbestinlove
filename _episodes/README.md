# _episodes

Content model for the TikTok series (Stage 2 of `REDESIGN_PLAN.md`). One file
per video: front matter only, body = summary prose. The story chronology,
watch pages (`/watch/<slug>/`), and share cards render from this data instead
of hand-edited HTML.

## Publishing a video

1. Copy `_template.md.txt` to `_episodes/<slug>.md` (short kebab-case name).
2. Fill in `title`, `episode`, `chapter` (must exist in `_data/chapters.yml`),
   `video_id`, `tiktok_url`, `posted` (YYYY-MM-DD).
3. Set `draft: false`. That's it — no template edits, ever.

The watch page, the homepage chronology entry, and the sitemap all pick the
file up automatically. Guardrails (`scripts/check.py`) validate every key
before CI will pass.

## Draft seeds

Five `draft: true` seed episodes mirror the promised-but-unposted series so
every code path a real upload will use is exercised **locally only**. Drafts
render exclusively when `JEKYLL_ENV=development` and `--drafts` are both set
(`docker compose up` does this); production builds emit zero episode pages
until a real video is un-drafted. Titles/dates should be replaced with
owner-provided facts as they arrive (ADR-009).

