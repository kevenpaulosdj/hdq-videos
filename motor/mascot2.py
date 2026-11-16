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
