import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

def face_sprite(base, t, talking):
    im = base.copy(); d = ImageDraw.Draw(im)
    fx, fy = 20, 44
    blink = (t % 3.3) < 0.12 and t > 1   # olhos abertos no quadro 0 (capa)
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

# ---------- GENTILEZA: rega um jardim que cresce aos poucos; corações sobem do mascote ----------
GARDEN = [(150, (255, 120, 170)), (172, (255, 200, 60)), (194, (170, 120, 255)), (216, (255, 90, 90)), (238, (255, 255, 255)), (160, (255, 160, 60)), (205, (120, 200, 255)), (228, (255, 120, 170))]
def gentil_setup(ctx):
    T = ctx['total']*0.85; n = len(GARDEN)
    ctx['bloom'] = [(i+1)*T/n for i in range(n)]
    for t in ctx['bloom']: ev('chime', t)
    ctx['jumps'] = []
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in ('MITO!', 'GENTILEZA', 'RESTAURADAS'):
                tt = i.start + 0.05*len(i.text) + 0.3; ctx['jumps'].append(tt); ev('applause', tt)

def _gentil_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    # jardim (x >= 148, longe do mascote)
    for k, (gx, col) in enumerate(GARDEN):
        age = t - ctx['bloom'][k]
        hgt = 10 if k < 5 else 6
        d.rectangle((gx - 6, G - 4, gx + 10, G), fill=(110, 70, 40))
        if age < -3: continue
        grow = clamp((age + 3) / 3)
        stem = q(8 + (22 + hgt)*grow, 2); sway = q(math.sin(t*2 + k)*2*grow)
        d.rectangle((gx + 1, G - 4 - stem, gx + 3, G - 4), fill=(60, 150, 60))
        if grow > 0.5: d.rectangle((gx + 4, G - 4 - stem//2, gx + 8, G - 2 - stem//2), fill=(80, 170, 70))
        if age >= 0:
            pp = clamp(age/0.25); r = q(2 + 4*pp, 2); cx, cy = gx + 2 + sway, G - 6 - stem
            for ox, oy in ((-r, 0), (r, 0), (0, -r), (0, r)): d.rectangle((cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3), fill=col)
            d.rectangle((cx - 2, cy - 2, cx + 2, cy + 2), fill=(255, 220, 60))
    beat = t*th['bpm']/60
    hop = 0
    for jt in ctx['jumps']:
        if 0 <= t - jt < 0.9: hop = q(-abs(math.sin((t - jt)*math.pi*3.3))*22)
    spr = face_sprite(base, t, talking)
    sway = q(math.sin(beat*math.pi/2)*3)
    place(cv, d, spr, MX + sway, G - 80 + hop + jumpoff(jump))
    # regador na mão do mascote, inclinando no ritmo; gotas caem perto do regador (não no mascote)
    wx, wy = MX + 76 + sway, G - 40 + hop
    tilt = (beat % 2) < 1
    can = (90, 160, 220)
    d.rectangle((wx, wy, wx + 18, wy + 14), fill=can); d.rectangle((wx + 2, wy + 2, wx + 16, wy + 4), fill=light(can, .4))
    d.rectangle((wx - 4, wy + 2, wx, wy + 10), fill=dark(can, .7))
    if tilt: d.rectangle((wx + 18, wy - 2, wx + 30, wy + 2), fill=can)
    else: d.rectangle((wx + 18, wy + 2, wx + 28, wy + 6), fill=can)
    if tilt:
        for k in range(4):
            ph = (beat*2 + k/4) % 1; d.rectangle((wx + 30 + k*2, wy + 2 + q(ph*34), wx + 32 + k*2, wy + 6 + q(ph*34)), fill=(120, 200, 255))
    # corações sobem acima da cabeça
    for k in range(3):
        ph = (t*0.5 + k/3) % 1
        if ph > 0.8: continue
        hx = q(MX + 28 + math.sin((t + k)*2)*10 + sway); hy = q(G - 96 - ph*70)
        c = (255, 90, 130)
        d.rectangle((hx, hy, hx + 3, hy + 3), fill=c); d.rectangle((hx + 5, hy, hx + 8, hy + 3), fill=c); d.rectangle((hx, hy + 2, hx + 8, hy + 5), fill=c); d.rectangle((hx + 2, hy + 6, hx + 6, hy + 8), fill=c)

# ---------- F1: kart que acelera e freia; bandeira quadriculada longe, à direita ----------
def f1_setup(ctx):
    P = 2.4; k = 0
    while k*P < ctx['total'] - 1: ev('rev', k*P); k += 1
    ctx['wins'] = []
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in ('CAMPEÃO MUNDIAL', '17 ANOS', 'LANDO NORRIS'):
                tt = i.start + 0.05*len(i.text) + 0.3; ctx['wins'].append((tt, tt + 2.2)); ev('applause', tt); ev('horn', tt)
            if isinstance(i, Stats): ctx['wins'].append((i.start + 1.7, i.start + 3.2)); ev('applause', i.start + 1.7)

def _f1_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    win = any(a <= t < b for a, b in ctx['wins'])
    # pista
    for x in range(0, LW, 24): d.rectangle((x + q((-t*120) % 24), G + 2, x + 11 + q((-t*120) % 24), G + 5), fill=(240, 240, 240))
    # bandeira quadriculada (x ~ 228)
    fx = 232; d.rectangle((fx, G - 92, fx + 2, G), fill=(200, 200, 210))
    for r in range(4):
        for c in range(5):
            wv = q(math.sin(t*6 + c*0.8)*3)
            col = (20, 20, 24) if (r + c) % 2 else (250, 250, 250)
            d.rectangle((fx + 3 + c*6, G - 92 + r*6 + wv, fx + 8 + c*6, G - 87 + r*6 + wv), fill=col)
    # kart: anda pra frente e volta (x 10..92) num ciclo de 2,4 s
    cyc = (t % 2.4) / 2.4
    off = q((math.sin(cyc*2*math.pi - math.pi/2) + 1)/2 * 70)
    bump = 2 if int(t*14) % 2 else 0
    kx = 8 + off; ky = G - 26
    spr = face_sprite(base, t, True if win else talking)
    hop = q(-abs(math.sin(t*math.pi*3))*16) if win else 0
    cv.alpha_composite(spr.resize((60, 60), Image.NEAREST), (kx + 14, ky - 48 + bump + hop))
    body = (255, 140, 0)
    d.rectangle((kx, ky, kx + 96, ky + 12), fill=body); d.rectangle((kx + 84, ky - 6, kx + 100, ky + 4), fill=dark(body, .7))
    d.rectangle((kx - 6, ky - 10, kx + 4, ky + 4), fill=(30, 30, 36)); d.rectangle((kx + 4, ky + 4, kx + 92, ky + 6), fill=(250, 220, 40))
    for wx in (kx + 10, kx + 76):
        d.rectangle((wx - 9, ky + 8, wx + 9, ky + 26), fill=(20, 20, 24)); d.rectangle((wx - 3, ky + 14, wx + 3, ky + 20), fill=(140, 140, 150))
    # fumaça/velocidade atrás
    for k in range(3):
        ph = (t*3 + k/3) % 1; sx = kx - 10 - q(ph*30); sy = ky + 14 - k*6
        d.rectangle((sx, sy, sx + 5 - int(ph*4), sy + 3), fill=(200, 200, 210))
    if win:
        r = random.Random(3); d2 = md
        for k in range(40):
            sp = r.uniform(60, 140); x0 = r.uniform(0, CW); ph = r.uniform(0, 8)
            yy = ((t*sp + ph*100) % (CH + 40)) - 40; xx = x0 + math.sin(t*3 + k)*10
            col = [(255, 140, 0), (250, 250, 250), (20, 20, 24), (250, 220, 40)][k % 4]
            d2.rectangle((q(xx), q(yy), q(xx)+5, q(yy)+3 + (k % 2)*2), fill=col)

# ---------- ESPARTA: escudo e lança no ritmo dos tambores; no bônus, microfone e notas ----------
def sparta_setup(ctx):
    P = 60/92; k = 0; n = len(ctx['cards']); bonus = ctx['cards'][n-2][0], ctx['cards'][n-2][0] + ctx['cards'][n-2][1]
    ctx['sing'] = bonus
    while k*P < ctx['total'] - 1:
        tt = k*P
        if not (bonus[0] <= tt < bonus[1]): ev('drum', tt, k=k)
        k += 1
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in ('300', 'GERARD BUTLER', 'DEMITIDO!', 'CORIOLANO'):
                tt = i.start + 0.05*len(i.text) + 0.3; ev('clank', tt); ev('clank', tt + 0.12)
                if i.text != 'DEMITIDO!': ev('applause', tt)
    ev('applause', bonus[0] + 1.0)

def _sparta_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    # coluna grega ao fundo, à direita (parada)
    cx = 222; st = (235, 225, 205)
    d.rectangle((cx - 4, G - 112, cx + 34, G - 104), fill=st); d.rectangle((cx, G - 104, cx + 30, G - 6), fill=st)
    for k in range(5): d.rectangle((cx + 3 + k*6, G - 100, cx + 4 + k*6, G - 10), fill=dark(st, .85))
    d.rectangle((cx - 4, G - 6, cx + 34, G), fill=st)
    sing = ctx['sing'][0] <= t < ctx['sing'][1]
    P = 60/th['bpm']; u = (t/P) % 1; hit = u < 0.18 and not sing
    spr = face_sprite(base, t, True if sing else talking)
    y0 = G - 80 + jumpoff(jump) + (3 if hit else 0)
    place(cv, d, spr, MX, y0)
    if sing:
        mx, my = MX + 74, y0 + 46
        d.rectangle((mx - 2, my + 6, mx + 3, my + 26), fill=(30, 30, 36)); d.rectangle((mx - 6, my - 6, mx + 7, my + 7), fill=(170, 170, 180))
        for k in range(3):
            ph = (t*0.8 + k/3) % 1
            if ph > 0.85: continue
            nx = q(mx + 24 + math.sin((t + k)*3)*10); ny = q(my - 10 - ph*70)
            col = [th['acc'], (255, 230, 150), (255, 255, 255)][k]
            d.rectangle((nx, ny, nx + 5, ny + 4), fill=col); d.rectangle((nx + 4, ny - 12, nx + 5, ny), fill=col); d.rectangle((nx + 5, ny - 12, nx + 9, ny - 10), fill=col)
        return
    # lança (sobe no ritmo) atrás do mascote
    sx = MX + 70; lift = 8 if hit else 0
    d.rectangle((sx, G - 120 - lift, sx + 3, G - 6 - lift), fill=(120, 80, 40))
    d.polygon([(sx - 4, G - 120 - lift), (sx + 1, G - 134 - lift), (sx + 7, G - 120 - lift)], fill=(200, 200, 210))
    # escudo redondo (bronze) na frente, à direita do mascote
    bx, by = MX + 78, y0 + 30; br = (205, 150, 60); r = 22
    for yy in range(-r, r + 1, 2):
        w = int(math.sqrt(max(0, r*r - yy*yy))); d.rectangle((bx + 22 - w, by + 22 + yy, bx + 22 + w, by + 23 + yy), fill=br if yy < r - 6 else dark(br, .75))
    for yy in range(-r + 4, r - 3, 2):
        w = int(math.sqrt(max(0, (r-4)**2 - yy*yy))); d.rectangle((bx + 22 - w, by + 22 + yy, bx + 22 + w, by + 23 + yy), fill=light(br, .15))
    # lambda vermelho
    lc = (200, 30, 40)
    for k in range(14):
        d.rectangle((bx + 22 - k//2 - 1, by + 12 + k, bx + 22 - k//2 + 1, by + 13 + k), fill=lc); d.rectangle((bx + 22 + k//2 - 1, by + 12 + k, bx + 22 + k//2 + 1, by + 13 + k), fill=lc)
    if hit:
        rr = random.Random(int(t/P))
        for _ in range(5):
            a = rr.uniform(-1.2, 1.2); dist = 10 + u/0.18*14
            px, py = bx + 46 + math.cos(a)*dist, by + 22 + math.sin(a)*dist
            d.rectangle((q(px), q(py), q(px) + 3, q(py) + 3), fill=(255, 230, 120))

# ---------- ACAMPAMENTO (Sexta-feira 13): lanterna, fogueira, barraca e vaga-lumes ----------
SCARE = ('SEXTA-FEIRA 13', 'A MÃE!', 'SÓ NO TERCEIRO', 'CAMP BLOOD', 'KI KI KI MA MA MA')
def camp_setup(ctx):
    ctx['scares'] = []
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in SCARE:
                tt = i.start + 0.05*len(i.text) + 0.3; ctx['scares'].append(tt); ev('owl', tt)
            if isinstance(i, Stats): ev('chime', i.start + 1.7)
    k = 0
    while k*3.1 < ctx['total'] - 1: ev('crackle', k*3.1); k += 1

def _camp_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    # barraca (x 214..262) e fogueira (x ~176), longe do mascote
    tc = (196, 120, 50); tx = 214
    for r in range(0, 36, 2):
        half = 24 - int(r*24/36)
        d.rectangle((tx + 24 - half, G - 4 - r - 2, tx + 24 + half, G - 4 - r), fill=tc if (r//6) % 2 else dark(tc, .85))
    d.rectangle((tx + 20, G - 22, tx + 28, G - 4), fill=(30, 22, 18))
    fx = 176
    d.rectangle((fx - 14, G - 6, fx + 14, G - 1), fill=(90, 56, 30)); d.rectangle((fx - 10, G - 10, fx + 10, G - 6), fill=(120, 74, 38))
    for k in range(5):
        fl = 8 + 6*abs(math.sin(t*9 + k*1.7)); ox = (k - 2)*5
        col = [(255, 80, 20), (255, 140, 30), (255, 210, 70)][k % 3]
        d.rectangle((fx + ox - 2, q(G - 10 - fl), fx + ox + 2, G - 10), fill=col)
    for k in range(4):
        ph = (t*0.9 + k/4) % 1; d.rectangle((q(fx + math.sin(k*3 + t*2)*10), q(G - 20 - ph*50), q(fx + math.sin(k*3 + t*2)*10) + 1, q(G - 20 - ph*50) + 1), fill=(255, 200, 80))
    # vaga-lumes (acima do chão, longe da cabeça do mascote)
    for k in range(7):
        bx = 120 + ((k*37) % 140) + math.sin(t*0.8 + k)*8; by = 110 + ((k*53) % 80) + math.cos(t*0.7 + k*2)*6
        if math.sin(t*2.2 + k*1.9) > 0.2: d.rectangle((q(bx), q(by), q(bx) + 1, q(by) + 1), fill=(220, 255, 120))
    scared = any(0 <= t - st < 0.9 for st in ctx['scares'])
    hop = 0
    for st in ctx['scares']:
        if 0 <= t - st < 0.9: hop = q(-abs(math.sin((t - st)*math.pi*3.3))*20)
    beat = t*th['bpm']/60
    spr = face_sprite(base, t, True if scared else talking)
    place(cv, d, spr, MX, G - 80 + hop + jumpoff(jump))
    # motosserra na mão do mascote: motor laranja, sabre cinza, corrente girando e vibração
    vib = 1 if int(t*30) % 2 else 0
    lx, ly = MX + 74, G - 48 + hop + vib
    d.rectangle((lx, ly - 2, lx + 16, ly + 12), fill=(230, 110, 20)); d.rectangle((lx + 2, ly, lx + 14, ly + 3), fill=(40, 40, 46))
    d.rectangle((lx + 4, ly - 6, lx + 12, ly - 2), fill=(40, 40, 46))
    d.rectangle((lx + 16, ly + 2, lx + 46, ly + 8), fill=(170, 175, 185)); d.rectangle((lx + 46, ly + 3, lx + 48, ly + 7), fill=(170, 175, 185))
    off = int(t*40) % 4
    for x in range(lx + 16 + off, lx + 46, 4):
        d.rectangle((x, ly + 1, x + 1, ly + 1), fill=(60, 60, 66)); d.rectangle((x, ly + 9, x + 1, ly + 9), fill=(60, 60, 66))
    for k in range(3):
        ph = (t*1.6 + k/3) % 1
        g = int(150 - ph*80); d.rectangle((q(lx - 2 - ph*10), q(ly - 6 - ph*22), q(lx - 2 - ph*10) + 2, q(ly - 6 - ph*22) + 2), fill=(g, g, g))
    if scared:
        d.rectangle((MX + 34, G - 120 + hop, MX + 38, G - 106 + hop), fill=(255, 220, 60)); d.rectangle((MX + 34, G - 102 + hop, MX + 38, G - 98 + hop), fill=(255, 220, 60))

KINDS = {'camp': (wrap(_camp_mascot), camp_setup), 'gentileza': (wrap(_gentil_mascot), gentil_setup), 'f1': (wrap(_f1_mascot), f1_setup), 'sparta': (wrap(_sparta_mascot), sparta_setup)}

def _title_times(ctx, names):
    out = []
    for s0, du, its in ctx['cards']:
        for i in its:
            if isinstance(i, Title) and i.text in names: out.append(i.start + 0.05*len(i.text) + 0.3)
    return out

# ---------- REPÚBLICA: bicorne, sabre no ritmo da marcha; bandeira provisória (EUA) vira a atual na tela 9 ----------
def rep_setup(ctx):
    n = len(ctx['cards']); ctx['flag_t'] = ctx['cards'][min(8, n-1)][0] + 0.6
    ctx['hits'] = _title_times(ctx, ('REPÚBLICA', 'BOATO!', 'CÓPIA DOS EUA'))
    for tt in ctx['hits']: ev('horn', tt)
    ev('horn', ctx['flag_t']); ev('applause', ctx['flag_t'] + 0.2); ctx['hits'].append(ctx['flag_t'])
    P = 60/100*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _rep_flag(d, fx, fy, t, new):
    W_, H_ = 52, 34
    for cx in range(0, W_, 2):
        wv = q(math.sin(t*5 - cx*0.18)*3*(cx/W_))
        for cy in range(0, H_, 2):
            if not new:
                if cx < 22 and cy < 18: col = (255, 255, 255) if (cx % 6 == 2 and cy % 6 == 2) else (20, 50, 140)
                else: col = (0, 150, 60) if int(cy*13/H_) % 2 == 0 else (250, 215, 0)
            else:
                ux, uy = (cx - W_/2)/(W_/2), (cy - H_/2)/(H_/2)
                col = (0, 150, 60)
                if abs(ux)*0.95 + abs(uy)*0.95 < 0.95: col = (250, 215, 0)
                r = math.hypot(ux*W_/2, uy*H_/2)
                if r < 10: col = (20, 50, 140)
                if r < 10 and abs((cy - H_/2) + (cx - W_/2)*0.18) < 2: col = (255, 255, 255)
            d.rectangle((fx + cx, fy + cy + wv, fx + cx + 1, fy + cy + wv + 1), fill=col)

def _rep_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    px = 214; d.rectangle((px, G - 132, px + 3, G), fill=(200, 200, 210)); d.rectangle((px - 1, G - 136, px + 4, G - 132), fill=(230, 190, 60))
    new = t >= ctx['flag_t']
    _rep_flag(d, px + 4, G - 130, t, new)
    if new and t - ctx['flag_t'] < 0.4:
        a = 1 - (t - ctx['flag_t'])/0.4
        for k in range(10):
            ang = k*0.63; r = 30*(1-a) + 6
            d.rectangle((q(px + 30 + math.cos(ang)*r), q(G - 113 + math.sin(ang)*r), q(px + 30 + math.cos(ang)*r) + 3, q(G - 113 + math.sin(ang)*r) + 3), fill=(255, 230, 120))
    beat = t*th['bpm']/60; step = int(beat) % 2
    hop = 0; raise_ = False
    for ht in ctx['hits']:
        if 0 <= t - ht < 1.0: hop = q(-abs(math.sin((t - ht)*math.pi*3))*18); raise_ = True
    spr = face_sprite(base, t, True if raise_ else talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if step else 0)
    place(cv, d, spr, MX, y0)
    hx, hy = MX + 74, y0 + 50
    d.rectangle((hx - 2, hy - 2, hx + 8, hy + 4), fill=(230, 190, 60))
    if raise_:
        for k in range(14): d.rectangle((hx + 2, hy - 6 - k*4, hx + 5, hy - 2 - k*4), fill=(210, 215, 225))
        d.rectangle((hx + 2, hy - 64, hx + 5, hy - 58), fill=(255, 255, 255))
    else:
        for k in range(10): d.rectangle((hx + 6 + k*3, hy + 4 + k*3, hx + 9 + k*3, hy + 7 + k*3), fill=(210, 215, 225))

# ---------- XBOX: headset, controle Duke com botões piscando, TV de tubo com o X verde; HALO na tela ----------
def xbox_setup(ctx):
    ev('boot', 0.2)
    ctx['halo'] = _title_times(ctx, ('HALO',)); ctx['hits'] = _title_times(ctx, ('XBOX', 'HALO'))
    for tt in ctx['hits']: ev('ding', tt)
    for tt in ctx['halo']: ev('applause', tt + 0.1)
    P = 60/112; k = 0
    while k*P < ctx['total'] - 1:
        if k % 2 == 0: ev('blip', k*P, k=k//2)
        k += 1

def _xbox_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    G_ = (120, 220, 60)
    tx, ty, tw, th_ = 168, G - 78, 86, 70
    d.rectangle((tx, ty, tx + tw, ty + th_), fill=(52, 52, 60)); d.rectangle((tx + 4, ty + th_, tx + tw - 4, ty + th_ + 4), fill=(30, 30, 36))
    d.rectangle((tx + tw - 14, ty + 10, tx + tw - 6, ty + 14), fill=(90, 90, 100)); d.rectangle((tx + tw - 14, ty + 20, tx + tw - 6, ty + 24), fill=(90, 90, 100))
    sx, sy, sw, sh = tx + 6, ty + 6, tw - 26, th_ - 12
    halo = any(0 <= t - h < 3.0 for h in ctx['halo'])
    beat = t*th['bpm']/60; pulse = 0.6 + 0.4*abs(math.sin(beat*math.pi))
    d.rectangle((sx, sy, sx + sw, sy + sh), fill=(10, 24, 12))
    for yy in range(sy, sy + sh, 4): d.rectangle((sx, yy, sx + sw, yy), fill=(18, 40, 20))
    cx_, cy_ = sx + sw//2, sy + sh//2
    if halo:
        for a in range(0, 360, 8):
            r = math.radians(a); px_, py_ = cx_ + math.cos(r)*22, cy_ + math.sin(r)*8
            col = (200, 230, 255) if math.sin(r) < 0 else (120, 170, 230)
            d.rectangle((q(px_), q(py_), q(px_) + 2, q(py_) + 2), fill=col)
        d.rectangle((cx_ - 3, cy_ - 3, cx_ + 3, cy_ + 3), fill=(90, 130, 220))
    else:
        c = lerp((40, 90, 30), G_, pulse)
        for k in range(-10, 11, 2):
            d.rectangle((cx_ + k - 1, cy_ + k - 1, cx_ + k + 2, cy_ + k + 2), fill=c); d.rectangle((cx_ + k - 1, cy_ - k - 1, cx_ + k + 2, cy_ - k + 2), fill=c)
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*20)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump)
    place(cv, d, spr, MX, y0)
    bx, by = MX + 46, y0 + 52
    d.rectangle((bx, by, bx + 46, by + 20), fill=(30, 30, 34)); d.rectangle((bx - 4, by + 6, bx + 4, by + 26), fill=(30, 30, 34)); d.rectangle((bx + 42, by + 6, bx + 50, by + 26), fill=(30, 30, 34))
    d.rectangle((bx + 19, by + 6, bx + 27, by + 14), fill=lerp((60, 110, 40), G_, pulse))
    d.rectangle((bx + 5, by + 6, bx + 11, by + 12), fill=(70, 70, 80))
    btn = int(beat*2) % 4
    for j, (ox, oy, col) in enumerate(((34, 4, (250, 210, 40)), (30, 9, (40, 110, 230)), (38, 9, (220, 40, 40)), (34, 13, (60, 190, 60)))):
        c = light(col, .5) if j == btn else dark(col, .8)
        d.rectangle((bx + ox, by + oy, bx + ox + 3, by + oy + 3), fill=c)

# ---------- FLAMENGO: faixa e barco azul e ouro que viram rubro-negro (tela 7); remo no ritmo; tempestade na tela 3 ----------
def fla_setup(ctx):
    n = len(ctx['cards'])
    ctx['red_t'] = ctx['cards'][min(6, n-1)][0] + 0.6
    s2 = ctx['cards'][min(2, n-1)]; ctx['storm'] = (s2[0], s2[0] + s2[1])
    s3 = ctx['cards'][min(3, n-1)]; ctx['gone'] = (s3[0], s3[0] + s3[1]*0.45)
    ctx['hits'] = _title_times(ctx, ('FLAMENGO',)) + [ctx['red_t']]
    for tt in ctx['hits']: ev('whistle', tt); ev('applause', tt + 0.15)
    ev('thunder', ctx['storm'][0] + 0.1); ev('thunder', ctx['storm'][0] + 3.5)
    P = 1.6; k = 0
    while k*P < ctx['total'] - 1: ev('splash', k*P + 0.55); k += 1

def _fla_cols(t, ctx):
    return ((200, 20, 30), (20, 20, 24)) if t >= ctx['red_t'] else ((30, 80, 200), (240, 200, 40))

def _fla_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    c1, c2 = _fla_cols(t, ctx)
    storm = ctx['storm'][0] <= t < ctx['storm'][1]
    for x in range(96, LW, 2):
        h = q(2 + math.sin(t*(4 if not storm else 9) + x*0.12)*(2 if not storm else 4))
        d.rectangle((x, G - 8 - h, x + 1, G + 10), fill=(36, 100, 180))
        if (x + int(t*30)) % 22 < 4: d.rectangle((x, G - 8 - h, x + 1, G - 7 - h), fill=(200, 230, 255))
    gone = ctx['gone'][0] <= t < ctx['gone'][1]
    stroke = (t % 1.6)/1.6
    if not gone:
        slide = 0
        if ctx['gone'][1] <= t < ctx['gone'][1] + 1.0: slide = q((1 - (t - ctx['gone'][1]))*120)
        tilt = math.sin(t*(2.2 if not storm else 6))*(2 if not storm else 6)
        bx, by = 150 + slide, G - 16
        for i in range(0, 96, 2):
            yo = q(tilt*(i - 48)/48)
            dep = 16 - (abs(i - 48)**2)//190
            top = by + yo - 4 + (abs(i - 48)//16)
            col = c1 if (i//8) % 2 == 0 else c2
            d.rectangle((bx + i, top, bx + i + 1, top + dep), fill=col)
            d.rectangle((bx + i, top, bx + i + 1, top + 1), fill=(120, 80, 40))
        for k, ox in enumerate((26, 60)):
            a = math.sin(stroke*2*math.pi + k)*0.8
            x0, y0_ = bx + ox, by + q(tilt*(ox - 48)/48)
            for j in range(10): d.rectangle((q(x0 - j*2*math.cos(a)), q(y0_ + j*2*math.sin(a) + j), q(x0 - j*2*math.cos(a)) + 1, q(y0_ + j*2*math.sin(a) + j) + 1), fill=(150, 100, 50))
    if storm:
        r = random.Random(int(t*12))
        for _ in range(70):
            x = r.randrange(0, LW); y = r.randrange(0, G)
            d.rectangle((x, y, x + 1, y + 10), fill=(110, 130, 175))
        if (t - ctx['storm'][0]) % 3.4 < 0.12 and md is not None:
            md.rectangle((0, 0, CW, 80), fill=(255, 255, 255))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 1.0: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*20)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump)
    place(cv, d, spr, MX, y0)
    for i in range(0, 56, 8):
        d.rectangle((MX + 10 + i, y0 + 26, MX + 17 + i, y0 + 32), fill=c1 if (i//8) % 2 == 0 else c2)
    a = math.sin(stroke*2*math.pi)*0.6 + 0.9
    hx, hy = MX + 74, y0 + 48
    for j in range(22):
        d.rectangle((q(hx + j*2*math.cos(a)), q(hy + j*2*math.sin(a)), q(hx + j*2*math.cos(a)) + 2, q(hy + j*2*math.sin(a)) + 2), fill=(160, 110, 55))
    ex, ey = hx + 44*math.cos(a), hy + 44*math.sin(a)
    d.rectangle((q(ex) - 3, q(ey) - 3, q(ex) + 5, q(ey) + 9), fill=(130, 85, 40))

KINDS.update({'republica': (wrap(_rep_mascot), rep_setup), 'xbox': (wrap(_xbox_mascot), xbox_setup), 'flamengo': (wrap(_fla_mascot), fla_setup)})

# ---------- CINEMA (16/11): chapéu de mago genérico, varinha com faíscas, balde de pipoca estourando ----------
def cine_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('HARRY POTTER', 'RECORDE!'))
    for tt in ctx['hits']: ev('chime', tt); ev('applause', tt + 0.15)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1:
        if k % 2 == 1: ev('tick', k*P)
        k += 1

def _cine_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # tela de cinema ao fundo com feixe do projetor
    sx0, sy0 = 150, G - 86
    d.rectangle((sx0 - 3, sy0 - 3, sx0 + 103, sy0 + 61), fill=(60, 20, 30))
    d.rectangle((sx0, sy0, sx0 + 100, sy0 + 58), fill=(235, 232, 220))
    fl = int(t*12) % 3
    for yy in range(sy0 + 4, sy0 + 56, 6):
        d.rectangle((sx0 + 6, yy, sx0 + 94, yy + 1), fill=(220 - fl*6, 216 - fl*6, 200 - fl*6))
    # balde de pipoca
    bx, by = 206, G - 30
    for i in range(0, 26, 2):
        d.rectangle((bx + i, by, bx + i + 1, by + 30), fill=(220, 30, 40) if (i//4) % 2 == 0 else (250, 245, 240))
    for i in range(7):
        d.rectangle((bx + 2 + i*3, by - 4 - (i % 3), bx + 6 + i*3, by), fill=(255, 240, 180))
    ph = beat % 1
    if ph < 0.5:
        for j in range(3):
            px_ = bx + 6 + j*7; py_ = by - 6 - q(math.sin(ph*2*math.pi)*14) - j*3
            d.rectangle((px_, py_, px_ + 3, py_ + 3), fill=(255, 245, 200))
    hop = 0; burst = None
    for h in ctx['hits']:
        if 0 <= t - h < 1.0: hop = q(-abs(math.sin((t - h)*math.pi*3.2))*18); burst = t - h
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump)
    place(cv, d, spr, MX, y0)
    # varinha
    sw = math.sin(beat*math.pi)*0.5 - 0.7 if burst is None else -1.3
    hx, hy = MX + 74, y0 + 50
    tipx, tipy = hx, hy
    for k in range(12):
        tipx = hx + q(math.cos(sw)*k*2.4); tipy = hy + q(math.sin(sw)*k*2.4)
        d.rectangle((tipx, tipy, tipx + 2, tipy + 2), fill=(110, 70, 40))
    tw = 2 + int(t*10) % 2
    d.rectangle((tipx - tw, tipy, tipx + 2 + tw, tipy + 2), fill=(255, 240, 150)); d.rectangle((tipx, tipy - tw, tipx + 2, tipy + 2 + tw), fill=(255, 240, 150))
    if burst is not None:
        rr = random.Random(int(burst*20))
        for _ in range(16):
            a = rr.uniform(0, 2*math.pi); dist = burst*60*rr.uniform(.5, 1)
            col = rr.choice(((255, 220, 80), (190, 140, 255), (255, 255, 255)))
            d.rectangle((q(tipx + math.cos(a)*dist), q(tipy + math.sin(a)*dist), q(tipx + math.cos(a)*dist) + 2, q(tipy + math.sin(a)*dist) + 2), fill=col)

# ---------- VACINA (1904): chapéu-coco e bigode; bonde que vira nos protestos; chifres na "cara de vaca" ----------
def vac_setup(ctx):
    n = len(ctx['cards'])
    c4 = ctx['cards'][min(4, n-1)]; ctx['cow'] = (c4[0] + 1.2, c4[0] + c4[1])
    c5 = ctx['cards'][min(5, n-1)]; ctx['tip_t'] = c5[0] + 1.0
    c8 = ctx['cards'][min(8, n-1)]; ctx['up_t'] = c8[0]
    c3 = ctx['cards'][min(3, n-1)]; ctx['paper'] = (c3[0], c3[0] + c3[1])
    ctx['hits'] = _title_times(ctx, ('VACINA', 'CARA DE VACA?'))
    for tt in ctx['hits']: ev('ding', tt)
    ev('moo', ctx['cow'][0] - 0.2)
    ev('clank', ctx['tip_t'] + 0.45); ev('thud', ctx['tip_t'] + 0.5); ev('crackle', ctx['tip_t'] + 0.6); ev('crackle', ctx['tip_t'] + 3.2)
    P = 60/96*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _bonde(d, bx, by):
    yl, gr = (225, 180, 50), (40, 100, 60)
    d.rectangle((bx, by - 34, bx + 80, by - 6), fill=yl); d.rectangle((bx - 2, by - 38, bx + 82, by - 34), fill=gr)
    for wx in range(bx + 6, bx + 74, 14): d.rectangle((wx, by - 30, wx + 9, by - 20), fill=(150, 190, 210))
    d.rectangle((bx, by - 10, bx + 80, by - 6), fill=gr)
    d.rectangle((bx + 38, by - 52, bx + 40, by - 38), fill=(60, 60, 60))
    for wx in (bx + 12, bx + 60): d.rectangle((wx, by - 6, wx + 8, by + 2), fill=(40, 40, 40))

def _vac_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    # poste de lampião
    lx = 136; d.rectangle((lx, G - 100, lx + 3, G), fill=(40, 40, 46)); d.rectangle((lx - 5, G - 112, lx + 8, G - 100), fill=(40, 40, 46))
    lit = not (ctx['tip_t'] <= t < ctx['up_t'])
    d.rectangle((lx - 3, G - 110, lx + 6, G - 102), fill=(255, 220, 120) if lit else (70, 70, 70))
    # bonde: em pé, tombado durante a revolta, em pé de novo depois
    tipped = ctx['tip_t'] <= t < ctx['up_t']
    lay = Image.new('RGBA', (120, 80), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); _bonde(ld, 18, 70)
    if tipped:
        a = min(1, (t - ctx['tip_t'])/0.5)
        lay = lay.rotate(-180*a*a, resample=Image.NEAREST, center=(58, 52))
    cv.alpha_composite(lay, (150, G - 70))
    if tipped and t - ctx['tip_t'] > 0.5:
        r = random.Random(int(t*10))
        for _ in range(14):
            sx_ = 150 + r.randrange(40, 115); sy_ = G - 40 - r.randrange(0, 70) - int((t*30) % 20)
            d.rectangle((sx_, sy_, sx_ + 5, sy_ + 5), fill=(120, 115, 110))
        for k in range(6):
            fx_ = 200 + k*6; fh = 6 + int(abs(math.sin(t*9 + k))*10)
            d.rectangle((fx_, G - fh, fx_ + 4, G), fill=(255, 140, 30) if k % 2 else (255, 210, 60))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*18)
    beat = t*th['bpm']/60
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    if ctx['cow'][0] <= t < ctx['cow'][1]:
        for hx in (MX + 16, MX + 60):
            d.rectangle((hx, y0 - 14, hx + 5, y0 + 4), fill=(240, 235, 220)); d.rectangle((hx + (-5 if hx < MX + 40 else 5), y0 - 20, hx + 5 + (-5 if hx < MX + 40 else 5), y0 - 12), fill=(240, 235, 220))
        for sx_, sy_ in ((MX + 14, y0 + 30), (MX + 50, y0 + 60), (MX + 24, y0 + 66)):
            d.rectangle((sx_, sy_, sx_ + 9, sy_ + 6), fill=(30, 30, 30))
    if ctx['paper'][0] <= t < ctx['paper'][1]:
        px_, py_ = MX + 70, y0 + 34
        d.rectangle((px_, py_, px_ + 30, py_ + 36), fill=(235, 228, 205)); d.rectangle((px_ + 3, py_ + 3, px_ + 27, py_ + 8), fill=(40, 40, 40))
        for yy in range(py_ + 12, py_ + 34, 4): d.rectangle((px_ + 3, yy, px_ + 27, yy + 1), fill=(120, 115, 105))

# ---------- BOIADEIRA: chapéu country, laço girando, cerca e vaquinha; estouro de confete nos títulos ----------
def boi_setup(ctx):
    n = len(ctx['cards'])
    ctx['hits'] = _title_times(ctx, ('ANA CASTELA', 'VIRALIZOU!', 'BOIADEIRA'))
    c7 = ctx['cards'][min(7, n-1)]; ctx['pop'] = (c7[0] + 0.4, c7[0] + c7[1])
    for tt in ctx['hits']: ev('ding', tt); ev('applause', tt + 0.15)
    c2 = ctx['cards'][min(2, n-1)]; ev('moo', c2[0] + 0.8)
    k = 0
    while ctx['pop'][0] + k*0.45 < ctx['pop'][1]: ev('pop', ctx['pop'][0] + k*0.45); k += 1
    P = 60/104; k = 0
    while k*P < ctx['total'] - 1: ev('tap', k*P); k += 1

def _boi_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    wd = (150, 100, 55)
    for px_ in range(130, LW, 34): d.rectangle((px_, G - 34, px_ + 5, G), fill=wd)
    for yy in (G - 28, G - 14): d.rectangle((130, yy, LW, yy + 3), fill=light(wd, .15))
    # vaquinha
    cx_, cy_ = 190, G - 52 + (1 if int(beat) % 2 else 0)
    d.rectangle((cx_, cy_, cx_ + 44, cy_ + 24), fill=(250, 250, 245))
    for sx_, sy_, w_, h_ in ((cx_ + 6, cy_ + 4, 12, 9), (cx_ + 26, cy_ + 12, 10, 8)): d.rectangle((sx_, sy_, sx_ + w_, sy_ + h_), fill=(30, 30, 30))
    hd = cx_ - 14; d.rectangle((hd, cy_ - 6, hd + 16, cy_ + 12), fill=(250, 250, 245)); d.rectangle((hd, cy_ + 6, hd + 16, cy_ + 12), fill=(240, 170, 180))
    d.rectangle((hd + 3, cy_ - 1, hd + 5, cy_ + 1), fill=(20, 20, 20)); d.rectangle((hd + 11, cy_ - 1, hd + 13, cy_ + 1), fill=(20, 20, 20))
    d.rectangle((hd - 2, cy_ - 10, hd + 1, cy_ - 6), fill=(230, 220, 190)); d.rectangle((hd + 15, cy_ - 10, hd + 18, cy_ - 6), fill=(230, 220, 190))
    for lx_ in (cx_ + 4, cx_ + 14, cx_ + 30, cx_ + 38): d.rectangle((lx_, cy_ + 24, lx_ + 3, G - 2), fill=(250, 250, 245))
    hop = 0; burst = None
    for h in ctx['hits']:
        if 0 <= t - h < 1.0: hop = q(-abs(math.sin((t - h)*math.pi*3.2))*18); burst = t - h
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump)
    place(cv, d, spr, MX, y0)
    # laço girando sobre a cabeça
    hx, hy = MX + 76, y0 + 46
    ang = t*2*math.pi*1.3
    lcx, lcy = MX + 50 + q(math.cos(ang)*6), y0 - 34
    for k in range(10): d.rectangle((q(hx - (hx - lcx)*k/10), q(hy - (hy - lcy)*k/10), q(hx - (hx - lcx)*k/10) + 1, q(hy - (hy - lcy)*k/10) + 1), fill=(200, 160, 90))
    for a in range(0, 360, 12):
        r = math.radians(a) + ang
        d.rectangle((q(lcx + math.cos(r)*26), q(lcy + math.sin(r)*7), q(lcx + math.cos(r)*26) + 2, q(lcy + math.sin(r)*7) + 2), fill=(200, 160, 90))
    pop = ctx['pop'][0] <= t < ctx['pop'][1]
    if burst is not None or pop:
        u = burst if burst is not None else ((t - ctx['pop'][0]) % 0.45)
        rr = random.Random(int((t if burst is None else burst)*7))
        ox, oy = (lcx, lcy) if burst is not None else (rr.randrange(140, 260), rr.randrange(40, 120))
        for _ in range(18):
            a = rr.uniform(0, 2*math.pi); dist = u*70*rr.uniform(.4, 1)
            col = rr.choice(((240, 110, 170), (255, 220, 80), (255, 255, 255), (120, 200, 255)))
            d.rectangle((q(ox + math.cos(a)*dist), q(oy + math.sin(a)*dist), q(ox + math.cos(a)*dist) + 3, q(oy + math.sin(a)*dist) + 3), fill=col)

KINDS.update({'cinema': (wrap(_cine_mascot), cine_setup), 'vacina': (wrap(_vac_mascot), vac_setup), 'boiadeira': (wrap(_boi_mascot), boi_setup)})

# ---------- APAGAO (boato): postes que apagam um de cada vez (regional) e voltam; nunca todos juntos ----------
def apa_setup(ctx):
    n = len(ctx['cards'])
    ctx['hits'] = _title_times(ctx, ('APAGÃO', 'CADA PAÍS'))
    for tt in ctx['hits']: ev('ding', tt)
    c7 = ctx['cards'][min(7, n-1)]; ctx['reg'] = (c7[0], c7[0] + c7[1])
    P = 60/100*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1
    t = 1.0
    while t < ctx['total'] - 1: ev('tick', t); t += 1.4

def _apa_off(t, i, ctx):
    if ctx['reg'][0] <= t < ctx['reg'][1]: return i < 2
    return int(t/1.4) % 6 == i + 1

def _apa_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    xs = (146, 262 - 90, 206, 238)
    ov = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i, lx in enumerate(xs):
        d.rectangle((lx, G - 88, lx + 3, G), fill=(40, 40, 50)); d.rectangle((lx - 4, G - 94, lx + 8, G - 88), fill=(40, 40, 50))
        off = _apa_off(t, i, ctx)
        d.rectangle((lx - 2, G - 90, lx + 6, G - 86), fill=(60, 60, 66) if off else (255, 225, 120))
        if not off:
            od.polygon([(lx, G - 86), (lx + 3, G - 86), (lx + 20, G), (lx - 17, G)], fill=(255, 225, 120, 30))
        else:
            for k in range(3): d.rectangle((lx + k*3 - 2, G - 100 - k*4 - int(t*8) % 4, lx + k*3, G - 98 - k*4 - int(t*8) % 4), fill=(110, 110, 120))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*18)
    beat = t*th['bpm']/60
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # capacete ja esta no sprite; lanterna na mao
    fx, fy = MX + 74, y0 + 46
    d.rectangle((fx, fy, fx + 12, fy + 6), fill=(70, 70, 80)); d.rectangle((fx + 12, fy - 1, fx + 15, fy + 7), fill=(255, 240, 150))
    od.polygon([(fx + 15, fy + 3), (fx + 70, fy - 14), (fx + 70, fy + 20)], fill=(255, 240, 150, 40))
    cv.alpha_composite(ov)

# ---------- CENARIO (e se o mundo apagasse): lanterna de cabeca, geladeira que estraga, celular sem sinal ----------
def cen_setup(ctx):
    n = len(ctx['cards'])
    ctx['hits'] = _title_times(ctx, ('APAGÃO', 'ESTRAGOU!'))
    for tt in ctx['hits']: ev('ding', tt)
    ctx['c2'] = ctx['cards'][min(2, n-1)]; c5 = ctx['cards'][min(5, n-1)]; ctx['c5'] = c5
    ev('thud', c5[0] + 0.5)
    for k in range(4): ev('tick', ctx['c2'][0] + 0.6 + k*(ctx['c2'][1] - 1.0)/4)
    P = 60/84*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _cen_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    ov = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    # celular
    px_, py_ = 150, G - 46
    d.rectangle((px_, py_, px_ + 22, py_ + 38), fill=(30, 30, 36)); d.rectangle((px_ + 2, py_ + 3, px_ + 20, py_ + 35), fill=(120, 180, 230) if t < ctx['c2'][0] else (60, 70, 90))
    c2s, c2d = ctx['c2'][0], ctx['c2'][1]
    bars = 3 if t < c2s else max(0, 3 - int((t - c2s)/c2d*4))
    for b in range(3):
        d.rectangle((px_ + 5 + b*5, py_ + 14 - b*3, px_ + 8 + b*5, py_ + 18), fill=(255, 255, 255) if b < bars else (70, 70, 80))
    if bars == 0:
        for k in range(8): d.rectangle((px_ + 6 + k, py_ + 24 + k, px_ + 8 + k, py_ + 26 + k), fill=(235, 70, 60)); d.rectangle((px_ + 14 - k, py_ + 24 + k, px_ + 16 - k, py_ + 26 + k), fill=(235, 70, 60))
    # geladeira
    fx, fy = 200, G - 78
    d.rectangle((fx, fy, fx + 38, G), fill=(225, 228, 236)); d.rectangle((fx, fy + 28, fx + 38, fy + 30), fill=(150, 155, 170))
    d.rectangle((fx + 31, fy + 8, fx + 33, fy + 20), fill=(120, 125, 140)); d.rectangle((fx + 31, fy + 38, fx + 33, fy + 52), fill=(120, 125, 140))
    led = t >= ctx['c5'][0] + 0.2 or int(t*2) % 2 == 0
    d.rectangle((fx + 4, fy + 4, fx + 7, fy + 7), fill=(60, 60, 60) if t >= ctx['c2'][0] else (80, 220, 120))
    if t >= ctx['c5'][0] + 0.5:
        d.rectangle((fx + 2, fy + 32, fx + 28, fy + 74), fill=(200, 205, 215))
        u = min(1, (t - ctx['c5'][0] - 0.5)/2.5)
        for k, (cx_, cy_) in enumerate(((fx + 5, fy + 38), (fx + 15, fy + 38), (fx + 5, fy + 54), (fx + 15, fy + 54), (fx + 9, fy + 66))):
            col = (220, int(70 + 130*(1 - u)), 70) if k % 2 == 0 else (int(240 - 140*u), int(220 - 40*u), int(90 - 20*u))
            d.rectangle((cx_, cy_, cx_ + 7, cy_ + 9), fill=col)
        for k in range(5):
            wy = fy + 24 - ((t*14 + k*9) % 26)
            d.rectangle((fx + 6 + k*6 + int(math.sin(t*5 + k)*2), wy, fx + 8 + k*6 + int(math.sin(t*5 + k)*2), wy + 3), fill=(120, 180, 70))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    beat = t*th['bpm']/60
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    spr = face_sprite(base, t, talking)
    place(cv, d, spr, MX, y0)
    od.polygon([(MX + 64, y0 + 6), (MX + 200, y0 - 24), (MX + 200, y0 + 56)], fill=(255, 240, 150, 34))
    od.polygon([(MX + 64, y0 + 6), (MX + 130, y0 - 6), (MX + 130, y0 + 26)], fill=(255, 240, 150, 40))
    cv.alpha_composite(ov)

# ---------- COVID (1o caso): oculos de pesquisa, calendario que marca as datas e particulas flutuando ----------
CAL = [('17', 'NOV', '2019')]*4 + [('01', 'DEZ', '2019'), ('08', 'DEZ', '2019'), ('05', 'JAN', '2020'), ('11', 'FEV', '2020'), ('17', 'NOV', '2019'), ('17', 'NOV', '2019')]
def _cal_at(ci, frac):
    ci = min(ci, len(CAL) - 1)
    if ci == 5 and frac > 0.5: return ('12', 'DEZ', '2019')
    if ci == 7 and frac > 0.5: return ('11', 'MAR', '2020')
    return CAL[ci]

def cov_setup(ctx):
    n = len(ctx['cards'])
    ctx['hits'] = _title_times(ctx, ('COVID', 'SEM CONFIRMAÇÃO'))
    for tt in ctx['hits']: ev('ding', tt)
    for i, (s0, du, its) in enumerate(ctx['cards']):
        if i > 0 and (CAL[min(i, 9)] != CAL[min(i-1, 9)] or i in (5, 7)): ev('tick', s0 + 0.15)
    for i in (5, 7):
        s0, du, _ = ctx['cards'][min(i, n-1)]; ev('tick', s0 + du*0.5)
    P = 60/88*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _cov_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    s0, du, _ = ctx['cards'][ci]
    dd, mm, yy = _cal_at(ci, (t - s0)/max(du, 0.1))
    cx0, cy0 = 176, G - 104
    d.rectangle((cx0, cy0, cx0 + 64, cy0 + 70), fill=(246, 246, 240)); d.rectangle((cx0, cy0, cx0 + 64, cy0 + 16), fill=(205, 60, 60))
    d.rectangle((cx0 + 12, cy0 - 5, cx0 + 15, cy0 + 3), fill=(60, 60, 70)); d.rectangle((cx0 + 48, cy0 - 5, cx0 + 51, cy0 + 3), fill=(60, 60, 70))
    f1 = font(PS2, 8); f2 = font(PS2, 22); f3 = font(PS2, 8)
    d.text((cx0 + 32 - f1.getlength(mm)/2, cy0 + 4), mm, font=f1, fill=(255, 255, 255))
    d.text((cx0 + 32 - f2.getlength(dd)/2, cy0 + 24), dd, font=f2, fill=(40, 40, 50))
    d.text((cx0 + 32 - f3.getlength(yy)/2, cy0 + 56), yy, font=f3, fill=(120, 120, 130))
    # particulas flutuando (fundo)
    for k in range(6):
        vx = 118 + (k*37) % 140 + int(math.sin(t*0.9 + k*1.7)*6); vy = G - 150 + (k*23) % 70 + int(math.cos(t*0.7 + k)*5)
        c_ = (110, 130, 150)
        d.rectangle((vx, vy, vx + 7, vy + 7), fill=c_); d.rectangle((vx + 2, vy - 2, vx + 5, vy - 1), fill=c_); d.rectangle((vx + 2, vy + 8, vx + 5, vy + 9), fill=c_)
        d.rectangle((vx - 2, vy + 2, vx - 1, vy + 5), fill=c_); d.rectangle((vx + 8, vy + 2, vx + 9, vy + 5), fill=c_)
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    beat = t*th['bpm']/60
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # prancheta
    bx, by = MX + 70, y0 + 40
    d.rectangle((bx, by, bx + 24, by + 32), fill=(150, 110, 70)); d.rectangle((bx + 2, by + 3, bx + 22, by + 30), fill=(245, 245, 235)); d.rectangle((bx + 8, by - 2, bx + 16, by + 2), fill=(120, 120, 130))
    for yy_ in range(by + 8, by + 28, 5): d.rectangle((bx + 5, yy_, bx + 19, yy_ + 1), fill=(130, 130, 140))

KINDS.update({'apagao': (wrap(_apa_mascot), apa_setup), 'cenario': (wrap(_cen_mascot), cen_setup), 'covid': (wrap(_cov_mascot), cov_setup)})

# ---------- 18/11: BLOCOS (pixel genérico), STEAMBOAT (P&B), FIAT ----------
def blo_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('MINECRAFT', 'VERSÃO 1.0'))
    for tt in ctx['hits']: ev('ding', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i > 0: ev('clank', s0 + 0.2)
    P = 60/108*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _blo_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    n = min(ci + 1, 10)
    pal = [(110, 80, 50), (120, 120, 126), (90, 170, 80), (80, 200, 220)]
    for r in range(4):
        for c in range(5):
            if (r*5 + c) < n*2:
                bx, by = 150 + c*18, G - 18 - r*18
                col = pal[(r + c) % 4]
                d.rectangle((bx, by, bx + 17, by + 17), fill=dark(col, .75)); d.rectangle((bx + 1, by + 1, bx + 16, by + 16), fill=col)
                d.rectangle((bx + 3, by + 3, bx + 7, by + 7), fill=light(col, .25))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    sw = math.sin(beat*math.pi)*0.6 - 0.2
    hx, hy = MX + 74, y0 + 46
    ex, ey = hx + q(math.cos(sw)*26), hy + q(math.sin(sw)*26)
    for k in range(14):
        d.rectangle((hx + q(math.cos(sw)*k*1.9), hy + q(math.sin(sw)*k*1.9), hx + q(math.cos(sw)*k*1.9) + 2, hy + q(math.sin(sw)*k*1.9) + 2), fill=(120, 80, 45))
    d.rectangle((ex - 8, ey - 3, ex + 8, ey + 1), fill=(200, 205, 210)); d.rectangle((ex - 8, ey + 1, ex - 5, ey + 5), fill=(200, 205, 210)); d.rectangle((ex + 5, ey + 1, ex + 8, ey + 5), fill=(200, 205, 210))

def ste_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('O VAPOR WILLIE', 'SUCESSO!'))
    for tt in ctx['hits']: ev('whistle', tt); ev('applause', tt + 0.2)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1:
        ev('tick' if k % 2 else 'tap', k*P); k += 1

def _ste_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    wob = int(math.sin(t*2.2)*3)
    bx, by = 138, G - 60 + wob
    d.rectangle((bx, by + 30, bx + 110, by + 44), fill=(60, 60, 64)); d.rectangle((bx + 8, by + 44, bx + 102, by + 48), fill=(40, 40, 44))
    d.rectangle((bx + 14, by + 12, bx + 96, by + 30), fill=(235, 235, 235)); d.rectangle((bx + 22, by + 17, bx + 30, by + 24), fill=(50, 50, 54)); d.rectangle((bx + 46, by + 17, bx + 54, by + 24), fill=(50, 50, 54)); d.rectangle((bx + 70, by + 17, bx + 78, by + 24), fill=(50, 50, 54))
    for sx_ in (bx + 34, bx + 66):
        d.rectangle((sx_, by - 8, sx_ + 14, by + 12), fill=(40, 40, 44)); d.rectangle((sx_ - 2, by - 12, sx_ + 16, by - 8), fill=(20, 20, 24))
        for j in range(4):
            sm = (t*18 + j*9 + sx_) % 36
            r_ = 3 + int(sm/8)
            d.rectangle((sx_ + 4 + int(sm*0.5), by - 16 - int(sm), sx_ + 4 + int(sm*0.5) + r_, by - 16 - int(sm) + r_), fill=(210 - j*10, 210 - j*10, 214 - j*10))
    wr = int(t*8) % 4
    for k in range(4):
        d.rectangle((bx + 4 + k*3, by + 32 + (wr + k) % 4, bx + 6 + k*3, by + 34 + (wr + k) % 4), fill=(170, 170, 176))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # clapperboard de cinema
    cx_, cy_ = MX + 72, y0 + 42
    d.rectangle((cx_, cy_ + 6, cx_ + 24, cy_ + 28), fill=(40, 40, 44)); d.rectangle((cx_ + 2, cy_ + 12, cx_ + 22, cy_ + 26), fill=(230, 230, 230))
    ang = int(math.sin(beat*math.pi)*3)
    for k in range(6): d.rectangle((cx_ + k*4, cy_ + ang, cx_ + k*4 + 2, cy_ + 5 + ang), fill=(240, 240, 240) if k % 2 else (30, 30, 34))

def fia_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('FIAT 147', 'PIONEIRO!', 'CACHACINHA'))
    for tt in ctx['hits']: ev('horn', tt)
    P = 60/104*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _fia_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    bump = 1 if int(t*6) % 2 else 0
    cx0, cy0 = 134, G - 50 - bump
    body = (240, 200, 60)
    d.rectangle((cx0, cy0 + 14, cx0 + 108, cy0 + 36), fill=body); d.rectangle((cx0 + 22, cy0, cx0 + 82, cy0 + 14), fill=body)
    d.rectangle((cx0 + 28, cy0 + 3, cx0 + 50, cy0 + 13), fill=(170, 220, 240)); d.rectangle((cx0 + 54, cy0 + 3, cx0 + 76, cy0 + 13), fill=(170, 220, 240))
    d.rectangle((cx0 + 100, cy0 + 20, cx0 + 108, cy0 + 26), fill=(255, 250, 200)); d.rectangle((cx0, cy0 + 20, cx0 + 5, cy0 + 26), fill=(210, 40, 40))
    d.rectangle((cx0, cy0 + 32, cx0 + 108, cy0 + 36), fill=dark(body, .7))
    for wx in (cx0 + 22, cx0 + 82):
        d.rectangle((wx - 9, cy0 + 28 + bump, wx + 9, cy0 + 46 + bump), fill=(30, 30, 34)); d.rectangle((wx - 4, cy0 + 33 + bump, wx + 4, cy0 + 41 + bump), fill=(190, 190, 196))
    if int(t*3) % 2 == 0:
        for j in range(3): d.rectangle((cx0 - 8 - j*7, cy0 + 36 - j*3, cx0 - 4 - j*7, cy0 + 40 - j*3), fill=(220, 220, 225))
    # bomba de etanol
    px_, py_ = 258, G - 56
    d.rectangle((px_, py_, px_ + 22, py_ + 56), fill=(60, 160, 80)); d.rectangle((px_ + 3, py_ + 6, px_ + 19, py_ + 22), fill=(230, 240, 230)); d.rectangle((px_ + 6, py_ + 10, px_ + 16, py_ + 18), fill=(40, 40, 44))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # chave inglesa
    sw = math.sin(beat*math.pi)*0.5 - 0.3
    hx, hy = MX + 74, y0 + 48
    ex, ey = hx + q(math.cos(sw)*24), hy + q(math.sin(sw)*24)
    for k in range(12): d.rectangle((hx + q(math.cos(sw)*k*2), hy + q(math.sin(sw)*k*2), hx + q(math.cos(sw)*k*2) + 2, hy + q(math.sin(sw)*k*2) + 2), fill=(190, 190, 198))
    d.rectangle((ex - 4, ey - 4, ex + 5, ey + 5), fill=(190, 190, 198)); d.rectangle((ex - 1, ey - 4, ex + 2, ey), fill=(60, 60, 66))

KINDS.update({'blocos': (wrap(_blo_mascot), blo_setup), 'steamboat': (wrap(_ste_mascot), ste_setup), 'fiat': (wrap(_fia_mascot), fia_setup)})

# ---------- 19/11: VICE (GTA VI genérico), APOLLO, PELE ----------
def vic_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('GTA VI', 'ADIADO 2X!'))
    for tt in ctx['hits']: ev('ding', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i == 1: ev('pop', s0 + 0.3)
        if i == 2: ev('chime', s0 + 0.3)
    P = 60/112*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _vic_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # sol de neon
    d.rectangle((176, G - 120, 236, G - 100), fill=(255, 190, 90)); d.rectangle((166, G - 100, 246, G - 84), fill=(255, 120, 130)); d.rectangle((156, G - 84, 256, G - 70), fill=(255, 70, 160))
    for sx_, hh in ((150, 74), (252, 90)):
        sw = int(math.sin(t*1.6 + sx_)*3)
        d.rectangle((sx_, G - hh, sx_ + 5, G), fill=(90, 60, 40))
        for k in range(5):
            a = -2.6 + k*1.05
            ex, ey = sx_ + 3 + q(math.cos(a)*22) + sw, G - hh + q(math.sin(a)*12)
            d.rectangle((min(sx_ + 3, ex), min(G - hh, ey), max(sx_ + 3, ex) + 2, max(G - hh, ey) + 2), fill=(40, 170, 110))
    # relogio de contagem na carta 6 (meia-noite)
    if ci == 2:
        d.rectangle((176, G - 50, 232, G - 26), fill=(10, 10, 20)); d.rectangle((178, G - 48, 230, G - 28), outline=(255, 90, 180), width=2)
        f1 = font(PS2, 12); d.text((204 - f1.getlength('00:00')/2, G - 45), '00:00', font=f1, fill=(255, 90, 180))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # controle de videogame
    cx_, cy_ = MX + 66, y0 + 50 + (2 if int(beat*2) % 2 else 0)
    d.rectangle((cx_, cy_, cx_ + 30, cy_ + 14), fill=(40, 40, 52)); d.rectangle((cx_ - 3, cy_ + 4, cx_, cy_ + 14), fill=(40, 40, 52)); d.rectangle((cx_ + 30, cy_ + 4, cx_ + 33, cy_ + 14), fill=(40, 40, 52))
    d.rectangle((cx_ + 5, cy_ + 5, cx_ + 11, cy_ + 7), fill=(200, 200, 210)); d.rectangle((cx_ + 7, cy_ + 3, cx_ + 9, cy_ + 9), fill=(200, 200, 210))
    d.rectangle((cx_ + 21, cy_ + 4, cx_ + 24, cy_ + 7), fill=(255, 90, 180)); d.rectangle((cx_ + 25, cy_ + 8, cx_ + 28, cy_ + 11), fill=(80, 200, 220))

def apo_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('NA LUA!', 'SALVOU!'))
    for tt in ctx['hits']: ev('chime', tt)
    for i in (1, 2):
        s0, du, _ = ctx['cards'][min(i, len(ctx['cards'])-1)]
        ev('thunder', s0 + 1.2)
    P = 60/92*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _apo_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # Terra ao fundo
    d.rectangle((222, G - 150, 246, G - 126), fill=(60, 130, 220)); d.rectangle((226, G - 146, 234, G - 138), fill=(70, 180, 100)); d.rectangle((236, G - 140, 242, G - 132), fill=(240, 240, 250))
    storm = ci in (1, 2)
    if storm:
        for k in range(3):
            cx0 = 130 + k*55 + int(math.sin(t*0.8 + k)*6)
            d.rectangle((cx0, G - 160, cx0 + 44, G - 146), fill=(50, 52, 70)); d.rectangle((cx0 + 8, G - 168, cx0 + 36, G - 160), fill=(50, 52, 70))
        ph = (t*1.7) % 2.4
        if ph < 0.35:
            bx = 190 + int(ph*20)
            pts = [(bx, G - 146), (bx - 6, G - 120), (bx + 4, G - 116), (bx - 8, G - 80), (bx + 2, G - 78), (bx - 4, G - 40)]
            d.line(pts, fill=(255, 245, 160), width=4)
    else:
        # modulo lunar generico
        lx, ly = 176, G - 44
        d.rectangle((lx, ly, lx + 44, ly + 26), fill=(200, 170, 80)); d.rectangle((lx + 8, ly - 14, lx + 36, ly), fill=(215, 215, 225)); d.rectangle((lx + 14, ly - 9, lx + 30, ly - 3), fill=(40, 40, 60))
        for ox in (-8, 46): d.line([(lx + (4 if ox < 0 else 40), ly + 26), (lx + ox, G)], fill=(180, 180, 190), width=3)
        # bandeira generica verde
        d.rectangle((248, G - 60, 250, G), fill=(220, 220, 225)); d.rectangle((250, G - 60, 268, G - 46), fill=(80, 200, 120))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*18)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    if not storm: y0 += 0
    place(cv, d, spr, MX, y0)
    if storm and ((t*1.7) % 2.4) < 0.12:
        ov = Image.new('RGBA', (LW, LH), (255, 255, 230, 90)); cv.alpha_composite(ov)

