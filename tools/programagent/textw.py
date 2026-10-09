# -*- coding: utf-8 -*-
"""Text widths for the figure's three faces, from the metric-compatible Liberation fonts."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ttfw import TTF
LIB = '/usr/share/fonts/truetype/liberation/'
def _ttf(name): return TTF(open(LIB + name, 'rb').read())
FONTS = {
    'serif': {0: _ttf('LiberationSerif-Regular.ttf'), 1: _ttf('LiberationSerif-Bold.ttf')},
    'sans':  {0: _ttf('LiberationSans-Regular.ttf'),  1: _ttf('LiberationSans-Bold.ttf')},
    'mono':  {0: _ttf('LiberationMono-Regular.ttf'),  1: _ttf('LiberationMono-Bold.ttf')},
}
FAMILY = {
    'serif': "Tinos,'Times New Roman',Times,serif",
    'sans':  "Inter,system-ui,-apple-system,'Segoe UI',sans-serif",
    'mono':  "'JetBrains Mono',Consolas,ui-monospace,monospace",
}
def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF
def measure(txt, fam, bold, fs):
    f = FONTS[fam][1 if bold else 0]; w = 0.0
    for ch in txt:
        o = ord(ch)
        if o in (0xFE0F, 0x200D): continue
        w += 1.3 * fs if is_emoji(ch) else f.width(ch, fs)
    return w

