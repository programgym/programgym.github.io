#!/usr/bin/env bash
# Regenerate every raster asset from icon.svg.
#
# icon.svg is a traced bitmap (~10k paths, 9 MB), far too heavy to ship to a
# browser, so the site serves rasterized PNGs instead. Rendering goes through
# the system librsvg/cairo via ctypes (svg2png.py), then each PNG is reduced to
# a 256-colour palette (pngquant.py), which cuts ~70% with no visible loss.
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

# Social card: mascot + wordmark composited at 1200x630.
python3 - <<'PY'
import base64
logo = base64.b64encode(open('static/images/logo.png', 'rb').read()).decode()
open('/tmp/pg-og.svg', 'w').write(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0b0f15"/>
  <rect x="0" y="0" width="1200" height="4" fill="#f0920b"/>
  <image x="80" y="105" width="420" height="420" xlink:href="data:image/png;base64,{logo}"/>
  <text x="556" y="290" font-family="DejaVu Sans Mono, monospace" font-size="72" font-weight="bold" fill="#e4e8ee">
    <tspan fill="#f0920b">./</tspan>Program<tspan fill="#f0920b">Gym</tspan>
  </text>
  <text x="556" y="350" font-family="DejaVu Sans, sans-serif" font-size="30" fill="#8d96a3">A training ground for coding agents.</text>
</svg>''')
PY
python3 tools/svg2png.py /tmp/pg-og.svg /tmp/pg-og.png 1200
python3 tools/pngquant.py /tmp/pg-og.png static/images/social-preview.png 256
rm -f /tmp/pg-og.svg /tmp/pg-og.png

echo "Done."
