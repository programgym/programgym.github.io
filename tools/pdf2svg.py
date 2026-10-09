# -*- coding: utf-8 -*-
"""Convert a flat vector PDF to SVG, with no third-party dependencies.

Written for tools/orgs/xmu-logo.pdf, which Cairo produced: one page, one
FlateDecode content stream, solid RGB fills and `m l c h f*` paths — no
images, fonts, clipping or transforms. That is the whole dialect this
handles; anything else is reported rather than silently dropped.

PDF's y-axis points up and SVG's points down, so the paths go inside one
flipping group rather than being rewritten coordinate by coordinate.

    python3 tools/pdf2svg.py tools/orgs/xmu-logo.pdf static/images/orgs/xmu.svg
"""
import re, sys, zlib

PATH_OPS = {'m': 'M', 'l': 'L', 'c': 'C'}
ARITY    = {'m': 2, 'l': 2, 'c': 6}


def convert(src, dst, precision=1):
    raw = open(src, 'rb').read()

    box = re.search(rb'/MediaBox\s*\[([^\]]*)\]', raw)
    if not box:
        raise SystemExit('no /MediaBox')
    x0, y0, x1, y1 = (float(v) for v in box.group(1).split())
    w, h = x1 - x0, y1 - y0

    streams = []
    for m in re.finditer(rb'stream\r?\n', raw):
        chunk = raw[m.end():raw.find(b'endstream', m.end())]
        try:
            streams.append(zlib.decompress(chunk))
        except zlib.error:
            pass                      # not a content stream (or not Flate)
    if not streams:
        raise SystemExit('no decompressable stream')

    for bad in ('Do', 'Tj', 'TJ', 'W', 'W*', 'cm', 'sh'):
        if re.search(r'(?<![\w*])%s(?![\w*])' % re.escape(bad),
                     max(streams, key=len).decode('latin-1')):
            raise SystemExit('unsupported operator %r — this converter only '
                             'handles solid-filled paths' % bad)

    def num(v):
        s = ('%.*f' % (precision, float(v))).rstrip('0').rstrip('.')
        return s or '0'

    paths, pend, args, colour = [], [], [], (0.0, 0.0, 0.0)
    for tok in max(streams, key=len).decode('latin-1').split():
        if re.fullmatch(r'-?\d*\.?\d+', tok):
            args.append(tok)
            continue                  # operands accumulate until an operator
        if tok == 'rg':
            colour = tuple(float(v) for v in args[-3:])
        elif tok in PATH_OPS:
            pend.append(PATH_OPS[tok] + ' '.join(num(v) for v in args[-ARITY[tok]:]))
        elif tok == 'h':
            pend.append('Z')
        elif tok in ('f', 'f*', 'b', 'b*', 'B', 'B*'):
            if pend:
                paths.append((''.join(pend), colour, tok.endswith('*')))
            pend = []
        elif tok == 'n':
            pend = []
        args = []

    if not paths:
        raise SystemExit('no filled paths found')

    def shapes():
        for d, (r, g, b), eo in paths:
            hexcol = '#%02x%02x%02x' % tuple(round(c * 255) for c in (r, g, b))
            rule = ' fill-rule="evenodd"' if eo else ''
            yield '<path fill="%s"%s d="%s"/>' % (hexcol, rule, d)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s">'
           '<g transform="translate(%s,%s) scale(1,-1)">%s</g></svg>'
           % (num(w), num(h), num(-x0), num(y1), ''.join(shapes())))
    open(dst, 'w', encoding='utf-8').write(svg)
    print('%s  %s  %d paths  %d bytes' % (dst, '%sx%s' % (num(w), num(h)), len(paths), len(svg)))


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
