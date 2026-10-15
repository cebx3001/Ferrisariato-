import assert from 'node:assert/strict';
import {XR8Tracking} from './home/js/xr8-provider.js';
const modules=[];let hitsCalled=0,stopped=false,configured=null;
Object.defineProperty(globalThis,'navigator',{configurable:true,value:{userAgent:'iPhone',maxTouchPoints:2}});
globalThis.window={DeviceMotionEvent:undefined,DeviceOrientationEvent:undefined};
globalThis.XR8={
 XrConfig:{device:()=>({MOBILE:'mobile'})},
 XrController:{configure:x=>configured=x,hitTest:()=>{hitsCalled++;return [{type:'DETECTED_SURFACE',position:{x:0,y:0,z:-2},rotation:{x:0,y:0,z:0,w:1}}];}},
 PlayCanvas:{runXr:(scene,m,opts)=>{modules.push(...m);assert.equal(opts.allowedDevices,'mobile');},stopXr:()=>{stopped=true;}}
};
const events={};let trackPoint=null;let stable=false;
const app={on:(n,cb)=>events[n]=cb,off:n=>delete events[n]};
const camera={setPosition:()=>{},getPosition:()=>({x:0,y:2,z:0}),get forward(){return {x:0,y:-1/Math.sqrt(2),z:-1/Math.sqrt(2)};}};
const provider=new XR8Tracking({app,camera,canvas:{},onHit:(p,s)=>{trackPoint=p;stable=s;}});
await provider.start();
assert.equal(configured.scale,'responsive');assert.equal(hitsCalled,0);
modules[0].onUpdate({processCpuResult:{}});assert.equal(hitsCalled,0);
for(let i=0;i<9;i++){modules[0].onUpdate({processCpuResult:{reality:{}}});events.update();}
assert.equal(hitsCalled,9);assert.ok(trackPoint&&stable,'Surface should be stable');
const fixed=provider.lock();assert.ok(fixed);assert.equal(provider.placed,true);
provider.stop();assert.equal(stopped,true);assert.equal(events.update,undefined);
console.log('PASS: Gaussian-AR XR8 configuration, hitTest lifecycle, stable surface, fixed anchor, teardown');
