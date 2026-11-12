import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

def face_sprite(base, t, talking):
    im = base.copy(); d = ImageDraw.Draw(im)
    fx, fy = 20, 44
    blink = (t % 3.3) < 0.12
    for ex in (fx+12, fx+34):
        if blink: d.rectangle((ex, fy+2, ex+9, fy+4), fill=(20,16,30))
        else: d.rectangle((ex, fy-6, ex+9, fy+7), fill=(255,255,255)); d.rectangle((ex+4, fy-4, ex+9, fy+3), fill=(20,16,30))
    if talking and int(t*11) % 2 == 0:
        d.rectangle((fx+20, fy+14, fx+35, fy+23), fill=(40,10,20)); d.rectangle((fx+23, fy+20, fx+32, fy+23), fill=(230,80,90))
    elif talking: d.rectangle((fx+20, fy+16, fx+35, fy+19), fill=(40,10,20))
    else:
        d.rectangle((fx+20, fy+16, fx+35, fy+18), fill=(40,10,20)); d.rectangle((fx+18, fy+14, fx+20, fy+16), fill=(40,10,20)); d.rectangle((fx+35, fy+14, fx+37, fy+16), fill=(40,10,20))
    return im

MX = 22
G = 230
LW, LH = 270, 240
def place(cv, d, spr, x, y, ang=0):
    if ang:
        big = Image.new('RGBA', (130, 130), (0,0,0,0)); big.alpha_composite(spr, (20, 20))
        big = big.rotate(ang, resample=Image.NEAREST); cv.alpha_composite(big, (x-20, y-20))
    else: cv.alpha_composite(spr, (x, y))
    d.rectangle((x+8, G-2, x+72, G+2), fill=(0,0,0))

def jumpoff(jump): return q(-18*math.sin(math.pi*clamp(jump/0.35))) if 0 <= jump < 0.35 else 0

# ---------- HIP HOP ----------
def _hiphop_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    bx, by = 112, G-44
    block(d, bx, by, 76, 44, (52, 52, 62), 6, tex=False)
    d.rectangle((bx+16, by-16, bx+60, by-12), fill=(30,30,36)); d.rectangle((bx+16, by-16, bx+20, by-6), fill=(30,30,36)); d.rectangle((bx+56, by-16, bx+60, by-6), fill=(30,30,36))
    pr = 15 if (beat % 1) < 0.25 else 12
    for cx in (bx+19, bx+57):
        d.rectangle((cx-pr, by+24-pr, cx+pr, by+24+pr), fill=(20,20,24)); d.rectangle((cx-pr+4, by+24-pr+4, cx+pr-4, by+24+pr-4), fill=(90,90,100)); d.rectangle((cx-3, by+21, cx+3, by+27), fill=th['acc'])
    d.rectangle((bx+31, by+6, bx+45, by+12), fill=th['acc'] if int(beat*2) % 2 else (255, 120, 200))
    for k in range(3):
        ph = (beat/2 + k/3) % 1
        if ph > 0.85: continue
        nx = q(bx + 30 + math.sin((beat/2 + k)*3)*14); ny = q(by - 20 - ph*50)
        col = [th['acc'], (255, 120, 200), (120, 220, 255)][k]
        d.rectangle((nx, ny, nx+5, ny+4), fill=col); d.rectangle((nx+4, ny-12, nx+5, ny), fill=col); d.rectangle((nx+5, ny-12, nx+9, ny-10), fill=col)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + jumpoff(jump)
    if ci % 3 == 1:
        cyc = t % 2.4
        if cyc < 1.8: ang = (int(cyc*16) * 45) % 360; hop = q(-abs(math.sin(cyc*math.pi*4))*8)
        else: ang = 90; hop = -4
        place(cv, d, spr, MX, y0 + hop, ang)
    else:
        nod = 4 if (beat % 1) < 0.3 else 0
        place(cv, d, spr, MX, y0 + nod)
        mx, my = MX + 70, y0 + nod + 56
        d.rectangle((mx-2, my+6, mx+3, my+22), fill=(30,30,36)); d.rectangle((mx-6, my-6, mx+7, my+7), fill=(170,170,180))
        for gx in range(-4, 6, 4):
            for gy in range(-4, 6, 4): d.rectangle((mx+gx, my+gy, mx+gx+1, my+gy+1), fill=(90,90,100))

def hiphop_setup(ctx): pass

# ---------- FLU ----------
CELEB = ('GOOOL!', '1 X 0', 'CARRASCO')
def flu_setup(ctx):
    wins = []
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in CELEB:
                wins.append((i.start + 0.05*len(i.text) + 0.3, s0 + du))
    ctx['celeb'] = wins
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1:
        tt = k*P
        if not any(a <= tt < b for a, b in wins): ev('tap', tt)
        k += 1
    ev('whistle', 0.3)

