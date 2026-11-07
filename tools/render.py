"""ai.pm.lab renderer: content.json -> carousel PNGs (1080x1350) + story PNG (1080x1920).
Usage: python3 render.py content.json OUT_DIR FONT_DIR LOGO_FILE (logo.jpg from the media repo: assets/logo.jpg)
FONT_DIR must contain: naskh-400.woff2 naskh-600.woff2 naskh-700.woff2 inter-400.woff2 inter-700.woff2 inter-800.woff2
(npm i @fontsource/noto-naskh-arabic @fontsource/inter, then copy/rename the arabic & latin files).
content.json:
{"cover":{"tag":"AI × Project Management","big":"۵","title":"line1<br>line2","lead":"..."},
 "points":[{"num":"۱","title":"...","sub":"...","label":"پرامپت","body":"html (<b>, <span class=ph>[..]</span>)"}],
 "final":{"title":"...","lead":"...","rows":["ذخیره کن ...","سوال ...","بفرست ..."]},
 "story":{"kicker":"پست جدید","title":"...","sub":"..."}}
Keep body <= ~45 words so it fits. Use Persian digits.
"""
import sys, os, json, asyncio, shutil
from playwright.async_api import async_playwright

content = json.load(open(sys.argv[1]))
OUT = os.path.abspath(sys.argv[2]); FD = os.path.abspath(sys.argv[3]); LOGO = os.path.abspath(sys.argv[4])
os.makedirs(OUT, exist_ok=True)
LOGO_NAME = 'logo' + os.path.splitext(LOGO)[1]
shutil.copy(LOGO, os.path.join(OUT, LOGO_NAME))
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

css = f"""
@font-face{{font-family:Vaz;font-weight:400;src:url(file://{FD}/naskh-400.woff2)}}
@font-face{{font-family:Vaz;font-weight:700;src:url(file://{FD}/naskh-600.woff2)}}
@font-face{{font-family:Vaz;font-weight:900;src:url(file://{FD}/naskh-700.woff2)}}
@font-face{{font-family:Int;font-weight:400;src:url(file://{FD}/inter-400.woff2)}}
@font-face{{font-family:Int;font-weight:700;src:url(file://{FD}/inter-700.woff2)}}
@font-face{{font-family:Int;font-weight:800;src:url(file://{FD}/inter-800.woff2)}}
*{{box-sizing:border-box;margin:0}}
body{{width:1080px;background:#FCFAF5;font-family:Vaz,Int;color:#1E1040;direction:rtl}}
.s{{width:1080px;height:1350px;padding:110px 90px 0;position:relative;overflow:hidden}}
.st{{width:1080px;height:1920px;padding:220px 90px 0;text-align:center;position:relative;overflow:hidden}}
.bar{{position:absolute;top:0;right:0;left:0;height:14px;background:#4F17A8}}
.foot{{position:absolute;bottom:40px;right:90px;left:90px;display:flex;align-items:center;justify-content:space-between;font-size:30px;color:#4F17A8;font-weight:700}}
.foot .h{{display:flex;align-items:center;gap:16px;direction:ltr;font-family:Int}}
.foot img{{width:104px;height:104px;border-radius:50%;border:3px solid #E4DCF3;object-fit:cover}}
.pg{{color:#6B5A8E;font-weight:400}}
.tag{{display:inline-block;background:#EDE6FA;color:#4F17A8;font-weight:700;font-size:30px;padding:12px 28px;border-radius:40px;font-family:Int,Vaz;direction:ltr}}
.num{{font-weight:900;font-size:150px;line-height:1;color:#F2662B}}
h1{{font-weight:900;font-size:100px;line-height:1.4;color:#4F17A8}}
h2{{font-weight:900;font-size:86px;line-height:1.3;color:#4F17A8;margin-top:6px}}
.use{{font-size:46px;line-height:1.6;margin-top:18px;color:#3A2C5C}}
.lbl{{font-weight:700;font-size:42px;color:#F2662B;margin-top:30px;margin-bottom:12px;display:flex;align-items:center;gap:12px}}
.box{{background:#EDE6FA;border:3px solid #C9B8EE;border-radius:28px;padding:42px 48px;font-size:48px;line-height:1.8;color:#1E1040}}
.box b{{color:#4F17A8}}
.ph{{background:#FCFAF5;border-radius:10px;padding:0 10px;color:#C2410C;font-weight:700;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.lead{{font-size:50px;line-height:1.65;color:#3A2C5C;margin-top:30px}}
.lead b{{color:#4F17A8}}
.swipe{{position:absolute;bottom:150px;right:90px;display:flex;align-items:center;gap:18px;font-weight:700;font-size:40px;color:#F2662B}}
.cta{{margin-top:56px;display:flex;flex-direction:column;gap:28px}}
.row{{display:flex;align-items:center;gap:28px;background:#FFFFFF;border:3px solid #E4DCF3;border-radius:28px;padding:34px 40px;font-size:48px;font-weight:700}}
.ic{{width:84px;height:84px;border-radius:22px;background:#4F17A8;display:flex;align-items:center;justify-content:center;flex:none}}
.ic.o{{background:#F2662B}}
.kick{{display:inline-block;background:#F2662B;color:#fff;font-weight:900;font-size:52px;padding:18px 44px;border-radius:60px}}
.stlogo{{width:340px;height:340px;border-radius:50%;border:5px solid #E4DCF3;display:block;margin:0 auto 60px;object-fit:cover}}
.sttitle{{font-weight:900;font-size:100px;line-height:1.4;color:#4F17A8;margin-top:60px}}
.stsub{{font-size:52px;line-height:1.65;color:#3A2C5C;margin-top:40px}}
.stcta{{position:absolute;bottom:260px;right:90px;left:90px;background:#4F17A8;color:#fff;border-radius:36px;padding:44px;text-align:center;font-weight:900;font-size:58px}}
"""
def ico(path, color='#fff', size=46, sw=2.4):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{path}"/></svg>'
ARROW = ico("M19 12H5M11 6l-6 6 6 6", '#F2662B', 44, 2.6)
SPARK = ico("M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M18 6l-2.5 2.5M8.5 15.5L6 18", '#F2662B', 34)
ICONS = [ico("M6 3h12v18l-6-4-6 4z"), ico("M21 12a8 8 0 0 1-11.5 7.2L4 21l1.8-5.5A8 8 0 1 1 21 12z"), ico("M22 2L11 13M22 2l-7 20-4-9-9-4z")]

