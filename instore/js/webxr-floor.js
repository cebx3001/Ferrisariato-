// IN-STORE: AR real sobre PlayCanvas/WebXR en dispositivos compatibles.
// Una sola onda radial sin brillo ni pulsos adicionales.
import * as pc from 'https://cdn.jsdelivr.net/npm/playcanvas@2.22.6/build/playcanvas.mjs';
import {XR8Tracking,loadXR8} from './xr8-provider.js';
import {preferredTracking} from '../../shared/tracking-policy.js';
globalThis.pc=pc;
const MATERIALS=[
 {name:'ROBLE NATURAL',url:'./assets/instore-e1f65608d.jpg'},
 {name:'PIEDRA CLARA',url:'./assets/instore-a941ebd35.jpg'},
 {name:'CEMENTO URBANO',url:'./assets/instore-c300b854c.jpg'},
 {name:'ARENA MATE',url:'./assets/instore-ed819f1ba.jpg'}
];
const byId=id=>document.getElementById(id);
const easing=t=>1-Math.pow(1-Math.min(1,Math.max(0,t)),2.1);
function loadImage(url){return new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('Falta textura '+url));i.src=url;});}
export class FloorWebXR {
 constructor(){this.isReady=false;this.supported=false;this.active=false;this.placed=false;this.hit=null;this.hitResult=null;this.hitSource=null;this.anchor=null;this.materialIndex=0;this.width=2.4;this.depth=3;this.radius=0;this.timer=0;this.revealing=false;this.canvas=byId('xr-canvas');this.overlay=byId('xr-overlay');this.status=byId('xr-status');this.action=byId('xr-action');this.message=byId('xr-step-message');this.finish=byId('xr-finish');this.sliders=byId('xr-sliders');this.crosshair=byId('xr-crosshair');this.backend=null;this.xr8Tracking=null;this.ready=this.init();}
 async init(){
  const app=new pc.Application(this.canvas,{graphicsDeviceOptions:{alpha:true,antialias:true,depth:true}});this.app=app;app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);app.setCanvasResolution(pc.RESOLUTION_AUTO);app.scene.ambientLight=new pc.Color(1,1,1);
  this.camera=new pc.Entity('AR-CAMERA');this.camera.addComponent('camera',{clearColor:new pc.Color(0,0,0,0),nearClip:.01,farClip:100});app.root.addChild(this.camera);
  this.root=new pc.Entity('AR-FLOOR-ANCHOR');app.root.addChild(this.root);
  const makeMat=()=>{let m=new pc.StandardMaterial();m.diffuse.set(1,1,1);m.useLighting=false;m.cull=pc.CULLFACE_NONE;m.update();return m;};
  this.oldMat=makeMat();this.newMat=makeMat();this.newMat.blendType=pc.BLEND_NORMAL;this.newMat.depthWrite=false;
  const plane=(name,mat,y)=>{let e=new pc.Entity(name);e.addComponent('render',{type:'plane',material:mat});e.setLocalPosition(0,y,0);e.setLocalScale(this.width,1,this.depth);this.root.addChild(e);e.enabled=false;return e;};
  this.basePlane=plane('FLOOR-BASE',this.oldMat,.006);this.revealPlane=plane('FLOOR-REVEAL',this.newMat,.012);
  const markMat=makeMat();markMat.emissive.set(1,.86,0);markMat.useLighting=false;markMat.update();this.reticle=new pc.Entity('RETICLE');app.root.addChild(this.reticle);
  for(const [w,d] of [[.15,.006],[.006,.15]]){let e=new pc.Entity('RETICLE-ARM');e.addComponent('render',{type:'box',material:markMat});e.setLocalPosition(0,.01,0);e.setLocalScale(w,.007,d);this.reticle.addChild(e);}this.reticle.enabled=false;
  this.mask=document.createElement('canvas');this.mask.width=this.mask.height=128;this.maskCtx=this.mask.getContext('2d');
  this.maskTex=new pc.Texture(app.graphicsDevice,{width:128,height:128,format:pc.PIXELFORMAT_RGBA8,mipmaps:false,minFilter:pc.FILTER_LINEAR,magFilter:pc.FILTER_LINEAR,addressU:pc.ADDRESS_CLAMP_TO_EDGE,addressV:pc.ADDRESS_CLAMP_TO_EDGE});this.newMat.opacityMap=this.maskTex;this.newMat.opacityMapChannel='r';this.newMat.update();
  this.textures=await Promise.all(MATERIALS.map(async m=>{let img=await loadImage(m.url);let tex=new pc.Texture(app.graphicsDevice,{width:img.naturalWidth,height:img.naturalHeight,format:pc.PIXELFORMAT_RGBA8,mipmaps:true,minFilter:pc.FILTER_LINEAR_MIPMAP_LINEAR,magFilter:pc.FILTER_LINEAR,addressU:pc.ADDRESS_REPEAT,addressV:pc.ADDRESS_REPEAT});tex.setSource(img);return tex;}));
  this.oldMat.diffuseMap=this.textures[0];this.newMat.diffuseMap=this.textures[0];this.sizeMaterials();this.paintMask(0);
  this.overlay.querySelectorAll('button,input').forEach(n=>n.addEventListener('beforexrselect',e=>e.preventDefault()));
  byId('xr-exit').addEventListener('click',()=>this.stop());
  this.action.addEventListener('click',()=>this.placed?this.reveal():this.place());
  this.finish.addEventListener('click',()=>{this.stop();const complete=byId('preview-complete');if(complete)complete.click();});
  for(const name of ['width','depth'])byId('xr-'+name).addEventListener('input',e=>{this[name]=Number(e.target.value);byId('xr-'+name+'-text').textContent=this[name].toFixed(1)+' m';this.sizeMaterials();this.basePlane.setLocalScale(this.width,1,this.depth);this.revealPlane.setLocalScale(this.width,1,this.depth);});
  const mList=byId('xr-materials');mList.innerHTML=MATERIALS.map((m,i)=>`<button class="xr-material ${i===0?'selected':''}" type="button" data-floor="${i}"><span>${m.name}</span></button>`).join('');
  mList.addEventListener('click',e=>{const button=e.target.closest('[data-floor]');if(!button)return;this.materialIndex=Number(button.dataset.floor);mList.querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b===button));if(this.placed)this.reveal();});
  app.on('update',dt=>this.update(dt));app.xr.on('end',()=>this.end());app.xr.on('error',error=>{this.status.textContent='ERROR WEBXR: '+(error?.message||error);});app.start();
  this.isIOS=/iPhone|iPad|iPod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);this.nativeSupported=Boolean(!this.isIOS&&navigator.xr&&await navigator.xr.isSessionSupported('immersive-ar').catch(()=>false));this.xr8Available=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)||navigator.maxTouchPoints>1;this.supported=this.nativeSupported||this.xr8Available;this.isReady=true;if(this.xr8Available&&!this.nativeSupported)loadXR8().catch(e=>console.warn('[8th Wall fallback preload]',e.message));
 }
 sizeMaterials(){for(const m of [this.oldMat,this.newMat]){m.diffuseMapTiling=new pc.Vec2(this.width/1.2,this.depth/1.2);m.update();}}
 start(){if(!this.isReady||!this.supported)return;this.backend=preferredTracking({mobile:this.xr8Available,ios:this.isIOS,nativeSupported:this.nativeSupported,xr8Available:this.xr8Available,override:new URLSearchParams(location.search).get('tracking')});this.active=true;this.placed=false;this.hit=null;this.canvas.style.display='block';this.overlay.style.display='block';this.basePlane.enabled=false;this.revealPlane.enabled=false;this.reticle.enabled=false;this.crosshair.classList.remove('detected');this.finish.hidden=true;this.sliders.hidden=true;this.action.textContent='COLOCAR SUELO';this.message.textContent='BUSCANDO SUPERFICIE...';this.app.resizeCanvas(window.innerWidth,window.innerHeight);if(this.backend==='xr8'){void this.startXR8();return;}this.app.xr.domOverlay.root=this.overlay;
 // Must be invoked directly within a click; no await before starting WebXR.
 this.app.xr.start(this.camera.camera,pc.XRTYPE_AR,pc.XRSPACE_LOCALFLOOR,{planeDetection:true,anchors:true,callback:err=>{if(err){this.status.textContent='ARCore/WebXR no inició: '+(err?.message||err);if(this.xr8Available){this.backend='xr8';void this.startXR8();}else this.end();}}});
 this.app.xr.once('start',()=>{if(!this.app.xr.hitTest.supported){this.status.textContent='WEBXR SIN DETECCIÓN DE SUELO · ACTIVANDO 8TH WALL';this.pendingXR8Fallback=this.xr8Available;this.app.xr.end();return;}this.status.textContent='MUEVE EL TELÉFONO HASTA DETECTAR EL PISO';this.app.xr.hitTest.start({spaceType:pc.XRSPACE_VIEWER,callback:(err,source)=>{if(err){this.status.textContent='NO SE PUDO DETECTAR EL PISO';return;}this.hitSource=source;source.on('result',(pos,rot,input,result)=>{this.hit=pos.clone();this.hitResult=result;if(!this.placed){this.reticle.setPosition(pos.x,pos.y+.02,pos.z);this.reticle.enabled=true;this.crosshair.classList.add('detected');this.status.textContent='PISO DETECTADO · PULSA COLOCAR';this.message.textContent='SUPERFICIE DISPONIBLE';}});}});});
 }
 async startXR8(){
  if(!this.xr8Tracking){this.xr8Tracking=new XR8Tracking({app:this.app,camera:this.camera,canvas:this.canvas,
    onStatus:(msg,isError)=>{this.status.textContent=msg;if(isError)this.message.textContent='ERROR DE SEGUIMIENTO';},
    onHit:(p,stable)=>{if(this.backend!=='xr8'||this.placed)return;this.hit=p?new pc.Vec3(p.x,p.y,p.z):null;this.reticle.enabled=!!(p&&stable);if(p){this.reticle.setPosition(p.x,p.y+.018,p.z);this.status.textContent=stable?'SUELO DETECTADO · PULSA COLOCAR':'ANALIZANDO SUPERFICIE…';this.message.textContent=stable?'SUPERFICIE DISPONIBLE':'BUSCANDO SUPERFICIE';}this.crosshair.classList.toggle('detected',!!(p&&stable));},
    onEnd:()=>this.end()
   });}
  try{await this.xr8Tracking.start();}catch(e){console.error(e);this.status.textContent='8TH WALL: '+(e?.message||e);this.end();const label=byId('xr-status');if(label)label.textContent='No se pudo iniciar AR. Abre la simulación para continuar.';}
 }
 place(){if(this.backend==='xr8'){const p=this.xr8Tracking?.lock();if(!p){this.message.textContent='BUSCA UNA SUPERFICIE ESTABLE';return;}this.hit=new pc.Vec3(p.x,p.y,p.z);}if(!this.hit){this.message.textContent='APUNTA A UNA SUPERFICIE HORIZONTAL';return;}this.placed=true;this.root.setPosition(this.hit);this.reticle.enabled=false;this.revealPlane.enabled=true;this.action.textContent='CAMBIAR MATERIAL';this.sliders.hidden=false;this.finish.hidden=false;this.reveal();if(this.backend!=='xr8'&&this.app.xr.anchors?.available && this.hitResult){try{this.app.xr.anchors.create(this.hitResult,(err,anchor)=>{if(!err&&anchor)this.anchor=anchor;});}catch{}}}
 reveal(){if(!this.placed)return;const idx=this.materialIndex;if(this.lastIndex!==undefined){this.oldMat.diffuseMap=this.textures[this.lastIndex];this.oldMat.update();this.basePlane.enabled=true;}else this.basePlane.enabled=false;this.newMat.diffuseMap=this.textures[idx];this.newMat.update();this.revealPlane.enabled=true;this.revealing=true;this.radius=0;this.timer=0;this.paintMask(0);this.message.textContent='REVELANDO MATERIAL...';}
 update(dt){if(!this.active)return;if(this.anchor&&this.placed){try{this.root.setPosition(this.anchor.getPosition());}catch{}}if(!this.revealing)return;this.timer=Math.min(1.35,this.timer+dt);this.radius=easing(this.timer/1.25)*(Math.hypot(this.width,this.depth)*.67+.3);this.paintMask(this.radius);if(this.timer>=1.25){this.revealing=false;this.lastIndex=this.materialIndex;this.oldMat.diffuseMap=this.textures[this.materialIndex];this.oldMat.update();this.basePlane.enabled=true;this.revealPlane.enabled=false;this.message.textContent='PRUEBA OTRO ACABADO O TERMINA LA EXPERIENCIA';}}
 paintMask(radius){const w=128,h=128,im=this.maskCtx.createImageData(w,h),d=im.data;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const px=(x/127-.5)*this.width,pz=(y/127-.5)*this.depth,t=Math.hypot(px,pz),a=Math.max(0,Math.min(1,(radius+.08-t)/.16));const v=Math.round(a*255),i=(y*w+x)*4;d[i]=d[i+1]=d[i+2]=v;d[i+3]=255;}this.maskCtx.putImageData(im,0,0);this.maskTex.setSource(this.mask);}
 stop(){this.pendingXR8Fallback=false;if(this.backend==='xr8'){this.xr8Tracking?.stop();return;}if(this.app.xr.active)this.app.xr.end();else this.end();}
 end(){const fallback=this.pendingXR8Fallback&&this.xr8Available;this.pendingXR8Fallback=false;this.active=false;this.backend=null;this.placed=false;this.canvas.style.display='none';this.overlay.style.display='none';this.reticle.enabled=false;this.revealPlane.enabled=false;this.basePlane.enabled=false;this.hitSource?.remove?.();this.hitSource=null;this.anchor?.destroy?.();this.anchor=null;this.lastIndex=undefined;if(fallback){this.active=true;this.backend='xr8';this.canvas.style.display='block';this.overlay.style.display='block';void this.startXR8();}}
}
