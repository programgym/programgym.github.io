# programgym.github.io

Landing page for **ProgramGym** — a training ground for coding agents.
Published with GitHub Pages at <https://programgym.github.io>.

## Layout

```
index.html                    GENERATED — do not edit, your change will be lost
tools/tpl.html                the page itself: markup, inline script
tools/gen.py                  chart geometry, icon sprite, cache-busting
tools/icons/                  icon sources (see tools/icons/README.md)
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

## Theming

Colours are CSS custom properties defined once per theme at the top of
`main.css`. The theme follows the OS setting, can be toggled in the nav, and
persists in `localStorage`; an inline script in `<head>` applies it before
first paint so the page never flashes the wrong theme.
