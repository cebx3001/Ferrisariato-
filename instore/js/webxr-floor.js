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
// Per-fragment ARCore/WebXR depth occlusion. No object-classification model required.
const floorVertexGLSL="\nattribute vec3 aPosition;\nattribute vec2 aUv0;\nuniform mat4 matrix_model;\nuniform mat4 matrix_viewProjection;\nuniform mat4 matrix_view;\nvarying highp vec2 vUv;\nvarying highp float vCameraDepth;\nvoid main(void){\n vec4 world=matrix_model*vec4(aPosition,1.0);\n vUv=aUv0;\n vCameraDepth=-(matrix_view*world).z;\n gl_Position=matrix_viewProjection*world;\n}";
const floorFragmentGLSL="\nprecision highp float;\nvarying highp vec2 vUv;\nvarying highp float vCameraDepth;\nuniform vec4 screen_size;\nuniform sampler2D uFloorMap;\nuniform sampler2D uRevealMask;\nuniform sampler2D depthMap;\nuniform mat4 matrix_depth_uv;\nuniform vec2 uFloorTiling;\nuniform vec3 uLightTint;\nuniform float depth_to_meters;\nuniform float uDepthFloat;\nuniform float uDepthRequired;\nuniform float uDepthReady;\nuniform float uReveal;\nvoid main(void){\n if(uDepthRequired>0.5){\n  if(uDepthReady<0.5)discard;\n  vec2 scr=gl_FragCoord.xy*screen_size.zw;\n  vec2 uv=(matrix_depth_uv*vec4(scr.x,1.0-scr.y,0.0,1.0)).xy;\n  if(uv.x<=0.0||uv.x>=1.0||uv.y<=0.0||uv.y>=1.0)discard;\n  vec4 d=texture2D(depthMap,uv);\n  float rawDepth=uDepthFloat>0.5?d.r:dot(d.ra,vec2(255.0,65280.0));\n  float realDepth=rawDepth*depth_to_meters;\n  if(realDepth<0.09||realDepth>15.0||vCameraDepth<=0.0)discard;\n  // Keep nearer tables, plants, chairs and shelves in front of the virtual floor.\n  float tolerance=0.035+vCameraDepth*0.016;\n  if(realDepth+tolerance<vCameraDepth)discard;\n }\n vec4 col=texture2D(uFloorMap,vUv*uFloorTiling);\n float wave=uReveal>0.5?texture2D(uRevealMask,vUv).r:1.0;\n if(wave<0.008)discard;\n gl_FragColor=vec4(col.rgb*uLightTint,col.a*wave);\n}";

function makeOccludedFloorMaterial(reveal){
 const m=new pc.ShaderMaterial({
  uniqueName:reveal?'FerrisariatoDepthReveal2026':'FerrisariatoDepthBase2026',
  attributes:{aPosition:pc.SEMANTIC_POSITION,aUv0:pc.SEMANTIC_TEXCOORD0},
  vertexGLSL:floorVertexGLSL,fragmentGLSL:floorFragmentGLSL
 });
 m.cull=pc.CULLFACE_NONE;
 m.depthWrite=!reveal;
 m.blendType=reveal?pc.BLEND_NORMAL:pc.BLEND_NONE;
 m.setParameter('uDepthRequired',0);
 m.setParameter('uDepthReady',0);
 m.setParameter('uDepthFloat',0);
 m.setParameter('depth_to_meters',1);
 m.setParameter('matrix_depth_uv',new pc.Mat4().data);
 m.setParameter('uReveal',reveal?1:0);
 m.setParameter('uLightTint',new Float32Array([1,1,1]));
 m.setParameter('uFloorTiling',new Float32Array([2,2]));
 m.update();
 return m;
}


