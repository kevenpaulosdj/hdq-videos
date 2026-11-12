#!/bin/bash
# usage: prep.sh name dir
name=$1; dir=$2; cd $dir
i=0; while read u; do curl -sS -o $(printf "%02d" $i).mp3 "$u"; i=$((i+1)); done < urls.txt
for f in [0-9][0-9].mp3; do ffmpeg -y -loglevel error -i $f -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse,atempo=1.25,loudnorm=I=-15:TP=-1.5:LRA=11" -ar 44100 -ac 2 ${f%.mp3}.wav; done
python3 - "$name" "$dir" <<'PY'
import json, subprocess, sys
name, d = sys.argv[1:3]
tl=json.load(open(f'/tmp/pix/tl2_{name}.json')); t=0
for i,c in enumerate(tl['cards']):
    a=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{d}/{i:02d}.wav']))
    c['audio']=a; c['start']=round(t,1); c['dur']=round(max(4.0,a+0.55),1); t+=c['dur']
tl['dur']=round(t,1); json.dump(tl,open(f'{d}/tl_voice.json','w'),ensure_ascii=False,indent=1); print(name, tl['dur'])
PY
