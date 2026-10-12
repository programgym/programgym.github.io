#!/usr/bin/env bash
# Regenerate the mascot raster assets and the current social preview.
#
# icon.svg is a traced bitmap (~10k paths, 9 MB), far too heavy to ship to a
# browser, so the site serves rasterized PNGs instead. Rendering goes through
# the system librsvg/cairo via ctypes (svg2png.py), then mascot PNGs are reduced
# to a 256-colour palette (pngquant.py), cutting ~70% with no visible loss.
set -euo pipefail
cd "$(dirname "$0")/.."

render() {  # render <out> <max-dimension-px>
  python3 tools/svg2png.py icon.svg "/tmp/pg-$$.png" "$2"
  python3 tools/pngquant.py "/tmp/pg-$$.png" "$1" 256
  rm -f "/tmp/pg-$$.png"
}

mkdir -p static/images
render static/images/logo.png             640
render static/images/favicon.png           64
render static/images/apple-touch-icon.png 180

# Social card has its own editable SVG layout. Keep text antialiasing in RGB.
python3 tools/build_social_preview.py

echo "Done."
