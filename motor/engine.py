import math, random, json, os, sys, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CW, CH, SC, FPS = 540, 960, 2, 30
GROUND = 760
FD = os.environ.get('HDQ_FONTS', os.path.expanduser('~/.hdq/fonts')) + '/'
WORK = os.environ.get('HDQ_WORK', 'work')
PIX = FD + 'jersey-10-latin-400-normal.woff'
PS2 = FD + 'press-start-2p-latin-400-normal.woff'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

@functools.lru_cache(None)
def font(p, s): return ImageFont.truetype(p, s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def q(v, step=2): return int(round(v / step) * step)
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(len(a)))
def dark(c, k=0.6): return tuple(int(v*k) for v in c[:3])
def light(c, k=0.35): return tuple(int(v + (255-v)*k) for v in c[:3])

EVENTS = []
def ev(kind, t, **kw): EVENTS.append(dict(kind=kind, t=round(t, 3), **kw))

# ---------- pixel helpers ----------
def wrapcrop(img, off, w=CW):
    off = int(off) % img.width
    if off + w <= img.width: return img.crop((off, 0, off + w, img.height))
    a = img.crop((off, 0, img.width, img.height)); b = img.crop((0, 0, w - a.width, img.height))
    out = Image.new('RGBA', (w, img.height)); out.paste(a, (0, 0)); out.paste(b, (a.width, 0)); return out

def noise_rect(d, box, base, amt=12, rnd=None, step=2):
    rnd = rnd or random
    x0, y0, x1, y1 = box
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            k = rnd.randint(-amt, amt)
            d.rectangle((x, y, x+step-1, y+step-1), fill=tuple(clamp_c(v+k) for v in base[:3]))
def clamp_c(v): return max(0, min(255, int(v)))

def block(d, x, y, w, h, c, depth=8, rnd=None, tex=True):
    """front face + top + right side (voxel look)"""
    top = light(c, 0.25); side = dark(c, 0.7)
    d.polygon([(x, y), (x+depth, y-depth), (x+w+depth, y-depth), (x+w, y)], fill=top)
    d.polygon([(x+w, y), (x+w+depth, y-depth), (x+w+depth, y+h-depth), (x+w, y+h)], fill=side)
    if tex: noise_rect(d, (x, y, x+w, y+h), c, 8, rnd, 4)
    else: d.rectangle((x, y, x+w-1, y+h-1), fill=c)

@functools.lru_cache(None)
def pix_emoji(ch, size, base=16):
    im = Image.new('RGBA', (160, 160), (0,0,0,0))
    ImageDraw.Draw(im).text((80, 80), ch, font=font(EMO, 109), embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox())
    s = base / max(im.size)
    sm = im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.BOX)
    a = np.array(sm); a[..., 3] = np.where(a[..., 3] > 110, 255, 0); sm = Image.fromarray(a)
    out = Image.new('RGBA', (sm.width+2, sm.height+2), (0,0,0,0))
    sil = Image.new('RGBA', sm.size, (20,16,30,255)); m = sm.getchannel('A')
    for dx, dy in ((0,1),(2,1),(1,0),(1,2)): out.paste(sil, (dx, dy), m)
    out.alpha_composite(sm, (1, 1))
    k = size // base
    return out.resize((out.width*k, out.height*k), Image.NEAREST)

def ptext(d, xy, s, f, fill, shadow=(20,16,30), off=2):
    d.text((xy[0]+off, xy[1]+off), s, font=f, fill=shadow)
    d.text(xy, s, font=f, fill=fill)

def parse_rich(text, base, acc):
    out = []; on = False
    for w in text.split(' '):
        ww = w
        if ww.startswith('*'): ww = ww[1:]; on = True
        c = acc if on else base
        if '*' in ww: ww = ww.replace('*', ''); on = False
        out.append((ww, c))
    return out