def pel_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('GOL MIL', 'GOOOL!'))
    for tt in ctx['hits']: ev('whistle', tt); ev('applause', tt + 0.2)
    P = 60/108*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _pel_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # torcida ao fundo
    rr = random.Random(7)
    for k in range(34):
        px_ = 120 + (k*9) % 150; py_ = G - 100 + (k % 3)*7 + int(math.sin(t*3 + k)*2)
        d.rectangle((px_, py_, px_ + 5, py_ + 5), fill=rr.choice(((250, 210, 60), (240, 240, 240), (90, 180, 100), (230, 80, 80))))
    # trave com rede
    gx, gy = 214, G - 60
    d.rectangle((gx, gy, gx + 50, gy + 3), fill=(240, 240, 240)); d.rectangle((gx, gy, gx + 3, G), fill=(240, 240, 240)); d.rectangle((gx + 47, gy, gx + 50, G), fill=(240, 240, 240))
    for yy in range(gy + 8, G, 8): d.line([(gx + 3, yy), (gx + 47, yy)], fill=(200, 205, 210), width=1)
    for xx in range(gx + 10, gx + 47, 10): d.line([(xx, gy + 3), (xx, G)], fill=(200, 205, 210), width=1)
    hop = 0; kick = None
    for h in ctx['hits']:
        if 0 <= t - h < 1.2: hop = q(-abs(math.sin((t - h)*math.pi*3.0))*16); kick = t - h
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # camisa 10 generica
    d.rectangle((MX + 22, y0 + 74, MX + 34, y0 + 90), fill=(240, 240, 240)); f1 = font(PS2, 8); d.text((MX + 23, y0 + 77), '10', font=f1, fill=(30, 30, 30))
    # bola
    if kick is None:
        bx = MX + 84 + int(abs(math.sin(beat*math.pi))*0); by = G - 14 - int(abs(math.sin(beat*math.pi))*10)
    else:
        bx = MX + 84 + q(kick*110); by = G - 14 - q(math.sin(min(kick, 1.0)*math.pi)*30)
        bx = min(bx, gx + 36)
    d.rectangle((bx, by, bx + 12, by + 12), fill=(245, 245, 245)); d.rectangle((bx + 4, by + 4, bx + 8, by + 8), fill=(30, 30, 34)); d.rectangle((bx + 1, by + 1, bx + 3, by + 3), fill=(30, 30, 34)); d.rectangle((bx + 9, by + 9, bx + 11, by + 11), fill=(30, 30, 34))

