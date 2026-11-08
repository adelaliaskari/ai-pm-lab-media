"""Generate a royalty-free soft lo-fi background track (WAV). Usage: python3 music.py out.wav seconds [seed]"""
import sys, numpy as np, wave
out=sys.argv[1]; dur=float(sys.argv[2]); seed=int(sys.argv[3]) if len(sys.argv)>3 else 0
sr=44100; rng=np.random.default_rng(seed); bpm=88; beat=60/bpm; n=int(sr*dur); t=np.arange(n)/sr
def note(f): return 440*2**((f-69)/12)
progs=[[60,57,53,55],[57,53,48,55],[62,58,55,57]]
prog=progs[seed%len(progs)]
mix=np.zeros(n)
bar=beat*4
for k in range(int(dur/bar)+1):
    root=prog[k%4]; st=int(k*bar*sr); en=min(n,int((k+1)*bar*sr))
    if st>=n: break
    tt=t[st:en]-k*bar
    env=np.minimum(1,tt/0.4)*np.exp(-tt*0.25)
    for iv,amp in [(0,.16),(4 if root in(60,53,55,48) else 3,.12),(7,.12),(12,.06)]:
        f=note(root+iv-12)
        mix[st:en]+=amp*env*(np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*2*f*tt))
    # bass
    f=note(root-24); mix[st:en]+=.18*np.exp(-tt*1.2)*np.sin(2*np.pi*f*tt)
# drums
for b in range(int(dur/beat)+1):
    s=int(b*beat*sr)
    if s>=n: break
    L=min(n-s,int(.25*sr)); tt=np.arange(L)/sr
    if b%2==0: mix[s:s+L]+=.35*np.sin(2*np.pi*(55+60*np.exp(-tt*25))*tt)*np.exp(-tt*9)
    else: mix[s:s+L]+=.08*rng.standard_normal(L)*np.exp(-tt*18)
    h=int((b+.5)*beat*sr)
    if h<n:
        L=min(n-h,int(.05*sr)); mix[h:h+L]+=.035*rng.standard_normal(L)*np.exp(-np.arange(L)/sr*60)
# melody sparkle
scale=[72,74,76,79,81]
for b in range(0,int(dur/beat),2):
    if rng.random()<.6:
        s=int(b*beat*sr); L=min(n-s,int(beat*sr)); tt=np.arange(L)/sr
        f=note(scale[rng.integers(len(scale))]); mix[s:s+L]+=.06*np.sin(2*np.pi*f*tt)*np.exp(-tt*3)
fade=int(1.5*sr); mix[:int(.5*sr)]*=np.linspace(0,1,int(.5*sr)); mix[-fade:]*=np.linspace(1,0,fade)
mix=mix/np.max(np.abs(mix))*.7
st=np.stack([mix,np.roll(mix,int(.012*sr))],1)
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype(np.int16).tobytes())