def layout_lines(text, f, maxw, base, acc):
    words = parse_rich(text, base, acc); sp = f.getlength(' ')
    lines = []; cur = []; cw = 0
    for w, c in words:
        wl = f.getlength(w)
        if cur and cw + sp + wl > maxw: lines.append((cur, cw)); cur = []; cw = 0
        cw += (sp if cur else 0) + wl; cur.append((w, c, wl))
    if cur: lines.append((cur, cw))
    res = []
    for ws, cw in lines:
        chars = []; x = 0
        for i, (w, c, wl) in enumerate(ws):
            for chn in w: chars.append((chn, x, c)); x += f.getlength(chn)
            if i < len(ws)-1: chars.append((' ', x, c)); x += sp
        res.append((chars, cw))
    return res

# ---------- items ----------
class Item:
    h = 0; start = 0.0; end = 0.0
    def draw(self, cv, d, tl): pass

class Kicker(Item):
    def __init__(s, text, th): s.text = text; s.th = th; s.f = font(PIX, 34); s.h = 36; s.dur = 0.25
    def draw(s, cv, d, tl):
        p = (tl - s.start) / 0.25
        if p < 0: return
        n = int(len(s.text) * clamp(p*1.0))
        w = s.f.getlength(s.text)
        ptext(d, (q((CW - w)/2), s.y), s.text[:n], s.f, s.th['kick'])

class Title(Item):
    def __init__(s, text, th):
        s.text = text; s.th = th
        size = 48
        while size > 16 and font(PS2, size).getlength(text) > 470: size -= 8
        s.size = size; s.f = font(PS2, size); s.h = size + 20; s.dur = 0.55 + 0.05*len(text)
    def setup(s):
        ev('thud', s.start + 0.05*len(s.text) + 0.3); ev('title', s.start + 0.05*len(s.text) + 0.3, text=s.text)
        rnd = random.Random(hash(s.text) & 0xffff)
        s.parts = [(rnd.uniform(-1, 1)*4, -rnd.uniform(3, 7), rnd.choice([s.th['acc'], (255,255,255), light(s.th['acc'], .5)]), rnd.uniform(0, CW)) for _ in range(18)]
    def draw(s, cv, d, tl):
        t0 = tl - s.start
        if t0 < 0: return
        w = s.f.getlength(s.text); x = (CW - w) / 2
        for i, ch in enumerate(s.text):
            lt = t0 - i*0.05
            if lt < 0: continue
            p = clamp(lt / 0.3)
            dy = -140*(1-p)**2 if p < 1 else -abs(math.sin(min(lt-0.3, 0.3)*math.pi/0.3))*8*(1 - clamp((lt-0.3)/0.3))
            cx = x + s.f.getlength(s.text[:i]); cy = s.y + q(dy)
            for k in range(5, 0, -1):
                d.text((cx + k, cy + k), ch, font=s.f, fill=dark(s.th['acc'], 0.45 if k > 1 else 0.3))
            d.text((cx, cy), ch, font=s.f, fill=s.th['acc'])
        land = t0 - (0.05*len(s.text) + 0.3)
        if 0 <= land < 0.8:
            for vx, vy, c, px in s.parts:
                tt = land
                xx = px*0.6 + CW*0.2 + vx*tt*60; yy = s.y + s.size/2 + vy*tt*60 + 300*tt*tt
                sz = 6 if tt < 0.4 else 4
                d.rectangle((q(xx), q(yy), q(xx)+sz, q(yy)+sz), fill=c)
    def shake(s, tl):
        land = tl - s.start - (0.05*len(s.text) + 0.3)
        if 0 <= land < 0.22: return 4 * (1 - land/0.22)
        return 0

class Hook(Item):
    """Gancho da abertura: frase grande, inteira na tela desde o primeiro quadro (sem animação de entrada).
    Palavras entre *asteriscos* ficam na cor de destaque."""
    def __init__(s, text, th):
        s.th = th; s.text = text
        size = 64
        while size > 40:
            s.f = font(PIX, size)
            s.lines = layout_lines(text, s.f, 480, (255,255,255), th['acc'])
            if len(s.lines) <= 4: break
            size -= 6
        s.size = size; s.lh = size + 4
        s.h = len(s.lines)*s.lh + 12; s.dur = 0.35
    def setup(s): ev('thud', s.start + 0.02)
    def draw(s, cv, d, tl):
        t0 = tl - s.start
        if t0 < 0: return
        bob = q(math.sin(t0*5)*3) if t0 < 2.5 else 0   # leve pulsar para não ficar parado
        for li, (chars, cw) in enumerate(s.lines):
            x0 = (CW - cw)/2; y = s.y + li*s.lh + bob
            for ch, x, c in chars:
                for k in (4, 3, 2):
                    d.text((x0 + x + k, y + k), ch, font=s.f, fill=(20,16,30))
                d.text((x0 + x, y), ch, font=s.f, fill=c)

