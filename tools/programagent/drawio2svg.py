# -*- coding: utf-8 -*-
"""programagent.drawio -> an SVG fragment whose every cell is an animatable
<g class="el" data-s="a:<name>" data-bb="x,y,w,h"> in the sheet's viewBox
(1280 x 760), plus build/cells.json with each cell's box / centre / text anchor.

Text is laid out here (no foreignObject): widths come from the Liberation
fonts, which are metric-compatible with the faces the figure asks for
(Times New Roman -> Tinos / Liberation Serif, Consolas -> Liberation Mono).
"""
import xml.etree.ElementTree as ET, re, html, json, base64, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ttfw import TTF

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'programagent.drawio')
OUT = os.path.join(os.path.dirname(__file__), 'build')
os.makedirs(OUT, exist_ok=True)

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

# ── placement: figure canvas (130,420)-(840,790) -> sheet 1280 x 760 ──
FX, FY, FW, FH = 130.0, 420.0, 710.0, 370.0
VW, VH = 1280.0, 760.0
S = VW / FW                 # 1.8028
OX = -FX * S
OY = 70.0 - FY * S          # 70px of sheet above the figure for the caption

# drawio ids -> semantic names
NAME = {
    'ZRhYcM33ONwBrgHbGgT--80': 'ground',
    'ZRhYcM33ONwBrgHbGgT--42': 'handoff',   'ZRhYcM33ONwBrgHbGgT--12': 'handoff-t',
    'ZRhYcM33ONwBrgHbGgT--51': 'ws',        'ZRhYcM33ONwBrgHbGgT--56': 'ws-t',
    'ZRhYcM33ONwBrgHbGgT--69': 'rev',       'ZRhYcM33ONwBrgHbGgT--75': 'rev-t',
    'ZRhYcM33ONwBrgHbGgT--39': 'analysis',  'ZRhYcM33ONwBrgHbGgT--40': 'implement', 'ZRhYcM33ONwBrgHbGgT--41': 'review',
    'ZRhYcM33ONwBrgHbGgT--43': 'h-analysis',
    'ZRhYcM33ONwBrgHbGgT--46': 'h-impl-tab', 'ZRhYcM33ONwBrgHbGgT--44': 'h-impl',
    'ZRhYcM33ONwBrgHbGgT--47': 'h-rev-tab',  'ZRhYcM33ONwBrgHbGgT--45': 'h-rev',
    'ZRhYcM33ONwBrgHbGgT--58': 'ws-src',     'ZRhYcM33ONwBrgHbGgT--73': 'ws-build', 'ZRhYcM33ONwBrgHbGgT--66': 'ws-compile',
    'ZRhYcM33ONwBrgHbGgT--71': 'rev-1',      'ZRhYcM33ONwBrgHbGgT--74': 'rev-2',
    'ZRhYcM33ONwBrgHbGgT--34': 'arrow-ai',   'ZRhYcM33ONwBrgHbGgT--83': 'arrow-store',
    'ZRhYcM33ONwBrgHbGgT--85': 'link-top',   'ZRhYcM33ONwBrgHbGgT--86': 'link-bot',
    'ZRhYcM33ONwBrgHbGT--102': 'ic-loop',    'ZRhYcM33ONwBrgHbGT--103': 'ic-archive', 'ZRhYcM33ONwBrgHbGT--104': 'ic-copy',
    'ZRhYcM33ONwBrgHbGT--105': 'ic-code',    'ZRhYcM33ONwBrgHbGT--106': 'ic-pen-a',   'ZRhYcM33ONwBrgHbGT--107': 'ic-pen-i',
    'ZRhYcM33ONwBrgHbGT--108': 'ic-pen-r',   'ZRhYcM33ONwBrgHbGgT--94': 'ic-docs',
    'dH30lgRbw9oe3YSkKiO0-5': 'ic-prog',     'dH30lgRbw9oe3YSkKiO0-1': 'prog-t', 'dH30lgRbw9oe3YSkKiO0-2': 'docs-t',
    'dH30lgRbw9oe3YSkKiO0-11': 'docs-arrow', 'dH30lgRbw9oe3YSkKiO0-12': 'prog-arrow',
}
# Real run (psampaz/go-mod-outdated, Go) in place of the figure's generic C++ labels.
# Lines are swapped again beat by beat; these are the resting labels.
TEXT = {
    'h-analysis': ['📂 analysis-initial/', '  📄 analysis.md', '  📄 samples/ ×2'],
    'h-impl-tab': ['📁 implementation-001…4'],
    'h-impl':     ['📂 implementation-005/', '  📄 delivery.md', '  📄 build.json ✓'],
    'h-rev-tab':  ['📁 review-001…3'],
    'h-rev':      ['📂 review-004/', '  📄 review.md', '  📄 fixtures ×7'],
    'ws-src':     ['📂 workspace/', '  📑 main.go', '  📑 width.go', '  📑 go.mod'],
    'ws-build':   ['📂 internal/mod', '  📑 mod.go', '  ···'],
    'ws-compile': ['📟 compile.sh', 'go build', '→ ./executable'],
    'rev-1':      ['📂 rev-001/', '  📁 source/', '  📟 compile.sh', '  ⚙ executable ✓'],
    'rev-2':      ['📂 rev-005/', '  📁 source/', '  📟 compile.sh', '  ⚙ executable ✓', '  last-stable'],
}
MONO_FS = 12.0   # the figure's Consolas 14 is a touch wide for the real file names
# small geometry nudges so the real names fit (figure coordinates)
GEO = {
    'ws-src':   dict(x=258, w=118, y=706, h=70),
    'ws-build': dict(x=384, w=126, y=706, h=70),
    'ws-compile': dict(x=518, w=114, y=706, h=70),
    'h-analysis': dict(w=165),
    'h-impl': dict(w=180),
    'h-impl-tab': dict(w=180),
    'rev-1': dict(y=474, h=86),
    'rev-2': dict(y=662, h=108),
}

