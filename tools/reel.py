"""ai.pm.lab weekly Reel builder (silent visuals + generated royalty-free music).
Usage: python3 reel.py reel.json OUT_DIR FONT_DIR LOGO_FILE MUSIC_PY [seed]
reel.json: {"hook":"line1<br><span>accent</span> line2","sub":"one line under hook (may contain <b>)",
 "items":[["title","body with <b>"], ... 3-5 items],
 "outro_title":"line1<br>line2","outro_pill":"💾 ذخیره کن و فالو کن"}
Output: OUT_DIR/reel.mp4 (1080x1920, 30fps, ~28-32s, AAC music) and OUT_DIR/cover.jpg"""
import sys, os, json, shutil, asyncio, subprocess
from playwright.async_api import async_playwright
cfg=json.load(open(sys.argv[1])); OUT=os.path.abspath(sys.argv[2]); FD=os.path.abspath(sys.argv[3]); LOGO=sys.argv[4]; MUSIC=sys.argv[5]
seed=sys.argv[6] if len(sys.argv)>6 else '0'
os.makedirs(OUT,exist_ok=True); shutil.copy(LOGO,os.path.join(OUT,'logo.jpg'))
FA=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')
css=f"""
@font-face{{font-family:Vaz;font-weight:400;src:url(file://{FD}/naskh-400.woff2)}}
@font-face{{font-family:Vaz;font-weight:700;src:url(file://{FD}/naskh-600.woff2)}}
@font-face{{font-family:Vaz;font-weight:900;src:url(file://{FD}/naskh-700.woff2)}}
@font-face{{font-family:Int;font-weight:800;src:url(file://{FD}/inter-800.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#FCFAF5;font-family:Vaz,Int;direction:rtl;color:#1E1040;overflow:hidden;position:relative}}
.bar{{position:absolute;top:0;left:0;right:0;height:18px;background:#4F17A8}}
.wrap{{position:absolute;top:330px;right:90px;left:90px}}
.num{{font-weight:900;font-size:260px;color:#F2662B;line-height:1}}
.t{{font-weight:900;font-size:110px;line-height:1.35;color:#4F17A8;margin-top:20px}}
.b{{font-size:62px;line-height:1.7;color:#3A2C5C;margin-top:50px;background:#EDE6FA;border:4px solid #C9B8EE;border-radius:36px;padding:50px 56px}}
.b b{{color:#4F17A8}}
.hook{{font-weight:900;font-size:120px;line-height:1.45;color:#4F17A8}}
.hook span{{color:#F2662B}}
.foot{{position:absolute;bottom:140px;right:90px;left:90px;display:flex;align-items:center;gap:24px;direction:ltr;justify-content:flex-end;font-family:Int;font-weight:800;font-size:44px;color:#4F17A8}}
.foot img{{width:120px;height:120px;border-radius:50%;border:4px solid #E4DCF3}}
.prog{{position:absolute;bottom:80px;left:90px;right:90px;height:12px;background:#EDE6FA;border-radius:6px}}
.prog i{{display:block;height:12px;background:#F2662B;border-radius:6px}}
.big{{width:520px;height:520px;border-radius:50%;border:8px solid #E4DCF3;display:block;margin:0 auto}}
.c{{text-align:center}}
.pill{{display:inline-block;background:#F2662B;color:#fff;font-weight:900;font-size:64px;padding:24px 60px;border-radius:80px;margin-top:70px}}
"""
foot='<div class="foot">@ai.pm.lab<img src="logo.jpg"></div>'
prog=lambda p:f'<div class="prog"><i style="width:{p}%"></i></div>'
items=cfg['items']; k=len(items); per=22.0/k
sc=[('s0a',1.6,f'<div class="bar"></div><div class="wrap" style="top:520px"><div class="hook">{cfg["hook"]}</div></div>{foot}{prog(3)}'),
    ('s0b',2.6,f'<div class="bar"></div><div class="wrap" style="top:520px"><div class="hook">{cfg["hook"]}</div><div class="b" style="margin-top:80px">{cfg["sub"]}</div></div>{foot}{prog(10)}')]
for i,(t,b) in enumerate(items,1):
    p=10+i*(80/k); n=str(i).translate(FA)
    sc.append((f's{i}a',1.3,f'<div class="bar"></div><div class="wrap"><div class="num">{n}</div><div class="t">{t}</div></div>{foot}{prog(int(p-40/k))}'))
    sc.append((f's{i}b',per-1.3,f'<div class="bar"></div><div class="wrap"><div class="num">{n}</div><div class="t">{t}</div><div class="b">{b}</div></div>{foot}{prog(int(p))}'))
sc.append(('s9',4.2,f'<div class="bar"></div><div class="wrap c" style="top:300px"><img class="big" src="logo.jpg"><div class="t" style="margin-top:60px">{cfg.get("outro_title","متن کامل در پست اسلایدی")}</div><div class="pill">{cfg.get("outro_pill","💾 ذخیره کن و فالو کن")}</div></div><div class="foot" style="justify-content:center">@ai.pm.lab</div>{prog(100)}'))
async def shots():
    async with async_playwright() as pw:
        exe=shutil.which('google-chrome') or shutil.which('chromium')
        b=await (pw.chromium.launch(executable_path=exe,args=['--allow-file-access-from-files']) if exe else pw.chromium.launch(args=['--allow-file-access-from-files']))
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        for n,_,h in sc:
            open(f'{OUT}/{n}.html','w').write(f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body>{h}</body></html>')
            await pg.goto(f'file://{OUT}/{n}.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(250)
            await pg.screenshot(path=f'{OUT}/{n}.png')
        await b.close()
asyncio.run(shots())
T=0.3; R=lambda c:subprocess.run(c,check=True)
for n,d,_ in sc:
    fr=int(round((d+T)*30))
    R(['ffmpeg','-y','-loglevel','error','-loop','1','-i',f'{OUT}/{n}.png','-vf',f"scale=1188:2112,zoompan=z='min(1+0.0006*on,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30,format=yuv420p",'-frames:v',str(fr),'-c:v','libx264','-preset','veryfast','-crf','18',f'{OUT}/c_{n}.mp4'])
inp=[];flt=[];prev='0:v';acc=sc[0][1]
for n,_,_ in sc: inp+=['-i',f'{OUT}/c_{n}.mp4']
for i in range(1,len(sc)):
    tr='slideleft' if sc[i][0].endswith('a') or sc[i][0]=='s9' else 'fade'
    flt.append(f'[{prev}][{i}:v]xfade=transition={tr}:duration={T}:offset={acc:.2f}[v{i}]'); prev=f'v{i}'; acc+=sc[i][1]
total=acc+T
R(['python3',MUSIC,f'{OUT}/bg.wav',f'{total:.2f}',seed])
R(['ffmpeg','-y','-loglevel','error']+inp+['-i',f'{OUT}/bg.wav','-filter_complex',';'.join(flt),'-map',f'[{prev}]','-map',f'{len(sc)}:a','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',f'{OUT}/reel.mp4'])
R(['ffmpeg','-y','-loglevel','error','-i',f'{OUT}/s0b.png','-q:v','3',f'{OUT}/cover.jpg'])
print('done',round(total,1),'s')
