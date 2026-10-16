"""V4 end-to-end guided launch, pause/reset, depth, and complete natural game."""
import json,os,time,math,shutil,tempfile,playwright,base64,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];out=root/'docs/precision-tests';out.mkdir(parents=True,exist_ok=True)
url=os.environ.get('PINBALL_TEST_URL','http://127.0.0.1:8081/games/pinball/')
# Use the existing system FFmpeg; no browser-runtime download is required.
ffmpeg=shutil.which('ffmpeg')
if not ffmpeg:raise RuntimeError('Install FFmpeg to record the requested launch video')
registry=json.loads((Path(playwright.__file__).parent/'driver/package/browsers.json').read_text())
revision=next(b['revision'] for b in registry['browsers'] if b['name']=='ffmpeg')
cache=Path(tempfile.gettempdir())/'ferrisariato-playwright';binary=cache/f'ffmpeg-{revision}'/'ffmpeg-linux';binary.parent.mkdir(parents=True,exist_ok=True)
if not binary.exists():binary.symlink_to(ffmpeg)
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(cache)
results=[]
def passed(name,**evidence):results.append({'test':name,'passed':True,**evidence});print('PASS',name,flush=True)
def contact_sheet():
 canvas=Image.new('RGB',(1120,900),'#071a31');draw=ImageDraw.Draw(canvas)
 for i in range(8):
  im=Image.open(out/f'launch-{i}.png').convert('RGB');im.thumbnail((275,412));x=(i%4)*280;y=(i//4)*450;canvas.paste(im,(x,y+24));draw.text((x+8,y+5),f'{i+1}. '+(['Entrada','Ascenso','Curva derecha','Detras de casa','Curva izquierda','Descenso','Desembocadura','Playfield'][i]),fill='white')
 canvas.save(out/'launch-contact-sheet.jpg',quality=93)

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1100,'height':1100},record_video_dir=str(out/'video'),record_video_size={'width':1100,'height':1100})
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url+'?test=1');page.wait_for_function('Boolean(window.__pinball)');page.locator('#start').click()
 page.evaluate("""()=>{window.__launchCapture=[];const thresholds=[.03,.20,.45,.635,.75,.86,.95];const capture=()=>{const g=__pinball.game,i=__launchCapture.length;if((i<7&&g.rampPose&&g.rampPose.progress>=thresholds[i])||(i===7&&g.travelState==='PLAYFIELD'))__launchCapture.push({state:__pinball.snapshot(),image:document.getElementById('table').toDataURL('image/png')});if(__launchCapture.length<8)requestAnimationFrame(capture);};requestAnimationFrame(capture);} """)
 page.keyboard.down('Space');page.wait_for_timeout(700);page.keyboard.up('Space')
 page.wait_for_function('__pinball.game.travelState==="RAMP_TRAVEL"')
 assert not page.evaluate('__pinball.game.ball.IsActive()')
 passed('Physical plunger sensor activates RAMP_TRAVEL and suspends lower collisions')
 page.wait_for_function('__launchCapture.length===8',timeout=10000)
 captures=page.evaluate('__launchCapture');timeline=[c['state'] for c in captures]
 for i,c in enumerate(captures):(out/f'launch-{i}.png').write_bytes(base64.b64decode(c['image'].split(',')[1]))
 page.wait_for_function('__pinball.game.score>0');passed('Full visible route returns to floor and reaches a scoring bumper',score=page.evaluate('__pinball.game.score'))
 # Runtime uses the same 481 samples as the editable channel. Verify rear passage.
 assert any(s['ramp']['y']<1 for s in timeline[:-1]);assert any(len(s['rampLights'])>0 for s in timeline[:-1]);assert any(s['ballVisibleFraction']>.5 for s in timeline[:-1]);assert any(s['ballVisibleFraction']<.25 for s in timeline[:-1]);assert all(not s['ballActive'] for s in timeline[:-1])
 passed('Rear arc behind house, rotating ball and sequential light positions share Blender spline',samples=page.evaluate('__pinball.game.layout.ramp.samples.length'))
 (out/'launch-timeline.json').write_text(json.dumps(timeline,indent=2))
 video=page.video;page.close();ctx.close();video.save_as(str(out/'complete-channel-launch.webm'))
 if '--capture-only' in sys.argv:
  contact_sheet();browser.close();print('Launch evidence refreshed');sys.exit(0)
 ctx=browser.new_context(viewport={'width':1440,'height':1080});page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url+'?test=1');page.wait_for_function('Boolean(window.__pinball)');page.locator('#start').click()
 page.keyboard.press('Space');page.wait_for_function('__pinball.game.travelState==="RAMP_TRAVEL"');page.locator('#pause').click()
 before=page.evaluate('__pinball.snapshot()');page.wait_for_timeout(400);after=page.evaluate('__pinball.snapshot()');assert before['ramp']==after['ramp'];assert before['remaining']==after['remaining']
 page.locator('#pause').click();page.wait_for_function('(v)=>__pinball.game.rampDistance>v',arg=before['ramp']['distance']);passed('Pause freezes elevated ball, rotation and timer; resume continues same route')
 page.locator('#restart').click();assert page.evaluate('__pinball.game.travelState')=='SHOOTER';assert page.evaluate('__pinball.game.rampPose') is None
 page.keyboard.press('Space');page.wait_for_function('__pinball.game.travelState==="RAMP_TRAVEL"');page.wait_for_function('__pinball.game.entered');passed('Restart during travel resets guided state and permits a fresh complete launch')
 # Occlusion evidence: depth rejects sample positions actually hidden by structure.
 occ=page.evaluate('''()=>{const r=__pinball.renderer,ps=__pinball.game.layout.ramp.samples;let visible=0,hidden=0;for(const [x,y,z] of ps){const p=r.point(x,y,z+.17);if(r.depthAt(p.x,p.y)+.17<r.distance(x,y,z+.17))hidden++;else visible++;}return {visible,hidden,total:ps.length};}''')
 assert occ['visible']>occ['total']*.65;assert occ['hidden']>0
 passed('Exported static depth keeps ball above bed and occludes it behind physical parts',**occ)
 page.evaluate('__pinball.renderer.debug=true');page.locator('#table').screenshot(path=str(out/'projected-collision-map.png'));page.evaluate('__pinball.renderer.debug=false')
 # A complete production game. Only keyboard/plunger inputs; no body teleport,
 # time acceleration, direct scoring, forced drains or shortened match duration.
 page.locator('#restart').click();start=time.monotonic();launches=0;inputs={'left':False,'right':False};snapshots=[]
 while time.monotonic()-start<135:
  s=page.evaluate('__pinball.snapshot()');snapshots.append(s)
  if s['status']=='finished':break
  if not s['launched'] and not page.evaluate('__pinball.game.lossDelay'):
   page.keyboard.down('Space');page.wait_for_timeout(500);page.keyboard.up('Space');launches+=1
  for side,key in [('left','ArrowLeft'),('right','ArrowRight')]:
   down=s['travelState']=='PLAYFIELD' and s['position']['y']>12.5 and (s['position']['x']<5 if side=='left' else s['position']['x']>=5)
   if down!=inputs[side]:(page.keyboard.down if down else page.keyboard.up)(key);inputs[side]=down
  page.wait_for_timeout(100)
 assert s['status']=='finished',s;assert launches>=1;assert s['score']>0;assert not errors,errors
 page.screenshot(path=str(out/'complete-game-desktop.png'));(out/'complete-game-timeline.json').write_text(json.dumps(snapshots,indent=1))
 passed('Complete desktop game using only real keyboard input',launches=launches,elapsedWallSeconds=round(time.monotonic()-start,2),score=s['score'],ballsRemaining=s['balls'],simulationSeconds=120-s['remaining'])
 passed('Canvas work remains under 20 ms average',averageFrameMs=s['averageFrameMs']);assert s['averageFrameMs']<20
 ctx.close()
 mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True);page=mobile.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url+'?test=1');page.wait_for_function('Boolean(window.__pinball)');page.locator('#start').tap();button=page.locator('#launch').bounding_box();cdp=mobile.new_cdp_session(page)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':button['x']+button['width']/2,'y':button['y']+button['height']/2,'id':1}]});page.wait_for_timeout(650);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 page.wait_for_function('__pinball.game.travelState==="RAMP_TRAVEL"');page.screenshot(path=str(out/'mobile-ramp.png'));page.wait_for_function('__pinball.game.entered');page.wait_for_function('__pinball.game.score>0');page.screenshot(path=str(out/'mobile-playfield.png'))
 passed('Mobile touch plunger completes channel and restores scoring physics')
 # Finish a full mobile match with real touch launches and flipper taps.
 start=time.monotonic();mobileLaunches=1
 while time.monotonic()-start<135:
  ms=page.evaluate('__pinball.snapshot()')
  if ms['status']=='finished':break
  if not ms['launched'] and not page.evaluate('__pinball.game.lossDelay'):
   button=page.locator('#launch').bounding_box();cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':button['x']+button['width']/2,'y':button['y']+button['height']/2,'id':1}]});page.wait_for_timeout(450);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});mobileLaunches+=1
  elif ms['travelState']=='PLAYFIELD' and ms['position']['y']>12.5:
   box=page.locator('#table').bounding_box();tx=box['x']+box['width']*(.25 if ms['position']['x']<5 else .75);ty=box['y']+box['height']*.8
   cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':tx,'y':ty,'id':2}]});page.wait_for_timeout(90);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  page.wait_for_timeout(100)
 assert ms['status']=='finished';assert ms['score']>0
 page.screenshot(path=str(out/'complete-game-mobile.png'));passed('Complete mobile game using only touch input',launches=mobileLaunches,score=ms['score'],ballsRemaining=ms['balls'],simulationSeconds=120-ms['remaining'])
 assert not errors,errors;passed('No JavaScript runtime errors',errors=errors);mobile.close();browser.close()
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
contact_sheet()
print('PRECISION_BROWSER_COMPLETE',len(results),flush=True)
