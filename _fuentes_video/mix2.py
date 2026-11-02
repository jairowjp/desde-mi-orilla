"""Mezcla v2: coloca cada bloque de voz al inicio de su escena + desfase, con música de fondo atenuada."""
import json, subprocess, os, sys
TL=json.load(open('/home/claude/video/timeline.json')); ST=TL['START']; TOTAL=TL['TOTAL']
# (archivo, escena, desfase en s)
PLAN=[('01','s0',1.0),('02','s1',0.5),('03','s2',0.4),('04','s3',0.6),('05','s4',0.8),('06','s5',1.0),('07','s6',0.6),
      ('08','s7',1.0),('09','s8',0.6),('10','s9',0.8),('11','s10',0.6),('12','s11',0.6),('13','s12',0.6),('14','s13',0.6),('15','s14',1.6)]
ins=[];ch=[];lab=[];n=0
for f,sc,off in PLAN:
    p=f'voz_final/{f}.wav'
    if not os.path.exists(p): print('falta',f); continue
    ms=int((ST[sc]+off)*1000); ins+=['-i',p]
    ch.append(f'[{n}:a]aresample=48000,aformat=channel_layouts=mono,highpass=f=85,equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9000:t=h:w=2000:g=1.5,acompressor=threshold=-24dB:ratio=3:attack=6:release=90:makeup=3,adelay={ms}|{ms},apad[v{n}]')
    lab.append(f'[v{n}]'); n+=1
fc=';'.join(ch)+';'+''.join(lab)+f'amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL},pan=stereo|c0=c0|c1=c0[out]'
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',fc,'-map','[out]','-ar','48000','-c:a','pcm_f32le','voz.wav'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','voz.wav','-i','/home/claude/video/music3.wav','-filter_complex',
 '[0:a]asplit=2[vo][sc];[1:a]aresample=48000,volume=-5dB[mu];[mu][sc]sidechaincompress=threshold=0.02:ratio=5:attack=25:release=450:makeup=1:knee=4[duck];[vo]volume=1.5dB[vv];[duck][vv]amix=inputs=2:normalize=0:duration=first,volume=1.3dB,alimiter=limit=0.74:attack=2:release=60:level=disabled[m]',
 '-map','[m]','-c:a','pcm_f32le','final.wav'],check=True)
print('ok',n,'bloques')