KINDS.update({'vice': (wrap(_vic_mascot), vic_setup), 'apollo': (wrap(_apo_mascot), apo_setup), 'pele': (wrap(_pel_mascot), pel_setup)})

# ---------- 20/11: QUILOMBO (Consciencia Negra), WIN (Windows 1.0) ----------
def quil_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('ZUMBI', 'FERIADO!'))
    for tt in ctx['hits']: ev('chime', tt)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _quil_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # serra ao fundo
    d.polygon([(110, G - 40), (170, G - 120), (215, G - 85), (255, G - 130), (270, G - 110), (270, G - 40)], fill=(60, 80, 40))
    # paliçada
    for k in range(12):
        x = 140 + k*11; h = 44 + (k % 3)*4
        d.rectangle((x, G - h, x + 8, G), fill=(120, 80, 45)); d.polygon([(x, G - h), (x + 4, G - h - 6), (x + 8, G - h)], fill=(120, 80, 45))
        d.rectangle((x + 1, G - h + 4, x + 2, G - 2), fill=(95, 60, 35))
    d.rectangle((140, G - 30, 272, G - 26), fill=(90, 58, 30))
    # palmeiras
    for sx_, hh in ((128, 96), (262, 110)):
        sw = int(math.sin(t*1.4 + sx_)*3)
        d.rectangle((sx_, G - hh, sx_ + 4, G), fill=(100, 70, 40))
        for kk in range(5):
            a = -2.6 + kk*1.05
            ex, ey = sx_ + 2 + q(math.cos(a)*20) + sw, G - hh + q(math.sin(a)*10)
            d.line([(sx_ + 2, G - hh), (ex, ey)], fill=(50, 140, 70), width=3)
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*14)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # atabaque
    ax, ay = MX + 70, G - 34
    d.rectangle((ax, ay, ax + 20, G), fill=(150, 90, 45)); d.rectangle((ax - 2, ay - 3, ax + 22, ay + 1), fill=(230, 210, 170))
    for yy in (ay + 8, ay + 20): d.rectangle((ax, yy, ax + 20, yy + 2), fill=(250, 200, 60))
    for kk in range(4): d.line([(ax + 2 + kk*5, ay + 1), (ax + 4 + kk*5, ay + 8)], fill=(90, 50, 25), width=1)
    if int(beat*2) % 2 == 0:
        d.rectangle((ax + 4, ay - 8, ax + 9, ay - 4), fill=(250, 200, 60)); d.rectangle((ax + 12, ay - 10, ax + 16, ay - 6), fill=(250, 200, 60))

