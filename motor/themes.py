import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

def sky(top, bot, horizon=GROUND):
    im = Image.new('RGBA', (CW, CH)); d = ImageDraw.Draw(im)
    for y in range(0, CH, 8): d.rectangle((0, y, CW, y+7), fill=lerp(top, bot, min(1, y/horizon)))
    return im

def hiphop_bg():
    rnd = random.Random(1)
    S = sky((18, 8, 40), (110, 40, 110)); d = ImageDraw.Draw(S)
    stars = [(rnd.randrange(0, CW, 2), rnd.randrange(0, 520, 2)) for _ in range(90)]
    for x, y in stars: d.rectangle((x, y, x+1, y+1), fill=(200, 190, 255))
    for yy in range(-30, 31, 2):
        w = int(math.sqrt(max(0, 30*30 - yy*yy))); d.rectangle((430-w, 190+yy, 430+w, 191+yy), fill=(245, 235, 200))
    for cx, cy, r in ((420, 182, 6), (440, 200, 4), (424, 206, 3)): d.rectangle((cx-r, cy-r, cx+r, cy+r), fill=(215, 205, 175))
    T = 1080
    far = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(far); x = 0
    while x < T:
        w = rnd.randrange(40, 90, 4); h = rnd.randrange(200, 400, 8)
        d.rectangle((x, GROUND-h, x+w, GROUND), fill=(46, 22, 74))
        for wy in range(GROUND-h+12, GROUND-10, 16):
            for wx in range(x+6, x+w-6, 12):
                if rnd.random() < 0.18: d.rectangle((wx, wy, wx+3, wy+5), fill=(120, 80, 140))
        x += w + rnd.randrange(0, 12, 4)
    mid = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(mid); x = 0
    pal = [(86, 46, 98), (70, 60, 110), (120, 52, 64), (60, 80, 110), (96, 70, 60)]
    while x < T:
        w = rnd.randrange(70, 130, 4); h = rnd.randrange(120, 300, 8); c = rnd.choice(pal)
        block(d, x, GROUND-h, w, h, c, 10, rnd)
        for wy in range(GROUND-h+14, GROUND-16, 20):
            for wx in range(x+8, x+w-10, 16):
                if rnd.random() < 0.45: d.rectangle((wx, wy, wx+7, wy+9), fill=rnd.choice([(255, 214, 90), (255, 170, 60), (255, 230, 150)]))
                else: d.rectangle((wx, wy, wx+7, wy+9), fill=dark(c, .5))
        if rnd.random() < 0.4:
            tx = x + w//2 - 12; block(d, tx, GROUND-h-26, 20, 18, (110, 80, 60), 6, rnd)
            d.rectangle((tx+2, GROUND-h-8, tx+4, GROUND-h), fill=(60,40,30)); d.rectangle((tx+16, GROUND-h-8, tx+18, GROUND-h), fill=(60,40,30))
        if rnd.random() < 0.35:
            nc = rnd.choice([(255, 60, 160), (60, 230, 255), (255, 212, 0)])
            d.rectangle((x+10, GROUND-h+30, x+w-14, GROUND-h+46), fill=nc); d.rectangle((x+14, GROUND-h+34, x+w-18, GROUND-h+42), fill=light(nc, .6))
        x += w + rnd.randrange(4, 20, 4)
    near = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(near)
    for bx in range(0, T, 24):
        noise_rect(d, (bx, GROUND, bx+24, GROUND+16), (150, 150, 160), 10, rnd, 4); d.rectangle((bx, GROUND, bx+1, GROUND+16), fill=(90, 90, 100))
    d.rectangle((0, GROUND, T, GROUND+1), fill=(200, 200, 210))
    noise_rect(d, (0, GROUND+16, T, CH), (44, 42, 52), 6, rnd, 4)
    for bx in range(0, T, 64): d.rectangle((bx, 880, bx+31, 885), fill=(230, 200, 60))
    def f(t):
        im = S.copy(); dd = ImageDraw.Draw(im)
        for k in range(8):
            x, y = stars[(int(t*3) * 7 + k*11) % len(stars)]; dd.rectangle((x-1, y-1, x+2, y+2), fill=(255, 255, 255))
        im.alpha_composite(wrapcrop(far, t*4)); im.alpha_composite(wrapcrop(mid, t*10)); im.alpha_composite(wrapcrop(near, t*30))
        return im
    return f