def _flu_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    celeb = any(a <= t < b for a, b in ctx['celeb'])
    spr = face_sprite(base, t, True if celeb else talking)
    y0 = G - 80
    if celeb:
        hop = q(-abs(math.sin(t*math.pi*3))*34)
        place(cv, d, spr, MX, y0 + hop)
        r = random.Random(7); d = md
        for k in range(46):
            sp = r.uniform(60, 140); x0 = r.uniform(0, CW); ph = r.uniform(0, 8)
            yy = ((t*sp + ph*100) % (CH + 40)) - 40; xx = x0 + math.sin(t*3 + k)*10
            col = [(122, 16, 48), (240, 240, 240), (0, 120, 70)][k % 3]
            d.rectangle((q(xx), q(yy), q(xx)+5, q(yy)+3 + (k % 2)*2), fill=col)
        return
    P = 60/th['bpm']; nb = t/P; u = nb % 1; k = int(nb)
    H = 58 if k % 4 == 3 else 38
    squash = 3 if u < 0.08 else 0
    place(cv, d, spr, MX, y0 + jumpoff(jump) + squash)
    head = y0 + 10 + squash
    bx = q(MX + 46 + math.sin(k*1.7)*6); byy = q(head - 14 - 4*u*(1-u)*H)
    d.rectangle((bx-1, byy+1, bx+14, byy+12), fill=(20,16,30)); d.rectangle((bx+1, byy-1, bx+12, byy+14), fill=(20,16,30))
    d.rectangle((bx, byy+2, bx+13, byy+11), fill=(250,250,250)); d.rectangle((bx+2, byy, bx+11, byy+13), fill=(250,250,250))
    d.rectangle((bx+5, byy+5, bx+8, byy+8), fill=(30,30,30)); d.rectangle((bx+1, byy+2, bx+2, byy+4), fill=(30,30,30)); d.rectangle((bx+11, byy+9, bx+12, byy+11), fill=(30,30,30))

# ---------- INVENTOR ----------
PATTERN = ["....WWWWW.......", "....W.W.W...WW..", "BBBBBBBBBBBBBBBB", "....W.W.W...WW..", "....WWWWW.......", ".......o...o...."]
CELLS = []
for r, row in enumerate(PATTERN[::-1]):
    for c, ch in enumerate(row):
        if ch != '.': CELLS.append((c, len(PATTERN)-1-r, ch))
COLS = {'W': (225, 170, 90), 'B': (100, 62, 34), 'o': (40, 40, 40)}
SX = 116
def inv_setup(ctx):
    P = 60/108; T = ctx['total']*0.9; n = len(CELLS)
    ctx['tb'] = [ (i+1)*T/n for i in range(n) ]
    k = 0
    while k*P < T + 0.5: ev('clank', k*P); k += 1
    ev('ding', T + 0.1)
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Plane): ev('applause', i.start + i.fdur - 0.3)
            if isinstance(i, Title) and i.text in ('100 METROS', '60 METROS'): ev('applause', i.start + 0.05*len(i.text) + 0.3)

def _inv_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    tb = ctx['tb']; n = sum(1 for x in tb if x <= t)
    for i in range(n):
        c, r, ch = CELLS[i]; age = t - tb[i]
        dy = q(-12*(1 - clamp(age/0.1)))
        x = SX + c*8; y = G - (len(PATTERN) - r)*8 + dy
        col = COLS[ch]; d.rectangle((x, y, x+7, y+7), fill=dark(col, .55)); d.rectangle((x+1, y+1, x+6, y+6), fill=col); d.rectangle((x, y+6, x+7, y+7), fill=dark(col, .75)); d.rectangle((x, y, x+7, y), fill=light(col, .3))
    done = n >= len(CELLS)
    if done and int(t*20) % 2:
        d.rectangle((SX+15*8+6, G-30, SX+15*8+9, G-6), fill=(60,60,60))
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + jumpoff(jump)
    P = 60/th['bpm']; u = (t/P) % 1
    hit = (u < 0.15) and not done
    place(cv, d, spr, MX, y0 + (2 if hit else 0))
    px, py = MX + 74, y0 + 58
    hc = (140, 95, 55); hh = (150, 150, 160)
    if hit:
        d.rectangle((px, py-2, px+22, py+2), fill=hc); d.rectangle((px+18, py-10, px+26, py+10), fill=hh)
        if n < len(CELLS):
            c, r, ch = CELLS[min(n, len(CELLS)-1)]
            sx, sy = SX + c*8 + 4, G - (len(PATTERN) - r)*8 + 4
            rr = random.Random(int(t/P))
            for _ in range(6):
                ang = rr.uniform(0, 2*math.pi); dist = u/0.15*16
                d.rectangle((q(sx + math.cos(ang)*dist), q(sy + math.sin(ang)*dist), q(sx + math.cos(ang)*dist)+3, q(sy + math.sin(ang)*dist)+3), fill=(255, 230, 90))
    else:
        d.rectangle((px-2, py-24, px+2, py), fill=hc); d.rectangle((px-10, py-30, px+10, py-22), fill=hh)

def wrap(fn):
    def f(cv, d, base, th, t, talking, jump, ci, ctx):
        lay = Image.new('RGBA', (LW, LH), (0,0,0,0)); ld = ImageDraw.Draw(lay)
        fn(lay, ld, base, th, t, talking, jump, ci, ctx, md=d)
        cv.alpha_composite(lay.resize((LW*2, LH*2), Image.NEAREST), (0, GROUND - (G*2)))
    return f
def _generic_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    spr = face_sprite(base, t, talking)
    sway = q(math.sin(beat*math.pi)*6); hop = -4 if (beat % 1) < 0.25 else 0
    place(cv, d, spr, MX + sway, G - 80 + hop + jumpoff(jump))
def generic_setup(ctx): pass
generic_mascot = wrap(_generic_mascot)
hiphop_mascot = wrap(_hiphop_mascot); flu_mascot = wrap(_flu_mascot); inv_mascot = wrap(_inv_mascot)
