import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {PinballPhysics} from '../src/physics.js';
const root=new URL('../',import.meta.url);
const context=vm.createContext({console});vm.runInContext(fs.readFileSync(new URL('vendor/box2d.js',root),'utf8'),context);
const b=context.box2d,layout=JSON.parse(fs.readFileSync(new URL('layout.json',root)));
const make=()=>{const g=new PinballPhysics(b,layout);g.start();return g;};
const step=(g,seconds)=>{for(let i=0;i<Math.ceil(seconds*120);i++)g.tick();};
const place=(g,x,y,vx,vy)=>{g.travelState='PLAYFIELD';g.rampPose=null;g.launched=true;g.ball.SetActive(true);g.ball.SetPosition(new b.b2Vec2(x,y));g.ball.SetLinearVelocity(new b.b2Vec2(vx,vy));};
const untilHit=(g,id)=>{for(let i=0;i<120&&!g.hits.has(id);i++)g.tick();assert.ok(g.hits.has(id),`No physical contact with ${id}`);};
for(const power of [.7,.85,1])test(`Charged plunger completes the channel: power ${power}`,()=>{
  const g=make();g.chargeStart();step(g,power*1.2);g.chargeRelease();
  step(g,5);assert.ok(g.events.some(e=>e.type==='entry'),'Charged ball must reach the playfield');
  assert.ok(g.events.some(e=>e.type==='hit'),'Charged ball must hit an interactive fixture');
});
for(const power of [0,.25,.5])test(`Weak plunger rolls back to launch lane: power ${power}`,()=>{
  const g=make();g.chargeStart();step(g,power*1.2);g.chargeRelease();
  step(g,7);assert.ok(g.events.some(e=>e.type==='weak-launch'),'Weak launch visibly stops on the channel');
  assert.ok(!g.events.some(e=>e.type==='entry'),'Weak ball must not reach the bumpers');
  assert.equal(g.launched,false,'The ball returns to the launcher without losing a life');
  assert.equal(g.balls,3);
});
for(const o of layout.bumpers)test(`${o.id}: physical collision, rebound, score and light`,()=>{
  const g=make();place(g,o.x,o.y+o.radius+.4,0,-6);untilHit(g,o.id);
  assert.equal(g.hits.get(o.id),1);assert.equal(g.score,o.points);assert.ok(g.ball.GetLinearVelocity().y>0);
  assert.ok(g.lights.get(o.id)>g.elapsed);step(g,.25);assert.ok(g.lights.get(o.id)<=g.elapsed);
});
for(const o of layout.targets)test(`${o.id}: independent contact and light`,()=>{
  const g=make();place(g,o.x,o.y+.55,0,-5);step(g,.12);
  assert.equal(g.hits.get(o.id),1);assert.equal(g.score,150);
  assert.equal([...g.lights].filter(([,t])=>t>g.elapsed).length,1);
  assert.ok(g.ball.GetLinearVelocity().y>0);
});
for(const o of layout.slings)test(`${o.id}: active triangular rebound`,()=>{
  const g=make();const left=o.id==='sling-left';place(g,left?2.8:6.7,12.0,left?-3:3,4);untilHit(g,o.id);
  assert.ok(g.hits.get(o.id)>0);assert.ok(g.ball.GetLinearVelocity().y<0);assert.ok(g.score>=25);
});
for(const side of ['left','right'])test(`${side}: motor sweeps, hits the ball and returns`,()=>{
  const g=make(),f=g.flippers.find(x=>x.id===side);step(g,.05);
  const x=f.x+Math.cos(f.rest)*.9,y=f.y+Math.sin(f.rest)*.9-.24;
  place(g,x,y,0,0);g.setFlipper(side,true);step(g,.05);
  assert.ok(g.ball.GetLinearVelocity().y<-2,'Motorized fixture must immediately transfer upward velocity');
  step(g,.08);
  assert.ok(Math.abs(f.body.GetAngle()-f.active)<.09);
  const other=g.flippers.find(x=>x.id!==side);assert.ok(Math.abs(other.body.GetAngle()-other.rest)<.06);
  g.setFlipper(side,false);step(g,.15);assert.ok(Math.abs(f.body.GetAngle()-f.rest)<.08);
});
test('Drain decrements lives, respawns and ends on the third loss',()=>{
  const g=make();for(let i=2;i>=0;i--){place(g,4.8,16.6,0,4);step(g,.02);assert.equal(g.balls,i);if(i){step(g,1);assert.equal(g.launched,false);assert.equal(g.ball.GetPosition().x,layout.spawn[0]);}}
  assert.equal(g.status,'finished');assert.equal(g.events.at(-1).reason,'balls');
});
test('Timer is real simulation time; reset clears score, lights, controls and lives',()=>{
  const g=make();step(g,1);assert.ok(Math.abs(g.remaining-119)<.02);g.elapsed=119.99;step(g,.02);assert.equal(g.status,'finished');assert.equal(g.remaining,0);
  g.start();assert.equal(g.score,0);assert.equal(g.balls,3);assert.equal(g.remaining,120);assert.equal(g.hits.size,0);
});
test('High-speed ball respects both side walls with continuous collision detection',()=>{
  for(const [x,vx] of [[1.0,-30],[8.3,30]]){const g=make();place(g,x,9.1,vx,0);step(g,.025);assert.ok(g.ball.GetPosition().x>.6);assert.ok(g.ball.GetPosition().x<8.75);assert.ok(Math.sign(g.ball.GetLinearVelocity().x)!==Math.sign(vx));}
});
test('Playing for 60 seconds keeps bodies finite and bounded without stuck launch',()=>{
  const g=make();for(let i=0;i<7200;i++){
    if(!g.launched&&!g.lossDelay&&g.status==='playing'){g.chargeStart();g.charge=1;g.chargeRelease();}
    g.setFlipper('left',i%71<16);g.setFlipper('right',i%83<20);g.tick();
    const p=g.ball.GetPosition();assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));assert.ok(p.x>0&&p.x<10.2);if(g.status==='finished')break;
  }
  assert.ok(g.score>0);assert.ok(g.events.some(e=>e.type==='entry'));
});

