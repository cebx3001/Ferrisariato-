import {PinballPhysics} from './physics.js?v=reference-5.6';
import {Renderer} from './renderer.js?v=reference-5.6';
import {PinballAudio} from './audio.js';
const BUILD='reference-5.6';
const $=id=>document.getElementById(id),audio=new PinballAudio();
const image=src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('No se pudo cargar '+src));i.src=src+'?v='+BUILD;});
const json=async url=>{const r=await fetch(url+'?v='+BUILD);if(!r.ok)throw Error('No se pudo cargar '+url);return r.json();};
try {
  const [layout,projection,background,interactives,foreground,glass,ballSprite,depth,flipperAtlas,flipperFrames]=await Promise.all([json('./layout.json'),json('./assets/projection.json'),image('./assets/table.webp'),image('./assets/interactives.webp'),image('./assets/foreground.webp'),image('./assets/glass.webp'),image('./assets/ball.webp'),image('./assets/depth.png'),image('./assets/flippers.webp'),json('./assets/flippers.json')]);
  const game=new PinballPhysics(window.box2d,layout),renderer=new Renderer($('table'),projection,layout,background,interactives,foreground,glass,ballSprite,depth,flipperAtlas,flipperFrames);
  await document.fonts.load('54px PinballSegment');
  const params=new URLSearchParams(location.search);renderer.debug=params.has('debug');
  let paused=false,accumulator=0,last=performance.now(),frameCount=0,maxFrame=0,totalFrame=0;
  const pointers=new Map(),keys=new Set();let launchPointer=null;
  const updateInputs=()=>{for(const side of ['left','right'])game.setFlipper(side,keys.has(side)||[...pointers.values()].includes(side));};
  const clear=()=>{pointers.clear();keys.clear();launchPointer=null;game.clearInputs();$('launch').classList.remove('active');};
  // A short acceleration spike nudges the physical ball. Regular hand movement
  // and device inclination do not apply a continuous force to the table.
  const motion={requested:false,gravity:null,lastShake:0};
  const onMotion=e=>{
    if(paused||game.status!=='playing'||game.travelState!=='PLAYFIELD')return;
    let x=e.acceleration?.x,y=e.acceleration?.y,z=e.acceleration?.z;
    if(![x,y,z].every(Number.isFinite)){
      const a=e.accelerationIncludingGravity;
      if(!a||![a.x,a.y,a.z].every(Number.isFinite))return;
      if(!motion.gravity){motion.gravity={x:a.x,y:a.y,z:a.z};return;}
      const g=motion.gravity;
      g.x=.88*g.x+.12*a.x;g.y=.88*g.y+.12*a.y;g.z=.88*g.z+.12*a.z;
      x=a.x-g.x;y=a.y-g.y;z=a.z-g.z;
    }
    const magnitude=Math.hypot(x,y,z),now=performance.now();
    if(magnitude<12||now-motion.lastShake<750)return;
    motion.lastShake=now;
    const lateral=Math.abs(x)>2?x:(y>=0?2:-2);
    if(game.nudge(lateral,-Math.max(2,Math.abs(y)*.55),Math.min(1.6,magnitude/16)))audio.play('sling');
  };
  const enableMotion=()=>{
    if(motion.requested||typeof DeviceMotionEvent==='undefined')return;
    motion.requested=true;
    const listen=()=>window.addEventListener('devicemotion',onMotion,{passive:true});
    if(typeof DeviceMotionEvent.requestPermission==='function'){
      // iOS requires the permission request in the direct INICIAR tap handler.
      try{DeviceMotionEvent.requestPermission().then(v=>{if(v==='granted')listen();}).catch(()=>{});}
      catch(_){}
    }else listen();
  };
  const start=()=>{enableMotion();clear();game.start();paused=false;accumulator=0;last=performance.now();$('overlay').hidden=true;$('pause').textContent='PAUSAR';$('pause').disabled=false;$('restart').disabled=false;audio.unlock();$('table').focus({preventScroll:true});};
  $('start').disabled=false;$('start').innerHTML='INICIAR PARTIDA <span>↗</span>';$('start').onclick=start;$('restart').onclick=start;
  $('sound').onclick=()=>{audio.enabled=!audio.enabled;$('sound').textContent='SONIDO: '+(audio.enabled?'SÍ':'NO');$('sound').setAttribute('aria-pressed',String(audio.enabled));if(audio.enabled)audio.unlock();};
  const togglePause=()=>{if(game.status!=='playing')return;paused=!paused;clear();$('pause').textContent=paused?'CONTINUAR':'PAUSAR';last=performance.now();accumulator=0;};
  $('pause').onclick=togglePause;
  const charge=()=>{if(paused)return;audio.unlock();game.chargeStart();if(game.charging)$('launch').classList.add('active');};
  const release=()=>{game.chargeRelease();$('launch').classList.remove('active');};
  $('launch').addEventListener('pointerdown',e=>{e.preventDefault();if(launchPointer!==null)return;launchPointer=e.pointerId;e.currentTarget.setPointerCapture(e.pointerId);charge();});
  $('launch').addEventListener('pointerup',e=>{if(e.pointerId===launchPointer){release();launchPointer=null;}});
  $('launch').addEventListener('pointercancel',()=>{launchPointer=null;game.charging=false;game.charge=0;$('launch').classList.remove('active');});
  $('table').addEventListener('pointerdown',e=>{e.preventDefault();if(game.status!=='playing'||paused)return;audio.unlock();e.currentTarget.setPointerCapture(e.pointerId);const r=e.currentTarget.getBoundingClientRect();pointers.set(e.pointerId,e.clientX<r.left+r.width/2?'left':'right');updateInputs();audio.play('flipper');});
  // Touches on the scoreboard, apron or surrounding screen also operate the
  // corresponding flipper; independent buttons keep their own pointer input.
  document.addEventListener('pointerdown',e=>{if(e.pointerType!=='touch'||e.target===$('table')||e.target.closest('button,.overlay')||paused||game.status!=='playing')return;e.preventDefault();$('table').setPointerCapture(e.pointerId);pointers.set(e.pointerId,e.clientX<innerWidth/2?'left':'right');updateInputs();audio.unlock();audio.play('flipper');});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])$('table').addEventListener(event,e=>{pointers.delete(e.pointerId);updateInputs();});
  document.addEventListener('keydown',e=>{
    if(!['ArrowLeft','ArrowRight','Space','KeyP','KeyN'].includes(e.code))return;
    if(e.code==='Space'&&e.target instanceof HTMLButtonElement&&game.status!=='playing')return;
    e.preventDefault();if(e.repeat)return;
    if(e.code==='KeyP'){togglePause();return;}if(paused||game.status!=='playing')return;
    if(e.code==='KeyN'){game.nudge(0,-1,1);return;}
    if(e.code==='Space')charge();else{keys.add(e.code==='ArrowLeft'?'left':'right');updateInputs();audio.play('flipper');}
  });
  document.addEventListener('keyup',e=>{if(e.code==='Space'){e.preventDefault();release();}else if(['ArrowLeft','ArrowRight'].includes(e.code)){keys.delete(e.code==='ArrowLeft'?'left':'right');updateInputs();}});
  window.addEventListener('blur',()=>{clear();if(!paused&&game.status==='playing')togglePause();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){clear();if(!paused&&game.status==='playing')togglePause();}});
  function frame(now){
    const begin=performance.now(),dt=Math.min(.1,(now-last)/1000);last=now;
    if(!paused){accumulator+=dt;while(accumulator>=1/120){game.tick(1/120);accumulator-=1/120;}}
    for(const event of game.events.splice(0)){
      if(event.type==='hit')audio.play(event.kind,event.id);
      if(event.type==='launch')audio.play('launch');
      if(event.type==='unstuck')audio.play('sling');
      if(event.type==='finish'){
        audio.play('finish');$('overlay').hidden=false;$('overlay-tag').textContent='PARTIDA TERMINADA';$('overlay-title').textContent=game.score.toLocaleString('es-EC')+' PUNTOS';$('overlay-description').textContent=event.reason==='time'?'¡Se acabó el tiempo! Vuelve a jugar y supera tu marca.':'¡Buen intento! Vuelve a lanzar y supera tu marca.';$('start').innerHTML='JUGAR OTRA VEZ <span>↗</span>';$('pause').disabled=true;clear();
      }
    }
    renderer.draw(game);
    $('score').textContent=String(game.score).padStart(6,'0').replace(/(\d{3})$/,'.$1');
    const seconds=Math.ceil(game.remaining);$('time').textContent=String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
    $('balls').textContent='● '.repeat(Math.max(0,game.balls)).trim()||'—';$('balls').setAttribute('aria-label',game.balls+' bolas');
    $('charge').style.height=game.charge*100+'%';$('launch').disabled=game.status!=='playing'||game.launched||!!game.lossDelay||paused;
    $('message').textContent=paused?'EN PAUSA · CONTINÚA CUANDO QUIERAS':game.status==='ready'?'CONSTRUYE TU CASA CON TODO':game.status==='finished'?'¡GRACIAS POR JUGAR!':game.lossDelay?'BOLA PERDIDA · PREPARANDO LANZADOR':!game.launched?'MANTÉN Y SUELTA PARA LANZAR':game.entered?'ENCIENDE LOS SIETE OBJETIVOS':game.rampDirection<0?'LANZAMIENTO DÉBIL · CARGA MÁS FUERZA':game.travelState==='RAMP_TRAVEL'?'RECORRIENDO EL CANAL':'¡LANZAMIENTO!';
    const duration=performance.now()-begin;maxFrame=Math.max(maxFrame,duration);totalFrame+=duration;frameCount++;requestAnimationFrame(frame);
  }
  // Controlled test instrumentation is only exposed under ?test=1; contacts
  // still run through the real Box2D world and production collision callbacks.
  if(params.get('test')==='1')window.__pinball={game,renderer,audio,snapshot:()=>({...game.snapshot(),rampLights:renderer.activeRampLights||[],ballVisibleFraction:renderer.ballVisibleFraction,paused,frames:frameCount,averageFrameMs:totalFrame/frameCount,maxFrameMs:maxFrame}),placeBall:(x,y,vx,vy)=>{game.travelState='PLAYFIELD';game.rampPose=null;game.launched=true;game.ball.SetActive(true);game.ball.SetPosition(new box2d.b2Vec2(x,y));game.ball.SetLinearVelocity(new box2d.b2Vec2(vx,vy));}};
  requestAnimationFrame(frame);
} catch(error){console.error(error);$('message').textContent='NO SE PUDO PREPARAR LA MESA';$('overlay-description').textContent='No se pudieron cargar los recursos. Recarga la página para intentarlo de nuevo.';$('start').textContent='RECARGAR';$('start').disabled=false;$('start').onclick=()=>location.reload();}
