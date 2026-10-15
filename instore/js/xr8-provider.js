/**
 * 8th Wall XR Engine / PlayCanvas adapter for Ferrisariato.
 * Ported from the production approach used in cebx3001/Gaussian-AR/src/ar-page.ts.
 * XR engine software © 2026 Niantic Spatial, Inc.; distributed UNMODIFIED
 * under the XR Engine License Agreement: https://github.com/8thwall/engine/blob/main/LICENSE
 */
const PRIORITY={DETECTED_SURFACE:3,ESTIMATED_SURFACE:2,FEATURE_POINT:1};
const isMobile=()=>/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)||navigator.maxTouchPoints>1;
let pendingEngine=null;
export function loadXR8(){
 if(globalThis.XR8) return Promise.resolve(globalThis.XR8);
 if(pendingEngine)return pendingEngine;
 pendingEngine=new Promise((resolve,reject)=>{
  const src=new URL('../../external/xr/xr.js',import.meta.url).href;
  const timer=setTimeout(()=>reject(Error('El motor local de 8th Wall no respondió en 30 segundos. Revisa /external/xr/')),30000);
  const ready=()=>{if(!globalThis.XR8)return;clearTimeout(timer);resolve(globalThis.XR8);};
  window.addEventListener('xrloaded',ready,{once:true});
  const script=document.createElement('script');script.async=true;script.dataset.preloadChunks='slam';script.src=src;
  script.onerror=()=>{clearTimeout(timer);reject(Error('Falta XR Engine en /external/xr/. Debe copiarse completo mediante el flujo de publicación.'));};
  document.head.append(script);ready();
 });
 pendingEngine.catch(()=>{pendingEngine=null;});return pendingEngine;
}
export async function requestXRPermissions(){
 for(const ev of [window.DeviceMotionEvent,window.DeviceOrientationEvent]){
  const ask=ev?.requestPermission;
  if(typeof ask==='function'&&await ask.call(ev)!=='granted')throw Error('No se autorizó el movimiento del dispositivo.');
 }
}
/** One XR Engine tracking system for each app: no second competing camera. */
export class XR8Tracking{
 constructor({app,camera,canvas,onStatus=()=>{},onEnd=()=>{},onHit=()=>{}}){
  Object.assign(this,{app,camera,canvas,onStatus,onEnd,onHit});
  this.active=false;this.ready=false;this.hit=null;this.hitTime=0;this.placed=false;this.position=null;
  this.ySamples=[];this.floorY=null;this.rejected=0;this.frames=0;this.valid=0;
  this._update=()=>this.update();
 }
 get available(){return isMobile();}
 async start(){
  if(this.active)return;
  await requestXRPermissions();
  const xr=await loadXR8();
  if(xr.loadChunk)await xr.loadChunk('slam');
  if(!xr.PlayCanvas?.runXr||!xr.XrController?.hitTest)throw Error('El motor cargó sin los módulos PlayCanvas/SLAM.');
  this.xr=xr;this.hit=null;this.placed=false;this.ready=false;this.position=null;this.floorY=null;
  this.ySamples=[];this.rejected=0;this.frames=0;this.valid=0;
  this.camera.setPosition(0,2,0); // Same initial tracking coordinate origin as Gaussian-AR.
  xr.XrController.configure({disableWorldTracking:false,scale:'responsive'});
  const that=this;
  const modules=[{name:'ferrisariato-xr8',onUpdate(e){that.onFrame(e);},onException(err){that.onStatus('8th Wall: '+(err?.message||err),true);},onDeviceIncompatible(){that.onStatus('Este dispositivo no es compatible con XR Engine.',true);},onCameraStatusChange(e){if(e.status==='failed')that.onStatus('No se pudo iniciar la cámara.',true);}}];
  this.active=true;this.app.on('update',this._update);
  try{xr.PlayCanvas.runXr({pcCamera:this.camera,pcApp:this.app},modules,{canvas:this.canvas,allowedDevices:xr.XrConfig.device().MOBILE});this.onStatus('Mueve el teléfono y apunta a una superficie horizontal.');}
  catch(e){this.active=false;this.app.off('update',this._update);throw e;}
 }
 onFrame(frame){
  if(!this.active||!frame?.processCpuResult?.reality)return;
  this.valid++;this.ready=true;
  if(this.placed)return;
  let hits=[];
  try{hits=this.xr.XrController.hitTest(.5,.5,[])||[];}catch{return;}
  let best=null;
  for(const h of hits){const rank=PRIORITY[h?.type]||0;if(!rank)continue;
   if(h.type==='DETECTED_SURFACE'&&h.rotation){const {x=0,z=0}=h.rotation;const ny=1-2*(x*x+z*z);if(Math.abs(ny)<.4)continue;}
   if(!best||rank>best.rank)best={rank,h};}
  if(!best)return;
  const p=best.h.position;if(!p||![p.x,p.y,p.z].every(Number.isFinite))return;
  this.position={x:p.x,y:p.y,z:p.z};this.hitTime=performance.now();
  if(this.floorY!==null&&this.ySamples.length>=5&&Math.abs(p.y-this.floorY)>.3){if(++this.rejected<10)return;this.ySamples=[];}
  this.rejected=0;this.ySamples.push(p.y);if(this.ySamples.length>15)this.ySamples.shift();
  const ordered=[...this.ySamples].sort((a,b)=>a-b);this.floorY=ordered[ordered.length>>1];
 }
 currentSurface(){
  if(!this.ready)return null;
  const c=this.camera.getPosition(),f=this.camera.forward;
  if(f.y>-.15)return null;
  const recent=this.position&&performance.now()-this.hitTime<2000;
  const y=recent?this.floorY:0;
  let d=(y-c.y)/f.y;
  if(recent&&this.floorY!==null&&Math.abs(this.position.y-this.floorY)<=.3){
    const measured=Math.hypot(this.position.x-c.x,this.position.y-c.y,this.position.z-c.z);
    if(d>measured*1.15)d=measured;
  }
  if(!Number.isFinite(d)||d<.25||d>8)return null;
  return {x:c.x+f.x*d,y:c.y+f.y*d,z:c.z+f.z*d};
 }
 update(){if(!this.active||this.placed)return;const p=this.currentSurface();this.hit=p;
  if(p){this.frames++;this.onHit(p,this.frames>=5);}else{this.frames=0;this.onHit(null,false);}}
 lock(){if(!this.hit||this.frames<5)return null;const v={...this.hit};this.placed=true;this.hit=null;return v;}
 scanAgain(){this.placed=false;this.hit=null;this.frames=0;}
 stop(){if(!this.active)return;this.active=false;this.app.off('update',this._update);try{this.xr?.PlayCanvas?.stopXr?.();}catch(err){console.warn('XR8 stop',err);}this.xr=null;this.ready=false;this.placed=false;this.hit=null;this.onEnd();}
}
