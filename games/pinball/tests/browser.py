"""Run after starting the repo-root HTTP server: python3 games/pinball/tests/browser.py.
Uses actual Chromium, keyboard input, CDP multi-touch and real Box2D contacts.
No fake physics, camera permission, CDN or disabled TLS verification.
"""
import json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=os.environ.get('PINBALL_TEST_URL','http://127.0.0.1:8080/games/pinball/')
ART=Path(os.environ.get('PINBALL_TEST_OUTPUT','/tmp/ferrisariato-pinball-tests'));ART.mkdir(exist_ok=True,parents=True)
checks=[]
def passed(name):checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
    errors=[];failed=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('requestfailed',lambda r:failed.append(r.url))
    page.goto(BASE+'?test=1');page.wait_for_function('Boolean(window.__pinball)')
    page.screenshot(path=str(ART/'desktop-ready.png'))
    page.locator('#start').click()
    page.keyboard.down('ArrowLeft');page.wait_for_timeout(150)
    s=page.evaluate('__pinball.snapshot()');assert abs(s['flippers'][0]['angle']+.5)<.1;assert abs(s['flippers'][1]['angle']-2.72159)<.1
    page.keyboard.up('ArrowLeft');page.keyboard.down('ArrowRight');page.wait_for_timeout(150)
    s=page.evaluate('__pinball.snapshot()');assert abs(s['flippers'][1]['angle']-3.64159)<.1
    page.keyboard.up('ArrowRight');passed('Independent keyboard flippers')
    page.keyboard.down('Space');page.wait_for_timeout(1100)
    s=page.evaluate('__pinball.snapshot()');assert s['charge']>.7;assert not s['launched']
    page.keyboard.up('Space');page.wait_for_function('__pinball.snapshot().entered',timeout=5000)
    passed('Keyboard charge, release, real lane entry')
    page.wait_for_function('__pinball.snapshot().score>0',timeout=5000)
    assert page.locator('#score').inner_text()!='000.000';assert page.locator('#time').inner_text()!='02:00'
    assert page.evaluate('__pinball.audio.context.state')=='running';assert page.evaluate('__pinball.audio.played')>0
    passed('Real scoring, countdown and running Web Audio')
    # Contacts are arranged deterministically, then executed by the running
    # production physics loop. No direct hit/scoring calls are used.
    for index in range(7):
        target=page.evaluate(f'__pinball.game.layout.targets[{index}]')
        page.evaluate('o=>{__pinball.game.start();__pinball.placeBall(o.x,o.y+.55,0,-5)}',target)
        page.wait_for_function('(id)=>__pinball.snapshot().hits[id]===1',arg=target['id'])
        s=page.evaluate('__pinball.snapshot()');assert s['score']==150;assert target['id'] in s['lights']
        assert len(s['lights'])==1
        page.wait_for_function('(id)=>!(id in __pinball.snapshot().lights)',arg=target['id'])
    passed('All seven independent target contacts, scores and transient lights')
    for o in page.evaluate('__pinball.game.layout.bumpers'):
        page.evaluate('o=>{__pinball.game.start();__pinball.placeBall(o.x,o.y+o.radius+.4,0,-6)}',o)
        page.wait_for_function('(id)=>__pinball.snapshot().hits[id]===1',arg=o['id']);assert page.evaluate('__pinball.snapshot().velocity.y')>0
    passed('All three main bumpers and both secondary tanks rebound')
    for i in range(2):
        page.evaluate('(i)=>{__pinball.game.start();__pinball.placeBall(i?6.7:2.8,12,i?3:-3,4)}',i)
        page.wait_for_function('(id)=>__pinball.snapshot().hits[id]>0',arg='sling-right' if i else 'sling-left')
        assert page.evaluate('__pinball.snapshot().velocity.y')<0
    passed('Both active slingshots')
    page.locator('#restart').click();page.locator('#pause').click();remaining=page.evaluate('__pinball.snapshot().remaining')
    page.wait_for_timeout(250);assert page.evaluate('__pinball.snapshot().remaining')==remaining
    page.locator('#pause').click();page.wait_for_function('__pinball.snapshot().remaining<'+str(remaining))
    passed('Pause freezes time and resumes')
    for lives in [2,1,0]:
        page.evaluate('__pinball.placeBall(4.8,16.6,0,4)')
        page.wait_for_function('(n)=>__pinball.snapshot().balls===n',arg=lives)
        if lives:page.wait_for_function('!__pinball.game.lossDelay')
    assert page.locator('#overlay').is_visible();assert page.evaluate('__pinball.snapshot().status')=='finished'
    page.locator('#start').click();assert page.evaluate('__pinball.snapshot().score')==0;assert page.evaluate('__pinball.snapshot().balls')==3
    page.evaluate('__pinball.game.elapsed=119.99');page.wait_for_function('__pinball.snapshot().status==="finished"')
    passed('Three losses, game over, restart and time limit')
    page.locator('#start').click();page.keyboard.down('Space');page.wait_for_timeout(1000);page.keyboard.up('Space')
    page.wait_for_timeout(1800);page.screenshot(path=str(ART/'desktop-playing.png'))
    performance=page.evaluate('__pinball.snapshot()');assert performance['averageFrameMs']<20
    passed('Desktop rendering average frame work < 20 ms')
    assert not errors,errors;assert not failed,failed
    page.close()
    mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page=mobile.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE+'?test=1');page.wait_for_function('Boolean(window.__pinball)');page.locator('#start').tap()
    cdp=mobile.new_cdp_session(page);box=page.locator('#table').bounding_box()
    left={'x':box['x']+box['width']*.25,'y':box['y']+box['height']*.8,'id':1}
    right={'x':box['x']+box['width']*.7,'y':box['y']+box['height']*.8,'id':2}
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[left,right]})
    page.wait_for_timeout(180);s=page.evaluate('__pinball.snapshot()')
    assert abs(s['flippers'][0]['angle']+.5)<.1 and abs(s['flippers'][1]['angle']-3.64159)<.1
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[left]});page.wait_for_timeout(150)
    s=page.evaluate('__pinball.snapshot()');assert abs(s['flippers'][0]['angle']-.42)<.1;assert abs(s['flippers'][1]['angle']-3.64159)<.1
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    passed('Mobile simultaneous multi-touch flippers and independent release')
    # The instruction specifies screen halves, including the bottom apron.
    apron=page.locator('.flipper-label').first.bounding_box()
    extra={'x':apron['x']+apron['width']/2,'y':apron['y']+apron['height']/2,'id':4}
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[extra]});page.wait_for_timeout(180)
    assert abs(page.evaluate('__pinball.snapshot().flippers[0].angle')+.5)<.1
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    passed('Touch outside the canvas still activates the corresponding screen half')
    box=page.locator('#launch').bounding_box();point={'x':box['x']+box['width']/2,'y':box['y']+box['height']/2,'id':3}
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[point]});page.wait_for_timeout(1000)
    assert page.evaluate('__pinball.snapshot().charge')>.7
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    page.wait_for_function('__pinball.snapshot().entered',timeout=5000)
    page.screenshot(path=str(ART/'mobile-playing.png'))
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors,errors
    passed('Mobile independent plunger, real launch and responsive layout')
    browser.close()
(ART/'results.json').write_text(json.dumps({'checks':checks,'desktop_performance':performance,'errors':errors,'failed_requests':failed},indent=2))
print(f'{len(checks)} browser checks passed. Artifacts: {ART}',flush=True)
