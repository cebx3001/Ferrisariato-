// Real PlayCanvas GLB viewer + native WebXR hit testing. No simulated AR tracking.
import * as pc from 'https://cdn.jsdelivr.net/npm/playcanvas@2.23.2/build/playcanvas.mjs';
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
  this.session=false;this.xrReady=false;this.hit=null;this.hitResult=null;this.lastHitAt=0;this.hitSource=null;this.anchor=null;this.hasPlaced=true;this.moving=false;
  this.active=null;this.item=null;this.rootModel=null;this.assetCache=new Map();this.selectedToken=0;this.yaw=0;this.scale=1;this.orbitYaw=22;this.orbitPitch=21;this.distance=5.6;this.drag=false;this.lastPointer=null;this.pointers=new Map();
  this._cameraLook();this.app.on('update',()=>this._update());this.app.start();
  this.app.xr.on('end',()=>this._xrEnded());this.app.xr.on('error',e=>this.onStatus('Error WebXR: '+(e?.message||e),true));
  this._wirePointer();this.resize();window.addEventListener('resize',()=>this.resize());
 }
 _cameraLook(){if(this.session)return;let yaw=this.orbitYaw*Math.PI/180,p=this.orbitPitch*Math.PI/180;let px=this.distance*Math.sin(yaw)*Math.cos(p),py=this.distance*Math.sin(p)+1.45,pz=this.distance*Math.cos(yaw)*Math.cos(p);this.camera.setPosition(px,py,pz);this.camera.lookAt(0,1.14,0);}
 resize(){this.app.resizeCanvas(this.canvas.clientWidth||window.innerWidth,this.canvas.clientHeight||window.innerHeight);}
 get arAvailable(){return !!(this.app.xr.supported && this.app.xr.isAvailable(pc.XRTYPE_AR));}
 async checkAR(){try{return Boolean(navigator.xr && await navigator.xr.isSessionSupported('immersive-ar'));}catch{return false;}}
 _loadGLB(url){if(this.assetCache.has(url))return this.assetCache.get(url);const promise=new Promise((resolve,reject)=>{this.app.assets.loadFromUrl(url,'container',(error,asset)=>{if(error){reject(new Error(typeof error==='string'?error:'No se pudo cargar '+url));return;}resolve(asset);});});this.assetCache.set(url,promise);promise.catch(()=>this.assetCache.delete(url));return promise;}
 async _instantiate(url){const asset=await this._loadGLB(url);return asset.resource.instantiateRenderEntity({castShadows:false});}
 _clear(){if(this.rootModel){this.rootModel.destroy();this.rootModel=null;}this.marker.enabled=false;}
 async select(product){this.item=product;const token=++this.selectedToken;this._clear();this.scale=1;this.yaw=0;this.onStatus('Cargando modelo 3D...');try{
  const root=await this._instantiate(product.local);if(token!==this.selectedToken){root.destroy();return;}this.rootModel=new pc.Entity('PRODUCT-'+product.id);this.rootModel.addChild(root);this.productRoot.addChild(this.rootModel);this._setTransform();this.shadow.setLocalScale(product.dimensions[0],1,product.dimensions[2]);this.hasPlaced=!this.session;this.productRoot.enabled=!this.session;this.onStatus('Modelo listo. Arrastra para girar la vista.');
  // Upgrade to sourced CC0 model when accessible, but retain local fallback if network/CDN fails.
  if(product.remote && !this.session) this._upgrade(product,token);
 }catch(e){this.onStatus('No se pudo cargar el GLB local: '+e.message,true);}
 }
 async _upgrade(product,token){try{const model=await this._instantiate(product.remote);if(token!==this.selectedToken||this.session){model.destroy();return;}if(product.extra){const umbrella=await this._instantiate(product.extra);model.addChild(umbrella);}if(token!==this.selectedToken){model.destroy();return;}this.rootModel.destroy();this.rootModel=new pc.Entity('PRODUCT-'+product.id+'-CC0');this.rootModel.addChild(model);this.productRoot.addChild(this.rootModel);this._setTransform();this.onStatus('Modelo CC0 cargado. Puedes verlo a escala real.');}catch(e){console.info('Conservando GLB local:',e.message);}}
 _setTransform(){if(!this.rootModel)return;this.rootModel.setLocalEulerAngles(0,this.yaw,0);this.rootModel.setLocalScale(this.scale,this.scale,this.scale);}
 setRotation(n){this.yaw=n;this._setTransform();}rotate(d){this.setRotation(((this.yaw+d+180)%360+360)%360-180);return this.yaw;}
 setScale(n){this.scale=clamp(n,.5,1.5);this._setTransform();}
 clear(){this._clear();this.item=null;this.selectedToken++;this.productRoot.enabled=false;this.hasPlaced=false;}
 resetPlacement(){if(!this.item)return;this.moving=true;this.hasPlaced=false;if(this.session){this.marker.enabled=false;this._destroyAnchor();this.onStatus('Apunta al suelo y pulsa COLOCAR.');}else{this.productRoot.setPosition(0,0,0);this.onStatus('Arrastra la imagen para cambiar el ángulo o utiliza los controles.');}}
 place(){if(!this.item)return false;if(!this.session){this.hasPlaced=true;this.onStatus('Producto colocado en el espacio demostrativo.');return true;}if(!this.hit||performance.now()-this.lastHitAt>1400){this.onStatus('Todavía no se ha detectado el suelo. Mueve el teléfono lentamente.',true);return false;}this.productRoot.setPosition(this.hit);this.productRoot.enabled=true;this.hasPlaced=true;this.moving=false;this.marker.enabled=false;this._destroyAnchor();if(this.app.xr.anchors?.available&&this.hitResult){try{this.app.xr.anchors.create(this.hitResult,(err,anchor)=>{if(!err&&anchor&&this.session)this.anchor=anchor;});}catch(e){console.warn('Anchor no disponible',e);}}this.onStatus('Producto colocado. Puedes girarlo o cambiar de producto.');return true;}
 _destroyAnchor(){if(this.anchor){try{this.anchor.destroy();}catch{}this.anchor=null;}}
 _wirePointer(){this.canvas.addEventListener('pointerdown',e=>{if(this.session)return;this.drag=true;this.lastPointer={x:e.clientX,y:e.clientY};this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});this.canvas.setPointerCapture?.(e.pointerId);});this.canvas.addEventListener('pointermove',e=>{if(this.session||!this.drag||!this.lastPointer)return;const dx=e.clientX-this.lastPointer.x,dy=e.clientY-this.lastPointer.y;this.lastPointer={x:e.clientX,y:e.clientY};this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(this.moving){const pos=this.productRoot.getPosition();this.productRoot.setPosition(clamp(pos.x+dx*.006,-2.5,2.5),0,clamp(pos.z+dy*.006,-2.5,2.5));}else{this.orbitYaw+=dx*.26;this.orbitPitch=clamp(this.orbitPitch-dy*.18,5,70);this._cameraLook();}});for(const name of ['pointerup','pointercancel','lostpointercapture'])this.canvas.addEventListener(name,e=>{this.pointers.delete(e.pointerId);this.drag=false;this.lastPointer=null;});this.canvas.addEventListener('wheel',e=>{if(this.session)return;e.preventDefault();this.distance=clamp(this.distance+Math.sign(e.deltaY)*.30,3,10);this._cameraLook();},{passive:false});}
 // IMPORTANT: startXR() is called directly inside a user click. Nothing awaits before starting session.
 startXR(){if(this.session)return;this.app.xr.domOverlay.root=document.getElementById('shell');this.hasPlaced=false;this.moving=false;this._destroyAnchor();this.marker.enabled=false;this.productRoot.enabled=false;
  this.app.xr.start(this.camera.camera,pc.XRTYPE_AR,pc.XRSPACE_LOCALFLOOR,{planeDetection:true,anchors:true,callback:(err)=>{if(err){this.onStatus('No se pudo iniciar AR: '+(err.message||err),true);this._xrEnded();}}});
  this.app.xr.once('start',()=>{this.session=true;this.onTracking(true);this.onStatus('Busca una superficie horizontal moviendo lentamente la cámara.');if(!this.app.xr.hitTest.supported){this.onStatus('Este dispositivo no ofrece hit testing de superficies.',true);return;}
   this.app.xr.hitTest.start({spaceType:pc.XRSPACE_VIEWER,callback:(err,source)=>{if(err){this.onStatus('No se pudo detectar el suelo: '+(err.message||err),true);return;}this.hitSource=source;source.on('result',(pos,rotation,input,result)=>{this.hit=pos.clone();this.hitResult=result;this.lastHitAt=performance.now();if(!this.hasPlaced){this.marker.setPosition(pos.x,pos.y+.008,pos.z);this.marker.enabled=true;this.onStatus('Superficie detectada. Pulsa COLOCAR EN TU ESPACIO.');}});}});
  });
 }
 endXR(){if(this.app.xr.active)this.app.xr.end();else this._xrEnded();}
 _xrEnded(){this.session=false;this._destroyAnchor();try{this.hitSource?.remove();}catch{}this.hitSource=null;this.hit=null;this.marker.enabled=false;this.productRoot.setPosition(0,0,0);this.productRoot.enabled=true;this.hasPlaced=true;this._cameraLook();this.onTracking(false);this.onStatus('Vista 3D de demostración.');}
 _update(){if(!this.session)return;if(this.anchor&&this.hasPlaced){try{const pos=this.anchor.getPosition();this.productRoot.setPosition(pos);}catch{}}}
}
