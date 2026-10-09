# minimal TrueType advance-width reader: cmap(format 4/12) + hhea + hmtx + head
import struct
class TTF:
    def __init__(self, data):
        self.d=data; n=struct.unpack('>H',data[4:6])[0]; self.t={}
        for i in range(n):
            tag,_,off,ln=struct.unpack('>4sIII',data[12+16*i:28+16*i]); self.t[tag.decode('latin1')]=(off,ln)
        off,_=self.t['head']; self.upem=struct.unpack('>H',data[off+18:off+20])[0]
        off,_=self.t['hhea']; nhm=struct.unpack('>H',data[off+34:off+36])[0]
        off,_=self.t['hmtx']; self.adv=[struct.unpack('>H',data[off+4*i:off+4*i+2])[0] for i in range(nhm)]
        self.cmap=self._cmap()
    def _cmap(self):
        off,_=self.t['cmap']; n=struct.unpack('>H',self.d[off+2:off+4])[0]; best=None
        for i in range(n):
            pid,eid,so=struct.unpack('>HHI',self.d[off+4+8*i:off+12+8*i]); fmt=struct.unpack('>H',self.d[off+so:off+so+2])[0]
            if fmt in (4,12) and (best is None or (pid==3 and eid in (1,10))): best=(off+so,fmt)
        m={}
        if best is None: return m
        so,fmt=best; d=self.d
        if fmt==4:
            segx2=struct.unpack('>H',d[so+6:so+8])[0]; seg=segx2//2
            ends=struct.unpack('>%dH'%seg,d[so+14:so+14+segx2]); starts=struct.unpack('>%dH'%seg,d[so+16+segx2:so+16+2*segx2])
            deltas=struct.unpack('>%dh'%seg,d[so+16+2*segx2:so+16+3*segx2]); rob=so+16+3*segx2; ros=struct.unpack('>%dH'%seg,d[rob:rob+segx2])
            for i in range(seg):
                for c in range(starts[i],min(ends[i],0xFFFE)+1):
                    if ros[i]==0: g=(c+deltas[i])&0xFFFF
                    else:
                        ga=rob+2*i+ros[i]+2*(c-starts[i]); g=struct.unpack('>H',d[ga:ga+2])[0]
                        if g: g=(g+deltas[i])&0xFFFF
                    if g: m[c]=g
        else:
            ng=struct.unpack('>I',d[so+12:so+16])[0]
            for i in range(ng):
                s,e,g=struct.unpack('>III',d[so+16+12*i:so+28+12*i])
                for c in range(s,e+1): m[c]=g+(c-s)
        return m
    def width(self, ch, size):
        g=self.cmap.get(ord(ch), 0); a=self.adv[g] if g<len(self.adv) else self.adv[-1]
        return a/self.upem*size
    def text(self, s, size): return sum(self.width(c,size) for c in s)
