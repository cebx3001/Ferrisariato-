/**
 * HOME touch interactions. One finger rotates the placed model in AR.
 * Pinch scales 50–150%, twist rotates; two-finger drag repositions on the plane.
 * In studio, one finger rotates the product and vertically orbits the viewpoint.
 * The PlayCanvas renderer remains interactive without extra HUD buttons.
 */
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const angle=(a,b)=>Math.atan2(b.y-a.y,b.x-a.x);
const angleDelta=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
const center=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
export function attachMobileGestures(viewer,layer,{onTransform=()=>{}}={}){
 const arTouches=new Map(),studioTouches=new Map();
 let arOne=null,arTwo=null,studioTwo=null;
 const getTwo=map=>[...map.values()].slice(0,2);
 const update=()=>onTransform({rotation:viewer.yaw,scale:viewer.scale});
 function onARStart(e){
  if(e.pointerType==='mouse'&&e.button!==0)return;
  e.preventDefault();
  arTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});
  try{layer.setPointerCapture(e.pointerId);}catch{}
  if(arTouches.size===1)arOne={x:e.clientX,y:e.clientY};
  if(arTouches.size===2){
   const [a,b]=getTwo(arTouches);arTwo={distance:Math.max(10,distance(a,b)),angle:angle(a,b),center:center(a,b),yaw:viewer.yaw,scale:viewer.scale,position:viewer.productRoot.getPosition().clone()};arOne=null;
  }
 }
 function onARMove(e){
  if(!arTouches.has(e.pointerId))return;e.preventDefault();
  const pt={x:e.clientX,y:e.clientY};arTouches.set(e.pointerId,pt);
  if(!viewer.session||!viewer.hasPlaced||!viewer.rootModel)return;
  if(arTouches.size>=2){
   if(!arTwo)return;
   const [a,b]=getTwo(arTouches),c=center(a,b);
   viewer.setScale(clamp(arTwo.scale*distance(a,b)/arTwo.distance,.5,1.5));
   viewer.setRotation(arTwo.yaw+angleDelta(angle(a,b),arTwo.angle)*180/Math.PI);
   const cam=viewer.camera,base=arTwo.position,fwd=cam.forward,right=cam.right;
   const d=Math.max(.4,base.distance(cam.getPosition()));
   const meter=2*d*Math.tan((cam.camera.fov||60)*Math.PI/360)/Math.max(1,viewer.canvas.clientHeight);
   const norm=Math.hypot(fwd.x,fwd.z)||1;
   const dx=c.x-arTwo.center.x,dy=c.y-arTwo.center.y;
   viewer.productRoot.setPosition(base.x+right.x*dx*meter+(fwd.x/norm)*dy*meter,base.y,base.z+right.z*dx*meter+(fwd.z/norm)*dy*meter);
   update();return;
  }
  if(!arOne){arOne=pt;return;}
  viewer.rotate((pt.x-arOne.x)*.55);arOne=pt;update();
 }
 function onARStop(e){
  arTouches.delete(e.pointerId);
  if(arTouches.size>=2){const [a,b]=getTwo(arTouches);arTwo={distance:Math.max(10,distance(a,b)),angle:angle(a,b),center:center(a,b),yaw:viewer.yaw,scale:viewer.scale,position:viewer.productRoot.getPosition().clone()};}
  else{arTwo=null;arOne=arTouches.size?[...arTouches.values()][0]:null;}
 }
 layer.addEventListener('pointerdown',onARStart,{passive:false});
 layer.addEventListener('pointermove',onARMove,{passive:false});
 for(const k of ['pointerup','pointercancel','lostpointercapture'])layer.addEventListener(k,onARStop);
 const canvas=viewer.canvas;
 const captureDown=e=>{
  if(viewer.session)return;
  studioTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(studioTouches.size>=2){
   const [a,b]=getTwo(studioTouches);studioTwo={distance:Math.max(10,distance(a,b)),scale:viewer.scale};
  }
 };
 const captureMove=e=>{
  if(viewer.session||!studioTouches.has(e.pointerId))return;
  studioTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(studioTouches.size<2)return;
  e.preventDefault();e.stopImmediatePropagation();
  if(!studioTwo)return;
  const [a,b]=getTwo(studioTouches);
  viewer.setScale(clamp(studioTwo.scale*distance(a,b)/studioTwo.distance,.5,1.5));update();
 };
 const captureStop=e=>{
  studioTouches.delete(e.pointerId);
  if(studioTouches.size>=2){const [a,b]=getTwo(studioTouches);studioTwo={distance:Math.max(10,distance(a,b)),scale:viewer.scale};}else studioTwo=null;
 };
 canvas.addEventListener('pointerdown',captureDown,true);
 canvas.addEventListener('pointermove',captureMove,{capture:true,passive:false});
 for(const k of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(k,captureStop,true);
}