class Panel(Item):
    def __init__(s, texts, th, maxw=440):
        s.th = th; s.f = font(PIX, 34); s.lh = 36
        s.lines = []
        for tx in texts:
            s.lines += layout_lines(tx, s.f, maxw, (255,255,255), th['acc'])
        s.nchars = sum(len(c) for c, _ in s.lines)
        s.w = 468; s.h = len(s.lines)*s.lh + 28 + 10
        s.rate = 40
    @property
    def dur(s): return 0.18 + s.nchars / s.rate
    def setup(s):
        k = 0
        for i in range(s.nchars):
            if i % 2 == 0: ev('blip', s.start + 0.18 + i/s.rate, k=k); k += 1
    def typing(s, tl): return s.start + 0.1 < tl < s.start + s.dur
    def draw(s, cv, d, tl):
        t0 = tl - s.start
        if t0 < 0: return
        p = clamp(t0/0.18); w = q(s.w*(0.3+0.7*eout(p)), 4); h = q((s.h-10)*(0.3+0.7*eout(p)), 4)
        x0 = (CW - w)//2; y0 = s.y + (s.h-10-h)//2
        ov = Image.new('RGBA', cv.size, (0,0,0,0)); od = ImageDraw.Draw(ov)
        od.rectangle((x0+6, y0+6, x0+w+6, y0+h+6), fill=(0,0,0,110))
        od.rectangle((x0+4, y0, x0+w-4, y0+h), fill=s.th['panel'])
        od.rectangle((x0, y0+4, x0+w, y0+h-4), fill=s.th['panel'])
        cv.alpha_composite(ov)
        b = s.th['border']
        d.rectangle((x0+4, y0, x0+w-4, y0+3), fill=b); d.rectangle((x0+4, y0+h-3, x0+w-4, y0+h), fill=dark(b, .7))
        d.rectangle((x0, y0+4, x0+3, y0+h-4), fill=b); d.rectangle((x0+w-3, y0+4, x0+w, y0+h-4), fill=dark(b, .7))
        d.rectangle((x0+4, y0+4, x0+7, y0+7), fill=b); d.rectangle((x0+w-7, y0+h-7, x0+w-4, y0+h-4), fill=dark(b, .7))
        if p < 1: return
        n = int((t0 - 0.18) * s.rate)
        yy = s.y + 12; shown = 0; cur = None
        for chars, cw in s.lines:
            xx = (CW - cw) / 2
            for ch, cx, c in chars:
                if shown >= n: break
                if ch != ' ':
                    d.text((xx+cx+2, yy+2), ch, font=s.f, fill=(10,8,16)); d.text((xx+cx, yy), ch, font=s.f, fill=c)
                shown += 1; cur = (xx + cx + s.f.getlength(ch), yy)
            if shown >= n: break
            yy += s.lh
        if n < s.nchars and cur and int(tl*6) % 2 == 0:
            d.rectangle((q(cur[0])+2, cur[1]+6, q(cur[0])+10, cur[1]+30), fill=s.th['acc'])