def win_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('WINDOWS 1.0', 'FRACASSO?!'))
    for tt in ctx['hits']: ev('ding', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i == 2: ev('thud', s0 + 0.4)
    P = 60/110*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _win_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # computador CRT generico
    cx, cy = 168, G - 92
    d.rectangle((cx, cy, cx + 76, cy + 60), fill=(215, 210, 190)); d.rectangle((cx + 6, cy + 6, cx + 70, cy + 50), fill=(20, 30, 90))
    # janelas genericas no monitor
    ws = [((cx + 10, cy + 10, cx + 44, cy + 32), (240, 240, 240)), ((cx + 30, cy + 22, cx + 66, cy + 46), (230, 230, 230))]
    for k, (r, c) in enumerate(ws):
        if (t*0.8 + k*0.5) % 3 < 2.7:
            d.rectangle(r, fill=c); d.rectangle((r[0], r[1], r[2], r[1] + 4), fill=(60, 120, 220))
    if ci == 1:  # ampulheta de espera
        hx, hy = cx + 34, cy + 20
        d.polygon([(hx, hy), (hx + 10, hy), (hx + 5, hy + 7)], fill=(250, 250, 250)); d.polygon([(hx, hy + 14), (hx + 10, hy + 14), (hx + 5, hy + 7)], fill=(250, 250, 250))
    d.rectangle((cx + 20, cy + 60, cx + 56, cy + 66), fill=(190, 185, 165)); d.rectangle((cx + 4, cy + 66, cx + 72, cy + 74), fill=(225, 220, 200))
    d.rectangle((cx + 8, cy + 76, cx + 70, cy + 86), fill=(200, 195, 175))
    for kk in range(10): d.rectangle((cx + 10 + kk*6, cy + 78, cx + 14 + kk*6, cy + 82), fill=(150, 145, 130))
    # pilha de disquetes
    for kk in range(4):
        fx, fy = 252, G - 10 - kk*9
        d.rectangle((fx, fy, fx + 16, fy + 8), fill=(40, 40, 50)); d.rectangle((fx + 4, fy + 1, fx + 12, fy + 4), fill=(190, 190, 200))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'quilombo': (wrap(_quil_mascot), quil_setup), 'win': (wrap(_win_mascot), win_setup)})

