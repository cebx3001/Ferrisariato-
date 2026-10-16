/**
 * HOME mobile gestures: one finger moves a placed model along the tracked ground;
 * two fingers rotate and pinch-scale. Studio keeps one-finger orbit and adds pinch zoom.
 */
const clamp=(n,a,b)=>Math.min(b,Math.max(a,n));
const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const angle=(a,b)=>Math.atan2(b.y-a.y,b.x-a.x);
const dAngle=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
export function attachMobileGestures(viewer,layer,{onTransform=()=>{}}={}){
 const points=new Map();let pinch=null,last=null,studio=null;
 const pair=()=>[...points.values()].slice(0,2);
 const initPinch=()=>{if(points.size<2)return;const [a,b]=pair();pinch={distance:Math.max(10,dist(a,b)),angle:angle(a,b),yaw:viewer.yaw,scale:viewer.scale};studio={distance:pinch.distance,zoom:viewer.distance};last=null;};
 const onDown=e=>{if(e.pointerType==='mouse'&&e.button!==0)return;e.preventDefault();points.set(e.pointerId,{x:e.clientX,y:e.clientY});try{layer.setPointerCapture(e.pointerId);}catch{}if(points.size>=2)initPinch();else last={x:e.clientX,y:e.clientY};};
 const onMove=e=>{
  if(!points.has(e.pointerId))return;e.preventDefault();
  const p={x:e.clientX,y:e.clientY};points.set(e.pointerId,p);
  if(!viewer.session||!viewer.hasPlaced||!viewer.rootModel||!viewer.item)return;
  if(points.size>=2){if(!pinch)initPinch();const [a,b]=pair();
   viewer.setScale(clamp(pinch.scale*dist(a,b)/pinch.distance,.5,1.5));
   viewer.setRotation(pinch.yaw+dAngle(angle(a,b),pinch.angle)*180/Math.PI);
   onTransform({rotation:viewer.yaw,scale:viewer.scale});return;}
  if(!last){last=p;return;}
  const dx=p.x-last.x,dy=p.y-last.y;last=p;
  const camera=viewer.camera,pos=viewer.productRoot.getPosition().clone();
  const distance=Math.max(.4,pos.distance(camera.getPosition()));
  const factor=2*distance*Math.tan((camera.camera.fov||60)*Math.PI/360)/Math.max(1,viewer.canvas.clientHeight);
  const right=camera.right,fwd=camera.forward;
  const norm=Math.hypot(fwd.x,fwd.z)||1;
  viewer.productRoot.setPosition(pos.x+right.x*dx*factor+fwd.x/norm*dy*factor,pos.y,pos.z+right.z*dx*factor+fwd.z/norm*dy*factor);
 };
 const onUp=e=>{points.delete(e.pointerId);if(points.size>=2)initPinch();else{pinch=null;last=points.size?pair()[0]:null;}};
 layer.addEventListener('pointerdown',onDown,{passive:false});
 layer.addEventListener('pointermove',onMove,{passive:false});
 for(const event of ['pointerup','pointercancel','lostpointercapture'])layer.addEventListener(event,onUp);
 const canvas=viewer.canvas;
 const studioDown=e=>{if(viewer.session)return;points.set(e.pointerId,{x:e.clientX,y:e.clientY});if(points.size>=2)initPinch();};
 const studioMove=e=>{if(viewer.session||!points.has(e.pointerId))return;points.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(points.size<2)return;e.preventDefault();e.stopImmediatePropagation();if(!studio)initPinch();
  const [a,b]=pair();viewer.distance=clamp(studio.zoom*studio.distance/Math.max(10,dist(a,b)),2,12);viewer._cameraLook();};
 const studioUp=e=>{points.delete(e.pointerId);if(points.size>=2)initPinch();else studio=null;};
 canvas.addEventListener('pointerdown',studioDown,true);
 canvas.addEventListener('pointermove',studioMove,{capture:true,passive:false});
 for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,studioUp,true);
}