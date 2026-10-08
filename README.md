# programgym.github.io

Landing page for **ProgramGym** — a training ground for coding agents.
Published with GitHub Pages at <https://programgym.github.io>.

## Layout

```
index.html                    the whole page (nav, hero, footer)
static/css/main.css           design tokens + styles, light & dark
static/images/                generated raster assets — do not edit by hand
icon.svg                      source artwork for every image below
tools/                        asset pipeline
```

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