const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
function loadImage(url){return new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('Falta textura '+url));i.src=url;});}
export class FloorWebXR {
 constructor(){this.isReady=false;this.supported=false;this.active=false;this.placed=false;this.hit=null;this.hitResult=null;this.hitSource=null;this.anchor=null;this.materialIndex=0;this.width=2.4;this.depth=3;this.radius=0;this.timer=0;this.revealing=false;this.canvas=byId('xr-canvas');this.overlay=byId('xr-overlay');this.status=byId('xr-status');this.action=byId('xr-action');this.message=byId('xr-step-message');this.finish=byId('xr-finish');this.sliders=byId('xr-sliders');this.crosshair=byId('xr-crosshair');this.backend=null;this.xr8Tracking=null;this.xr8ExposureReference=null;this.lightEstimateAvailable=false;this.depthReady=false;this.depthStatusFrames=0;this.depthWarningShown=false;this.ready=this.init();}
 async init(){
  const app=new pc.Application(this.canvas,{graphicsDeviceOptions:{alpha:true,antialias:true,depth:true}});this.app=app;app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);app.setCanvasResolution(pc.RESOLUTION_AUTO);app.scene.ambientLight=new pc.Color(.60,.62,.64);
  this.arLight=new pc.Entity('FLOOR-ENVIRONMENT-LIGHT');
  this.arLight.addComponent('light',{type:'directional',intensity:.86,color:new pc.Color(1,.97,.93),castShadows:false});
  this.arLight.setEulerAngles(40,30,0);app.root.addChild(this.arLight);
  this.camera=new pc.Entity('AR-CAMERA');this.camera.addComponent('camera',{clearColor:new pc.Color(0,0,0,0),nearClip:.01,farClip:100});app.root.addChild(this.camera);
  this.root=new pc.Entity('AR-FLOOR-ANCHOR');app.root.addChild(this.root);
  const makeMat=()=>{let m=new pc.StandardMaterial();m.diffuse.set(1,1,1);
   // Unlit textures cannot respond to Environmental HDR or XR8 exposure.
   m.useLighting=true;m.metalness=0;m.gloss=15;m.cull=pc.CULLFACE_NONE;m.update();return m;};
  this.oldMat=makeOccludedFloorMaterial(false);this.newMat=makeOccludedFloorMaterial(true);
  const plane=(name,mat,y)=>{let e=new pc.Entity(name);e.addComponent('render',{type:'plane',material:mat});e.setLocalPosition(0,y,0);e.setLocalScale(this.width,1,this.depth);this.root.addChild(e);e.enabled=false;return e;};
  this.basePlane=plane('FLOOR-BASE',this.oldMat,.006);this.revealPlane=plane('FLOOR-REVEAL',this.newMat,.012);
  const markMat=makeMat();markMat.emissive.set(1,.86,0);markMat.useLighting=false;markMat.update();this.reticle=new pc.Entity('RETICLE');app.root.addChild(this.reticle);
  for(const [w,d] of [[.15,.006],[.006,.15]]){let e=new pc.Entity('RETICLE-ARM');e.addComponent('render',{type:'box',material:markMat});e.setLocalPosition(0,.01,0);e.setLocalScale(w,.007,d);this.reticle.addChild(e);}this.reticle.enabled=false;
  this.mask=document.createElement('canvas');this.mask.width=this.mask.height=128;this.maskCtx=this.mask.getContext('2d');
  this.maskTex=new pc.Texture(app.graphicsDevice,{width:128,height:128,format:pc.PIXELFORMAT_RGBA8,mipmaps:false,minFilter:pc.FILTER_LINEAR,magFilter:pc.FILTER_LINEAR,addressU:pc.ADDRESS_CLAMP_TO_EDGE,addressV:pc.ADDRESS_CLAMP_TO_EDGE});this.oldMat.setParameter('uRevealMask',this.maskTex);
  this.newMat.setParameter('uRevealMask',this.maskTex);
  // Bind a harmless texture until WebXR provides its real depth buffer.
  this.emptyDepth=new pc.Texture(app.graphicsDevice,{width:1,height:1,format:pc.PIXELFORMAT_RGBA8,mipmaps:false});
  const emptyCanvas=document.createElement('canvas');emptyCanvas.width=emptyCanvas.height=1;
  emptyCanvas.getContext('2d').clearRect(0,0,1,1);this.emptyDepth.setSource(emptyCanvas);
  for(const m of [this.oldMat,this.newMat])m.setParameter('depthMap',this.emptyDepth);
  this.textures=await Promise.all(MATERIALS.map(async m=>{let img=await loadImage(m.url);let tex=new pc.Texture(app.graphicsDevice,{width:img.naturalWidth,height:img.naturalHeight,format:pc.PIXELFORMAT_RGBA8,mipmaps:true,minFilter:pc.FILTER_LINEAR_MIPMAP_LINEAR,magFilter:pc.FILTER_LINEAR,addressU:pc.ADDRESS_REPEAT,addressV:pc.ADDRESS_REPEAT});tex.setSource(img);return tex;}));
  this.oldMat.setParameter('uFloorMap',this.textures[0]);this.newMat.setParameter('uFloorMap',this.textures[0]);this.sizeMaterials();this.paintMask(0);
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

