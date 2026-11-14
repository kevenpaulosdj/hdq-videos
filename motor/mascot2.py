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