class Icons(Item):
    def __init__(s, chars, th, size=None):
        s.chars = chars; size = size or (80 if len(chars) == 1 else 64)
        s.imgs = [pix_emoji(c, size) for c in chars]; s.h = max(i.height for i in s.imgs) + 8; s.dur = 0.3 + 0.15*len(chars)
    def setup(s):
        for i in range(len(s.chars)): ev('pop', s.start + i*0.15)
    def draw(s, cv, d, tl):
        n = len(s.imgs); gap = 26; tw = sum(i.width for i in s.imgs) + gap*(n-1); x = (CW - tw)//2
        for i, im in enumerate(s.imgs):
            lt = tl - s.start - i*0.15
            if lt >= 0:
                sc = [0.5, 1.25, 1.1, 1.0][min(3, int(lt/0.06))]
                bob = q(math.sin(tl*4 + i)*3, 2)
                ii = im if sc == 1.0 else im.resize((q(im.width*sc), q(im.height*sc)), Image.NEAREST)
                cv.alpha_composite(ii, (x + (im.width - ii.width)//2, s.y + (im.height - ii.height)//2 + bob))
            x += im.width + gap

def make_vinyl(r, label, th):
    s = r*2; im = Image.new('RGBA', (s+2, s+2), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s, s), fill=(20,18,26), outline=(70,70,90), width=2)
    for rr in range(int(r*0.45), r-4, 6): d.ellipse((r-rr, r-rr, r+rr, r+rr), outline=(42,40,52), width=2)
    d.pieslice((4, 4, s-4, s-4), 300, 330, fill=(90,90,110))
    lr = int(r*0.38); d.ellipse((r-lr, r-lr, r+lr, r+lr), fill=th['acc'])
    d.text((r, r), label, font=font(PIX, 26), fill=(20,16,30), anchor='mm')
    d.rectangle((r-2, r-2, r+2, r+2), fill=(10,10,10))
    return im

class Vinyls(Item):
    def __init__(s, th, labels):
        s.th = th; s.labels = labels; s.r = 64 if len(labels) == 2 else 52
        s.v = [make_vinyl(s.r, l, th) for l in labels]; s.h = s.r*2 + 12; s.dur = 0.5
    def setup(s): ev('pop', s.start); ev('scratch', s.start + 0.6)
    def draw(s, cv, d, tl):
        lt = tl - s.start
        if lt < 0: return
        n = len(s.v); xs = [CW//2] if n == 1 else [CW//2 - 100, CW//2 + 100]
        for i, (v, x) in enumerate(zip(s.v, xs)):
            ang = -lt*240 if i == 0 else -lt*240 + 120
            ang = round(ang / 15) * 15
            im = v.rotate(ang, resample=Image.NEAREST)
            sc = clamp(lt/0.25)
            if sc < 1: im = im.resize((max(2, q(im.width*sc)), max(2, q(im.height*sc))), Image.NEAREST)
            cv.alpha_composite(im, (x - im.width//2, s.y + s.h//2 - im.height//2))
        if n == 2 and lt > 0.5:
            side = int(lt*1.5) % 2
            ax = CW//2; ay = s.y + s.h//2
            pts = [(ax-14, ay-10), (ax+6, ay-10), (ax+6, ay-18), (ax+18, ay), (ax+6, ay+18), (ax+6, ay+10), (ax-14, ay+10)]
            if side: pts = [(2*ax - px, py) for px, py in pts]
            d.polygon(pts, fill=s.th['acc'], outline=(20,16,30))

class Grid4(Item):
    def __init__(s, th):
        s.th = th; s.items = [('🎧','DJ'), ('🎤','MC'), ('🕺','BREAKING'), ('🎨','GRAFITE')]
        s.imgs = [pix_emoji(e, 80) for e, _ in s.items]; s.h = 300; s.dur = 1.6
    def setup(s):
        for i in range(4): ev('pop', s.start + i*0.35)
    def draw(s, cv, d, tl):
        f = font(PS2, 16)
        if tl >= s.start:
            ov = Image.new('RGBA', cv.size, (0,0,0,0)); ImageDraw.Draw(ov).rectangle((60, s.y - 6, CW - 60, s.y + 290), fill=s.th['panel'])
            cv.alpha_composite(ov)
        for i, (im, (_, lb)) in enumerate(zip(s.imgs, s.items)):
            lt = tl - s.start - i*0.35
            if lt < 0: continue
            cx = CW//2 + (-110 if i % 2 == 0 else 110); cy = s.y + (i//2)*150
            # pedestal block
            block(d, cx-56, cy+70, 112, 16, s.th['ped'], 6, random.Random(i), tex=False)
            sc = [0.5, 1.25, 1.1, 1.0][min(3, int(lt/0.06))]
            ii = im if sc == 1 else im.resize((q(im.width*sc), q(im.height*sc)), Image.NEAREST)
            bob = q(math.sin(tl*4+i)*3)
            cv.alpha_composite(ii, (cx - ii.width//2, cy + 36 - ii.height//2 + bob - 8))
            w = f.getlength(lb); ptext(d, (q(cx - w/2), cy + 100), lb, f, s.th['acc'])

class Stats(Item):
    def __init__(s, th, vals):  # vals: [(target, dec, label)]
        s.th = th; s.vals = vals; s.h = 150; s.dur = 1.8
    def setup(s):
        for k in range(16): ev('tick', s.start + k*0.1)
        ev('ding', s.start + 1.7)
    def draw(s, cv, d, tl):
        lt = tl - s.start
        if lt < 0: return
        n = len(s.vals)
        for i, (tg, dec, lb) in enumerate(s.vals):
            cx = CW//2 + (0 if n == 1 else (-120 if i == 0 else 120))
            p = eout(clamp((lt - i*0.2)/1.5))
            v = f'{tg*p:.{dec}f}'.replace('.', ',')
            f = font(PS2, 48 if len(v) <= 3 else 40); w = f.getlength(v)
            for k in range(5, 0, -1): d.text((cx - w/2 + k, s.y + k), v, font=f, fill=dark(s.th['acc'], .4))
            d.text((cx - w/2, s.y), v, font=f, fill=s.th['acc'])
            fl = font(PIX, 34); wl = fl.getlength(lb); ptext(d, (q(cx - wl/2), s.y + 70), lb, fl, (255,255,255))

def make_plane():
    im = Image.new('RGBA', (124, 58), (0,0,0,0)); d = ImageDraw.Draw(im)
    br = (74, 50, 30); cl = (240, 226, 190); sh = (205, 188, 150)
    d.rectangle((8, 30, 112, 33), fill=br)
    def cell(x0, y0, x1, y1, div):
        d.rectangle((x0, y0, x1, y1), fill=cl, outline=br, width=2)
        d.rectangle((x0+2, y1-6, x1-2, y1-2), fill=sh)
        for xx in div: d.rectangle((xx, y0, xx+1, y1), fill=br)
    cell(94, 20, 122, 42, [108]); cell(18, 6, 58, 52, [28, 38, 48]); d.rectangle((18, 28, 58, 29), fill=br)
    d.rectangle((70, 22, 78, 31), fill=(120, 70, 40)); d.rectangle((71, 15, 77, 21), fill=(236, 196, 160)); d.rectangle((70, 13, 78, 15), fill=(30,30,30))
    d.line((72, 33, 66, 48), fill=br, width=2); d.line((78, 33, 84, 48), fill=br, width=2)
    for cx in (66, 84): d.rectangle((cx-4, 46, cx+4, 54), fill=(40, 40, 40))
    return im

class Plane(Item):
    cy = 360
    def __init__(s, th, dur): s.th = th; s.h = 0; s.fdur = dur - 0.8; s.dur = 0.2; s.sp = make_plane()
    def setup(s): ev('engine', s.start + 0.3, dur=s.fdur)
    def draw(s, cv, d, tl):
        lt = tl - s.start
        if lt < 0: return
        x0, x1 = 60, 480; gy = GROUND
        for k in range(0, 221, 55):
            xx = q(x0 + (x1-x0)*k/220)
            d.rectangle((xx, gy+4, xx+3, gy+18), fill=(255,255,255))
            ptext(d, (xx-10, gy+22), f'{k}m', font(PIX, 24), (255,255,255))
        p = clamp(lt / s.fdur); p = p*p*(3-2*p)
        nose = -40 + (x1 + 180) * p
        lift = eout(clamp((nose - x0)/160)) * (1 - clamp((nose - x1)/140))
        alt = gy - 56 - lift*290 + q(math.sin(lt*8)*2)*lift
        cv.alpha_composite(s.sp, (q(nose - 124), q(alt)))
        if int(lt*20) % 2: d.rectangle((q(nose-124)+2, q(alt)+18, q(nose-124)+5, q(alt)+40), fill=(60,60,60))
        else: d.rectangle((q(nose-124)+2, q(alt)+26, q(nose-124)+5, q(alt)+32), fill=(60,60,60))
        dist = clamp((min(nose - 20, x1) - x0)/(x1 - x0))*220
        v = f'{int(round(dist))} M'; f = font(PS2, 48); w = f.getlength(v)
        for k in range(5, 0, -1): d.text(((CW-w)/2 + k, s.cy + k), v, font=f, fill=dark(s.th['acc'], .4))
        d.text(((CW-w)/2, s.cy), v, font=f, fill=s.th['acc'])

# ---------- mascot ----------
def mascot_base(th):
    im = Image.new('RGBA', (90, 90), (0,0,0,0)); d = ImageDraw.Draw(im); rnd = random.Random(3)
    x, y, s, dp = 10, 22, 56, 12; c = th['mascot']
    d.polygon([(x, y), (x+dp, y-dp), (x+s+dp, y-dp), (x+s, y)], fill=light(c, .3))
    d.polygon([(x+s, y), (x+s+dp, y-dp), (x+s+dp, y+s-dp), (x+s, y+s)], fill=dark(c, .65))
    noise_rect(d, (x, y, x+s, y+s), c, 10, rnd, 4)
    d.rectangle((x, y, x+s-1, y+1), fill=light(c, .45))
    acc = th['accessory']
    if acc == 'cap':
        cc = (220, 40, 60)
        d.polygon([(x, y-4), (x+dp, y-dp-6), (x+s+dp, y-dp-6), (x+s, y-4)], fill=light(cc, .2))
        d.rectangle((x, y-4, x+s, y+6), fill=cc); d.rectangle((x+s-10, y+4, x+s+18, y+8), fill=dark(cc, .7))
        d.rectangle((x+20, y-2, x+34, y+4), fill=(255, 212, 0))
    elif acc == 'headphones':
        k = (30, 30, 36); d.rectangle((x+4, y-dp-8, x+s+dp-4, y-dp-4), fill=k)
        d.rectangle((x-6, y+10, x+2, y+34), fill=k); d.rectangle((x-4, y+14, x, y+30), fill=th['acc'])
        d.rectangle((x+s+dp-2, y+2, x+s+dp+6, y+26), fill=k)
    elif acc == 'headband':
        cols = [(122, 16, 48), (240, 240, 240), (0, 97, 60)]
        for i in range(0, s, 8): d.rectangle((x+i, y+4, x+i+7, y+9), fill=cols[(i//8) % 3])
    elif acc == 'flower':
        sx, sy = x+s-8, y-dp-10
        d.rectangle((sx+3, sy+8, sx+5, sy+16), fill=(60,150,60))
        for ox, oy in ((0,4),(8,4),(4,0),(4,8)): d.rectangle((sx+ox-2, sy+oy-2, sx+ox+4, sy+oy+4), fill=(255,120,170))
        d.rectangle((sx+2, sy+2, sx+6, sy+6), fill=(255,220,60))
    elif acc == 'racehelmet':
        hc = (255, 140, 0); d.polygon([(x-2, y+4), (x+dp-2, y-dp-4), (x+s+dp+2, y-dp-4), (x+s+2, y+4)], fill=light(hc, .2))
        d.rectangle((x-2, y-2, x+s+2, y+12), fill=hc); d.rectangle((x+s, y-dp+2, x+s+dp+2, y+8), fill=dark(hc, .7))
        d.rectangle((x+8, y+2, x+s-8, y+6), fill=(250, 220, 40)); d.rectangle((x-2, y+10, x+s+2, y+12), fill=(40, 40, 50))
    elif acc == 'spartan':
        br = (205, 160, 70); d.polygon([(x-2, y+4), (x+dp-2, y-dp-4), (x+s+dp+2, y-dp-4), (x+s+2, y+4)], fill=light(br, .2))
        d.rectangle((x-2, y-2, x+s+2, y+12), fill=br); d.rectangle((x-2, y+12, x+6, y+40), fill=br); d.rectangle((x+s-6, y+12, x+s+2, y+40), fill=dark(br, .8))
        cr = (200, 30, 40)
        for i in range(0, s+dp, 4):
            hh = 22 - abs(i - (s+dp)//2)//3
            d.rectangle((x+i, y-dp-4-hh, x+i+3, y-dp-4), fill=cr if (i//4) % 2 else dark(cr, .8))
    elif acc == 'goggles':
        d.rectangle((x, y+6, x+s, y+9), fill=(90, 60, 30))
        for gx in (x+10, x+32):
            d.rectangle((gx-2, y+1, gx+14, y+14), fill=(110, 75, 40)); d.rectangle((gx+1, y+4, gx+11, y+11), fill=(150, 220, 255)); d.rectangle((gx+2, y+5, gx+5, y+7), fill=(255,255,255))
    return im

def draw_mascot(cv, d, base, th, t, talking, jump):
    x = 22; by = GROUND - 80
    bob = 2 if int(t * th['bpm'] / 60) % 2 else 0
    jy = q(-18 * math.sin(math.pi * clamp(jump/0.35))) if 0 <= jump < 0.35 else 0
    y = by + bob + jy
    cv.alpha_composite(base, (x, y))
    fx, fy = x + 10, y + 22
    blink = (t % 3.3) < 0.12
    for ex in (fx+12, fx+34):
        if blink: d.rectangle((ex, fy+24, ex+9, fy+26), fill=(20,16,30))
        else:
            d.rectangle((ex, fy+16, ex+9, fy+29), fill=(255,255,255)); d.rectangle((ex+4, fy+18, ex+9, fy+25), fill=(20,16,30))
    if talking and int(t*11) % 2 == 0:
        d.rectangle((fx+20, fy+36, fx+35, fy+45), fill=(40,10,20)); d.rectangle((fx+23, fy+42, fx+32, fy+45), fill=(230,80,90))
    elif talking: d.rectangle((fx+20, fy+38, fx+35, fy+41), fill=(40,10,20))
    else:
        d.rectangle((fx+20, fy+38, fx+35, fy+40), fill=(40,10,20)); d.rectangle((fx+18, fy+36, fx+20, fy+38), fill=(40,10,20)); d.rectangle((fx+35, fy+36, fx+37, fy+38), fill=(40,10,20))
    # shadow
    d.rectangle((x+8, GROUND - 2, x+72, GROUND + 2), fill=(0,0,0))

# ---------- card building ----------
def build_card(spec, th, dur):
    items = []; texts = []
    def flush():
        if texts: items.append(Panel(list(texts), th)); texts.clear()
    for it in spec:
        k = it[0]
        if k == 'text': texts.append(it[1]); continue
        flush()
        if k == 'hook': items.append(Hook(it[1], th))
        elif k == 'kicker': items.append(Kicker(it[1], th))
        elif k == 'title': items.append(Title(it[1], th))
        elif k == 'icons': items.append(Icons(it[1], th))
        elif k == 'special':
            nm = it[1]
            if nm == 'vinyl': items.append(Vinyls(th, ['1973']))
            elif nm == 'vinyl2': items.append(Vinyls(th, ['1', '2']))
            elif nm == 'grid4': items.append(Grid4(th))
            elif nm == 'stats': items.append(Stats(th, it[2]))
            elif nm == 'plane': items.append(Plane(th, dur))
    flush()
    # vertical layout
    gap = 16; tot = sum(i.h for i in items if i.h) + gap*(len([i for i in items if i.h])-1)
    y = max(160, (160 + 580)//2 - tot//2)
    if any(isinstance(i, Plane) for i in items): y = 180
    for i in items:
        i.y = y
        if i.h: y += i.h + gap
        if isinstance(i, Plane): i.cy = y + 30
    # timing
    panels = [i for i in items if isinstance(i, Panel)]
    fixed = sum(i.dur for i in items if not isinstance(i, Panel)) + 0.25*len(items)
    chars = sum(p.nchars for p in panels)
    if chars:
        avail = max(1.0, dur - 0.7 - fixed)
        rate = clamp(chars / (avail * 0.85), 26, 60)
        for p in panels: p.rate = rate
    t = 0.0 if items and isinstance(items[0], Hook) else 0.3   # gancho já aparece no quadro 0
    for i in items:
        i.start = t; t += i.dur + (0.12 if isinstance(i, Kicker) else 0.25)
    return items

def render_video(name, th, specs, out, tl):
    durs = [c['dur'] for c in tl['cards']]; total = tl['dur']
    EVENTS.clear()
    cards = []; c0 = 0
    for spec, du in zip(specs, durs):
        its = build_card(spec, th, du)
        for i in its:
            i.start += c0
            if hasattr(i, 'setup'): i.setup()
        cards.append((c0, du, its)); c0 += du
        if len(cards) > 1: ev('wipe', c0 - du - 0.2)
    base = mascot_base(th)
    ctx = dict(total=total, cards=cards, name=name)
    if th.get('setup'): th['setup'](ctx)
    bg = th['bg']
    n = int(round(total*FPS)); tmp = out.replace('.mp4', '.part.mp4')
    p = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{CW*SC}x{CH*SC}','-r',str(FPS),'-i','-',
                          '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p', tmp], stdin=subprocess.PIPE)
    only = os.environ.get('STILLS')
    frames = range(n) if not only else [int(float(x)*FPS) for x in only.split(',')]
    for fi in frames:
        t = fi / FPS
        ci = max(k for k, (s0, _, _) in enumerate(cards) if s0 <= t + 1e-6)
        s0, du, its = cards[ci]
        shake = max([i.shake(t) for i in its if isinstance(i, Title)] + [0])
        cv = bg(t); d = ImageDraw.Draw(cv); d.fontmode = '1'
        talking = any(isinstance(i, Panel) and i.typing(t) for i in its)
        th['mascot_fn'](cv, d, base, th, t, talking, t - s0, ci, ctx)
        for i in its: i.draw(cv, d, t)
        header(cv, d, th, t, total)
        wipe(d, th, t, [c[0] for c in cards[1:]])
        if shake:
            r = random.Random(fi); cv = cv.transform(cv.size, Image.AFFINE, (1, 0, q(r.uniform(-shake, shake)), 0, 1, q(r.uniform(-shake, shake))), Image.NEAREST)
        fr = cv.convert('RGB').resize((CW*SC, CH*SC), Image.NEAREST)
        if only: fr.save(f'{WORK}/still_{name}_{t:05.1f}.png'); continue
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    if only: os.remove(tmp) if os.path.exists(tmp) else None; return
    os.replace(tmp, out)
    json.dump(EVENTS, open(f'{WORK}/events_{name}.json', 'w'))

def header(cv, d, th, t, total):
    f = font(PIX, 26); lab = th['label']; w = int(f.getlength(lab))
    d.rectangle((26, 16, 26 + w + 24, 48), fill=th['acc']); d.rectangle((24, 18, 28 + w + 24, 46), fill=th['acc'])
    d.rectangle((26, 46, 26 + w + 24, 50), fill=dark(th['acc'], .6))
    d.text((38, 18), lab, font=f, fill=(20,16,30))
    ptext(d, (26, 56), 'HOJE É DIA DE QUÊ?', font(PIX, 22), th.get('brand', (255,255,255)))

def wipe(d, th, t, starts):
    for c0 in starts:
        p = (t - (c0 - 0.2)) / 0.4
        if not 0 <= p <= 1: continue
        S = 36; cols = CW//S + 1; rows = CH//S + 1
        for r in range(rows):
            for c in range(cols):
                o = (c + r) / (cols + rows)
                s = clamp(min((p*2 - o*0.7)/0.3, ((1-p)*2 - (1-o)*0.7)/0.3))
                if s <= 0: continue
                hs = q(S*s/2)
                cx, cy = c*S + S//2, r*S + S//2
                col = th['acc'] if (r + c) % 2 else dark(th['acc'], .75)
                d.rectangle((cx-hs, cy-hs, cx+hs, cy+hs), fill=col)