 _enterLightMode(){
  this.xr8ExposureReference=null;this.lightEstimateAvailable=false;
  this.arLight.light.intensity=.86;
  this.arLight.light.color=new pc.Color(1,.97,.93);
  this.arLight.setEulerAngles(40,30,0);
  this.app.scene.ambientLight=new pc.Color(.60,.62,.64);
 }
 _applyNativeLight(){
  // Optional PlayCanvas/WebXR Environmental Light Estimation data.
  const est=this.app.xr.lightEstimation;
  if(!est?.available)return;
  if(Number.isFinite(est.intensity)&&est.intensity>0)
    this.arLight.light.intensity+=(clamp(est.intensity,.16,3.2)-this.arLight.light.intensity)*.08;
  const color=est.color;
  if(color&&[color.r,color.g,color.b].every(Number.isFinite)){
   const c=this.arLight.light.color;
   this.arLight.light.color=new pc.Color(c.r+(color.r-c.r)*.08,
     c.g+(color.g-c.g)*.08,c.b+(color.b-c.b)*.08);
  }
  const q=est.rotation();if(q)this.arLight.setRotation(q);
  const sh=est.sphericalHarmonics;
  if(sh?.length>=3&&[sh[0],sh[1],sh[2]].every(Number.isFinite)){
    const c=this.app.scene.ambientLight,v=n=>clamp(Math.max(0,n)*.2821,.12,.86);
    this.app.scene.ambientLight=new pc.Color(c.r+(v(sh[0])-c.r)*.07,
      c.g+(v(sh[1])-c.g)*.07,c.b+(v(sh[2])-c.b)*.07);
  }
  this.lightEstimateAvailable=true;
 }
 _applyXR8Light(lighting){
  // XR8 currently exposes exposure, not true ARCore HDR color/direction.
  const value=lighting?.exposure;
  if(!Number.isFinite(value)||value<=0)return;
  if(this.xr8ExposureReference===null)this.xr8ExposureReference=value;
  const ratio=clamp(Math.pow(value/this.xr8ExposureReference,.35),.65,1.55);
  const target=clamp(.85*ratio,.55,1.35);
  this.arLight.light.intensity+=(target-this.arLight.light.intensity)*.07;
  const c=this.app.scene.ambientLight,amb=clamp(.60*ratio,.38,.85);
  this.app.scene.ambientLight=new pc.Color(c.r+(amb-c.r)*.06,
   c.g+(amb-c.g)*.06,c.b+(amb-c.b)*.06);
  this.lightEstimateAvailable=true;
 }


