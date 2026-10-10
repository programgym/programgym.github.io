# programgym.github.io

Landing page for **ProgramGym** — a training ground for coding agents.
Published with GitHub Pages at <https://programgym.github.io>.

## Layout

```
index.html                    GENERATED — do not edit, your change will be lost
tools/tpl.html                the page itself: markup, inline script
tools/gen.py                  chart geometry, icon sprite, cache-busting
tools/icons/                  icon sources (see tools/icons/README.md)
tools/orgs/                   affiliation logos as supplied (PDF, Illustrator SVG)
tools/pdf2svg.py              flat-vector PDF -> SVG, no dependencies
static/images/orgs/           affiliation logos, web-ready
program-agent.html            GENERATED — the agent walkthrough iframe (tools/programagent/README.md)
tools/programagent/           its generator: drawio -> SVG, beats, page assembly
static/css/main.css           design tokens + styles, light & dark
static/images/                generated raster assets — do not edit by hand
icon.svg                      source artwork for every image below
```

## Editing the page

`index.html` is written by `tools/gen.py` from `tools/tpl.html`. Editing it
directly looks like it works until the next `gen.py` run silently reverts it,
which is easy to miss when more than one person is in the repo.

```sh
python3 tools/gen.py          # after editing tpl.html, gen.py, or main.css
```

Run it after a `main.css` edit too: `gen.py` stamps the stylesheet's content
hash into its `<link>` URL. Pages serves both files with `max-age=600`, so
without a fresh stamp a visitor can pair new markup with the stylesheet they
already had cached — new class names then match no rule and, for example, a
tinted icon falls back to the inherited text colour.

## Affiliation logos

`static/images/orgs/` is built from `tools/orgs/`, not edited by hand:

```sh
python3 tools/pdf2svg.py tools/orgs/xmu-logo.pdf static/images/orgs/xmu.svg
```

`unisound.svg` is the supplied Illustrator file with its `<style>` block folded
into `fill` attributes — once inlined, `.cls-1` and `.cls-2` are global class
names and have no business in a page. `deeplit.png` is the lab's own icon,
reduced to 256 colours by `tools/pngquant.py`.

They render on a white tile in both themes: two of the three are navy on
transparent and vanish against the dark footer, and a tile keeps the brand
colours correct rather than filtering them.

## Assets

`icon.svg` is a traced bitmap: ~10,000 paths and 62,000 distinct colours in
9 MB. Serving it directly would mean a 9 MB download and a slow render, so the
site ships PNGs generated from it:

| File | Size | Use |
| --- | --- | --- |
| `logo.png` (640px) | 117 KB | hero image |
| `favicon.png` (64px) | 4 KB | browser tab |
| `apple-touch-icon.png` (180px) | 17 KB | iOS home screen |
| `social-preview.png` (1200×630) | 78 KB | Open Graph / Twitter card |

Regenerate them all after editing `icon.svg`:

```sh
./tools/build_assets.sh
```

The pipeline has no third-party dependencies — it calls the system
`librsvg`/`cairo` through `ctypes` (`tools/svg2png.py`), then reduces each PNG
to a 256-colour palette with a median-cut quantizer (`tools/pngquant.py`),
which saves about 70% with no visible quality loss.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

With Playwright and Chromium available, run `node tools/check-responsive.cjs`
against that preview. It checks 320–1920px layouts, both themes, embedded
walkthrough controls, and mouse/touch/keyboard tooltip dismissal. `BASE_URL`,
`PLAYWRIGHT_MODULE`, and `CHROMIUM_EXECUTABLE` can select an existing preview
or browser installation.

Run `node tools/check-walkthrough-scroll.cjs` with the same settings to check
step-list buttons, W/S shortcuts, complete list access, and native page scrolling.
Set `BROWSER_TYPE=webkit` to run this interaction check with Playwright WebKit.
The embedded walkthroughs accept W/S only while their frame has focus; they do
not bind keyboard up/down arrows or intercept wheel/touch gestures.

Run `node tools/check-theme.cjs` to check the circular theme transition in
both directions, repeated clicks, cancellation, iframe theme sync and fallbacks.
It samples the transition frames to detect a second cross-fade at the end.

Chart tooltips share `static/js/tooltips.js`. Re-run `python3 tools/gen.py`
after editing it to refresh its content hash, just as for `main.css`.

## Theming

Colours are CSS custom properties defined once per theme at the top of
`main.css`. The theme follows the OS setting, can be toggled in the nav, and
persists in `localStorage`; an inline script in `<head>` applies it before
first paint so the page never flashes the wrong theme.
