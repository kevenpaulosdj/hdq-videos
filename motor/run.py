"""Uso: python run.py spec.json [--stills 3,20,40]
spec.json: {"name": "flu", "theme": "flu|hiphop|inventor|generic", "label": "DIA DO FLUMINENSE",
            "theme_cfg": {...só para generic...}, "cards": [["narração", [["kicker","..."],["title","..."],["text","..."],["icons",["⚽"]],["special","stats",[[179,0,"jogos"]]]]], ...]}
Gera: WORK/<name>.mp4 (vídeo + trilha + efeitos) e WORK/tl_<name>.json (tempos para o roteiro)."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from themes import *
from mascot2 import *
import sound
WPS = float(os.environ.get('HDQ_WPS', 3.8))
spec = json.load(open(sys.argv[1])); name = spec['name']; theme = spec['theme']
os.makedirs(WORK, exist_ok=True)
if theme == 'generic':
    c = spec['theme_cfg']
    th = dict(acc=tuple(c['acc']), kick=tuple(c.get('kick', (255,255,255))), panel=tuple(c.get('panel', (14,20,40,205))), border=tuple(c.get('border', (255,255,255))),
              mascot=tuple(c['mascot']), accessory=c.get('accessory', 'none'), bpm=c.get('bpm', 104), ped=tuple(c.get('ped', (90,90,110))), brand=tuple(c.get('brand', (255,255,255))))
    th['bg'] = generic_bg(c); th['mascot_fn'], th['setup'] = generic_mascot, generic_setup
else:
    th = dict(THEMES[theme]); th['bg'] = BG[theme]()
    th['mascot_fn'], th['setup'] = {'hiphop': (hiphop_mascot, hiphop_setup), 'flu': (flu_mascot, flu_setup), 'inventor': (inv_mascot, inv_setup)}[theme]
th['label'] = spec.get('label', th.get('label', ''))
cards = []; t = 0
for nar, items in spec['cards']:
    d = max(4.0, round(len(nar.split())/WPS + 0.7, 1)); cards.append(dict(start=round(t, 1), dur=d, nar=nar)); t += d
tl = dict(name=name, dur=round(t, 1), cards=cards); json.dump(tl, open(f'{WORK}/tl_{name}.json', 'w'), ensure_ascii=False, indent=1)
items = [[tuple(i) for i in it] for _, it in spec['cards']]
if '--stills' in sys.argv:
    os.environ['STILLS'] = sys.argv[sys.argv.index('--stills')+1]
    import engine; engine.render_video.__globals__['os'].environ['STILLS'] = os.environ['STILLS']
render_video(name, th, items, f'{WORK}/{name}_video.mp4', tl)
if '--stills' in sys.argv: sys.exit()
sound.build(name, theme, th['bpm'])
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{WORK}/{name}_video.mp4','-i',f'{WORK}/audio_{name}.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',f'{WORK}/{name}.mp4'], check=True)
print('OK', f'{WORK}/{name}.mp4', tl['dur'])