 _setDepthRequired(required){
  for(const m of [this.oldMat,this.newMat])m.setParameter('uDepthRequired',required?1:0);
 }
 _updateDepthOcclusion(){
  if(this.backend!=='native'||!this.app.xr.active){this.depthReady=false;return;}
  const views=this.app.xr.views;
  const view=views?.get?.(pc.XREYE_NONE)||views?.list?.[0];
  const depthTexture=view?.textureDepth;
  const pixelFormat=views?.depthPixelFormat;
  // WebGL phone path: packed LA8 or float32.
  const understood=pixelFormat===pc.PIXELFORMAT_LA8||pixelFormat===pc.PIXELFORMAT_R32F;
  const ready=!!(views?.availableDepth&&depthTexture&&view?.depthUvMatrix&&understood&&Number.isFinite(view.depthValueToMeters)&&view.depthValueToMeters>0);
  this.depthReady=ready;
  // Use ARCore depth for occlusion when available; always show the floor otherwise.
  this._setDepthRequired(ready);
  for(const mat of [this.oldMat,this.newMat]){
   mat.setParameter('uDepthReady',ready?1:0);
   if(ready){
    mat.setParameter('depthMap',depthTexture);
    mat.setParameter('matrix_depth_uv',view.depthUvMatrix.data);
    mat.setParameter('depth_to_meters',view.depthValueToMeters);
    mat.setParameter('uDepthFloat',pixelFormat===pc.PIXELFORMAT_R32F?1:0);
   }
  }
  if(!this.placed&&++this.depthStatusFrames%90===0){
   this.status.textContent=ready?'PROFUNDIDAD ARCORE ACTIVA · UBICA EL PISO':'SIN MAPA DE PROFUNDIDAD · PUEDES COLOCAR EL PISO';
   this.message.textContent=ready?'OBJETOS REALES EXCLUIDOS · LISTO PARA COLOCAR':'PUEDES COLOCAR EL PISO · SIN OCLUSIÓN DE OBJETOS';
  }
  if(this.placed&&!ready){
   if(!this.depthWarningShown){
    this.depthWarningShown=true;
    this.message.textContent='SIN PROFUNDIDAD · EL PISO CONTINÚA VISIBLE';
   }
  }else if(ready&&this.depthWarningShown){
   this.depthWarningShown=false;
   this.message.textContent='PROFUNDIDAD RESTABLECIDA · OCLUSIÓN ACTIVA';
  }
 }
 _updateFloorLighting(){
  // Depth shader cannot receive StandardMaterial lighting automatically.
  // Reuse the existing smoothly estimated ARCore/8th Wall illumination.
  const dir=this.arLight.light,amb=this.app.scene.ambientLight;
  const strength=clamp(.56+dir.intensity*.30,.62,1.27);
  const tint=new Float32Array([
   clamp((amb.r*.42+dir.color.r*.58)*strength,.44,1.25),
   clamp((amb.g*.42+dir.color.g*.58)*strength,.44,1.25),
   clamp((amb.b*.42+dir.color.b*.58)*strength,.44,1.25)
  ]);
  for(const mat of [this.oldMat,this.newMat])mat.setParameter('uLightTint',tint);
 }

