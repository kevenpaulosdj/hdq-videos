import numpy as np, wave, json, sys, os
WORK = os.environ.get('HDQ_WORK', 'work')
SR = 44100
def sq(f, n, duty=0.5): ph = (np.arange(n)*f/SR) % 1; return np.where(ph < duty, 1.0, -1.0)
def tri(f, n): ph = (np.arange(n)*f/SR) % 1; return 4*np.abs(ph-0.5)-1
def env(n, d): return np.exp(-np.arange(n)/SR/d)
rng = np.random.default_rng(1)
CH = {'hiphop': (90, [(55.0,[220,261.63,329.63]),(43.65,[174.61,220,261.63]),(65.41,[196,261.63,329.63]),(49.0,[196,246.94,293.66])]),
      'flu': (100, [(65.41,[261.63,329.63,392]),(55.0,[220,261.63,329.63]),(43.65,[174.61,220,261.63]),(49.0,[196,246.94,293.66])]),
      'inventor': (108, [(49.0,[196,246.94,293.66]),(73.42,[293.66,369.99,440]),(41.2,[164.81,196,246.94]),(65.41,[261.63,329.63,392])])}
def build(name, theme, bpm=None):
    tl = json.load(open(f'{WORK}/tl_{name}.json')); TOT = tl['dur']; N = int(SR*TOT)
    M = np.zeros(N); X = np.zeros(N)
    def add(buf, sig, t, g):
        i = int(t*SR); j = min(N, i+len(sig))
        if 0 <= i < N: buf[i:j] += sig[:j-i]*g
    bpm0, ch = CH.get(theme, CH['inventor']); bpm = bpm or bpm0; st = 60/bpm/4; bar = 16*st; b = 0
    while b*bar < TOT:
        t0 = b*bar; root, chord = ch[b % 4]
        n16 = int(st*SR)
        for s in range(16):
            f = chord[(s if theme != 'hiphop' else s//2) % 3] * (2 if s % 8 >= 4 else 1)
            add(M, sq(f*2 if theme == 'inventor' else f, n16, 0.25)*env(n16, 0.06), t0+s*st, 0.05)
        for s, d in ((0,3),(4,2),(8,3),(12,2),(14,2)):
            n = int(d*st*SR*0.9); add(M, tri(root*2, n)*(1-np.arange(n)/n*0.3), t0+s*st, 0.22)
        kick = [0, 7, 10] if theme == 'hiphop' else ([0, 4, 8, 12] if theme == 'inventor' else [0, 8])
        for s in kick:
            n = int(0.18*SR); tt = np.arange(n)/SR; add(M, np.sin(2*np.pi*np.cumsum(60+140*np.exp(-tt*30))/SR)*env(n, .08), t0+s*st, 0.45)
        for s in (4, 12):
            n = int(0.15*SR); add(M, rng.standard_normal(n)*env(n, .05), t0+s*st, 0.18)
        for s in range(0, 16, 2):
            n = int(0.03*SR); add(M, np.diff(rng.standard_normal(n+1))*env(n, .01), t0+s*st, 0.08)
        b += 1
    for e in json.load(open(f'{WORK}/events_{name}.json')):
        k, t = e['kind'], e['t']
        if k == 'blip':
            n = int(0.03*SR); f = [660, 740, 830, 880][e.get('k', 0) % 4]; add(X, sq(f, n, 0.5)*env(n, .015), t, 0.05)
        elif k == 'thud':
            n = int(0.3*SR); tt = np.arange(n)/SR
            add(X, (np.sin(2*np.pi*np.cumsum(50+120*np.exp(-tt*20))/SR) + 0.5*rng.standard_normal(n)*np.exp(-tt*30))*env(n, .12), t, 0.5)
        elif k == 'pop':
            n = int(0.09*SR); tt = np.arange(n)/SR; add(X, sq(1, n)*0 + np.sign(np.sin(2*np.pi*np.cumsum(400+1400*tt/0.09)/SR))*env(n, .04), t, 0.12)
        elif k == 'wipe' and theme == 'hiphop':
            n = int(0.25*SR); tt = np.arange(n)/SR; nz = rng.standard_normal(n)
            rate = np.sin(2*np.pi*4*tt); sig = nz*np.abs(rate)*(1 + np.sign(rate))*0.5 + np.sin(2*np.pi*np.cumsum(300 + 500*rate)/SR)*0.4
            add(X, sig*np.exp(-tt*4), t + 0.05, 0.16)
        elif k == 'wipe':
            n = int(0.4*SR); tt = np.arange(n)/SR; nz = rng.standard_normal(n)
            add(X, nz*np.sin(np.pi*tt/0.4)**2*0.6 + np.sign(np.sin(2*np.pi*np.cumsum(200+900*tt/0.4)/SR))*0.25*np.sin(np.pi*tt/0.4), t, 0.12)
        elif k == 'tick':
            n = int(0.02*SR); add(X, sq(1760, n)*env(n, .008), t, 0.06)
        elif k == 'ding':
            for f, dt in ((1318.5, 0), (1760, 0.09)):
                n = int(0.35*SR); add(X, sq(f, n, 0.5)*env(n, .12), t+dt, 0.1)
        elif k == 'scratch':
            n = int(0.35*SR); tt = np.arange(n)/SR; add(X, rng.standard_normal(n)*np.abs(np.sin(2*np.pi*6*tt))*env(n, .2), t, 0.25)
        elif k == 'title':
            tx = e.get('text', '')
            if theme == 'hiphop' and tx in ('HIP HOP', 'DJ KOOL HERC', 'BREAKBEAT'):
                for dt, ln in ((0, .14), (.18, .14), (.36, .55)):
                    n = int(ln*SR); tt = np.arange(n)/SR; sig = np.zeros(n)
                    for f in (415, 523, 622, 830): sig += ((tt*f*(1 - 0.03*tt/ln)) % 1)*2 - 1
                    sig = np.tanh(sig*0.8)*np.minimum(1, tt/0.01)*np.minimum(1, (ln-tt)/0.03); add(X, sig, t+dt, 0.12)
            if theme == 'flu' and tx in ('GOOOL!', '1 X 0', 'CARRASCO'):
                n = int(3.2*SR); tt = np.arange(n)/SR; nz = rng.standard_normal(n)
                F = np.fft.rfft(nz); fr = np.fft.rfftfreq(n, 1/SR); F[(fr < 250) | (fr > 2600)] = 0; band = np.fft.irfft(F, n)
                band /= np.max(np.abs(band)) + 1e-9
                voices = np.zeros(n)
                for _ in range(24):
                    f0 = rng.uniform(180, 420); vib = 1 + 0.02*np.sin(2*np.pi*rng.uniform(4, 7)*tt)
                    voices += np.sin(2*np.pi*np.cumsum(f0*vib*(1 + 0.15*np.minimum(tt, 1)))/SR)*rng.uniform(.3, 1)
                voices /= np.max(np.abs(voices))
                envl = np.minimum(1, tt/0.25)*np.where(tt < 2.2, 1, np.maximum(0, 1 - (tt-2.2)/1.0))
                add(X, (band*0.8 + voices*0.35)*envl, t - 0.05, 0.42)
            if theme == 'inventor' and tx in ('INVENTOR',):
                pass
        elif k == 'tap':
            n = int(0.06*SR); tt = np.arange(n)/SR; add(X, np.sin(2*np.pi*np.cumsum(220 - 1200*tt)/SR)*env(n, .02) + rng.standard_normal(n)*env(n, .004)*0.3, t, 0.07)
        elif k == 'whistle':
            for dt, ln in ((0, .22), (.32, .7)):
                n = int(ln*SR); tt = np.arange(n)/SR
                sig = np.sin(2*np.pi*2900*tt + 3*np.sin(2*np.pi*35*tt))*(0.7 + 0.3*np.sign(np.sin(2*np.pi*28*tt)))*np.minimum(1, tt/0.01)*np.minimum(1, (ln-tt)/0.03)
                add(X, sig, t+dt, 0.1)
        elif k == 'clank':
            n = int(0.18*SR); tt = np.arange(n)/SR; sig = sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*dcy) for f, dcy in ((640, 25), (1510, 30), (2380, 40), (3700, 50)))
            add(X, sig/3, t, 0.05)
        elif k == 'applause':
            n = int(2.6*SR); sig = np.zeros(n); cl = int(0.006*SR)
            for _ in range(900):
                i0 = int(abs(rng.normal(0.9, 0.55))*SR)
                if i0 + cl < n: sig[i0:i0+cl] += rng.standard_normal(cl)*np.exp(-np.arange(cl)/(cl/4))*rng.uniform(.3, 1)
            add(X, sig/np.max(np.abs(sig)), t, 0.3)
        elif k == 'engine':
            n = int(e['dur']*SR); tt = np.arange(n)/SR
            s = sq(70 + 30*np.minimum(tt, 2), n, 0.3) * (0.6 + 0.4*np.sin(2*np.pi*14*tt)); s[:2000] *= np.linspace(0, 1, 2000); s[-4000:] *= np.linspace(1, 0, 4000)
            add(X, s, t, 0.06)
    if theme == 'flu':
        nz = rng.standard_normal(N); F = np.fft.rfft(nz); fr = np.fft.rfftfreq(N, 1/SR); F[(fr < 200) | (fr > 1800)] = 0
        bed = np.fft.irfft(F, N); bed /= np.max(np.abs(bed)); tt = np.arange(N)/SR
        X += bed*(0.6 + 0.4*np.sin(2*np.pi*0.13*tt))*0.05
    fo = int(2.5*SR); M[-fo:] *= np.linspace(1, 0, fo); X[-fo:] *= np.linspace(1, 0, fo)
    M = M/np.max(np.abs(M))*0.32
    L = M + X; pk = np.max(np.abs(L))
    if pk > 0.95: L *= 0.95/pk
    S = (np.stack([L, L], 1)*32767).astype(np.int16)
    w = wave.open(f'{WORK}/audio_{name}.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(S.tobytes()); w.close()
if __name__ == '__main__': build(sys.argv[1], sys.argv[2])
