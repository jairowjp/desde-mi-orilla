import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
SR=44100; import json,sys
TL=json.load(open("timeline.json")); S=1.0; DUR=TL["TOTAL"]+0.5
ST=TL["START"]; T_LOGO=ST["s5"]+1.2; T_END=ST["s14"]+0.3; D0=ST["s5"]+1.2; D1=ST["s13"]; B0=ST["s13"]; B1=ST["s14"]; BASS0=ST["s2"]; PL0=ST["s1"]; N=int(SR*DUR)
rng=np.random.default_rng(7)
t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)
BPM=84; beat=60/BPM; bar=4*beat
def hz(m): return 440*2**((m-69)/12)
def env(n,a,d,s_level,r,total):
    e=np.ones(total)*s_level
    na=int(a*SR); nd=int(d*SR); nr=int(r*SR)
    e[:na]=np.linspace(0,1,na) if na else e[:na]
    e[na:na+nd]=np.linspace(1,s_level,len(e[na:na+nd]))
    if nr: e[-nr:]*=np.linspace(1,0,nr)
    return e
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); j=min(N,i+len(sig)); sig=sig[:j-i]*gain
    L[i:j]+=sig*np.sqrt((1-pan)/2); R[i:j]+=sig*np.sqrt((1+pan)/2)
# chords (midi) — Dmaj9, Bm9, Gmaj9, A6sus
CH=[[50,57,62,64,66,69],[47,54,61,62,66,69],[43,50,57,59,62,66],[45,52,57,59,62,64]]
ROOT=[38,35,31,33]
# pad: 2 bars per chord, detuned additive
t0=0.0; k=0
while t0<DUR:
    ch=CH[k%4]; dur=2*bar+1.2; n=int(dur*SR); tt=np.arange(n)/SR
    pad=np.zeros(n)
    for m in ch[1:]:
        for det in (-0.07,0.07):
            f=hz(m+det/1.0)
            pad+= (np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt)+0.08*np.sin(2*np.pi*3*f*tt))
    pad*=env(n,1.6,0.5,0.85,1.6,n)*(1+0.15*np.sin(2*np.pi*0.2*tt))
    add(pad/len(ch)/2,t0,pan=0.0,gain=0.11)
    t0+=2*bar; k+=1
# pluck arpeggio (marimba-like) from 7s, 8ths
def pluck(f,dur=1.2):
    n=int(dur*SR); tt=np.arange(n)/SR
    s=np.sin(2*np.pi*f*tt)*np.exp(-tt*5)+0.35*np.sin(2*np.pi*4*f*tt)*np.exp(-tt*18)+0.15*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*9)
    s[:60]*=np.linspace(0,1,60); return s
pat=[0,2,4,3,1,4,2,3]
x=PL0; i=0
while x<DUR-2:
    seg=int(x//(2*bar))%4; ch=CH[seg]
    # breakdown thinner 70-78
    if not (B0<x<B0+4 and i%2):
        m=ch[1:][pat[i%8]]+12
        g=0.16 if x<BASS0 else 0.2
        if x>DUR-6: g*=max(0,(DUR-2-x)/4)
        add(pluck(hz(m)),x,pan=0.35*np.sin(i*0.9),gain=g)
    x+=beat/2; i+=1
# bass from 19s
x=BASS0
while x<DUR-6:
    seg=int(x//(2*bar))%4; f=hz(ROOT[seg]); n=int(beat*1.9*SR); tt=np.arange(n)/SR
    b=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt))*env(n,0.01,0.3,0.6,0.3,n)
    if not(B0<x<B1): add(b,x,gain=0.2)
    x+=2*beat
# drums 30-70 (soft kick + shaker + rim)
def kick():
    n=int(0.35*SR); tt=np.arange(n)/SR; f=55+70*np.exp(-tt*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)
def shaker():
    n=int(0.09*SR); s=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*45)
    sos=butter(4,5000,'hp',fs=SR,output='sos'); return sosfilt(sos,s)
x=D0; i=0
while x<D1:
    if i%4 in (0,) or (i%8==6): add(kick(),x,gain=0.5)
    add(shaker(),x+beat/2,pan=0.3,gain=0.05); add(shaker(),x,pan=-0.3,gain=0.03)
    x+=beat; i+=1
# swells (noise risers) before logo (29.6) and end (78.4)
for end in (T_LOGO,T_END):
    d=2.4; n=int(d*SR); s=rng.standard_normal(n)*np.linspace(0,1,n)**2
    sos=butter(2,[800,6000],'bp',fs=SR,output='sos'); add(sosfilt(sos,s),end-d,gain=0.05)
# low boom at logo reveal & ending
for at in (T_LOGO,T_END):
    n=int(3*SR); tt=np.arange(n)/SR; add(np.sin(2*np.pi*hz(26)*tt)*np.exp(-tt*1.4),at,gain=0.35)
# final chord
n=int(7*SR); tt=np.arange(n)/SR; fin=np.zeros(n)
for m in CH[0]: fin+=np.sin(2*np.pi*hz(m+12)*tt)*np.exp(-tt*0.5)
add(fin/6,T_END+0.6,gain=0.18)
# reverb
ir_n=int(2.6*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.2); ir[0]=0
irL=ir; irR=np.roll(ir,331)
wetL=fftconvolve(L,irL)[:N]*0.02; wetR=fftconvolve(R,irR)[:N]*0.02
L2=L+wetL; R2=R+wetR
# master fade + normalize
fade=np.ones(N); fi=int(1.5*SR); fade[:fi]=np.linspace(0,1,fi); fo=int(2.5*SR); fade[-fo:]=np.linspace(1,0,fo)
st=np.stack([L2*fade,R2*fade],1); st/=np.max(np.abs(st))*1.12
st=np.tanh(st*1.1)/np.tanh(1.1)*0.89
wavfile.write('music3.wav',SR,(st*32767).astype(np.int16))
print('ok',st.shape)
