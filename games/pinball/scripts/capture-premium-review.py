"""Capture the real ready-state canvas and produce a same-camera comparison."""
import os,base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
url=os.environ.get('PINBALL_TEST_URL','http://127.0.0.1:8080/games/pinball/')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1050})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url+'?test=1');page.wait_for_function('window.__pinball && __pinball.snapshot().frames>8')
    png=page.locator('#table').evaluate("canvas=>canvas.toDataURL('image/png')")
    (root/'docs/premium-after-table.png').write_bytes(base64.b64decode(png.split(',')[1]))
    page.goto(url+'docs/premium-comparison.html')
    page.locator('#split').fill('35');page.locator('#split').dispatch_event('input')
    assert page.locator('#comparison').evaluate("e=>e.style.getPropertyValue('--split')")=='35%'
    assert not errors,errors
    browser.close()
canvas=Image.new('RGB',(1808,1210),'#061526');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('DejaVuSans.ttf',27);small=ImageFont.truetype('DejaVuSans.ttf',17)
for i,(name,label) in enumerate([('premium-before-table','ANTES · V2'),('premium-after-table','ACTUAL · V3')]):
    x=16+i*896;draw.text((x+12,18),label,font=font,fill='#ffda4d')
    im=Image.open(root/'docs'/f'{name}.png').convert('RGB');assert im.size==(880,1100);canvas.paste(im,(x,64))
draw.text((28,1179),'Misma cámara y posiciones · Capturas del juego real · Física y controles conservados',font=small,fill='#b7c9dd')
canvas.save(root/'docs/premium-comparison.png')
print('COMPARISON_CAPTURED; slider verified')