def nameOf(cid):
    for k, v in NAME.items():
        if cid.endswith(k[-5:]): return v
    return None
def style(st):
    d = {}
    for kv in (st or '').split(';'):
        if not kv: continue
        if '=' in kv: k, v = kv.split('=', 1); d[k] = v
        else: d[kv] = '1'
    return d
def label(v):
    """drawio HTML label -> (lines, fam, fs, bold, colour)"""
    v = v or ''
    fam = 'sans'
    m = re.search(r'face="([^"]+)"', v) or re.search(r'font-family:\s*([^;"]+)', v)
    if m:
        f = m.group(1)
        fam = 'mono' if 'Consolas' in f else ('serif' if 'Times' in f else 'sans')
    m = re.search(r'font-size:\s*(\d+)px', v); fs = float(m.group(1)) if m else 12.0
    bold = '<b' in v
    m = re.search(r'color:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)', v)
    col = '#%02X%02X%02X' % tuple(int(x) for x in m.groups()) if m else '#000000'
    v = re.sub(r'<br\s*/?>', '\n', v); v = re.sub(r'</div>', '\n', v); v = re.sub(r'<[^>]+>', '', v)
    v = html.unescape(v).replace('\xa0', ' ')
    lines = [ln.rstrip() for ln in v.split('\n')]
    while lines and not lines[-1].strip(): lines.pop()
    while lines and not lines[0].strip(): lines.pop(0)
    return lines, fam, fs, bold, col
def esc(s): return html.escape(s, quote=True)
def T(x, y): return (x * S + OX, y * S + OY)

root = ET.parse(SRC).getroot()
cells = {c.get('id'): c for c in root.iter('mxCell') if c.get('id') not in ('0', '1')}
geo = {}
for cid, c in cells.items():
    g = c.find('mxGeometry')
    if c.get('vertex'):
        d = dict(x=float(g.get('x') or 0), y=float(g.get('y') or 0), w=float(g.get('width') or 0), h=float(g.get('height') or 0))
        d.update(GEO.get(nameOf(cid) or '', {}))
        geo[cid] = d
def port(cid, fx, fy):
    d = geo[cid]; return (d['x'] + d['w'] * fx, d['y'] + d['h'] * fy)