# ---------- 21/11: TVDAY (TV de tubo com antena), GUGU (palco/auditório), SNES (console 16 bits genérico) ----------
def tv_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('TELEVISÃO', 'NO AR!'))
    for tt in ctx['hits']: ev('ding', tt)
    P = 60/104*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _tv_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    tx, ty = 170, G - 96
    # antena
    sw = int(math.sin(t*2)*3)
    d.line([(tx + 38, ty), (tx + 18 + sw, ty - 30)], fill=(200, 200, 210), width=2)
    d.line([(tx + 38, ty), (tx + 58 + sw, ty - 30)], fill=(200, 200, 210), width=2)
    d.rectangle((tx + 32, ty - 4, tx + 44, ty + 2), fill=(60, 50, 40))
    # gabinete de madeira
    d.rectangle((tx, ty, tx + 80, ty + 70), fill=(140, 90, 50)); d.rectangle((tx + 4, ty + 4, tx + 60, ty + 60), fill=(30, 30, 30))
    sx0, sy0, sx1, sy1 = tx + 8, ty + 8, tx + 56, ty + 56
    phase = int(t*1.2) % 3 if ci != 0 else (0 if t % 2 < 1 else 1)
    if phase == 0:  # chiado
        for k in range(60):
            px = sx0 + (k*37 + int(t*90)*13) % (sx1 - sx0); py = sy0 + (k*53 + int(t*90)*7) % (sy1 - sy0)
            v = 120 + (k*71 + int(t*60)) % 130; d.rectangle((px, py, px + 2, py + 2), fill=(v, v, v))
        d.rectangle((sx0, sy0, sx1, sy1), outline=(80, 80, 80))
    else:  # barras de cor
        cols = [(230, 230, 230), (230, 220, 40), (40, 210, 220), (40, 200, 60), (210, 40, 200), (220, 40, 40), (40, 40, 220)]
        w = (sx1 - sx0) / 7
        for k, c in enumerate(cols): d.rectangle((sx0 + int(k*w), sy0, sx0 + int((k + 1)*w), sy1 - 12), fill=c)
        d.rectangle((sx0, sy1 - 12, sx1, sy1), fill=(20, 20, 60))
    # botões
    for k in range(2): d.ellipse((tx + 64, ty + 10 + k*16, tx + 74, ty + 20 + k*16), fill=(220, 200, 150))
    for k in range(4): d.rectangle((tx + 64, ty + 46 + k*4, tx + 76, ty + 47 + k*4), fill=(90, 60, 30))
    d.rectangle((tx + 8, ty + 70, tx + 14, G), fill=(90, 60, 30)); d.rectangle((tx + 66, ty + 70, tx + 72, G), fill=(90, 60, 30))
    # controle remoto piscando
    rx, ry = 256, G - 18
    d.rectangle((rx, ry, rx + 10, ry + 18), fill=(40, 40, 45))
    d.rectangle((rx + 3, ry + 3, rx + 7, ry + 6), fill=(230, 50, 50) if int(beat*2) % 2 else (90, 30, 30))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def gugu_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('GUGU', 'AUDIÊNCIA!'))
    for i, tt in enumerate(ctx['hits']): ev('applause' if i == 1 else 'chime', tt)
    P = 60/84*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _gugu_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    sad = ci == 3
    cur = (150, 25, 40) if not sad else (90, 20, 30); fold = (110, 15, 30) if not sad else (60, 12, 20)
    # cortinas nas laterais
    for x0, x1, sgn in ((0, 26, 1), (244, 270, -1)):
        d.rectangle((x0, G - 120, x1, G), fill=cur)
        for k in range(4): d.rectangle((x0 + 3 + k*6, G - 120, x0 + 4 + k*6, G), fill=fold)
        d.rectangle((x0, G - 124, x1, G - 118), fill=(200, 160, 60))
    # holofote no chão atrás do mascote
    for j in range(5):
        d.ellipse((MX - 14 - j*4, G - 6 - j, MX + 66 + j*4, G + 4 + j), outline=(255, 235, 170) if not sad else (170, 170, 210))
    # estrela
    sx, sy = 200, G - 110 + q(math.sin(t*1.5)*3)
    r = 7 if int(t*3) % 2 else 5
    d.polygon([(sx, sy - r), (sx + 2, sy - 2), (sx + r, sy), (sx + 2, sy + 2), (sx, sy + r), (sx - 2, sy + 2), (sx - r, sy), (sx - 2, sy - 2)], fill=(255, 220, 90))
    # pedestal de microfone
    mx = 170
    d.rectangle((mx, G - 64, mx + 2, G), fill=(90, 90, 95)); d.rectangle((mx - 8, G - 3, mx + 10, G), fill=(90, 90, 95))
    d.ellipse((mx - 3, G - 74, mx + 5, G - 62), fill=(40, 40, 45)); d.rectangle((mx - 2, G - 72, mx + 4, G - 70), fill=(170, 170, 180))
    # plateia
    for k in range(4):
        hx = 192 + k*12; d.ellipse((hx, G - 14, hx + 10, G - 4), fill=(45, 35, 55)); d.rectangle((hx - 1, G - 6, hx + 11, G), fill=(45, 35, 55))
    if not sad and 'hits' in ctx and len(ctx['hits']) > 1 and 0 <= t - ctx['hits'][1] < 2.5:
        for k in range(4):
            if int(t*10 + k) % 2: d.rectangle((194 + k*12, G - 22, 198 + k*12, G - 18), fill=(250, 220, 170))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*14)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (0 if sad else (2 if int(beat) % 2 else 0))
    place(cv, d, spr, MX, y0)