test('Single ramp: physical sensor, monotonic travel, collision isolation and tangent handoff',()=>{
 const g=make();g.chargeStart();g.charge=1;g.chargeRelease();let last=0,seen=false,exit=false;
 for(let i=0;i<650;i++){
  g.tick();if(g.travelState==='RAMP_TRAVEL'){
   seen=true;assert.equal(g.ball.IsActive(),false);assert.equal(g.score,0);assert.ok(g.rampPose.distance>=last);
   assert.ok(g.rampPose.z>=layout.ramp.floorHeight-1e-5);last=g.rampPose.distance;
  }else if(seen){exit=true;assert.equal(g.travelState,'PLAYFIELD');assert.equal(g.ball.IsActive(),true);
   assert.ok(g.ball.GetLinearVelocity().x>7);assert.ok(Math.abs(g.ball.GetPosition().y-7.05)<.02);break;
  }
 }
 assert.ok(seen&&exit);assert.equal(g.events.filter(e=>e.type==='ramp-enter').length,1);assert.equal(g.events.filter(e=>e.type==='ramp-exit').length,1);
});
test('Ramp restart, new ball and timeout discard guided state',()=>{
 const g=make();const launch=()=>{g.chargeStart();g.chargeRelease();step(g,.2);assert.equal(g.travelState,'RAMP_TRAVEL');};
 launch();g.start();assert.equal(g.travelState,'SHOOTER');assert.equal(g.rampPose,null);
 launch();g.respawn();assert.equal(g.travelState,'SHOOTER');assert.equal(g.ball.IsActive(),false);
 launch();g.elapsed=119.99;step(g,.02);assert.equal(g.status,'finished');assert.equal(g.rampPose,null);
});
test('Ramp has continuous floor, clear width, one endpoint and no descending floor overshoot',()=>{
 const r=layout.ramp;assert.ok(r.innerWidth>layout.ballRadius*2+.2);assert.deepEqual(r.samples[0].slice(0,2),layout.spawn);
 assert.equal(r.samples.at(-1)[2],r.floorHeight);
 for(let i=1;i<r.samples.length;i++){assert.ok(Math.hypot(...r.samples[i].map((v,k)=>v-r.samples[i-1][k]))<.15);assert.ok(r.samples[i][2]>=r.floorHeight-1e-5);}
 const p=r.samples.at(-1);for(const b of layout.bumpers)assert.ok(Math.hypot(p[0]-b.x,p[1]-b.y)>b.radius+layout.ballRadius+.2);
});