pts = content['points']; N = len(pts) + 2
def foot(i): return f'<div class="foot"><div class="h"><img src="{LOGO_NAME}" alt="">@ai.pm.lab</div><div class="pg">{str(i).translate(FA)} / {str(N).translate(FA)}</div></div>'
c = content['cover']; slides = []
slides.append(f'''<div class="s"><div class="bar"></div><span class="tag">{c.get("tag","AI × Project Management")}</span>
<div style="margin-top:50px"><span class="num" style="font-size:230px">{c.get("big","")}</span></div>
<h1>{c["title"]}</h1><p class="lead">{c.get("lead","")}</p><div class="swipe">ورق بزن {ARROW}</div>{foot(1)}</div>''')
for k, p in enumerate(pts, 2):
    slides.append(f'''<div class="s"><div class="bar"></div><div class="num">{p.get("num", str(k-1).translate(FA))}</div>
<h2>{p["title"]}</h2><p class="use">{p.get("sub","")}</p><div class="lbl">{SPARK} {p.get("label","نکته")}</div>
<div class="box">{p["body"]}</div>{foot(k)}</div>''')
f = content['final']
rows = ''.join(f'<div class="row"><div class="ic{" o" if i==1 else ""}">{ICONS[i%3]}</div>{r}</div>' for i, r in enumerate(f['rows']))
slides.append(f'''<div class="s"><div class="bar"></div><h1 style="font-size:84px">{f["title"]}</h1>
<p class="lead" style="margin-top:24px">{f.get("lead","")}</p><div class="cta">{rows}</div>{foot(N)}</div>''')
st = content.get('story') or {"kicker": "پست جدید", "title": c["title"], "sub": c.get("lead","")}
story = f'''<div class="st"><div class="bar"></div><img class="stlogo" src="{LOGO_NAME}" alt="">
<span class="kick">{st.get("kicker","پست جدید")}</span><div class="sttitle">{st["title"]}</div><p class="stsub">{st.get("sub","")}</p>
<div class="stcta">پست کامل در پیج <span dir="ltr">@ai.pm.lab</span></div></div>'''

def page(body, h): return f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><style>{css}body{{height:{h}px}}</style></head><body>{body}</body></html>'
files = []
for i, s in enumerate(slides, 1):
    open(f'{OUT}/slide{i}.html', 'w').write(page(s, 1350)); files.append((f'slide{i}', 1350))
open(f'{OUT}/story.html', 'w').write(page(story, 1920)); files.append(('story', 1920))

async def main():
    async with async_playwright() as pw:
        exe = shutil.which('google-chrome') or shutil.which('chromium')
        b = await pw.chromium.launch(executable_path=exe, args=['--allow-file-access-from-files']) if exe else await pw.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await b.new_page()
        for name, h in files:
            await pg.set_viewport_size({'width': 1080, 'height': h})
            await pg.goto(f'file://{OUT}/{name}.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
            over = await pg.evaluate("""()=>{const r=[...document.querySelectorAll('.box,.cta,.lead,.stsub')].map(e=>e.getBoundingClientRect().bottom);const f=document.querySelector('.swipe,.stcta,.foot');return f?Math.max(0,...r)-f.getBoundingClientRect().top:0}""")
            if over > -10: print(f'WARNING {name}: content reaches footer ({over:.0f}px) - shorten text')
            await pg.screenshot(path=f'{OUT}/{name}.jpg', type='jpeg', quality=92)
        await b.close()
asyncio.run(main())
print('done', len(files))
