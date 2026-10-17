"""Verify the real rendered assemblies are used throughout both motor sweeps."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
r=Path(__file__).resolve().parents[1];out=r/'docs/component-tests';out.mkdir(exist_ok=True);results=[]
url=os.environ.get('PINBALL_TEST_URL','http://127.0.0.1:8081/games/pinball/')
def passed(name,**evidence):results.append({'test':name,'passed':True,**evidence});print('PASS',name,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1150});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url+'?test=1');page.wait_for_function('Boolean(window.__pinball)');page.locator('#start').click()
 meta=page.evaluate('({frames:__pinball.renderer.flipperFrames,atlas:[__pinball.renderer.flipperAtlas.naturalWidth,__pinball.renderer.flipperAtlas.naturalHeight]})')
 assert meta['atlas']==[meta['frames']['atlasWidth'],meta['frames']['atlasHeight']]
 assert all(len(frames)==31 for frames in meta['frames']['frames'].values());passed('Both assembled Blender models load as 31 Cycles motor poses each')
 page.wait_for_timeout(100);page.locator('#table').screenshot(path=str(out/'desktop-rest.png'))
 for key,side in [('ArrowLeft','left'),('ArrowRight','right')]:
  page.keyboard.down(key);page.wait_for_timeout(170)
  f=page.evaluate(f'__pinball.renderer.flipperRenderFrames.{side}');assert abs(f['angle']-f['physicalAngle'])<.022
  page.locator('#table').screenshot(path=str(out/f'{side}-active.png'));page.keyboard.up(key);page.wait_for_timeout(170)
  f=page.evaluate(f'__pinball.renderer.flipperRenderFrames.{side}');assert abs(f['angle']-f['physicalAngle'])<.022
  passed(side+' model follows the real pivot at active and rest angles',maxAngleErrorRadians=.022)
 page.goto(url+'docs/component-review.html');page.locator('section').last.scroll_into_view_if_needed();page.wait_for_timeout(200)
 for target in page.locator('img').evaluate_all('(es)=>es.map(e=>e.src)'):
  response=page.request.get(target);assert response.ok,(target,response.status)
 passed('General view, six closeups, references and before/after images are reachable')
 assert not errors,errors;passed('No JavaScript errors in the game or review page')
 b.close()
(out/'results.json').write_text(json.dumps({'checks':results,'errors':errors},indent=2))
