import sys, json, subprocess, numpy as np, wave
name, vdir, video, out = sys.argv[1:5]
tl = json.load(open(f'/tmp/pix/tl2_{name}.json')); SR=44100; N=int(SR*tl['dur'])
def rd(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,w.getnchannels()).astype(np.float32)/32768; return a
bg = rd(f'/tmp/pix/audio_{name}.wav')[:N]
bg = np.pad(bg, ((0, max(0, N-len(bg))), (0,0)))
V = np.zeros((N,2),np.float32)
for i,c in enumerate(tl['cards']):
    a = rd(f'{vdir}/{i:02d}.wav'); s=int((c['start']+(0.0 if i==0 else 0.2))*SR)  # 1a fala começa no segundo zero; e=min(N,s+len(a)); V[s:e]+=a[:e-s]
env = np.convolve((np.abs(V[:,0])>0.02).astype(np.float32), np.ones(int(0.3*SR))/(0.3*SR), 'same')
duck = 1 - 0.45*np.clip(env*3,0,1)
mix = V + bg*duck[:,None]*0.8
mix /= max(1, np.max(np.abs(mix))/0.97)
w=wave.open(f'/tmp/el/mix_{name}.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',video,'-i',f'/tmp/el/mix_{name}.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],check=True)
print('ok', out)
