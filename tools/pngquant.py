"""Quantize an RGBA PNG to a <=256-colour palette PNG (PLTE + tRNS) via median cut."""
import zlib, struct, sys, os
from collections import Counter

def read_rgba(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat, hdr = 8, [], None
    while i < len(data):
        ln = struct.unpack('>I', data[i:i+4])[0]
        typ = data[i+4:i+8]
        payload = data[i+8:i+8+ln]
        if typ == b'IHDR': hdr = payload
        elif typ == b'IDAT': idat.append(payload)
        i += 12 + ln
    w, h, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', hdr)
    assert depth == 8 and interlace == 0 and color in (2, 6), "need 8-bit RGB/RGBA, non-interlaced"
    raw = zlib.decompress(b''.join(idat))
    bpp = 3 if color == 2 else 4
    stride = w * bpp
    px, prev, pos = bytearray(), bytearray(stride), 0
    for _ in range(h):
        ft = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos+stride]); pos += stride
        if ft:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x-bpp] if x >= bpp else 0
                if   ft == 1: line[x] = (line[x] + a) & 0xff
                elif ft == 2: line[x] = (line[x] + b) & 0xff
                elif ft == 3: line[x] = (line[x] + ((a + b) >> 1)) & 0xff
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                    line[x] = (line[x] + (a if (pa <= pb and pa <= pc) else (b if pb <= pc else c))) & 0xff
        px += line; prev = line
    if bpp == 3:  # pad to RGBA so the quantizer sees one uniform format
        rgba = bytearray()
        for i in range(0, len(px), 3):
            rgba += px[i:i+3] + b'\xff'
        px = rgba
    return w, h, bytes(px)

def median_cut(hist, n):
    """hist: {(r,g,b,a): count}. Returns list of boxes, each a list of colours."""
    boxes = [list(hist.keys())]
    while len(boxes) < n:
        # Split the box with the largest weighted spread on its widest channel.
        target, best = None, -1
        for bi, box in enumerate(boxes):
            if len(box) < 2: continue
            weight = sum(hist[c] for c in box)
            spread = max(max(c[ch] for c in box) - min(c[ch] for c in box) for ch in range(4))
            score = spread * (weight ** 0.5)
            if score > best: best, target = score, bi
        if target is None: break
        box = boxes.pop(target)
        ch = max(range(4), key=lambda k: max(c[k] for c in box) - min(c[k] for c in box))
        box.sort(key=lambda c: c[ch])
        # Split at the weighted median so both halves carry similar pixel mass.
        total = sum(hist[c] for c in box)
        acc, cut = 0, 1
        for i, c in enumerate(box):
            acc += hist[c]
            if acc >= total / 2: cut = max(1, min(i, len(box)-1)); break
        boxes.append(box[:cut]); boxes.append(box[cut:])
    return boxes

def quantize(src, dst, ncolors=256):
    w, h, px = read_rgba(src)
    hist = Counter()
    for i in range(0, len(px), 4):
        hist[px[i:i+4]] = hist[px[i:i+4]] + 1 if False else hist[px[i:i+4]] + 1
    hist = Counter({tuple(k): v for k, v in hist.items()})
    boxes = median_cut(hist, ncolors)

    palette, lookup = [], {}
    for idx, box in enumerate(boxes):
        tw = sum(hist[c] for c in box)
        avg = tuple(round(sum(c[k] * hist[c] for c in box) / tw) for k in range(4))
        palette.append(avg)
        for c in box: lookup[c] = idx

    idx_rows = bytearray()
    prev = None
    for y in range(h):
        idx_rows.append(0)  # filter 0; palette rows rarely benefit from filtering
        base = y * w * 4
        for x in range(w):
            idx_rows.append(lookup[tuple(px[base+x*4: base+x*4+4])])

    plte = b''.join(bytes(c[:3]) for c in palette)
    trns = bytes(c[3] for c in palette)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 3, 0, 0, 0)

    def chunk(typ, payload):
        return struct.pack('>I', len(payload)) + typ + payload + \
               struct.pack('>I', zlib.crc32(typ + payload) & 0xffffffff)

    out = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'PLTE', plte)
    if any(a != 255 for a in trns):
        out += chunk(b'tRNS', trns)
    out += chunk(b'IDAT', zlib.compress(bytes(idx_rows), 9)) + chunk(b'IEND', b'')
    open(dst, 'wb').write(out)
    print(f"{os.path.basename(dst)}: {os.path.getsize(src)} -> {len(out)} bytes "
          f"({100*(os.path.getsize(src)-len(out))//os.path.getsize(src)}% smaller), "
          f"{len(hist)} unique -> {len(palette)} colours")

if __name__ == '__main__':
    quantize(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 256)