def flu_bg():
    rnd = random.Random(2)
    S = sky((8, 18, 36), (30, 66, 86)); d = ImageDraw.Draw(S)
    for _ in range(40):
        x, y = rnd.randrange(0, CW, 2), rnd.randrange(0, 300, 2); d.rectangle((x, y, x+1, y+1), fill=(180, 200, 230))
    T = 1080; G, Wt, V = (122, 16, 48), (235, 235, 235), (0, 110, 66)
    crowd_pal = [G, G, Wt, V, V, (230, 190, 150), (160, 110, 80), (90, 60, 40), (40, 40, 50)]
    def stands(variant):
        im = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(im); r = random.Random(5)
        d.rectangle((0, 420, T, 436), fill=(70, 74, 90)); d.rectangle((0, 436, T, 700), fill=(36, 40, 54))
        for row, y in enumerate(range(444, 692, 12)):
            for x in range(0, T, 8):
                c = r.choice(crowd_pal); jump = 2 if (variant and r.random() < 0.5) else 0
                d.rectangle((x+1, y - jump, x+6, y + 7 - jump), fill=c)
                d.rectangle((x+2, y - 4 - jump, x+5, y - 1 - jump), fill=r.choice([(230, 190, 150), (160, 110, 80), (90, 60, 40)]))
        for bx in range(20, T, 180):
            for i, c in enumerate([G, Wt, V, Wt, G]): d.rectangle((bx + i*12, 650, bx + i*12 + 11, 698), fill=c)
        d.rectangle((0, 698, T, 712), fill=(90, 90, 100))
        for bx in range(0, T, 90):
            d.rectangle((bx, 700, bx + 70, 710), fill=r.choice([(255, 255, 255), (140, 230, 170), (122, 16, 48)]))
        for tx in (140, 700):
            d.rectangle((tx, 190, tx+12, 430), fill=(110, 110, 120)); d.rectangle((tx+12, 190, tx+16, 430), fill=(70, 70, 80))
            for gx in range(0, 4):
                for gy in range(0, 3): d.rectangle((tx - 24 + gx*16, 160 + gy*12, tx - 24 + gx*16 + 13, 160 + gy*12 + 9), fill=(255, 250, 210))
        return im
    st = [stands(0), stands(1)]
    glow = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(glow)
    for tx in (140, 700):
        for k, a in ((90, 22), (64, 30), (40, 40)): d.rectangle((tx - k + 8, 176 - k//2, tx + k + 8, 176 + k//2), fill=(255, 250, 200, a))
    pitch = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(pitch)
    for i, y in enumerate(range(712, CH, 16)):
        noise_rect(d, (0, y, T, y+16), (44, 140, 62) if i % 2 else (56, 158, 74), 6, rnd, 4)
    d.rectangle((0, GROUND, T, GROUND+3), fill=(240, 240, 240))
    def f(t):
        im = S.copy()
        im.alpha_composite(wrapcrop(st[int(t*100/60*2) % 2], t*6)); im.alpha_composite(wrapcrop(glow, t*6))
        im.alpha_composite(wrapcrop(pitch, t*20))
        return im
    return f

def inventor_bg():
    rnd = random.Random(3)
    S = sky((70, 160, 240), (200, 235, 255)); d = ImageDraw.Draw(S)
    sx, sy = 430, 110
    d.rectangle((sx-22, sy-22, sx+22, sy+22), fill=(255, 230, 90)); d.rectangle((sx-16, sy-16, sx+16, sy+16), fill=(255, 245, 160))
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        for r in (32, 40): d.rectangle((q(sx+dx*r)-3, q(sy+dy*r)-3, q(sx+dx*r)+3, q(sy+dy*r)+3), fill=(255, 225, 100))
    T = 1080
    def clouds(seed, n, ys, sc):
        im = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(im); r = random.Random(seed)
        for _ in range(n):
            x = r.randrange(0, T-160, 4); y = r.randrange(*ys, 4); w = q(r.randrange(60, 140)*sc, 4); h = q(r.randrange(18, 34)*sc, 4)
            d.rectangle((x, y, x+w, y+h), fill=(250, 252, 255)); d.rectangle((x, y+h-6, x+w, y+h), fill=(210, 222, 238))
            d.rectangle((x+8, y-8, x+w-16, y), fill=(255, 255, 255))
        return im
    cA = clouds(11, 7, (160, 420), 0.7); cB = clouds(12, 5, (200, 560), 1.2)
    hills = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(hills); x = 0
    while x < T:
        w = rnd.randrange(100, 220, 8); h = rnd.randrange(60, 140, 8)
        for k in range(0, h, 16):
            inset = k * w // (2*h); d.rectangle((x + inset, 700 - k - 16, x + w - inset, 700 - k), fill=(130, 180, 200))
        x += w - 20
    d.rectangle((0, 700, T, GROUND), fill=(130, 180, 200))
    mid = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(mid); x = 0
    while x < T:
        w = rnd.randrange(50, 90, 4); h = rnd.randrange(50, 100, 4)
        if 620 < x < 820: x += w; continue
        block(d, x, GROUND - h, w, h, (232, 216, 180), 8, rnd)
        d.rectangle((x - 2, GROUND - h - 14, x + w + 2, GROUND - h), fill=(96, 106, 128))
        for wy in range(GROUND - h + 10, GROUND - 12, 16):
            for wx in range(x + 6, x + w - 8, 12): d.rectangle((wx, wy, wx+5, wy+8), fill=(70, 80, 110))
        x += w + 6
    ex = 720; tc = (112, 92, 70)
    for yy in range(GROUND - 340, GROUND, 4):
        k = (GROUND - yy) / 340
        half = int(70 * (1 - k)**2.2 + 4)
        d.rectangle((ex - half, yy, ex + half, yy + 3), fill=tc)
        d.rectangle((ex + half - 3, yy, ex + half, yy + 3), fill=dark(tc, .7))
    for yy in range(GROUND - 60, GROUND, 4):
        k = (yy - (GROUND - 60)) / 60; aw = int(40 * math.sqrt(max(0, k)))
        d.rectangle((ex - aw, yy, ex + aw, yy + 3), fill=(0,0,0,0))
    for py in (GROUND - 120, GROUND - 230): 
        half = int(70 * (1 - (GROUND - py)/340)**2.2 + 4) + 8
        d.rectangle((ex - half, py, ex + half, py + 8), fill=dark(tc, .8))
    d.rectangle((ex - 2, GROUND - 360, ex + 1, GROUND - 340), fill=tc)
    near = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(near)
    d.rectangle((0, GROUND, T, GROUND + 4), fill=(140, 220, 100)); noise_rect(d, (0, GROUND + 4, T, GROUND + 20), (88, 178, 64), 10, rnd, 4)
    noise_rect(d, (0, GROUND + 20, T, CH), (126, 88, 56), 10, rnd, 4)
    for _ in range(140):
        sx2, sy2 = rnd.randrange(0, T, 4), rnd.randrange(GROUND + 28, CH, 4); d.rectangle((sx2, sy2, sx2 + 7, sy2 + 3), fill=(120, 116, 112))
    for _ in range(70):
        fx = rnd.randrange(0, T, 4); c = rnd.choice([(255, 70, 70), (255, 220, 60), (255, 255, 255), (200, 120, 255)])
        d.rectangle((fx, GROUND - 6, fx + 1, GROUND), fill=(60, 140, 50)); d.rectangle((fx - 2, GROUND - 10, fx + 3, GROUND - 6), fill=c)
    def f(t):
        im = S.copy()
        im.alpha_composite(wrapcrop(cA, t*5)); im.alpha_composite(wrapcrop(hills, t*3)); im.alpha_composite(wrapcrop(cB, t*12))
        im.alpha_composite(wrapcrop(mid, t*9)); im.alpha_composite(wrapcrop(near, t*26))
        return im
    return f

Y = (255, 212, 0); FLU = (120, 230, 160); OR = (255, 140, 40)
THEMES = {
 'hiphop': dict(acc=Y, kick=(255, 120, 200), panel=(14, 8, 28, 205), border=(255, 212, 0), mascot=(160, 90, 220), accessory='cap', bpm=90, ped=(110, 70, 140), label='DIA MUNDIAL DO HIP HOP', bg=None),
 'flu': dict(acc=FLU, kick=(255, 255, 255), panel=(30, 6, 18, 210), border=(140, 230, 170), mascot=(150, 30, 60), accessory='headband', bpm=100, ped=(0, 97, 60), label='DIA DO FLUMINENSE', bg=None),
 'inventor': dict(acc=OR, kick=(20, 50, 100), panel=(14, 30, 60, 205), border=(255, 255, 255), mascot=(80, 150, 230), accessory='goggles', brand=(20, 40, 80), bpm=108, ped=(90, 170, 60), label='DIA NACIONAL DO INVENTOR', bg=None),
}
BG = {'hiphop': hiphop_bg, 'flu': flu_bg, 'inventor': inventor_bg}


def generic_bg(cfg):
    rnd = random.Random(9)
    S = sky(tuple(cfg['sky_top']), tuple(cfg['sky_bot'])); T = 1080
    def clouds(seed, n, ys, sc):
        im = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(im); r = random.Random(seed)
        for _ in range(n):
            x = r.randrange(0, T-160, 4); y = r.randrange(*ys, 4); w = q(r.randrange(60, 140)*sc, 4); h = q(r.randrange(18, 34)*sc, 4)
            d.rectangle((x, y, x+w, y+h), fill=(250, 252, 255, 220)); d.rectangle((x, y+h-6, x+w, y+h), fill=(210, 222, 238, 220))
        return im
    cA = clouds(21, 7, (120, 420), 0.8)
    hills = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(hills); x = 0
    hc = tuple(cfg.get('hills', (120, 160, 190)))
    while x < T:
        w = rnd.randrange(100, 220, 8); h = rnd.randrange(80, 200, 8)
        for k in range(0, h, 16):
            inset = k * w // (2*h); d.rectangle((x + inset, GROUND - k - 16, x + w - inset, GROUND - k), fill=hc)
        x += w - 20
    near = Image.new('RGBA', (T, CH), (0,0,0,0)); d = ImageDraw.Draw(near)
    gc = tuple(cfg.get('ground', (88, 178, 64)))
    d.rectangle((0, GROUND, T, GROUND + 4), fill=light(gc, .3)); noise_rect(d, (0, GROUND + 4, T, GROUND + 20), gc, 10, rnd, 4)
    noise_rect(d, (0, GROUND + 20, T, CH), dark(gc, .55), 10, rnd, 4)
    def f(t):
        im = S.copy(); im.alpha_composite(wrapcrop(cA, t*6)); im.alpha_composite(wrapcrop(hills, t*4)); im.alpha_composite(wrapcrop(near, t*24))
        return im
    return f