 sizeMaterials(){const tiling=new Float32Array([this.width/1.2,this.depth/1.2]);for(const m of [this.oldMat,this.newMat])m.setParameter('uFloorTiling',tiling);}
 start(){if(!this.isReady||!this.supported)return;this.backend=preferredTracking({mobile:this.xr8Available,ios:this.isIOS,nativeSupported:this.nativeSupported,xr8Available:this.xr8Available,override:new URLSearchParams(location.search).get('tracking')});this.active=true;this.placed=false;this.hit=null;this.depthReady=false;this.depthStatusFrames=0;this.depthWarningShown=false;this._enterLightMode();this.canvas.style.display='block';this.overlay.style.display='block';this.basePlane.enabled=false;this.revealPlane.enabled=false;this.reticle.enabled=false;this.crosshair.classList.remove('detected');this.finish.hidden=true;this.sliders.hidden=true;this.action.textContent='COLOCAR SUELO';this.message.textContent='BUSCANDO SUPERFICIE...';this.app.resizeCanvas(window.innerWidth,window.innerHeight);this._setDepthRequired(false);if(this.backend==='xr8'){if(!this.isIOS){this.status.textContent='ANDROID 8TH WALL SIN PROFUNDIDAD';this.message.textContent='PUEDES COLOCAR EL PISO SIN OCLUSIÓN';}void this.startXR8();return;}this.app.xr.domOverlay.root=this.overlay;
 // Must be invoked directly within a click; no await before starting WebXR.
 this.app.xr.start(this.camera.camera,pc.XRTYPE_AR,pc.XRSPACE_LOCALFLOOR,{planeDetection:true,anchors:true,optionalFeatures:['light-estimation'],depthSensing:{usagePreference:pc.XRDEPTHSENSINGUSAGE_CPU,dataFormatPreference:pc.XRDEPTHSENSINGFORMAT_L8A8},callback:err=>{if(err){this.status.textContent='ARCore/WebXR no inició: '+(err?.message||err);if(this.xr8Available){this.backend='xr8';void this.startXR8();}else this.end();}}});
 this.app.xr.once('start',()=>{try{if(this.app.xr.lightEstimation?.supported)this.app.xr.lightEstimation.start();}catch(e){console.warn('Light estimation unavailable',e);}if(!this.app.xr.hitTest.supported){this.status.textContent='WEBXR SIN DETECCIÓN DE SUELO · ACTIVANDO 8TH WALL';this.pendingXR8Fallback=this.xr8Available;this.app.xr.end();return;}this.status.textContent='MUEVE EL TELÉFONO · ANALIZANDO PISO Y PROFUNDIDAD';this.app.xr.hitTest.start({spaceType:pc.XRSPACE_VIEWER,callback:(err,source)=>{if(err){this.status.textContent='NO SE PUDO DETECTAR EL PISO';return;}this.hitSource=source;source.on('result',(pos,rot,input,result)=>{this.hit=pos.clone();this.hitResult=result;if(!this.placed){this.reticle.setPosition(pos.x,pos.y+.02,pos.z);this.reticle.enabled=true;this.crosshair.classList.add('detected');this.status.textContent=this.depthReady?'SUELO Y PROFUNDIDAD DETECTADOS · COLOCA EL PISO':'SUELO DETECTADO · ESPERANDO PROFUNDIDAD ARCORE';this.message.textContent=this.depthReady?'OCLUSIÓN ACTIVA: MUEBLES Y PLANTAS PROTEGIDOS':'ESPERANDO PROFUNDIDAD DE LA HABITACIÓN';}});}});});
 }
 async startXR8(){
  this.depthReady=false;this._setDepthRequired(false);
  if(!this.xr8Tracking){this.xr8Tracking=new XR8Tracking({app:this.app,camera:this.camera,canvas:this.canvas,
    onStatus:(msg,isError)=>{this.status.textContent=msg;if(isError)this.message.textContent='ERROR DE SEGUIMIENTO';},
    onLighting:(lighting)=>this._applyXR8Light(lighting),
    onHit:(p,stable)=>{if(this.backend!=='xr8'||this.placed)return;this.hit=p?new pc.Vec3(p.x,p.y,p.z):null;this.reticle.enabled=!!(p&&stable);if(p){this.reticle.setPosition(p.x,p.y+.018,p.z);this.status.textContent=stable?'SUELO DETECTADO · PULSA COLOCAR':'ANALIZANDO SUPERFICIE…';this.message.textContent=stable?'SUPERFICIE DISPONIBLE':'BUSCANDO SUPERFICIE';}this.crosshair.classList.toggle('detected',!!(p&&stable));},
    onEnd:()=>this.end()
   });}
  try{await this.xr8Tracking.start();}catch(e){console.error(e);this.status.textContent='8TH WALL: '+(e?.message||e);this.end();const label=byId('xr-status');if(label)label.textContent='No se pudo iniciar AR. Abre la simulación para continuar.';}
 }
 place(){if(this.backend==='xr8'){const p=this.xr8Tracking?.lock();if(!p){this.message.textContent='BUSCA UNA SUPERFICIE ESTABLE';return;}this.hit=new pc.Vec3(p.x,p.y,p.z);}if(!this.hit){this.message.textContent='APUNTA A UNA SUPERFICIE HORIZONTAL';return;}this.placed=true;this.root.setPosition(this.hit);this.reticle.enabled=false;this.revealPlane.enabled=true;this.action.textContent='CAMBIAR MATERIAL';this.sliders.hidden=false;this.finish.hidden=false;this.reveal();if(this.backend!=='xr8'&&this.app.xr.anchors?.available && this.hitResult){try{this.app.xr.anchors.create(this.hitResult,(err,anchor)=>{if(!err&&anchor)this.anchor=anchor;});}catch{}}}
 reveal(){if(!this.placed)return;const idx=this.materialIndex;if(this.lastIndex!==undefined){this.oldMat.setParameter('uFloorMap',this.textures[this.lastIndex]);this.basePlane.enabled=true;}else this.basePlane.enabled=false;this.newMat.setParameter('uFloorMap',this.textures[idx]);this.revealPlane.enabled=true;this.revealing=true;this.radius=0;this.timer=0;this.paintMask(0);this.message.textContent='REVELANDO MATERIAL...';}
 update(dt){if(!this.active)return;if(this.backend==='native'){this._applyNativeLight();this._updateDepthOcclusion();}this._updateFloorLighting();if(this.anchor&&this.placed){try{this.root.setPosition(this.anchor.getPosition());}catch{}}if(!this.revealing)return;this.timer=Math.min(1.35,this.timer+dt);this.radius=easing(this.timer/1.25)*(Math.hypot(this.width,this.depth)*.67+.3);this.paintMask(this.radius);if(this.timer>=1.25){this.revealing=false;this.lastIndex=this.materialIndex;this.oldMat.setParameter('uFloorMap',this.textures[this.materialIndex]);this.basePlane.enabled=true;this.revealPlane.enabled=false;this.message.textContent='PRUEBA OTRO ACABADO O TERMINA LA EXPERIENCIA';}}
 paintMask(radius){const w=128,h=128,im=this.maskCtx.createImageData(w,h),d=im.data;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const px=(x/127-.5)*this.width,pz=(y/127-.5)*this.depth,t=Math.hypot(px,pz),a=Math.max(0,Math.min(1,(radius+.08-t)/.16));const v=Math.round(a*255),i=(y*w+x)*4;d[i]=d[i+1]=d[i+2]=v;d[i+3]=255;}this.maskCtx.putImageData(im,0,0);this.maskTex.setSource(this.mask);}
 stop(){this.pendingXR8Fallback=false;if(this.backend==='xr8'){this.xr8Tracking?.stop();return;}if(this.app.xr.active)this.app.xr.end();else this.end();}
 end(){const fallback=this.pendingXR8Fallback&&this.xr8Available;this.pendingXR8Fallback=false;this.active=false;this.backend=null;this.placed=false;this.depthReady=false;this._setDepthRequired(false);this._enterLightMode();this.canvas.style.display='none';this.overlay.style.display='none';this.reticle.enabled=false;this.revealPlane.enabled=false;this.basePlane.enabled=false;this.hitSource?.remove?.();this.hitSource=null;this.anchor?.destroy?.();this.anchor=null;this.lastIndex=undefined;if(fallback){this.active=true;this.backend='xr8';this.canvas.style.display='block';this.overlay.style.display='block';void this.startXR8();}}
}