test('Physical guide posts match visible supports and leave the ramp mouth clear',()=>{
 const g=make();assert.ok(layout.posts.length>20);
 const end=layout.ramp.samples.at(-1);
 for(const post of layout.posts){assert.ok(g.fixtures.has(post.id));assert.ok(Math.hypot(end[0]-post.x,end[1]-post.y)>post.radius+layout.ballRadius+.06);}
 const p=layout.posts.find(o=>o.id.startsWith('channel-support'));
 place(g,p.x+.5,p.y,-5,0);step(g,.1);assert.ok(g.ball.GetLinearVelocity().x>0);assert.equal(g.score,0);
});

test('Reference flippers have a broad pivot and a narrower physical tip',()=>{
 const g=make();
 assert.ok(layout.flipperRadius>layout.flipperTipRadius);
 for(const f of g.flippers){
  const inside=(x,y)=>{const p=f.body.GetWorldPoint(new b.b2Vec2(x,y),new b.b2Vec2());for(let fx=f.body.GetFixtureList();fx;fx=fx.GetNext())if(fx.TestPoint(p))return true;return false;};
  assert.ok(inside(0,layout.flipperRadius-.02),'Pivot uses the modeled broad body');
  assert.ok(inside(f.length,layout.flipperTipRadius-.02),'Nose retains its solid collision surface');
  assert.equal(inside(f.length,layout.flipperRadius-.02),false,'No invisible capsule-width contact around narrow nose');
 }
});

test('Physics varies: sling > main bumper > small tank, without identical rebound',()=>{
 const g=make(),kinds=[
  g.layout.slings[0],
  g.layout.bumpers.find(o=>o.kind==='main'),
  g.layout.bumpers.find(o=>o.kind==='tank')
 ];
 const speeds=kinds.map(o=>{
  g.launched=true;g.ball.SetActive(true);
  g.ball.SetPosition(new b.b2Vec2(o.x!=null?o.x+.3:3,o.y??11));
  g.ball.SetLinearVelocity(new b.b2Vec2(0,0));
  g.hit({...o,type:o.kick?'sling':'bumper',points:o.points??25});
  return Math.hypot(g.ball.GetLinearVelocity().x,g.ball.GetLinearVelocity().y);
 });
 assert.ok(speeds[0]>speeds[1]&&speeds[1]>speeds[2],JSON.stringify(speeds));
});
test('Nudge displaces a playfield ball but not during guided ramp; repeated nudges cause TILT',()=>{
 const g=make();place(g,4.75,11.4,0,0);
 assert.equal(g.nudge(1,-1),true);
 assert.ok(Math.hypot(g.ball.GetLinearVelocity().x,g.ball.GetLinearVelocity().y)>1);
 g.travelState='RAMP_TRAVEL';assert.equal(g.nudge(),false);
 g.travelState='PLAYFIELD';
 for(let i=0;i<3;i++)assert.equal(g.nudge(0,-1),true);
 assert.equal(g.nudge(0,-1),false);assert.equal(g.snapshot().tilted,true);
 assert.equal(g.nudge(0,-1),false);
});
test('Stalled balls are freed; persistent pinning returns to a safe playfield area',()=>{
 const g=make();place(g,4.75,11.3,0,0);
 // Force repeated diagnostic scans at the same physical position to represent
 // a trapped ball without simulating several seconds of collisions.
 for(let attempt=0;attempt<3;attempt++){
   g.ball.SetPosition(new b.b2Vec2(4.75,11.3));
   g.stallOrigin={x:4.75,y:11.3};g.stallSeconds=2.99;
   g.detectStuck(.02);
 }
 assert.ok(g.events.filter(e=>e.type==='unstuck').length>=3);
 assert.equal(g.balls,3);
 assert.equal(g.stuckAttempts,0);
});
