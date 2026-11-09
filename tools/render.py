"""ai.pm.lab renderer: content.json -> carousel PNGs (1080x1350) + story PNG (1080x1920).
Usage: python3 render.py content.json OUT_DIR FONT_DIR LOGO_FILE (logo.jpg from the media repo: assets/logo.jpg)
FONT_DIR must contain: naskh-400.woff2 naskh-600.woff2 naskh-700.woff2 inter-400.woff2 inter-700.woff2 inter-800.woff2
(npm i @fontsource/noto-naskh-arabic @fontsource/inter, then copy/rename the arabic & latin files).
content.json:
{"cover":{"icon":"(optional ICON_LIB name; else auto from tag)","tag":"AI × Project Management","title":"line1<br>line2","lead":"..."},
 "points":[{"num":"۱","icon":"(optional, see ICON_LIB names; else auto from label/title)","title":"...","sub":"...","label":"پرامپت","body":"html (<b>, <span class=ph>[..]</span>)"}],
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
.top{{display:flex;justify-content:space-between;align-items:center}}
.tile{{position:relative;flex:none;margin-left:24px}}
.tile .sq{{position:absolute;inset:0;border-radius:24%;transform:rotate(-11deg);display:flex;align-items:center;justify-content:center}}
.tile .d1,.tile .d2{{position:absolute;border-radius:10px;display:block}}
.tile .d1{{width:13px;height:52px;background:#F2662B;top:-46px;left:-4px;transform:rotate(-38deg)}}
.tile .d2{{width:52px;height:13px;background:#9A88D0;top:28px;left:-62px;transform:rotate(22deg)}}
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


# ---- small 3D-style icon tiles (one per slide) ----
ICON_LIB = {
 "mail":'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
 "calendar":'<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 "clock":'<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "chat":'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
 "quote":'<path fill="#fff" stroke="none" d="M10 6H5.5A1.5 1.5 0 0 0 4 7.5V12a1.5 1.5 0 0 0 1.5 1.5H8c0 2-1 3.2-3 3.6V19c3.6-.4 6.5-2.6 6.5-7V7.5A1.5 1.5 0 0 0 10 6zm9 0h-4.5A1.5 1.5 0 0 0 13 7.5V12a1.5 1.5 0 0 0 1.5 1.5H17c0 2-1 3.2-3 3.6V19c3.6-.4 6.5-2.6 6.5-7V7.5A1.5 1.5 0 0 0 19 6z"/>',
 "doc":'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
 "table":'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/>',
 "chart":'<path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/>',
 "presentation":'<path d="M2 3h20M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3M7 21l5-5 5 5"/>',
 "image":'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
 "video":'<path d="m22 8-6 4 6 4V8z"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
 "mic":'<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3"/>',
 "bot":'<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M12 8V4H8M2 14h2M20 14h2M9 13v2M15 13v2"/>',
 "cpu":'<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
 "sparkles":'<path d="M12 3l1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2z"/><path d="M19 3v4M17 5h4"/>',
 "bolt":'<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
 "settings":'<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
 "check":'<circle cx="12" cy="12" r="10"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
 "alert":'<path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3z"/><path d="M12 9v4M12 17h.01"/>',
 "x":'<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
 "bulb":'<path d="M9 18h6M10 22h4"/><path d="M15.1 14c.2-1 .7-1.7 1.4-2.5A5.9 5.9 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.4 2.5"/>',
 "target":'<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
 "users":'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "search":'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
 "link":'<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
 "lock":'<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
 "shield":'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
 "folder":'<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
 "pencil":'<path d="M17 3a2.8 2.8 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5z"/>',
 "list":'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
 "rocket":'<path d="M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.9A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22.4 22.4 0 0 1-4 2z"/><path d="M9 12H4s.6-3 2-4c1.6-1.1 5 0 5 0M12 15v5s3-.6 4-2c1.1-1.6 0-5 0-5"/>',
 "code":'<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
 "workflow":'<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/>',
 "bell":'<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
 "star":'<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
 "globe":'<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
 "book":'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
 "briefcase":'<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
 "send":'<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
 "play":'<circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4z"/>',
 "camera":'<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
 "database":'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
 "cloud":'<path d="M17.5 19H9a7 7 0 1 1 6.7-9h1.8a4.5 4.5 0 1 1 0 9z"/>',
 "compare":'<rect x="3" y="3" width="7" height="18" rx="1.5"/><rect x="14" y="3" width="7" height="18" rx="1.5"/>',
 "asterisk":'<path d="M12 5v14M18 8.5 6 15.5M6 8.5l12 7"/>',
 "download":'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
 "refresh":'<path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M8 16H3v5"/>',
 "filter":'<path d="M22 3H2l8 9.5V19l4 2v-8.5z"/>',
 "eye":'<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
 "bookmark":'<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
}
LABEL_ICON = [("پرامپت","quote"),("تنظیم","settings"),("مثال","briefcase"),("خروجی","download"),("خطا","alert"),("اشتباه","x"),("ساده","bulb"),("نکته","bulb"),("ابزار","settings"),("امنیت","shield"),("زمان","clock"),("مقایسه","compare")]
TAG_ICON = [("mail","mail"),("email","mail"),("gmail","mail"),("excel","table"),("sheet","table"),("power bi","chart"),("video","video"),("image","image"),("n8n","workflow"),("automation","workflow"),("meeting","calendar"),("schedul","calendar"),("gamma","presentation"),("slide","presentation"),("present","presentation"),("prompt","quote"),("jira","list"),("mcp","link"),("agent","bot"),("ml","cpu"),("voice","mic"),("avatar","mic"),("research","search")]
FALLBACK = ["sparkles","bolt","target","rocket","check","star"]
def pick_icon(name, *hints, k=0):
    if name in ICON_LIB: return name
    h = ' '.join(x or '' for x in hints).lower()
    for key, ic in LABEL_ICON + TAG_ICON:
        if key in h: return ic
    return FALLBACK[k % len(FALLBACK)]
def tile(name, size=160, purple=False):
    g = ('#7B3FE4', '#4F17A8', '#36107A') if purple else ('#F7854F', '#E2541C', '#B8410F')
    isz = int(size*0.56); sw = 2.3
    svg = f'<svg width="{isz}" height="{isz}" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICON_LIB[name]}</svg>'
    return (f'<div class="tile" style="width:{size}px;height:{size}px"><i class="d1"></i><i class="d2"></i>'
            f'<div class="sq" style="background:linear-gradient(145deg,{g[0]},{g[1]});box-shadow:0 {size//12}px 0 {g[2]},0 {size//6}px {size//4}px rgba(60,20,0,.25),inset 0 3px 0 rgba(255,255,255,.35)">{svg}</div></div>')

pts = content['points']; N = len(pts) + 2
def foot(i): return f'<div class="foot"><div class="h"><img src="{LOGO_NAME}" alt="">@ai.pm.lab</div><div class="pg">{str(i).translate(FA)} / {str(N).translate(FA)}</div></div>'
c = content['cover']; slides = []
slides.append(f'''<div class="s"><div class="bar"></div><span class="tag">{c.get("tag","AI × Project Management")}</span>
<div class="top" style="justify-content:flex-end;margin-top:40px">{tile(pick_icon(c.get("icon"), c.get("tag")), 190)}</div>
<h1>{c["title"]}</h1><p class="lead">{c.get("lead","")}</p><div class="swipe">ورق بزن {ARROW}</div>{foot(1)}</div>''')
for k, p in enumerate(pts, 2):
    slides.append(f'''<div class="s"><div class="bar"></div><div class="top"><div class="num">{p.get("num", str(k-1).translate(FA))}</div>{tile(pick_icon(p.get("icon"), p.get("label"), p.get("title"), k=k), 150, purple=(k%2==1))}</div>
<h2>{p["title"]}</h2><p class="use">{p.get("sub","")}</p><div class="lbl">{SPARK} {p.get("label","نکته")}</div>
<div class="box">{p["body"]}</div>{foot(k)}</div>''')
f = content['final']
rows = ''.join(f'<div class="row"><div class="ic{" o" if i==1 else ""}">{ICONS[i%3]}</div>{r}</div>' for i, r in enumerate(f['rows']))
slides.append(f'''<div class="s"><div class="bar"></div><div class="top"><h1 style="font-size:84px">{f["title"]}</h1>{tile(pick_icon(f.get("icon","bookmark")), 130)}</div>
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
