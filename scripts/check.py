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


def fail(rule, msg):
    failures.append(f"[{rule}] {msg}")


# ---------------------------------------------------------------- structural
config = yaml.safe_load(ROOT.joinpath("_config.yml").read_text())

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
links = yaml.safe_load(ROOT.joinpath("_data/links.yml").read_text()) or []
site_data = yaml.safe_load(ROOT.joinpath("_data/site.yml").read_text())

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
for f in ("index.md", "_data/links.yml"):
    text = ROOT.joinpath(f).read_text()
    if "tiktok.com/@" in text:
        fail("R-single-source", f"{f} hardcodes a channel URL — reference site.data.site instead.")

# ---------------------------------------------------------------- episodes
# R-schema: every episode file must carry the keys the templates consume.
ep_dir = ROOT.joinpath("_episodes")
required = {"title", "video_id", "tiktok_url", "posted", "chapter", "summary"}
ep_count = 0
if ep_dir.is_dir():
    for ep in sorted(ep_dir.glob("*.md")):
        text = ep.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue  # collection README etc. — no front matter, not an episode
        ep_count += 1
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get("draft"):
            continue
        missing = required - set(fm)
        if missing:
            fail("R-schema", f"{ep.name}: episode front matter missing {sorted(missing)}")

# ---------------------------------------------------------------- house rules
# R-type: the EB Garamond / Jost pairing is load-bearing brand identity.
css = ROOT.joinpath("assets/css/styles.css").read_text()
if "Garamond" not in css or "Jost" not in css:
    fail("R-type", "styles.css lost the EB Garamond/Jost pairing — swapping it back is a 'what not to do' item.")

# R-no-js-year: footer year comes from Liquid, never a DOM script hook.
if re.search(r"getElementById\(['\"]year['\"]\)", ROOT.joinpath("assets/js/main.js").read_text()):
    fail("R-no-js-year", "main.js references #year — the footer renders the year via {{ site.time }}.")

# ---------------------------------------------------------------- report
if failures:
    print("Guardrail violations:")
    for f in failures:
        print("  FAIL", f)
    sys.exit(1)
print(f"All guardrails pass ({len(links)} link(s), {ep_count} episode(s)).")
