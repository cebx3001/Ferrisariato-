// Real PlayCanvas GLB viewer + native WebXR hit testing. No simulated AR tracking.
import * as pc from 'https://cdn.jsdelivr.net/npm/playcanvas@2.22.6/build/playcanvas.mjs';
import {XR8Tracking,loadXR8} from './xr8-provider.js';
import {preferredTracking} from '../../shared/tracking-policy.js';
// The official XR8.PlayCanvas adapter expects the global pc symbol.
globalThis.pc = pc;
import {PRODUCTS} from './products.js';
const clamp=(n,min,max)=>Math.min(max,Math.max(min,n));
export class FerrisARViewer {
 constructor(canvas,{onStatus=()=>{},onTracking=()=>{},onXRStop=()=>{}}={}){
  this.canvas=canvas;this.onStatus=onStatus;this.onTracking=onTracking;this.onXRStop=onXRStop;
  this.app=new pc.Application(canvas,{graphicsDeviceOptions:{alpha:true,antialias:true,depth:true,preserveDrawingBuffer:true}});
  this.app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);this.app.setCanvasResolution(pc.RESOLUTION_AUTO);
  this.app.scene.ambientLight=new pc.Color(.70,.75,.80);
  this.camera=new pc.Entity('CAMERA');this.camera.addComponent('camera',{clearColor:new pc.Color(0,0,0,0),nearClip:.015,farClip:120,fov:60});this.app.root.addChild(this.camera);
  this.light=new pc.Entity('DIRECTIONAL-SOFTBOX');this.light.addComponent('light',{type:'directional',intensity:1.8,castShadows:false,color:new pc.Color(1,.94,.82)});this.light.setEulerAngles(40,30,0);this.app.root.addChild(this.light);
  this.productRoot=new pc.Entity('PLACEMENT-ROOT');this.app.root.addChild(this.productRoot);
  this.previewShadowMat=new pc.StandardMaterial();this.previewShadowMat.diffuse=new pc.Color(.025,.22,.33);this.previewShadowMat.opacity=.10;this.previewShadowMat.blendType=pc.BLEND_NORMAL;this.previewShadowMat.depthWrite=false;this.previewShadowMat.update();
  const sh=new pc.Entity('PREVIEW-FOOTPRINT');sh.addComponent('render',{type:'plane',material:this.previewShadowMat});sh.setLocalScale(2.5,1,2.5);sh.setLocalPosition(0,.001,0);this.productRoot.addChild(sh);this.shadow=sh;
  const markerMat=new pc.StandardMaterial();markerMat.emissive=new pc.Color(1,.85,0);markerMat.useLighting=false;markerMat.update();
  this.marker=new pc.Entity('XR-HIT-RETICLE');this.app.root.addChild(this.marker);
  for (const [x,z,w,d] of [[0,0,.18,.008],[0,0,.008,.18]]){const e=new pc.Entity('CROSS');e.addComponent('render',{type:'box',material:markerMat});e.setLocalPosition(x,.015,z);e.setLocalScale(w,.004,d);this.marker.addChild(e);}this.marker.enabled=false;
  this.session=false;this.xrBackend=null;this.xr8Tracking=null;this.xrReady=false;this.hit=null;this.hitResult=null;this.lastHitAt=0;this.hitSource=null;this.anchor=null;this.hasPlaced=true;this.moving=false;
  this.active=null;this.item=null;this.rootModel=null;this.assetCache=new Map();this.selectedToken=0;this.yaw=0;this.scale=1;this.orbitYaw=22;this.orbitPitch=21;this.distance=5.6;this.drag=false;this.lastPointer=null;this.pointers=new Map();
  this._cameraLook();this.app.on('update',()=>this._update());this.app.start();
  this.app.xr.on('end',()=>this._xrEnded());this.app.xr.on('error',e=>this.onStatus('Error WebXR: '+(e?.message||e),true));
  this._wirePointer();this.nativeSupported=false;this.pendingXR8Fallback=false;this.resize();window.addEventListener('resize',()=>this.resize());
 }
 _cameraLook(){if(this.session)return;let yaw=this.orbitYaw*Math.PI/180,p=this.orbitPitch*Math.PI/180;let px=this.distance*Math.sin(yaw)*Math.cos(p),py=this.distance*Math.sin(p)+1.45,pz=this.distance*Math.cos(yaw)*Math.cos(p);this.camera.setPosition(px,py,pz);this.camera.lookAt(0,this.item?.dimensions?clamp(this.item.dimensions[1]*.48,.28,1.5):1.14,0);}
 resize(){this.app.resizeCanvas(this.canvas.clientWidth||window.innerWidth,this.canvas.clientHeight||window.innerHeight);}
 get xr8Available(){return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || navigator.maxTouchPoints>1;}
 get isIOS(){return /iPhone|iPad|iPod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);}
 get arAvailable(){return !!(this.app.xr.supported && this.app.xr.isAvailable(pc.XRTYPE_AR));}
 get preferredTracking(){return preferredTracking({mobile:this.xr8Available,ios:this.isIOS,nativeSupported:this.nativeSupported,xr8Available:this.xr8Available,override:new URLSearchParams(location.search).get('tracking')});}
 async checkAR(){
  try{this.nativeSupported=Boolean(!this.isIOS&&navigator.xr&&await navigator.xr.isSessionSupported('immersive-ar')&&this.arAvailable);}catch{this.nativeSupported=false;}
  if(this.xr8Available&&!this.nativeSupported)loadXR8().catch(e=>console.warn('[8th Wall fallback preload]',e.message));
  return this.nativeSupported;
 }
 _loadGLB(url){if(this.assetCache.has(url))return this.assetCache.get(url);const promise=new Promise((resolve,reject)=>{this.app.assets.loadFromUrl(url,'container',(error,asset)=>{if(error){reject(new Error(typeof error==='string'?error:'No se pudo cargar '+url));return;}resolve(asset);});});this.assetCache.set(url,promise);promise.catch(()=>this.assetCache.delete(url));return promise;}
 async _instantiate(url){const asset=await this._loadGLB(url);return asset.resource.instantiateRenderEntity({castShadows:false});}
 _clear(){if(this.rootModel){this.rootModel.destroy();this.rootModel=null;}this.marker.enabled=false;}
 async select(product){this.item=product;const token=++this.selectedToken;this._clear();this.scale=1;this.yaw=0;this.onStatus('Cargando modelo 3D...');try{
  if(!this.session){this.distance=clamp(Math.max(...product.dimensions)*1.65,3.5,18);this.orbitYaw=24;this.orbitPitch=19;this._cameraLook();}
  const url=product.local;const root=await this._instantiate(url);if(token!==this.selectedToken){root.destroy();return;}this.rootModel=new pc.Entity('PRODUCT-'+product.id);this.rootModel.addChild(root);this.productRoot.addChild(this.rootModel);this._setTransform();this.shadow.setLocalScale(product.dimensions[0],1,product.dimensions[2]);this.hasPlaced=!this.session;this.productRoot.enabled=!this.session;if(this.session&&this.xrBackend==='xr8')this.xr8Tracking?.scanAgain();this.onStatus('Modelo listo. Arrastra para girar la vista.');
  // Upgrade to sourced CC0 model when accessible, but retain local fallback if network/CDN fails.
  if(product.remote && !this.session) this._upgrade(product,token);
 }catch(e){this.onStatus('No se pudo cargar el GLB local: '+e.message,true);}
 }
 async _upgrade(product,token){try{const model=await this._instantiate(product.remote);if(token!==this.selectedToken||this.session){model.destroy();return;}if(product.extra){const umbrella=await this._instantiate(product.extra);model.addChild(umbrella);}if(token!==this.selectedToken){model.destroy();return;}this.rootModel.destroy();this.rootModel=new pc.Entity('PRODUCT-'+product.id+'-CC0');this.rootModel.addChild(model);this.productRoot.addChild(this.rootModel);this._setTransform();this.onStatus('Modelo CC0 cargado. Puedes verlo a escala real.');}catch(e){console.info('Conservando GLB local:',e.message);}}
 _setTransform(){if(!this.rootModel)return;this.rootModel.setLocalEulerAngles(0,this.yaw,0);this.rootModel.setLocalScale(this.scale,this.scale,this.scale);}
 setRotation(n){this.yaw=n;this._setTransform();}rotate(d){this.setRotation(((this.yaw+d+180)%360+360)%360-180);return this.yaw;}
 setScale(n){this.scale=clamp(n,.5,1.5);this._setTransform();}
 clear(){this._clear();this.item=null;this.selectedToken++;this.productRoot.enabled=false;this.hasPlaced=false;if(this.session&&this.xrBackend==='xr8')this.xr8Tracking?.scanAgain();}
 resetPlacement(){if(!this.item)return;this.moving=true;this.hasPlaced=false;if(this.session){this.marker.enabled=false;this._destroyAnchor();if(this.xrBackend==='xr8')this.xr8Tracking?.scanAgain();this.onStatus('Apunta al suelo y pulsa COLOCAR.');}else{this.productRoot.setPosition(0,0,0);this.onStatus('Arrastra la imagen para cambiar el ángulo o utiliza los controles.');}}
 place(){if(!this.item)return false;if(!this.session){this.hasPlaced=true;this.onStatus('Producto colocado en el espacio demostrativo.');return true;}if(!this.hit||performance.now()-this.lastHitAt>1400){this.onStatus('Todavía no se ha detectado el suelo. Mueve el teléfono lentamente.',true);return false;}if(this.xrBackend==='xr8'){const p=this.xr8Tracking?.lock();if(!p){this.onStatus('Mantén el teléfono apuntando al piso hasta detectar una superficie.',true);return false;}this.hit=new pc.Vec3(p.x,p.y,p.z);}
 this.productRoot.setPosition(this.hit);this.productRoot.enabled=true;this.hasPlaced=true;this.moving=false;this.marker.enabled=false;this._destroyAnchor();if(this.xrBackend!=='xr8'&&this.app.xr.anchors?.available&&this.hitResult){try{this.app.xr.anchors.create(this.hitResult,(err,anchor)=>{if(!err&&anchor&&this.session)this.anchor=anchor;});}catch(e){console.warn('Anchor no disponible',e);}}this.onStatus('Producto colocado. Puedes girarlo o cambiar de producto.');return true;}
 _destroyAnchor(){if(this.anchor){try{this.anchor.destroy();}catch{}this.anchor=null;}}
 _wirePointer(){this.canvas.addEventListener('pointerdown',e=>{if(this.session)return;this.drag=true;this.lastPointer={x:e.clientX,y:e.clientY};this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});this.canvas.setPointerCapture?.(e.pointerId);});this.canvas.addEventListener('pointermove',e=>{if(this.session||!this.drag||!this.lastPointer)return;const dx=e.clientX-this.lastPointer.x,dy=e.clientY-this.lastPointer.y;this.lastPointer={x:e.clientX,y:e.clientY};this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(this.moving){const pos=this.productRoot.getPosition();this.productRoot.setPosition(clamp(pos.x+dx*.006,-2.5,2.5),0,clamp(pos.z+dy*.006,-2.5,2.5));}else{if(this.pointers.size>1)return;if(window.matchMedia('(max-width:760px)').matches){this.setRotation(this.yaw+dx*.55);this.orbitPitch=clamp(this.orbitPitch-dy*.38,-88,88);}else{this.orbitYaw+=dx*.32;this.orbitPitch=clamp(this.orbitPitch-dy*.38,-88,88);}this._cameraLook();}});for(const name of ['pointerup','pointercancel','lostpointercapture'])this.canvas.addEventListener(name,e=>{this.pointers.delete(e.pointerId);this.drag=false;this.lastPointer=null;});this.canvas.addEventListener('wheel',e=>{if(this.session)return;e.preventDefault();this.distance=clamp(this.distance+Math.sign(e.deltaY)*.30,.6,28);this._cameraLook();},{passive:false});}
 async startXR8(){
  if(this.session)return;
  if(!this.xr8Available){this.onStatus('8th Wall necesita un teléfono compatible con cámara y sensores.',true);return;}
  this.session=true;this.xrBackend='xr8';this.hasPlaced=false;this.moving=false;this.marker.enabled=false;this._destroyAnchor();this.productRoot.enabled=false;
  this.onTracking(true);this.onStatus('Iniciando cámara y seguimiento 8th Wall…');
  if(!this.xr8Tracking){
   this.xr8Tracking=new XR8Tracking({app:this.app,camera:this.camera,canvas:this.canvas,
    onStatus:(m,error)=>this.onStatus(m,error),
    onHit:(p,stable)=>{if(!this.session||this.hasPlaced||this.xrBackend!=='xr8')return;this.hit=p?new pc.Vec3(p.x,p.y,p.z):null;this.lastHitAt=p?performance.now():0;this.marker.enabled=!!(p&&stable);if(p)this.marker.setPosition(p.x,p.y+.015,p.z);},
    onEnd:()=>{if(this.xrBackend==='xr8')this._xrEnded();}
   });
  }
  try{await this.xr8Tracking.start();}catch(e){this._xrEnded();this.onStatus('8th Wall: '+(e?.message||e),true);}
 }
 // IMPORTANT: startXR() is called directly inside a user click. Nothing awaits before starting session.
 startXR(){if(this.session)return;this.xrBackend='native';this.app.xr.domOverlay.root=document.getElementById('shell');this.hasPlaced=false;this.moving=false;this._destroyAnchor();this.marker.enabled=false;this.productRoot.enabled=false;
  this.app.xr.start(this.camera.camera,pc.XRTYPE_AR,pc.XRSPACE_LOCALFLOOR,{planeDetection:true,anchors:true,callback:(err)=>{if(err){this.pendingXR8Fallback=this.xr8Available;this.onStatus('ARCore/WebXR no pudo iniciar: '+(err.message||err),true);this._xrEnded();}}});
  this.app.xr.once('start',()=>{this.session=true;this.onTracking(true);this.onStatus('Busca una superficie horizontal moviendo lentamente la cámara.');if(!this.app.xr.hitTest.supported){this.onStatus('WebXR no ofrece hit testing. Cambiando a 8th Wall.',true);this.pendingXR8Fallback=this.xr8Available;this.app.xr.end();return;}
   this.app.xr.hitTest.start({spaceType:pc.XRSPACE_VIEWER,callback:(err,source)=>{if(err){this.onStatus('No se pudo detectar el suelo: '+(err.message||err),true);return;}this.hitSource=source;source.on('result',(pos,rotation,input,result)=>{this.hit=pos.clone();this.hitResult=result;this.lastHitAt=performance.now();if(!this.hasPlaced){this.marker.setPosition(pos.x,pos.y+.008,pos.z);this.marker.enabled=true;this.onStatus('Superficie detectada. Pulsa COLOCAR EN TU ESPACIO.');}});}});
  });
 }
 endXR(){this.pendingXR8Fallback=false;if(this.xrBackend==='xr8'){this.xr8Tracking?.stop();return;}if(this.app.xr.active)this.app.xr.end();else this._xrEnded();}
 _xrEnded(){const fallback=this.pendingXR8Fallback&&this.xr8Available;this.pendingXR8Fallback=false;this.session=false;this.xrBackend=null;this._destroyAnchor();try{this.hitSource?.remove();}catch{}this.hitSource=null;this.hit=null;this.marker.enabled=false;this.productRoot.setPosition(0,0,0);this.productRoot.enabled=true;this.hasPlaced=true;this._cameraLook();this.onTracking(false);this.onStatus('Vista 3D de demostración.');if(fallback){this.onStatus('ARCore no disponible. Activando seguimiento 8th Wall.');void this.startXR8();}}
 _update(){if(!this.session)return;if(this.anchor&&this.hasPlaced){try{const pos=this.anchor.getPosition();this.productRoot.setPosition(pos);}catch{}}}
}