def snes_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('SUPER NINTENDO', 'ESGOTOU!'))
    for tt in ctx['hits']: ev('ding', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i == 0: ev('boot', s0 + 0.2)
        if i == 1: ev('engine', s0 + 0.3, dur=min(du - 0.5, 3.5))
    P = 60/120; k = 0
    while k*P < ctx['total'] - 1: ev('blip', k*P, k=k); k += 1

def _snes_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    if ci == 1:  # lua e caminhão na madrugada
        d.ellipse((240, G - 170, 262, G - 148), fill=(240, 240, 210)); d.ellipse((248, G - 172, 268, G - 152), fill=th.get('sky_top', (20, 20, 50)))
        s0 = ctx['cards'][1][0]
        tx = 300 - int(((t - s0)*55) % 260)
        d.rectangle((tx, G - 26, tx + 34, G - 6), fill=(230, 230, 235)); d.rectangle((tx - 14, G - 20, tx, G - 6), fill=(70, 90, 160))
        d.rectangle((tx - 12, G - 18, tx - 4, G - 12), fill=(170, 210, 240))
        for wx in (tx - 8, tx + 8, tx + 26): d.ellipse((wx, G - 10, wx + 8, G - 2), fill=(30, 30, 30))
        d.polygon([(tx - 14, G - 14), (tx - 40, G - 22), (tx - 40, G - 6)], fill=(255, 250, 180))
    # console genérico 16 bits
    cx, cy = 140, G - 40
    d.rectangle((cx, cy, cx + 78, cy + 30), fill=(205, 205, 210)); d.rectangle((cx + 4, cy - 6, cx + 74, cy), fill=(190, 190, 196))
    d.rectangle((cx + 22, cy - 10, cx + 56, cy - 4), fill=(60, 60, 65))
    # cartucho entra no gancho
    cart_y = cy - 30
    for h in ctx['hits']:
        if 0 <= t - h < 0.5: cart_y = cy - 30 - int((0.5 - (t - h))*30)
    d.rectangle((cx + 25, cart_y, cx + 53, cy - 6), fill=(80, 80, 88)); d.rectangle((cx + 29, cart_y + 4, cx + 49, cart_y + 14), fill=(200, 60, 60))
    for k, c in enumerate(((150, 120, 220), (150, 120, 220))): d.rectangle((cx + 8 + k*52, cy + 8, cx + 18 + k*52, cy + 14), fill=c)
    d.ellipse((cx + 34, cy + 18, cx + 42, cy + 24), fill=(220, 40, 40) if int(beat) % 2 else (120, 30, 30))
    # controle com 4 botões coloridos
    jx, jy = 226, G - 14
    d.line([(cx + 70, cy + 28), (jx, jy + 6)], fill=(60, 60, 60), width=1)
    d.rounded_rectangle((jx, jy, jx + 34, jy + 14), radius=6, fill=(200, 200, 205))
    d.rectangle((jx + 4, jy + 6, jx + 12, jy + 8), fill=(60, 60, 60)); d.rectangle((jx + 7, jy + 3, jx + 9, jy + 11), fill=(60, 60, 60))
    bc = [(230, 50, 50), (240, 200, 40), (50, 120, 230), (50, 180, 80)]
    pos = [(26, 7), (22, 3), (22, 10), (18, 7)]
    lit = int(beat*2) % 4
    for k, ((bx, by), c) in enumerate(zip(pos, bc)):
        cc = c if k == lit else tuple(int(v*0.55) for v in c)
        d.rectangle((jx + bx, jy + by, jx + bx + 3, jy + by + 3), fill=cc)
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'tvday': (wrap(_tv_mascot), tv_setup), 'gugu': (wrap(_gugu_mascot), gugu_setup), 'snes': (wrap(_snes_mascot), snes_setup)})

# ---------- 22/11: JFK (TV P&B com plantão + jornal), JUSTICA (colunas, martelo, tornozeleira, relógio 00:08), SCARLETT (set de filmagem + bolo) ----------
def jfk_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('KENNEDY', 'AO VIVO!'))
    for tt in ctx['hits']: ev('thud', tt)
    P = 60/88*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _jfk_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    tx, ty = 170, G - 92
    d.line([(tx + 38, ty), (tx + 22, ty - 26)], fill=(190, 190, 190), width=2); d.line([(tx + 38, ty), (tx + 54, ty - 26)], fill=(190, 190, 190), width=2)
    d.rectangle((tx, ty, tx + 80, ty + 66), fill=(110, 80, 55)); d.rectangle((tx + 6, ty + 6, tx + 60, ty + 56), fill=(30, 30, 30))
    sx0, sy0, sx1, sy1 = tx + 9, ty + 9, tx + 57, ty + 53
    g = 150 + int(abs(math.sin(t*9))*40)
    d.rectangle((sx0, sy0, sx1, sy1), fill=(g - 60, g - 60, g - 60))
    if int(t*2) % 2 == 0 or ci != 0:
        d.rectangle((sx0 + 4, sy0 + 16, sx1 - 4, sy0 + 28), fill=(235, 235, 235))
        for k in range(6): d.rectangle((sx0 + 7 + k*7, sy0 + 20, sx0 + 11 + k*7, sy0 + 24), fill=(30, 30, 30))
    for k in range(0, sy1 - sy0, 3): d.line([(sx0, sy0 + k), (sx1, sy0 + k)], fill=(g - 90, g - 90, g - 90))
    for k in range(2): d.ellipse((tx + 64, ty + 10 + k*16, tx + 74, ty + 20 + k*16), fill=(200, 190, 160))
    d.rectangle((tx + 8, ty + 66, tx + 14, G), fill=(80, 60, 40)); d.rectangle((tx + 66, ty + 66, tx + 72, G), fill=(80, 60, 40))
    # jornal no chão
    nx, ny = 250, G - 12
    d.rectangle((nx, ny, nx + 18, ny + 12), fill=(230, 225, 210)); d.rectangle((nx + 2, ny + 2, nx + 16, ny + 4), fill=(40, 40, 40))
    for k in range(3): d.rectangle((nx + 2, ny + 6 + k*2, nx + 16, ny + 6 + k*2), fill=(140, 140, 140))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*12)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def jus_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BOLSONARO', 'DEFINITIVA'))
    for tt in ctx['hits']: ev('thud', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i == 1: ev('ding', s0 + 0.5)
    P = 60/92*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _jus_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # fachada com colunas
    bx = 150
    d.polygon([(bx - 6, G - 104), (bx + 60, G - 128), (bx + 126, G - 104)], fill=(215, 215, 220))
    d.rectangle((bx - 6, G - 104, bx + 126, G - 98), fill=(190, 190, 200))
    for k in range(5):
        cx = bx + 4 + k*26
        d.rectangle((cx, G - 98, cx + 10, G - 6), fill=(225, 225, 230)); d.rectangle((cx + 2, G - 98, cx + 3, G - 6), fill=(200, 200, 205))
    d.rectangle((bx - 10, G - 6, bx + 130, G), fill=(180, 180, 190))
    # relógio digital 00:08 (tela 1)
    if ci == 1:
        d.rectangle((bx + 30, G - 150, bx + 90, G - 134), fill=(20, 20, 25))
        on = int(t*2) % 2 == 0
        col = (255, 70, 70) if on else (120, 30, 30)
        digs = '0008'
        seg = {'0': ['a', 'b', 'c', 'd', 'e', 'f'], '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g']}
        for k, ch in enumerate(digs):
            x0 = bx + 34 + k*13 + (4 if k >= 2 else 0); y0_ = G - 147
            S = seg[ch]
            if 'a' in S: d.rectangle((x0, y0_, x0 + 6, y0_ + 1), fill=col)
            if 'g' in S: d.rectangle((x0, y0_ + 5, x0 + 6, y0_ + 6), fill=col)
            if 'd' in S: d.rectangle((x0, y0_ + 10, x0 + 6, y0_ + 11), fill=col)
            if 'f' in S: d.rectangle((x0, y0_, x0 + 1, y0_ + 5), fill=col)
            if 'b' in S: d.rectangle((x0 + 5, y0_, x0 + 6, y0_ + 5), fill=col)
            if 'e' in S: d.rectangle((x0, y0_ + 5, x0 + 1, y0_ + 11), fill=col)
            if 'c' in S: d.rectangle((x0 + 5, y0_ + 5, x0 + 6, y0_ + 11), fill=col)
        d.rectangle((bx + 59, G - 144, bx + 60, G - 143), fill=col); d.rectangle((bx + 59, G - 139, bx + 60, G - 138), fill=col)
    # tornozeleira com luz piscando
    ax, ay = MX + 8, G - 6
    d.rectangle((ax, ay, ax + 20, ay + 6), fill=(30, 30, 35)); d.rectangle((ax + 7, ay - 4, ax + 15, ay + 6), fill=(50, 50, 55))
    d.rectangle((ax + 9, ay - 2, ax + 12, ay + 1), fill=(255, 50, 50) if int(beat*2) % 2 else (60, 200, 80))
    # martelo que bate nos títulos
    gx, gy = MX + 70, G - 30
    ang = 0.0
    for h in ctx['hits']:
        if 0 <= t - h < 0.35: ang = 0.9*(1 - (t - h)/0.35)
    d.rectangle((gx - 4, G - 8, gx + 22, G - 2), fill=(120, 80, 45))
    hx, hy = gx + 9 + int(math.sin(ang)*14), gy - int(math.cos(ang)*4)
    d.line([(gx + 20, gy + 10), (hx, hy)], fill=(140, 95, 55), width=2)
    d.rectangle((hx - 6, hy - 4, hx + 6, hy + 4), fill=(110, 70, 40))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.6: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*8)
    spr = face_sprite(base, t, talking)
    y0 = G - 86 + hop + jumpoff(jump) + (1 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def sca_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('SCARLETT', '9 FILMES'))
    for i, tt in enumerate(ctx['hits']): ev('applause' if i == 0 else 'ding', tt)
    P = 60/112; k = 0
    while k*P < ctx['total'] - 1: ev('blip', k*P, k=k); k += 1

def _sca_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # claquete
    cx, cy = 168, G - 44
    d.rectangle((cx, cy, cx + 40, cy + 30), fill=(30, 30, 35))
    for k in range(3): d.rectangle((cx + 4, cy + 8 + k*7, cx + 36, cy + 9 + k*7), fill=(220, 220, 220))
    op = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.4: op = int((0.4 - (t - h))*30)
    d.polygon([(cx, cy - 1), (cx + 40, cy - 1 - op), (cx + 40, cy - 7 - op), (cx, cy - 7)], fill=(240, 240, 240))
    for k in range(4): d.polygon([(cx + 4 + k*9, cy - 1 - op*(4 + k*9)//40), (cx + 9 + k*9, cy - 1 - op*(9 + k*9)//40), (cx + 9 + k*9, cy - 7 - op*(9 + k*9)//40), (cx + 4 + k*9, cy - 7 - op*(4 + k*9)//40)], fill=(30, 30, 35))
    # bolo com velas
    kx, ky = 222, G - 26
    d.rectangle((kx, ky, kx + 40, ky + 26), fill=(240, 170, 190)); d.rectangle((kx, ky, kx + 40, ky + 6), fill=(255, 245, 250))
    for k in range(5): d.ellipse((kx + 2 + k*8, ky + 3, kx + 8 + k*8, ky + 9), fill=(255, 245, 250))
    for k in range(2):
        vx = kx + 13 + k*12
        d.rectangle((vx, ky - 12, vx + 3, ky), fill=(120, 180, 255) if k else (255, 220, 90))
        fl = 2 if int(t*8 + k) % 2 else 0
        d.ellipse((vx - 1, ky - 18 - fl, vx + 4, ky - 12), fill=(255, 190, 60)); d.ellipse((vx, ky - 16 - fl, vx + 3, ky - 13), fill=(255, 250, 200))
    # confete
    for k in range(14):
        px = (k*37 + int(t*30)) % 270; py = (k*53 + int(t*40)) % 150 + int(G - 200)
        if int(beat + k) % 3: d.rectangle((px, py, px + 2, py + 2), fill=[(255, 90, 120), (255, 210, 70), (120, 200, 255), (140, 230, 140)][k % 4])
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'jfk': (wrap(_jfk_mascot), jfk_setup), 'justica': (wrap(_jus_mascot), jus_setup), 'scarlett': (wrap(_sca_mascot), sca_setup)})

# ---------- 23/11: LIBERTA (final 2019), ONIBUS (Maduro), TIMBAL (Carlinhos Brown) ----------
def lib_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('LIBERTADORES', 'GOOOL!'))
    for tt in ctx['hits']: ev('whistle', tt); ev('applause', tt + 0.2)
    P = 60/108*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _lib_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # torcida ao fundo
    rr = random.Random(7)
    for k in range(34):
        px_ = 120 + (k*9) % 150; py_ = G - 100 + (k % 3)*7 + int(math.sin(t*3 + k)*2)
        d.rectangle((px_, py_, px_ + 5, py_ + 5), fill=rr.choice(((220, 30, 40), (25, 25, 25), (220, 30, 40), (240, 240, 240))))
    # trave com rede
    gx, gy = 214, G - 60
    d.rectangle((gx, gy, gx + 50, gy + 3), fill=(240, 240, 240)); d.rectangle((gx, gy, gx + 3, G), fill=(240, 240, 240)); d.rectangle((gx + 47, gy, gx + 50, G), fill=(240, 240, 240))
    for yy in range(gy + 8, G, 8): d.line([(gx + 3, yy), (gx + 47, yy)], fill=(200, 205, 210), width=1)
    for xx in range(gx + 10, gx + 47, 10): d.line([(xx, gy + 3), (xx, G)], fill=(200, 205, 210), width=1)
    hop = 0; kick = None
    for h in ctx['hits']:
        if 0 <= t - h < 1.2: hop = q(-abs(math.sin((t - h)*math.pi*3.0))*16); kick = t - h
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # camisa 10 generica
    d.rectangle((MX + 22, y0 + 74, MX + 34, y0 + 90), fill=(200, 25, 35)); d.rectangle((MX + 22, y0 + 80, MX + 34, y0 + 83), fill=(25, 25, 25)); f1 = font(PS2, 8); d.text((MX + 25, y0 + 77), '9', font=f1, fill=(255, 255, 255))
    # bola
    if kick is None:
        bx = MX + 84 + int(abs(math.sin(beat*math.pi))*0); by = G - 14 - int(abs(math.sin(beat*math.pi))*10)
    else:
        bx = MX + 84 + q(kick*110); by = G - 14 - q(math.sin(min(kick, 1.0)*math.pi)*30)
        bx = min(bx, gx + 36)
    d.rectangle((bx, by, bx + 12, by + 12), fill=(245, 245, 245)); d.rectangle((bx + 4, by + 4, bx + 8, by + 8), fill=(30, 30, 34)); d.rectangle((bx + 1, by + 1, bx + 3, by + 3), fill=(30, 30, 34)); d.rectangle((bx + 9, by + 9, bx + 11, by + 11), fill=(30, 30, 34))


