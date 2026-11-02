import os,sys
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.sync_api import sync_playwright
a,b=int(sys.argv[1]),int(sys.argv[2]); FPS=30
with sync_playwright() as p:
  br=p.chromium.launch();pg=br.new_page(viewport={'width':1920,'height':1080})
  pg.goto('file:///home/claude/video/promo2.html');pg.wait_for_timeout(1000)
  for f in range(a,b):
    out=f'frames3/f{f:05d}.jpg'
    if os.path.exists(out): continue
    pg.evaluate(f'render({f/FPS})')
    pg.screenshot(path=out,type='jpeg',quality=94)
  br.close()
open(f'done3_{a}','w').write('ok')
