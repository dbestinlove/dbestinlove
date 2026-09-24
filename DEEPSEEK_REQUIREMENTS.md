# DEEPSEEK_REQUIREMENTS.md

> **⚠️ Superseded as a description of the current environment — 2026-09-24.**
> Everything below was written for a `danger-full-access` container that had
> passwordless `sudo`, a writable `$HOME`, and a full toolchain (Ruby, Jekyll,
> ImageMagick, Chromium, the `vision-skills` toolkit). **None of that holds now.**
> The sandbox is back to `workspace-write`, `sudo` is blocked again (*"The 'no new
> privileges' flag is set"*, `/etc/sudo.conf` owned by uid 65534), `$HOME` is
> read-only, and there is no system Ruby, ImageMagick or headless Chromium.
>
> What works today: a workspace-local **Ruby 3.3.8 + RubyGems 3.5.22 + Bundler
> 2.5.22** in the gitignored `.tools/ruby/`, built without root by extracting
> Debian debs with `dpkg-deb -x`. Run `source .tools/ruby/env.sh` before
> `bundle install` / `bundle exec jekyll build`. `node`/`npm` exist. See
> `HANDOFF.md` gotcha 5. Note `.tools/` is gitignored, so a fresh clone has to
> rebuild the toolchain from scratch.
>
> Read the rest of this file as a **historical record and a rebuild recipe** —
> the package list and §3's locked-down-sandbox workarounds are still useful.
> Treat the status claims below as history, not as current fact.

This file started as a request for help, because the agent could not install its own packages. It is now a **record of the environment and a recipe to rebuild it**, which is what makes it worth keeping.

Environment: Debian 13 (trixie), aarch64, user `dbest`.

---

## 0a. Rebuild recipe — rootless Ruby (current)

Verified working on 2026-09-24. `apt-get download` needs no root; `dpkg-deb -x` unpacks
into the repo; `.tools/` is gitignored so none of it is committed.

```bash
cd "/home/dbest/Plus One Project/dbestinlove"
mkdir -p .tools/ruby/debs .tools/ruby/root
cd .tools/ruby/debs
apt-get download ruby3.3 libruby3.3 ruby3.3-dev ruby-rubygems rubygems-integration
cd ..
for d in debs/*.deb; do dpkg-deb -x "$d" root; done
# the extracted scripts shebang /usr/bin/ruby3.3, which needs root to create
sed -i '1s|^#!/usr/bin/ruby3\.3$|#!/usr/bin/env ruby|' root/usr/bin/*
```

Then create `.tools/ruby/bin/` wrappers (`ruby`, `ruby3.3` → alias of `ruby`, `gem`,
`bundle`, `bundler`) that each export `LD_LIBRARY_PATH="$RUBY_ROOT/root/usr/lib/aarch64-linux-gnu"`
and `RUBYLIB` covering `root/usr/lib/ruby/3.3.0`, `root/usr/lib/ruby/vendor_ruby`,
`root/usr/lib/aarch64-linux-gnu/ruby/3.3.0` and `.../ruby/vendor_ruby`, then exec
`ruby3.3` with the matching `gem3.3`/`bundle3.3` script. Finish with an `env.sh` that
prepends `bin/` to `PATH` and sets a repo-local `GEM_HOME`.

Three traps, all hit during setup:

- The interpreter is compiled with `prefix=/usr`, so its built-in `$LOAD_PATH` misses the
  extracted stdlib — **`RUBYLIB` is mandatory**, or `require "rubygems"` fails outright.
- The `gem`/`bundle` scripts shebang `/usr/bin/ruby3.3`, which cannot be created without
  root; repoint them to `#!/usr/bin/env ruby`.
- Gem-installed executables are written with `#!/usr/bin/env ruby3.3`, so the wrapper dir
  needs a `ruby3.3` alias too, or `bundle exec jekyll` dies with
  `env: 'ruby3.3': No such file or directory`.

Bundler also warns *"`/home/dbest` is not writable"* on every run and falls back to a
`/tmp` home. Cosmetic; the build is unaffected.

---

## 0. What changed

| | Before | Now |
|---|---|---|
| File sandbox | `workspace-write` — only the repo was writable | `danger-full-access` |
| `$HOME` | **read-only** — `~/.gem`, `~/.cache`, `~/.npm` unusable | writable |
| `sudo` | blocked: *"The 'no new privileges' flag is set"* | works — `sudo -n id` returns `uid=0(root)` |
| Consequence | every tool needed its cache redirected into the repo via env vars; 790 MB of tooling lived in `.tools/` inside the git repo | tools install normally; the repo is back to 3.0 MB of actual project files |

The old workaround is documented in §3 in case a future container reverts to a locked-down sandbox.

---

## 1. Installed and verified

Every package below was proven by doing this project's real work, not by checking `--version`.

| Package | Version | How it was verified |
|---|---|---|
| `imagemagick` | 7.1.1-43 Q16 | Ran the pipeline `HANDOFF.md` documents: `convert hero-1400.jpg -strip -interlace Plane -resize 700x -quality 78` produced a valid 30,937-byte JPEG (the existing `hero-700.jpg` is 36,459 bytes, so the documented settings hold up). Also produced a 1200×630 crop for `og.jpg`. |
| `python3-pil` | Pillow 11.1.0 | Read dimensions of all four images in `assets/img/`. |
| `python3-yaml` | PyYAML 6.0.2 | Parsed `_config.yml` and `_data/links.yml` structurally — no more regex. |
| `yamllint` | 1.37.1 | **Found a real bug**: `_data/links.yml` had no trailing newline. Fixed. `_config.yml` also had an 81-char comment line; rewrapped. Both now lint clean. |
| `optipng` | 0.7.8 | installed |
| `jpegoptim` | 1.4.7 | installed |
| `webp` (`cwebp`) | — | installed |
| `librsvg2-bin` (`rsvg-convert`) | 2.60.0 | Rasterized `favicon.svg` to a 512×512 PNG. |
| `jq` | 1.7 | Wrangled GitHub API JSON through `gh api --jq`. |
| `bundler` | 4.0.21 | see below |
| `jekyll` | 4.4.1 | see below |
| `webrick` | 1.9.2 | required for `jekyll serve` on Ruby 3.x |
| `jekyll-seo-tag` | 2.9.0 | see below |

Plus five default gems installed as root — `base64 0.2.0`, `bigdecimal 3.1.5`, `csv 3.3.4`, `logger 1.6.0`, `json 2.7.2`. **These were the reason `bundle install` failed**: as an unprivileged user, Bundler tried to write its cache to root-owned `/var/lib/gems/3.3.0/cache/` and hit `Bundler::PermissionError`.

### The repo's own documented workflow now works

`README.md` tells a contributor to run `bundle install` and `bundle exec jekyll serve --baseurl ""`. Both are now true for an ordinary user — no env vars, no `JEKYLL_NO_BUNDLER_REQUIRE`:

```
$ bundle install
Bundle complete! 2 Gemfile dependencies, 36 gems now installed.

$ bundle exec jekyll serve --baseurl "" --port 4000
HTTP 200  5462 bytes at http://127.0.0.1:4000/
  <title>DBest In Love | 10 Years Apart · Together Forever</title>
  /assets/css/styles.css -> HTTP 200
```

---

## 2. Where the agent's tooling lives

**This depends on the file policy, and the two are coupled.** Anything the agent must *write* has to be inside the session workspace whenever the policy is `workspace-write`:

| What | `danger-full-access` | `workspace-write` (current) |
|---|---|---|
| Jekyll toolchain | system-wide — works either way | system-wide — works either way |
| ImageMagick, Pillow, PyYAML, yamllint, optipng, jpegoptim, cwebp, rsvg-convert | system-wide — works either way | system-wide — works either way |
| Chromium + Playwright browsers | `~/.cache/ms-playwright/` | same — **read-only is fine**, browsers only need to be readable |
| Playwright *module*, driver script, screenshots | `~/.local/share/dsh-pw/` | **`.tools/pw/` and `.tools/shots/`** — outputs must be writable |

So: reads from `$HOME` work under either policy; **writes** do not. The 660 MB browser payload stays in `~/.cache` and is never copied — only the 20 MB module and its outputs come into the repo, and `.tools/` is gitignored.

Measure the deployed page at any width:

```bash
cd .tools/pw
node shot.js "https://dbestinlove.github.io/dbestinlove/" "$PWD/../shots"
```

### Gotcha: leaked environment variables survive policy changes

Earlier setup exported `GEM_HOME`, `GEM_SPEC_CACHE`, `XDG_CACHE_HOME`, `npm_config_cache`, `PLAYWRIGHT_BROWSERS_PATH` and `JEKYLL_NO_BUNDLER_REQUIRE`. **These persisted into the session environment** and outlived the directories they pointed at. When the policy reverted to `workspace-write`, Playwright broke looking for `.tools/browsers` — a directory that no longer existed.

`.tools/pw/shot.js` now defends itself: if the configured browsers path does not exist, it falls back to `~/.cache/ms-playwright`. Note the ordering trap — **Playwright resolves browser paths at `require()` time, not at `launch()`**, so the override has to be set before the `require('playwright')` line or it silently does nothing.

If a future session sees odd tool behaviour, check `env` for stale workspace paths first.

Screenshots of the live page at 400 / 768 / 900 / 1400 / 1920px are written to `.tools/shots/`.

---

## 3. Rebuilding this environment from scratch

If the container is reset or the sandbox reverts to `workspace-write`, this is the whole recipe.

```bash
# --- packages (needs root) ---
sudo apt-get update -qq
sudo apt-get install -y imagemagick jq python3-pil python3-yaml yamllint \
                        optipng jpegoptim webp librsvg2-bin

# --- Ruby / Jekyll (needs root) ---
sudo gem install bundler jekyll webrick jekyll-seo-tag --no-document

# --- the five default gems Bundler needs, or `bundle install` fails ---
sudo gem install base64:0.2.0 bigdecimal:3.1.5 csv:3.3.4 logger:1.6.0 json:2.7.2 --no-document

# --- browser tooling (no root needed) ---
mkdir -p ~/.local/share/dsh-pw && cd ~/.local/share/dsh-pw
npm install playwright --no-audit --no-fund
npx --yes playwright@latest install chromium     # lands in ~/.cache/ms-playwright
```

### If `sudo` is unavailable and `$HOME` is read-only again

The old workaround, which worked but is fragile. Every path has to be redirected into the repo:

```bash
cd "/home/dbest1/Plus One Project/dbestinlove"
export GEM_HOME="$PWD/.tools/gems"              GEM_PATH="$PWD/.tools/gems"
export GEM_SPEC_CACHE="$PWD/.tools/spec-cache"  # else RubyGems dies writing ~/.cache/gem
export XDG_CACHE_HOME="$PWD/.tools/cache"
export HOME="$PWD/.tools/home"                  # last resort for stray writes
export PATH="$PWD/.tools/gems/bin:$PATH"
export JEKYLL_NO_BUNDLER_REQUIRE=1              # else Jekyll hands off to Bundler and dies
export npm_config_cache="$PWD/.tools/npm-cache"
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers"
jekyll build --source . --destination _site
```

If you have to do this, re-add `.tools/` to `.gitignore`.

---

## 4. ✅ Resolved — the agent can see images

**The vision toolkit landed.** `read_image` still refuses on this model (*"does not declare image input"*), but the `vision-skills` toolkit routes images to a configured vision service instead, which closes the gap without needing a different model.

Available now: `vision_glance` (describe / answer / OCR), `vision_ground` (locate a named thing), `vision_detect` (enumerate a kind), `vision_crop`, `vision_dominant_colors`, `vision_pixel_diff`, `vision_trace` (exact geometry, local), `vision_extract_foreground`, `vision_html_screenshot`, `vision_long_screenshot_ocr`.

**Why it matters here.** The hero-crop question was settled by DOM measurement, which was a *better* instrument than looking — but measurement only answers questions that can be phrased numerically. It cannot say *"the type looks wrong"* or *"that photo is unflattering."* This can.

**First real findings** — on `hero-700.jpg`, confirmed by sha256 `eb77998d…`:

- The image's "white" is **#ECF2F5** and **#D8DFE5** — a cool blue-grey, not the page's `#FFFFFF`. A large cool-grey photo on a pure-white page can read as a faint grey band.
- **No brand colour appears in it.** The palette is dusty and desaturated: darkest tone `#4D1333` (wine), mid `#6D4472` (plum), then `#8B7F9A` and `#B5BED3` (muted blue). Flag red `#DA1A35` and Old Glory blue `#3C3B6E` scored **0%** against it. The image *echoes* the merge palette rather than matching it.
- The letterbox a desktop visitor sees (1400×380, cut per `object-position: 50% 55%`) **reads well**: the focal knot is fully visible and not crowded by an edge, and the curved glass bowl walls at both ends give it a natural frame.

**Caveat that still stands:** `vision_glance` prose is not a measurement. Exact colours come from `vision_dominant_colors`, exact geometry from `vision_trace`, exact differences from `vision_pixel_diff`. Never take a description's word for a styling fact.

---

## 5. Harness asks

1. **Nothing outstanding.** The vision toolkit closed the last gap (§4) — visual work no longer routes through a human.
2. Keep `danger-full-access` if you can. It removed 790 MB from the repo and turned a five-`export` install command into a one-liner.
3. Network egress is sufficient — nothing to enable.

**On GitHub Pages "plugins"**: there is nothing to turn on in repo settings. `jekyll-seo-tag` and `jekyll-sitemap` are enabled purely by listing them under `plugins:` in `_config.yml`. The Pages source should stay **GitHub Actions**.

---

## 6. Open decision — `Gemfile.lock`

`bundle install` now generates a `Gemfile.lock`, and it is currently **gitignored**, so it is not committed.

- **Keep it ignored (current):** the Pages build resolves gems fresh each time. The deploy works today and nothing about it changes.
- **Commit it:** reproducible builds pinned to exact versions — but it changes how the Pages Action resolves gems, so it deserves a deliberate commit and a watched deploy rather than being swept in.

Left as-is on purpose. Not the agent's call to change deployment behaviour silently.