def oni_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('MADURO', 'CAPTURADO'))
    for tt in ctx['hits']: ev('thud', tt)
    for i, (s0, du, _) in enumerate(ctx['cards']):
        if i == 1: ev('horn', s0 + 0.4)
    P = 60/96*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _oni_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # prédios ao fundo
    for k, (x0, h) in enumerate(((120, 70), (150, 100), (186, 84), (220, 120), (250, 76))):
        d.rectangle((x0, G - h, x0 + 26, G), fill=(70, 75, 95))
        for yy in range(G - h + 6, G - 8, 10):
            for xx in (x0 + 5, x0 + 15):
                if (xx + yy + int(t)) % 3: d.rectangle((xx, yy, xx + 4, yy + 4), fill=(250, 220, 120))
    # ônibus atravessando
    s0 = ctx['cards'][min(ci, len(ctx['cards']) - 1)][0]
    bx = 300 - int(((t - s0)*45) % 300)
    d.rectangle((bx, G - 34, bx + 70, G - 8), fill=(240, 200, 40)); d.rectangle((bx, G - 34, bx + 70, G - 30), fill=(200, 60, 50))
    for k in range(5): d.rectangle((bx + 4 + k*13, G - 28, bx + 14 + k*13, G - 19), fill=(170, 210, 240))
    for wx in (bx + 8, bx + 52): d.ellipse((wx, G - 12, wx + 11, G - 1), fill=(30, 30, 30))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.7: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*10)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (1 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def tim_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BROWN', 'TIMBALADA'))
    for tt in ctx['hits']: ev('applause', tt)
    P = 60/110/2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _tim_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    cols = [(240, 60, 60), (250, 200, 40), (60, 170, 90), (60, 130, 230)]
    # timbaus coloridos
    for k in range(3):
        x0 = 168 + k*30; h = 40 + k*6; y0_ = G - h
        hit = int(beat*2) % 3 == k
        d.polygon([(x0, y0_), (x0 + 22, y0_), (x0 + 18, G), (x0 + 4, G)], fill=cols[k])
        d.rectangle((x0 - 1, y0_ - 3 + (2 if hit else 0), x0 + 23, y0_ + (2 if hit else 0)), fill=(240, 230, 200))
        for yy in (y0_ + 10, y0_ + 22): d.rectangle((x0 + 2, yy, x0 + 20, yy + 2), fill=cols[(k + 1) % 4])
        if hit:
            d.rectangle((x0 + 4, y0_ - 12, x0 + 8, y0_ - 8), fill=(255, 255, 255)); d.rectangle((x0 + 14, y0_ - 14, x0 + 18, y0_ - 10), fill=(255, 255, 255))
    # notas musicais
    for k in range(4):
        nx = 140 + k*34; ny = G - 120 - int(((t*25 + k*30) % 60))
        d.rectangle((nx, ny, nx + 4, ny + 4), fill=cols[k]); d.rectangle((nx + 3, ny - 10, nx + 4, ny), fill=cols[k]); d.rectangle((nx + 4, ny - 10, nx + 8, ny - 8), fill=cols[k])
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (3 if int(beat*2) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'liberta': (wrap(_lib_mascot), lib_setup), 'onibus': (wrap(_oni_mascot), oni_setup), 'timbal': (wrap(_tim_mascot), tim_setup)})

# ---------- 24/11: ROCK (palco com amplificadores), HOSP (hospital genérico), FOSSIL (escavação no deserto) ----------
def rock_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('FREDDIE', 'TOPO DE NOVO!'))
    for i, tt in enumerate(ctx['hits']): ev('applause', tt)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _rock_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    sad = ci == 1
    # amplificadores
    for x0 in (150, 210):
        for r in range(2):
            y0_ = G - 40 - r*38
            d.rectangle((x0, y0_, x0 + 52, y0_ + 36), fill=(30, 30, 32)); d.rectangle((x0 + 3, y0_ + 3, x0 + 49, y0_ + 33), fill=(55, 55, 58))
            for cx_ in (x0 + 14, x0 + 38):
                pulse = 2 if (int(beat*2) % 2 and not sad) else 0
                d.ellipse((cx_ - 9 - pulse, y0_ + 9 - pulse, cx_ + 9 + pulse, y0_ + 27 + pulse), fill=(20, 20, 22))
                d.ellipse((cx_ - 3, y0_ + 15, cx_ + 3, y0_ + 21), fill=(90, 90, 95))
    # holofotes coloridos no alto
    cols = [(255, 80, 120), (255, 210, 60), (90, 160, 255)]
    for k in range(3):
        if sad and k != 1: continue
        lx = 140 + k*50
        on = (int(beat) + k) % 3 != 0 or sad
        if on:
            for j in range(0, 60, 3):
                f = j/60; xa = int(lx - 4 - f*20); xb = int(lx + 4 + f*20)
                if (j//3 + int(t*6)) % 2 == 0: d.line([(xa, G - 190 + j*2), (xb, G - 190 + j*2)], fill=cols[k] if not sad else (200, 200, 230), width=1)
    # pedestal de microfone
    mx = MX + 64
    d.rectangle((mx, G - 64, mx + 2, G), fill=(170, 170, 175)); d.rectangle((mx - 8, G - 3, mx + 10, G), fill=(170, 170, 175))
    d.ellipse((mx - 3, G - 74, mx + 5, G - 62), fill=(40, 40, 45))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (0 if sad else (2 if int(beat) % 2 else 0))
    place(cv, d, spr, MX, y0)

def hosp_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('KATHERINE', 'EMMY!'))
    for tt in ctx['hits']: ev('ding', tt)
    P = 60/104*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _hosp_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # monitor cardíaco
    mx0, my0 = 166, G - 110
    d.rectangle((mx0, my0, mx0 + 70, my0 + 46), fill=(60, 64, 70)); d.rectangle((mx0 + 4, my0 + 4, mx0 + 66, my0 + 40), fill=(10, 25, 20))
    pts = []
    for x in range(62):
        ph = (x + int(t*40)) % 31
        yy = 22 + (-14 if ph == 10 else (10 if ph == 12 else (-4 if ph == 8 else 0)))
        pts.append((mx0 + 4 + x, my0 + yy))
    d.line(pts, fill=(80, 255, 120), width=1)
    d.rectangle((mx0 + 32, my0 + 46, mx0 + 36, G), fill=(120, 124, 130)); d.rectangle((mx0 + 20, G - 3, mx0 + 48, G), fill=(120, 124, 130))
    # cruz vermelha
    d.rectangle((250, G - 150, 258, G - 126), fill=(230, 50, 60)); d.rectangle((242, G - 142, 266, G - 134), fill=(230, 50, 60))
    # troféu dourado genérico
    tx, ty = 246, G - 36
    d.rectangle((tx + 6, ty + 26, tx + 20, ty + 36), fill=(120, 90, 40))
    d.rectangle((tx + 11, ty + 14, tx + 15, ty + 26), fill=(240, 200, 70))
    d.ellipse((tx + 3, ty, tx + 23, ty + 18), fill=(250, 210, 80))
    if int(t*3) % 2: d.rectangle((tx + 7, ty + 4, tx + 9, ty + 6), fill=(255, 255, 220))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # estetoscópio no pescoço
    d.arc((MX + 14, y0 + 62, MX + 46, y0 + 88), 0, 180, fill=(60, 60, 70), width=2)
    d.ellipse((MX + 40, y0 + 80, MX + 48, y0 + 88), fill=(180, 180, 190))

def fos_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('LUCY', 'DE PÉ!'))
    for tt in ctx['hits']: ev('chime', tt)
    P = 60/96*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _fos_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # dunas e cacto
    d.polygon([(110, G), (170, G - 40), (230, G - 10), (270, G - 50), (270, G)], fill=(210, 160, 100))
    # ossos no chão (revelados aos poucos)
    s0 = ctx['cards'][min(ci, len(ctx['cards']) - 1)][0]
    rev = min(1.0, (t - s0)/2.0) if ci >= 1 else 0.3
    bx, by = 172, G - 14
    bones = [(0, 0, 22, 4), (26, -4, 40, 0), (6, -10, 18, -6), (44, 0, 64, 4), (30, 6, 46, 10)]
    for k, (a, b, c, e) in enumerate(bones):
        if k/len(bones) <= rev:
            d.rectangle((bx + a, by + b, bx + c, by + e), fill=(245, 235, 210))
            d.ellipse((bx + a - 2, by + b - 2, bx + a + 3, by + e + 2), fill=(245, 235, 210)); d.ellipse((bx + c - 3, by + b - 2, bx + c + 2, by + e + 2), fill=(245, 235, 210))
    # pincel de arqueólogo balançando
    sw = int(math.sin(t*6)*6)
    d.line([(bx + 30 + sw, by - 30), (bx + 36 + sw, by - 6)], fill=(140, 90, 50), width=2)
    d.rectangle((bx + 34 + sw, by - 8, bx + 40 + sw, by - 2), fill=(230, 200, 120))
    # gravador de fita (tela 2)
    if ci == 2:
        rx, ry = 236, G - 22
        d.rectangle((rx, ry, rx + 30, ry + 18), fill=(50, 50, 55)); d.ellipse((rx + 4, ry + 4, rx + 12, ry + 12), fill=(200, 200, 200)); d.ellipse((rx + 18, ry + 4, rx + 26, ry + 12), fill=(200, 200, 200))
        nx = rx + 10 + int((t*20) % 20); ny = ry - 10 - int((t*15) % 20)
        d.rectangle((nx, ny, nx + 3, ny + 3), fill=(255, 220, 90)); d.rectangle((nx + 3, ny - 7, nx + 4, ny), fill=(255, 220, 90))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'rock': (wrap(_rock_mascot), rock_setup), 'hosp': (wrap(_hosp_mascot), hosp_setup), 'fossil': (wrap(_fos_mascot), fos_setup)})

# ---------- 25/11: BEST (camisa 7 vermelha), ACARAJE (tabuleiro da baiana) ----------
def best_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BEST', 'GOOOL!'))
    for tt in ctx['hits']: ev('whistle', tt); ev('applause', tt + 0.2)
    P = 60/108*2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _best_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # torcida ao fundo
    rr = random.Random(7)
    for k in range(34):
        px_ = 120 + (k*9) % 150; py_ = G - 100 + (k % 3)*7 + int(math.sin(t*3 + k)*2)
        d.rectangle((px_, py_, px_ + 5, py_ + 5), fill=rr.choice(((220, 30, 40), (25, 25, 25), (220, 30, 40), (240, 240, 240))))
    # trave com rede
    gx, gy = 214, G - 60
    d.rectangle((gx, gy, gx + 50, gy + 3), fill=(240, 240, 240)); d.rectangle((gx, gy, gx + 3, G), fill=(240, 240, 240)); d.rectangle((gx + 47, gy, gx + 50, G), fill=(240, 240, 240))
    for yy in range(gy + 8, G, 8): d.line([(gx + 3, yy), (gx + 47, yy)], fill=(200, 205, 210), width=1)
    for xx in range(gx + 10, gx + 47, 10): d.line([(xx, gy + 3), (xx, G)], fill=(200, 205, 210), width=1)
    hop = 0; kick = None
    for h in ctx['hits']:
        if 0 <= t - h < 1.2: hop = q(-abs(math.sin((t - h)*math.pi*3.0))*16); kick = t - h
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # camisa 10 generica
    d.rectangle((MX + 22, y0 + 74, MX + 34, y0 + 90), fill=(200, 25, 35)); d.rectangle((MX + 22, y0 + 80, MX + 34, y0 + 83), fill=(25, 25, 25)); f1 = font(PS2, 8); d.text((MX + 25, y0 + 77), '7', font=f1, fill=(255, 255, 255))
    # bola
    if kick is None:
        bx = MX + 84 + int(abs(math.sin(beat*math.pi))*0); by = G - 14 - int(abs(math.sin(beat*math.pi))*10)
    else:
        bx = MX + 84 + q(kick*110); by = G - 14 - q(math.sin(min(kick, 1.0)*math.pi)*30)
        bx = min(bx, gx + 36)
    d.rectangle((bx, by, bx + 12, by + 12), fill=(245, 245, 245)); d.rectangle((bx + 4, by + 4, bx + 8, by + 8), fill=(30, 30, 34)); d.rectangle((bx + 1, by + 1, bx + 3, by + 3), fill=(30, 30, 34)); d.rectangle((bx + 9, by + 9, bx + 11, by + 11), fill=(30, 30, 34))


def acar_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BAIANA', 'PATRIMÔNIO'))
    for tt in ctx['hits']: ev('chime', tt)
    P = 60/104/2; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _acar_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # tabuleiro
    tx, ty = 168, G - 40
    d.rectangle((tx + 6, ty + 10, tx + 10, G), fill=(120, 80, 45)); d.rectangle((tx + 82, ty + 10, tx + 86, G), fill=(120, 80, 45))
    d.rectangle((tx, ty, tx + 92, ty + 10), fill=(150, 100, 55)); d.rectangle((tx, ty - 2, tx + 92, ty), fill=(240, 240, 235))
    # acarajés
    for k in range(4):
        ax = tx + 6 + k*14
        d.ellipse((ax, ty - 9, ax + 12, ty), fill=(205, 110, 40)); d.rectangle((ax + 3, ty - 6, ax + 9, ty - 4), fill=(240, 180, 60))
    # tacho de dendê borbulhando
    px = tx + 64
    d.rectangle((px, ty - 14, px + 24, ty), fill=(60, 60, 65)); d.rectangle((px + 2, ty - 13, px + 22, ty - 9), fill=(235, 140, 30))
    for k in range(3):
        if int(t*6 + k) % 2: d.ellipse((px + 4 + k*7, ty - 16, px + 8 + k*7, ty - 12), fill=(250, 190, 60))
    # vapor
    for k in range(3):
        sy = ty - 20 - int(((t*20) + k*10) % 30)
        d.rectangle((px + 6 + k*6, sy, px + 8 + k*6, sy + 3), fill=(230, 230, 230))
    # fitas coloridas penduradas
    for k in range(6):
        fx = 120 + k*26; fl = int(math.sin(t*3 + k)*3)
        d.line([(fx, G - 170), (fx + fl, G - 140)], fill=[(240, 60, 60), (250, 200, 40), (60, 170, 90), (60, 130, 230), (230, 90, 180), (250, 250, 250)][k], width=3)
    d.line([(110, G - 170), (270, G - 170)], fill=(120, 80, 45), width=1)
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*14)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # torso branco (turbante de baiana)
    d.ellipse((MX + 4, y0 - 14, MX + 56, y0 + 10), fill=(250, 250, 248)); d.ellipse((MX + 18, y0 - 22, MX + 42, y0 - 6), fill=(250, 250, 248))
    d.rectangle((MX + 10, y0 - 2, MX + 50, y0 + 2), fill=(230, 200, 120))

KINDS.update({'best': (wrap(_best_mascot), best_setup), 'acaraje': (wrap(_acar_mascot), acar_setup)})

# ---------- 27/11: BLACK FRIDAY (vitrine), DOJO (artes marciais) ----------
def bf_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BLACK FRIDAY', 'DESCONTO!'))
    for tt in ctx['hits']: ev('chime', tt)
    P = 60/118/2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _bf_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # vitrine
    d.rectangle((150, G - 70, 266, G), fill=(25, 25, 30)); d.rectangle((154, G - 66, 262, G - 4), fill=(45, 40, 55))
    blink = int(t*3) % 2
    d.rectangle((150, G - 84, 266, G - 70), fill=(230, 40, 60) if blink else (200, 30, 50))
    # sacolas
    for k, col in enumerate([(240, 200, 40), (220, 60, 90), (60, 160, 230)]):
        bx = 162 + k*32; by = G - 34 - (k % 2)*6
        d.rectangle((bx, by, bx + 24, G - 4), fill=col); d.arc((bx + 6, by - 8, bx + 18, by + 4), 180, 360, fill=(30, 30, 30), width=2)
    # etiquetas % caindo
    for k in range(5):
        fy = G - 150 + int((t*30 + k*23) % 60)
        fx = 120 + k*30 + int(math.sin(t*2 + k)*6)
        d.rectangle((fx, fy, fx + 16, fy + 10), fill=(255, 230, 80)); d.text((fx + 4, fy), "%", fill=(200, 30, 40))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # carrinho
    cx = MX + 66
    d.rectangle((cx, G - 30, cx + 34, G - 12), outline=(200, 200, 210), width=2)
    d.line([(cx, G - 30), (cx - 8, G - 40)], fill=(200, 200, 210), width=2)
    d.ellipse((cx + 3, G - 10, cx + 9, G - 4), fill=(200, 200, 210)); d.ellipse((cx + 25, G - 10, cx + 31, G - 4), fill=(200, 200, 210))

