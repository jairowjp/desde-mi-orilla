import os
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.sync_api import sync_playwright
def html(col,line,shadow):
    return f"""<style>@font-face{{font-family:GV;src:url(file:///home/claude/fonts/GreatVibes-Regular.ttf)}}
html,body{{margin:0;width:1920px;height:1080px;background:transparent}}
.w{{position:absolute;right:46px;bottom:20px;display:flex;align-items:center;gap:14px}}
.l{{width:46px;height:1.5px;background:{line};opacity:.9}}
.s{{width:6px;height:6px;transform:rotate(45deg);background:{line}}}
.t{{font-family:GV;font-size:46px;color:{col};text-shadow:{shadow};line-height:1}}</style>
<div class="w"><span class="l"></span><span class="s"></span><span class="t">Jhayyayim Studio</span></div>"""
with sync_playwright() as p:
  b=p.chromium.launch();pg=b.new_page(viewport={'width':1920,'height':1080})
  for name,col,line,sh in [('wm_claro','#F3ECDF','#E3A584','0 2px 10px rgba(0,0,0,.35)'),('wm_oscuro','#144556','#CF764E','0 1px 6px rgba(243,236,223,.6)')]:
    open('/home/claude/fonts/w.html','w').write(html(col,line,sh));pg.goto('file:///home/claude/fonts/w.html');pg.wait_for_timeout(600)
    pg.screenshot(path=f'{name}.png',omit_background=True)
  b.close()
