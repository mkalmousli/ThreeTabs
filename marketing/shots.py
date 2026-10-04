import sys, os
from playwright.sync_api import sync_playwright
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, 'out'); os.makedirs(out, exist_ok=True)
jobs = [('s1','screenshot-1-hero'),('s2','screenshot-2-popup'),('s3','screenshot-3-settings'),('s4','screenshot-4-blocked'),('s5','screenshot-5-foss'),('tile','promo-small-440x280'),('marquee','promo-large-1400x560')]
sizes = {'tile':(440,280),'marquee':(1400,560)}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--allow-file-access-from-files'])
    for s, name in jobs:
        w, h = sizes.get(s, (1280, 800))
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.add_init_script(path=os.path.join(here, 'mock.js'))
        pg.goto(f'file://{here}/scenes.html?s={s}'); pg.wait_for_timeout(700)
        f = os.path.join(out, name + '.png'); pg.screenshot(path=f); pg.close()
        Image.open(f).convert('RGB').save(f)  # 24-bit, no alpha
        print(name, Image.open(f).size, Image.open(f).mode)
    b.close()