def dojo_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('BRUCE LEE', 'KIAI!'))
    for tt in ctx['hits']: ev('thud', tt)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _dojo_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # parede de madeira e pergaminho
    for k in range(6):
        d.line([(110 + k*28, G - 170), (110 + k*28, G)], fill=(90, 55, 30), width=1)
    d.rectangle((196, G - 110, 222, G - 66), fill=(240, 230, 200)); d.rectangle((194, G - 112, 224, G - 108), fill=(110, 60, 30)); d.rectangle((194, G - 68, 224, G - 64), fill=(110, 60, 30))
    for k in range(3): d.rectangle((204, G - 102 + k*11, 214, G - 99 + k*11), fill=(30, 30, 30))
    # boneco de madeira
    wx = 236
    d.rectangle((wx, G - 80, wx + 18, G), fill=(140, 90, 50)); d.rectangle((wx - 12, G - 60, wx, G - 54), fill=(120, 75, 40)); d.rectangle((wx - 10, G - 40, wx, G - 35), fill=(120, 75, 40))
    # tábua quebrando nos hits
    broke = any(0 <= t - h < 1.2 for h in ctx['hits'])
    bx, by = 150, G - 50
    if broke:
        d.rectangle((bx, by, bx + 14, by + 8), fill=(200, 160, 100)); d.rectangle((bx + 22, by + 4, bx + 36, by + 12), fill=(200, 160, 100))
    else:
        d.rectangle((bx, by, bx + 36, by + 8), fill=(200, 160, 100))
    d.rectangle((bx + 4, by + 8, bx + 8, G), fill=(80, 50, 30)); d.rectangle((bx + 28, by + 8, bx + 32, G), fill=(80, 50, 30))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*18)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

KINDS.update({'bfriday': (wrap(_bf_mascot), bf_setup), 'dojo': (wrap(_dojo_mascot), dojo_setup)})

# ---------- 28-30/11: MEMORIAL, VILA, QUANTUM, STREET, THRILLER ----------
def thr_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('THRILLER', 'RECORDE!'))
    for i, tt in enumerate(ctx['hits']): ev('applause', tt)
    P = 60/100; k = 0
    while k*P < ctx['total'] - 1: ev('drum', k*P, k=k); k += 1

def _thr_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    sad = False
    # amplificadores
    for x0 in (150, 210):
        for r in range(2):
            y0_ = G - 40 - r*38
            d.rectangle((x0, y0_, x0 + 52, y0_ + 36), fill=(30, 30, 32)); d.rectangle((x0 + 3, y0_ + 3, x0 + 49, y0_ + 33), fill=(55, 55, 58))
            for cx_ in (x0 + 14, x0 + 38):
                pulse = 2 if (int(beat*2) % 2 and not sad) else 0
                d.ellipse((cx_ - 9 - pulse, y0_ + 9 - pulse, cx_ + 9 + pulse, y0_ + 27 + pulse), fill=(20, 20, 22))
                d.ellipse((cx_ - 3, y0_ + 15, cx_ + 3, y0_ + 21), fill=(90, 90, 95))
    # holofotes coloridos no alto
    cols = [(255, 80, 120), (255, 210, 60), (90, 160, 255)]
    for k in range(3):
        if sad and k != 1: continue
        lx = 140 + k*50
        on = (int(beat) + k) % 3 != 0 or sad
        if on:
            for j in range(0, 60, 3):
                f = j/60; xa = int(lx - 4 - f*20); xb = int(lx + 4 + f*20)
                if (j//3 + int(t*6)) % 2 == 0: d.line([(xa, G - 190 + j*2), (xb, G - 190 + j*2)], fill=cols[k] if not sad else (200, 200, 230), width=1)
    # pedestal de microfone
    mx = MX + 64
    d.rectangle((mx, G - 64, mx + 2, G), fill=(170, 170, 175)); d.rectangle((mx - 8, G - 3, mx + 10, G), fill=(170, 170, 175))
    d.ellipse((mx - 3, G - 74, mx + 5, G - 62), fill=(40, 40, 45))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (0 if sad else (2 if int(beat) % 2 else 0))
    place(cv, d, spr, MX, y0)

def hosp_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('KATHERINE', 'EMMY!'))
    for tt in ctx['hits']: ev('ding', tt)
    P = 60/104*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _hosp_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # monitor cardíaco
    mx0, my0 = 166, G - 110
    d.rectangle((mx0, my0, mx0 + 70, my0 + 46), fill=(60, 64, 70)); d.rectangle((mx0 + 4, my0 + 4, mx0 + 66, my0 + 40), fill=(10, 25, 20))
    pts = []
    for x in range(62):
        ph = (x + int(t*40)) % 31
        yy = 22 + (-14 if ph == 10 else (10 if ph == 12 else (-4 if ph == 8 else 0)))
        pts.append((mx0 + 4 + x, my0 + yy))
    d.line(pts, fill=(80, 255, 120), width=1)
    d.rectangle((mx0 + 32, my0 + 46, mx0 + 36, G), fill=(120, 124, 130)); d.rectangle((mx0 + 20, G - 3, mx0 + 48, G), fill=(120, 124, 130))
    # cruz vermelha
    d.rectangle((250, G - 150, 258, G - 126), fill=(230, 50, 60)); d.rectangle((242, G - 142, 266, G - 134), fill=(230, 50, 60))
    # troféu dourado genérico
    tx, ty = 246, G - 36
    d.rectangle((tx + 6, ty + 26, tx + 20, ty + 36), fill=(120, 90, 40))
    d.rectangle((tx + 11, ty + 14, tx + 15, ty + 26), fill=(240, 200, 70))
    d.ellipse((tx + 3, ty, tx + 23, ty + 18), fill=(250, 210, 80))
    if int(t*3) % 2: d.rectangle((tx + 7, ty + 4, tx + 9, ty + 6), fill=(255, 255, 220))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)
    # estetoscópio no pescoço
    d.arc((MX + 14, y0 + 62, MX + 46, y0 + 88), 0, 180, fill=(60, 60, 70), width=2)
    d.ellipse((MX + 40, y0 + 80, MX + 48, y0 + 88), fill=(180, 180, 190))

def fos_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('LUCY', 'DE PÉ!'))
    for tt in ctx['hits']: ev('chime', tt)
    P = 60/96*2; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _fos_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # dunas e cacto
    d.polygon([(110, G), (170, G - 40), (230, G - 10), (270, G - 50), (270, G)], fill=(210, 160, 100))
    # ossos no chão (revelados aos poucos)
    s0 = ctx['cards'][min(ci, len(ctx['cards']) - 1)][0]
    rev = min(1.0, (t - s0)/2.0) if ci >= 1 else 0.3
    bx, by = 172, G - 14
    bones = [(0, 0, 22, 4), (26, -4, 40, 0), (6, -10, 18, -6), (44, 0, 64, 4), (30, 6, 46, 10)]
    for k, (a, b, c, e) in enumerate(bones):
        if k/len(bones) <= rev:
            d.rectangle((bx + a, by + b, bx + c, by + e), fill=(245, 235, 210))
            d.ellipse((bx + a - 2, by + b - 2, bx + a + 3, by + e + 2), fill=(245, 235, 210)); d.ellipse((bx + c - 3, by + b - 2, bx + c + 2, by + e + 2), fill=(245, 235, 210))
    # pincel de arqueólogo balançando
    sw = int(math.sin(t*6)*6)
    d.line([(bx + 30 + sw, by - 30), (bx + 36 + sw, by - 6)], fill=(140, 90, 50), width=2)
    d.rectangle((bx + 34 + sw, by - 8, bx + 40 + sw, by - 2), fill=(230, 200, 120))
    # gravador de fita (tela 2)
    if ci == 2:
        rx, ry = 236, G - 22
        d.rectangle((rx, ry, rx + 30, ry + 18), fill=(50, 50, 55)); d.ellipse((rx + 4, ry + 4, rx + 12, ry + 12), fill=(200, 200, 200)); d.ellipse((rx + 18, ry + 4, rx + 26, ry + 12), fill=(200, 200, 200))
        nx = rx + 10 + int((t*20) % 20); ny = ry - 10 - int((t*15) % 20)
        d.rectangle((nx, ny, nx + 3, ny + 3), fill=(255, 220, 90)); d.rectangle((nx + 3, ny - 7, nx + 4, ny), fill=(255, 220, 90))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def mem_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('CHAPECOENSE', 'HOMENAGEM'))
    for tt in ctx['hits']: ev('chime', tt)

def _mem_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    # bandeira verde e branca ondulando
    fx, fy = 206, G - 96
    d.rectangle((fx - 2, fy, fx, G), fill=(200, 200, 205))
    for j in range(0, 50, 2):
        w = int(math.sin(t*3 + j*0.15)*3)
        col = (20, 140, 70) if (j//10) % 2 == 0 else (240, 240, 240)
        d.rectangle((fx + j, fy + w, fx + j + 2, fy + 24 + w), fill=col)
    # velas acesas
    for k in range(5):
        vx = 140 + k*24; vy = G - 22 - (k % 2)*4
        d.rectangle((vx, vy, vx + 6, G), fill=(245, 240, 225))
        fl = 1 if int(t*7 + k) % 2 else 0
        d.ellipse((vx, vy - 9 - fl, vx + 6, vy - 1), fill=(255, 180, 60)); d.ellipse((vx + 2, vy - 6 - fl, vx + 4, vy - 2), fill=(255, 250, 210))
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + jumpoff(jump)
    place(cv, d, spr, MX, y0)
    # fita de luto verde no peito
    d.polygon([(MX + 26, y0 + 58), (MX + 34, y0 + 58), (MX + 38, y0 + 72), (MX + 30, y0 + 64), (MX + 22, y0 + 72)], fill=(20, 140, 70))

def vila_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('CHESPIRITO', 'SUCESSO!'))
    for tt in ctx['hits']: ev('applause', tt)
    P = 60/112; k = 0
    while k*P < ctx['total'] - 1: ev('blip', k*P, k=k); k += 1

def _vila_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # muro de tijolos do pátio
    for r in range(6):
        for c in range(6):
            bx = 130 + c*24 + (12 if r % 2 else 0); by = G - 120 + r*12
            if bx < 268: d.rectangle((bx, by, min(bx + 22, 268), by + 10), fill=(180, 110, 80))
    # barril de madeira
    bx, by = 196, G - 56
    d.rectangle((bx, by, bx + 40, G), fill=(150, 95, 50))
    for k in range(4): d.line([(bx + 6 + k*9, by), (bx + 6 + k*9, G)], fill=(110, 70, 35), width=1)
    for yy in (by + 8, G - 10): d.rectangle((bx - 2, yy, bx + 42, yy + 4), fill=(90, 90, 95))
    d.ellipse((bx, by - 6, bx + 40, by + 6), fill=(120, 75, 40))
    # sanduíche pulando nos hits
    hop2 = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.8: hop2 = int(-abs(math.sin((t - h)*math.pi*2.5))*14)
    sx, sy = 150, G - 20 + hop2
    d.rectangle((sx, sy, sx + 22, sy + 5), fill=(225, 180, 110)); d.rectangle((sx, sy + 5, sx + 22, sy + 8), fill=(240, 150, 150)); d.rectangle((sx, sy + 8, sx + 22, sy + 13), fill=(225, 180, 110))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def qua_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('SCHRODINGER', 'VIVO E MORTO?'))
    for tt in ctx['hits']: ev('ding', tt)
    P = 60/96; k = 0
    while k*P < ctx['total'] - 1: ev('tick', k*P, k=k); k += 1

def _qua_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # caixa fechada
    bx, by = 178, G - 60
    d.rectangle((bx, by, bx + 70, G), fill=(170, 125, 70)); d.rectangle((bx - 4, by - 8, bx + 74, by), fill=(150, 105, 55))
    d.line([(bx, by + 20), (bx + 70, by + 20)], fill=(140, 100, 50), width=1)
    # simbolo de alerta
    d.polygon([(bx + 35, by + 26), (bx + 47, by + 48), (bx + 23, by + 48)], fill=(250, 210, 40)); d.rectangle((bx + 34, by + 32, bx + 36, by + 41), fill=(30, 30, 30)); d.rectangle((bx + 34, by + 43, bx + 36, by + 45), fill=(30, 30, 30))
    # orelhas de gato aparecendo e sumindo (superposição)
    vis = (math.sin(t*2.2) > 0)
    alpha_col = (60, 60, 65) if vis else (110, 110, 140)
    for ex in (bx + 22, bx + 42):
        d.polygon([(ex, by - 8), (ex + 6, by - 22), (ex + 12, by - 8)], fill=alpha_col if vis or int(t*10) % 2 else (40, 40, 60))
    # pontos de interrogação flutuando
    for k in range(3):
        qx = 140 + k*40; qy = G - 140 - int(((t*20 + k*25) % 50))
        d.text((qx, qy), "?", fill=(150, 220, 255))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*16)
    spr = face_sprite(base, t, talking)
    y0 = G - 80 + hop + jumpoff(jump) + (2 if int(beat) % 2 else 0)
    place(cv, d, spr, MX, y0)

def str_setup(ctx):
    ctx['hits'] = _title_times(ctx, ('PAUL WALKER', 'LEGADO'))
    for tt in ctx['hits']: ev('chime', tt)
    for k in range(int(ctx['total']//3)): ev('engine', 1.0 + k*3, dur=1.2)

def _str_mascot(cv, d, base, th, t, talking, jump, ci, ctx, md=None):
    beat = t*th['bpm']/60
    # palmeiras
    for px in (150, 236):
        d.rectangle((px, G - 110, px + 4, G), fill=(110, 75, 40))
        for k in range(5):
            ang = -1.2 + k*0.6
            d.line([(px + 2, G - 110), (px + 2 + int(math.cos(ang)*22), G - 110 + int(math.sin(ang)*10) + 6)], fill=(40, 140, 70), width=3)
    # estrada com faixa
    d.rectangle((0, G - 6, 270, G), fill=(50, 50, 55))
    for k in range(9):
        lx = int((k*36 - t*120) % 300) - 30
        d.rectangle((lx, G - 4, lx + 16, G - 3), fill=(240, 220, 90))
    # carro esportivo passando
    cx = int((t*90) % 420) - 120
    d.rectangle((cx, G - 20, cx + 54, G - 10), fill=(230, 50, 50)); d.polygon([(cx + 12, G - 20), (cx + 20, G - 30), (cx + 38, G - 30), (cx + 46, G - 20)], fill=(200, 40, 40))
    d.rectangle((cx + 22, G - 28, cx + 36, G - 21), fill=(160, 210, 240))
    for wx in (cx + 8, cx + 40): d.ellipse((wx, G - 14, wx + 10, G - 4), fill=(25, 25, 25))
    hop = 0
    for h in ctx['hits']:
        if 0 <= t - h < 0.9: hop = q(-abs(math.sin((t - h)*math.pi*3.3))*12)
    spr = face_sprite(base, t, talking)
    y0 = G - 86 + hop + jumpoff(jump)
    place(cv, d, spr, MX, y0)

KINDS.update({'thriller': (wrap(_thr_mascot), thr_setup), 'memorial': (wrap(_mem_mascot), mem_setup), 'vila': (wrap(_vila_mascot), vila_setup), 'quantum': (wrap(_qua_mascot), qua_setup), 'street': (wrap(_str_mascot), str_setup)})
