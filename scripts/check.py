#!/usr/bin/env python3
"""Repo guardrails — every rule here is a bug that actually happened (or a
deliberate policy that must not silently rot). Runs in CI on every PR/push and
locally via `python3 scripts/check.py` (needs only Python 3 + PyYAML; no Ruby).

Exit 0 = all clear. Non-zero with a list of violations otherwise.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML missing — run: pip install pyyaml")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
failures = []


def load_yaml_str(text, where):
    """yaml.safe_load with a duplicate-top-level-key detector (ADR-010:
    PyYAML silently keeps the LAST duplicate key — same silent-loss class as
    the og:image bug). Raises ValueError on duplicates."""
    def no_dupes(loader, node, deep=False):
        mapping = {}
        for k_node, v_node in node.value:
            key = loader.construct_object(k_node, deep=deep)
            if key in mapping:
                raise ValueError(f"duplicate top-level key '{key}' in {where}")
            mapping[key] = loader.construct_object(v_node, deep=deep)
        return mapping
    class StrictLoader(yaml.SafeLoader):
        pass
    StrictLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_dupes)
    return yaml.load(text, Loader=StrictLoader)


def fail(rule, msg):
    failures.append(f"[{rule}] {msg}")


# ---------------------------------------------------------------- structural
config = load_yaml_str(ROOT.joinpath("_config.yml").read_text(), "_config.yml")

# R1 (v1 bug): GitHub Pages serves index.html *before* index.md, silently
# hiding the whole site. An index.html at the source root is always a mistake.
if ROOT.joinpath("index.html").exists():
    fail("R1-index-html", "index.html exists at repo root — Pages will serve it instead of index.md.")

# R2 (live once): url must be the domain only; baseurl lives in its own key.
url, baseurl = str(config.get("url", "")), str(config.get("baseurl", ""))
if baseurl and url.endswith(baseurl.rstrip("/")):
    fail("R2-url-baseurl", f"url '{url}' already contains baseurl — canonical tags/share previews break.")

# R7: image swap contract — these filenames are referenced by index.md and
# _config.yml defaults; renaming them forces template edits.
for name in ("hero-1400.jpg", "hero-700.jpg", "og.jpg"):
    if not ROOT.joinpath("assets/img", name).exists():
        fail("R7-image-contract", f"assets/img/{name} missing — keep image filenames stable across swaps.")

# og.jpg share-card dimensions (1200x630), read from JPEG headers directly.
og = ROOT.joinpath("assets/img/og.jpg")
if og.exists():
    data, i = og.read_bytes(), 2
    dims = None
    while i < len(data):
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h = int.from_bytes(data[i + 5:i + 7], "big")
            w = int.from_bytes(data[i + 7:i + 9], "big")
            dims = (w, h)
            break
        i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    if dims and dims != (1200, 630):
        fail("R7-og-dims", f"og.jpg is {dims[0]}x{dims[1]}, expected 1200x630 for summary_large_image cards.")

# ---------------------------------------------------------------- links.yml
links = load_yaml_str(ROOT.joinpath("_data/links.yml").read_text(), "_data/links.yml") or []
site_data = load_yaml_str(ROOT.joinpath("_data/site.yml").read_text(), "_data/site.yml")

# R8 (policy): dead channels were deleted, not placeholdered. A link entry
# without a resolvable URL reintroduces the "Soon" buttons deliberately removed.
for entry in links:
    raw = str(entry.get("url", ""))
    def lookup(m):
        node = site_data
        for key in m.group(1).split("."):
            node = node.get(key) if isinstance(node, dict) else None
        return str(node) if node is not None else ""

    resolved = re.sub(r"\{\{\s*site\.data\.site\.([\w.]+)\s*\}\}", lookup, raw)
    if not resolved.startswith("http"):
        fail("R8-dead-links", f"links.yml entry '{entry.get('label')}' has no real url ('{raw}') — delete until the account exists.")

# R-single-source: channel URLs exist in exactly one place (_data/site.yml).
for f in ("index.md", "_data/links.yml", "_layouts/episode.html"):
    text = ROOT.joinpath(f).read_text()
    if "tiktok.com/@" in text:
        fail("R-single-source", f"{f} hardcodes a channel URL — reference site.data.site instead.")

# R-ep-url-source (Stage 2): episode `tiktok_url` must be the literal live URL
# (TikTok ids are opaque; no template can reconstruct it). This is the ONLY
# sanctioned place a tiktok.com/@ URL may appear outside _data/site.yml — and
# only once the video actually exists (drafts carry an empty string).

# ---------------------------------------------------------------- episodes
# R-schema (Stage 2): every episode file must carry the keys the templates
# consume; chapter ids must exist; published episodes need real URLs and a
# date; exactly one may be featured. Drafts are validated too (they become
# published with one flag flip), except the url/posted rules which only apply
# once `draft: false`.
chapters = load_yaml_str(ROOT.joinpath("_data/chapters.yml").read_text(), "_data/chapters.yml") or []
chapter_ids = {c.get("id") for c in chapters}

# R-chapter-source: story prose lives in data, never hardcoded in templates.
for f in ("index.md", "_layouts/default.html", "_layouts/episode.html"):
    if "It started the way the best things do" in ROOT.joinpath(f).read_text():
        fail("R-chapter-source", f"{f} hardcodes story prose — render it from _data/chapters.yml instead.")

ep_dir = ROOT.joinpath("_episodes")
required = {"title", "episode", "video_id", "tiktok_url", "posted", "chapter", "summary"}
ep_count = 0
draft_count = 0
published_count = 0
featured_count = 0
if ep_dir.is_dir():
    for ep in sorted(ep_dir.glob("*.md")):
        if ep.name == "README.md":
            continue
        text = ep.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            fail("R-schema", f"{ep.name}: episode without parseable front matter")
            continue
        ep_count += 1
        fm = yaml.safe_load(m.group(1)) or {}
        missing = required - set(fm)
        if missing:
            fail("R-schema", f"{ep.name}: episode front matter missing {sorted(missing)}")
        if fm.get("chapter") not in chapter_ids:
            fail("R-chapter", f"{ep.name}: chapter '{fm.get('chapter')}' not in _data/chapters.yml")
        if not isinstance(fm.get("episode"), int):
            fail("R-episode-int", f"{ep.name}: 'episode' must be an integer")
        body = text.split("---", 2)[-1]
        if re.search(r"<(p|em|div|section)\b", body):
            fail("R-ep-html", f"{ep.name}: raw HTML in episode body — keep prose plain (ADR-004 class of bug)")
        if fm.get("featured"):
            featured_count += 1
        if fm.get("draft"):
            draft_count += 1
            continue
        published_count += 1
        if not str(fm.get("tiktok_url", "")).startswith("https://www.tiktok.com/"):
            fail("R-ep-url", f"{ep.name}: published episode needs a real tiktok_url — keep draft: true until the video exists")
        posted = str(fm.get("posted", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", posted):
            fail("R-ep-posted", f"{ep.name}: published episode needs posted: YYYY-MM-DD")
if featured_count > 1:
    fail("R-feature", f"{featured_count} episodes marked featured — exactly one may pin 'Begin with Episode 1'")

# ---------------------------------------------------------------- house rules
# R-type: the EB Garamond / Jost pairing is load-bearing brand identity.
css = ROOT.joinpath("assets/css/styles.css").read_text()
if "Garamond" not in css or "Jost" not in css:
    fail("R-type", "styles.css lost the EB Garamond/Jost pairing — swapping it back is a 'what not to do' item.")

# R-single-footer (Stage 2): index.md owns the footer markup; episode pages
# get it from the shared layout. A second <footer> in episode.html means the
# layout contract broke.
ep_layout = ROOT.joinpath("_layouts/episode.html").read_text()
if "<footer" in ep_layout:
    fail("R-single-footer", "_layouts/episode.html contains a <footer> — the default layout already renders one.")

# R-no-js-year: footer year comes from Liquid, never a DOM script hook.
if re.search(r"getElementById\(['\"]year['\"]\)", ROOT.joinpath("assets/js/main.js").read_text()):
    fail("R-no-js-year", "main.js references #year — the footer renders the year via {{ site.time }}.")

# ---------------------------------------------------------------- report
if failures:
    print("Guardrail violations:")
    for f in failures:
        print("  FAIL", f)
    sys.exit(1)
if not chapter_ids:
    fail("R-chapters-empty", "_data/chapters.yml has no chapters — the story spine renders nothing.")
print(f"All guardrails pass ({len(links)} link(s), {ep_count} episode(s): "
      f"{published_count} published, {draft_count} draft, {featured_count} featured).")