out = []; meta = {}
for cid, c in cells.items():
    name = nameOf(cid)
    if not name: print('unnamed cell', cid, file=sys.stderr); continue
    st = style(c.get('style')); body = []
    if c.get('vertex'):
        d = geo[cid]; x, y, w, h = d['x'], d['y'], d['w'], d['h']
        if st.get('shape') == 'image':
            img = re.search(r'image=([^;]+)', c.get('style')).group(1)
            href = 'data:image/svg+xml;base64,' + img[len('data:image/svg+xml,'):] if img.startswith('data:image/svg+xml,') else img
            body.append('<image x="%.2f" y="%.2f" width="%.2f" height="%.2f" href="%s" preserveAspectRatio="xMidYMid meet"/>' % (x, y, w, h, href))
        elif st.get('text') == '1':
            pass
        else:
            fill = st.get('fillColor', '#ffffff'); stroke = st.get('strokeColor', '#000000'); sw = float(st.get('strokeWidth', '1'))
            r = 0.15 * min(w, h) if st.get('rounded') == '1' else 0
            a = ['fill="%s"' % (fill if fill != 'none' else 'none')]
            if stroke != 'none': a.append('stroke="%s" stroke-width="%.2f"' % (stroke, sw))
            if st.get('dashed') == '1': a.append('stroke-dasharray="%s"' % ('8 6' if sw >= 3 else '5 4'))
            body.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" %s/>' % (x, y, w, h, r, ' '.join(a)))
        lines, fam, fs, bold, col = label(c.get('value'))
        if name in TEXT: lines = TEXT[name]; fs = MONO_FS if fam == 'mono' else fs
        if lines:
            al = st.get('align', 'center'); va = st.get('verticalAlign', 'middle')
            sp = float(st.get('spacing', '2')); padL = sp + float(st.get('spacingLeft', '0')); padR = sp + float(st.get('spacingRight', '0'))
            lh = fs * 1.2; n = len(lines)
            if va == 'top': y0 = y + sp + fs * 0.85
            elif va == 'bottom': y0 = y + h - sp - (n - 1) * lh - fs * 0.25
            else: y0 = y + (h - n * lh) / 2 + fs * 0.85
            if al == 'left': tx = x + padL + 2; anchor = 'start'
            elif al == 'right': tx = x + w - padR - 2; anchor = 'end'
            else: tx = x + (padL + w - padR) / 2; anchor = 'middle'
            attrs = 'font-family="%s" font-size="%.1f" fill="%s" text-anchor="%s"%s xml:space="preserve"' % (
                FAMILY[fam], fs, col, anchor, ' font-weight="700"' if bold else (' font-weight="600"' if fam == 'sans' else ''))
            for ln in lines:
                tw = measure(ln, fam, bold, fs)
                if tw > w - padL - padR + 4: print('  ! %s: "%s" is %.0f wide in a %.0f box' % (name, ln, tw, w - padL - padR), file=sys.stderr)
            body.append('<text %s data-box="%.2f,%.2f,%.2f,%.2f" data-tx="%.2f" data-lh="%.2f">%s</text>' % (
                attrs, x, y, w, h, tx, lh, ''.join('<tspan x="%.2f" y="%.2f">%s</tspan>' % (tx, y0 + k * lh, esc(ln)) for k, ln in enumerate(lines))))
            tw = max(measure(ln, fam, bold, fs) for ln in lines)
            cx = tx + tw / 2 if anchor == 'start' else (tx - tw / 2 if anchor == 'end' else tx)
            cy = y0 + (n - 1) * lh / 2 - fs * 0.33
            meta.setdefault(name, {})['tc'] = [round(v, 1) for v in T(cx, cy)]
        bb = [x, y, x + w, y + h]
    elif c.get('edge'):
        g = c.find('mxGeometry')
        src, tgt = c.get('source'), c.get('target')
        sp = g.find("mxPoint[@as='sourcePoint']"); tp = g.find("mxPoint[@as='targetPoint']")
        p0 = port(src, float(st.get('exitX', 0.5)), float(st.get('exitY', 0.5))) if src else (float(sp.get('x')), float(sp.get('y')))
        p1 = port(tgt, float(st.get('entryX', 0.5)), float(st.get('entryY', 0.5))) if tgt else (float(tp.get('x')), float(tp.get('y')))
        mid = [(float(p.get('x')), float(p.get('y'))) for p in g.findall('Array/mxPoint')]
        if st.get('edgeStyle') == 'orthogonalEdgeStyle' and not mid:
            xm = (p0[0] + p1[0]) / 2; mid = [(xm, p0[1]), (xm, p1[1])]
        pts = [p0] + mid + [p1]
        stroke = st.get('strokeColor', '#000000'); stroke = '#000000' if stroke == 'default' else stroke
        sw = float(st.get('strokeWidth', '1'))
        if st.get('shape') == 'flexArrow':
            (ax, ay), (bx, by) = pts[0], pts[-1]
            L = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5; ux, uy = (bx - ax) / L, (by - ay) / L; nx, ny = -uy, ux
            hw, hh, hl = 4.0, 9.0, 11.0      # shaft half-width, head half-width, head length
            hx, hy = bx - ux * hl, by - uy * hl
            poly = [(ax + nx * hw, ay + ny * hw), (hx + nx * hw, hy + ny * hw), (hx + nx * hh, hy + ny * hh), (bx, by),
                    (hx - nx * hh, hy - ny * hh), (hx - nx * hw, hy - ny * hw), (ax - nx * hw, ay - ny * hw)]
            body.append('<polygon points="%s" fill="%s"/>' % (' '.join('%.2f,%.2f' % p for p in poly), st.get('fillColor', '#34383B')))
        else:
            a = ['fill="none"', 'stroke="%s"' % stroke, 'stroke-width="%.2f"' % sw, 'stroke-linejoin="round"']
            if st.get('dashed') == '1': a.append('stroke-dasharray="%s"' % ('1.5 3' if st.get('dashPattern') else '6 4'))
            if st.get('endArrow', 'classic') != 'none': a.append('marker-end="url(#aarrow-%s)"' % stroke.lstrip('#'))
            body.append('<polyline points="%s" %s/>' % (' '.join('%.2f,%.2f' % p for p in pts), ' '.join(a)))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; bb = [min(xs), min(ys), max(xs), max(ys)]
        meta.setdefault(name, {})['pts'] = [[round(v, 1) for v in T(*p)] for p in pts]
    else:
        continue
    sb = list(T(bb[0], bb[1])) + list(T(bb[2], bb[3]))
    m = meta.setdefault(name, {})
    m['bb'] = [round(v, 1) for v in sb]; m['c'] = [round((sb[0] + sb[2]) / 2, 1), round((sb[1] + sb[3]) / 2, 1)]
    out.append('<g class="el" data-s="a:%s" data-bb="%.1f,%.1f,%.1f,%.1f">%s</g>' % (name, sb[0], sb[1], sb[2] - sb[0], sb[3] - sb[1], ''.join(body)))

# draw order: ground, regions, then everything else as in the file (file order already has regions first)
cols = sorted(set(re.findall(r'aarrow-([0-9A-Fa-f]{6})', '\n'.join(out))))
defs = ''.join('<marker id="aarrow-%s" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#%s"/></marker>' % (c, c) for c in cols)
frag = '<g id="afig" transform="translate(%.3f %.3f) scale(%.5f)">%s%s</g>' % (OX, OY, S, defs, ''.join(out))
ET.fromstring(frag)
open(os.path.join(OUT, 'fig.svgfrag'), 'w', encoding='utf-8').write(frag)
json.dump({'meta': meta, 'S': S, 'OX': OX, 'OY': OY, 'VW': VW, 'VH': VH}, open(os.path.join(OUT, 'cells.json'), 'w'), indent=0)
prev = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="1280"><rect width="100%%" height="100%%" fill="#fff"/>%s</svg>'
        % (VW, VH, frag))
open(os.path.join(OUT, 'preview.svg'), 'w', encoding='utf-8').write(prev)
print('cells %d | frag %.0f KB | S=%.4f OX=%.1f OY=%.1f' % (len(out), len(frag) / 1024, S, OX, OY))
