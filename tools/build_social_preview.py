"""Render the SVG share-card layout with the existing, unchanged mascot.

Run python3 tools/build_social_preview.py, then python3 tools/gen.py to update
the social image's content hash in the page metadata.
"""
import base64
from pathlib import Path
from tempfile import TemporaryDirectory

from svg2png import render

ROOT = Path(__file__).resolve().parent.parent


def main():
    logo = base64.b64encode((ROOT / 'static/images/logo.png').read_bytes()).decode('ascii')
    source = (ROOT / 'tools/social-preview.svg').read_text(encoding='utf-8')
    source = source.replace('{{LOGO_DATA_URI}}', f'data:image/png;base64,{logo}')
    with TemporaryDirectory(prefix='programgym-social-') as directory:
        svg_path = Path(directory) / 'social-preview.svg'
        svg_path.write_text(source, encoding='utf-8')
        render(str(svg_path), str(ROOT / 'static/images/social-preview-light.png'), 1200)


if __name__ == '__main__':
    main()
