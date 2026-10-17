import {rampPose} from './ramp.js';
// Adapted from lrusso/Pinball: Box2D bullet ball, motorized revolute
// flippers, contact-triggered scoring and transient 200 ms illumination.
// Rendering, table fixtures, launcher and match lifecycle are independent.
export class PinballPhysics {
  constructor(box2d, layout) {
    this.b = box2d; this.layout = layout; this.inputs = {left:false,right:false};
    this.events = []; this.reset();
  }
  reset() {
    const b=this.b;
    this.world = new b.b2World(new b.b2Vec2(0,this.layout.gravity));
    this.score=0; this.elapsed=0; this.remaining=this.layout.duration;
    this.balls=this.layout.balls; this.status='ready'; this.charge=0;
    this.travelState='SHOOTER';this.rampPose=null;this.rampDistance=0;this.launchPower=0;
    this.rampDirection=1;this.rampMaxDistance=0;this.rampSpeed=0;
    this.charging=false; this.launched=false; this.entered=false; this.lossDelay=0;
    this.stallOrigin=null;this.stallSeconds=0;this.stuckAttempts=0;
    this.nudgeHistory=[];this.tiltUntil=0;
    this.inputs.left=this.inputs.right=false; this.events=[]; this.cooldowns=new Map();
    this.hits=new Map(); this.lights=new Map(); this.pending=[]; this.fixtures=new Map();
    this.ground=this.body(0,0);
    this.layout.walls.forEach((line,i)=>line.slice(1).forEach((p,j)=>this.edge(line[j],p,`wall-${i}-${j}`)));
    for(const o of this.layout.posts||[])this.fixture(this.body(o.x,o.y),new b.b2CircleShape(o.radius),{...o,type:'post'},.55);
    for(const o of this.layout.bumpers) {
      const body=this.body(o.x,o.y); const shape=new b.b2CircleShape(o.radius);
      this.fixture(body,shape,{...o,type:'bumper'},o.kind==='tank'?.43:.68);
    }
    for(const o of this.layout.targets) {
      const body=this.body(o.x,o.y); const shape=new b.b2PolygonShape();shape.SetAsBox(.31,.17);
      this.fixture(body,shape,{...o,type:'target',points:150},.8);
    }
    for(const o of this.layout.slings) {
      const body=this.body(0,0); const shape=new b.b2PolygonShape();
      shape.Set(o.vertices.map(p=>new b.b2Vec2(...p)),o.vertices.length);
      this.fixture(body,shape,{...o,type:'sling',points:25},.82);
    }
    if(this.layout.ramp){const shape=new b.b2PolygonShape();shape.SetAsBox(.32,.08);const sensor=this.fixture(this.body(...this.layout.ramp.sensor),shape,{id:'ramp-entry',type:'ramp-entry'});sensor.SetSensor(true);}
    this.flippers=this.layout.flippers.map((o,i)=> {
      const body=this.body(o.x,o.y,true); body.SetAngle(o.rest);
      const root=this.layout.flipperRadius||.14,tip=this.layout.flipperTipRadius||root;
      const nx=(root-tip)/o.length,ny=Math.sqrt(1-nx*nx);
      const shape=new b.b2PolygonShape();
      shape.Set([[root*nx,root*ny],[o.length+tip*nx,tip*ny],[o.length+tip*nx,-tip*ny],[root*nx,-root*ny]].map(p=>new b.b2Vec2(...p)),4);
      this.fixture(body,shape,{id:o.id,type:'flipper'},.25,10);
      for(const x of [0,o.length]) {
        const cap=new b.b2CircleShape(x===0?root:tip);cap.m_p.SetXY(x,0);
        this.fixture(body,cap,{id:o.id,type:'flipper'},.25,10);
      }
      const def=new b.b2RevoluteJointDef();def.Initialize(this.ground,body,new b.b2Vec2(o.x,o.y));
      def.enableLimit=true;def.lowerAngle=Math.min(0,o.active-o.rest);def.upperAngle=Math.max(0,o.active-o.rest);
      def.enableMotor=true;def.maxMotorTorque=12000;def.motorSpeed=i? -34:34;
      return {body,joint:this.world.CreateJoint(def),...o};
    });
    this.ball=this.body(...this.layout.spawn,true);
    this.ball.SetBullet(true);this.ball.SetLinearDamping(.12);
    const ballFixture=new b.b2FixtureDef();ballFixture.shape=new b.b2CircleShape(this.layout.ballRadius);
    ballFixture.density=1;ballFixture.restitution=.35;ballFixture.friction=.08;
    ballFixture.filter.categoryBits=1;ballFixture.filter.maskBits=2;
    const fixture=this.ball.CreateFixture(ballFixture);fixture.SetUserData({id:'ball',type:'ball'});
    const listener=new b.b2ContactListener();
    listener.BeginContact=contact=>{
      const a=contact.GetFixtureA().GetUserData(),c=contact.GetFixtureB().GetUserData();
      const other=a?.type==='ball'?c:c?.type==='ball'?a:null;
      if(other&&['bumper','target','sling','ramp-entry'].includes(other.type))this.pending.push(other);
    };
    this.world.SetContactListener(listener);
    this.ball.SetActive(false);
  }
  body(x,y,dynamic=false) {
    const d=new this.b.b2BodyDef();d.position.SetXY(x,y);
    if(dynamic)d.type=this.b.b2BodyType.b2_dynamicBody;
    return this.world.CreateBody(d);
  }
  fixture(body,shape,data,restitution=.5,density=0) {
    const f=new this.b.b2FixtureDef();f.shape=shape;f.restitution=restitution;f.friction=.06;f.density=density;
    f.filter.categoryBits=2;f.filter.maskBits=1;
    const out=body.CreateFixture(f);out.SetUserData(data);this.fixtures.set(data.id,{body,fixture:out,data});return out;
  }
  edge(a,c,id){const s=new this.b.b2EdgeShape();s.Set(new this.b.b2Vec2(...a),new this.b.b2Vec2(...c));return this.fixture(this.ground,s,{id,type:'wall'},.55);}
  start(){this.reset();this.status='playing';this.events.push({type:'start'});}
  setFlipper(side,down){if(side in this.inputs)this.inputs[side]=down;}
  chargeStart(){if(this.status==='playing'&&!this.launched&&!this.lossDelay){this.charging=true;this.charge=0;}}
  chargeRelease(){
    if(!this.charging||this.status!=='playing')return;
    this.launchPower=this.charge;this.travelState='SHOOTER';this.charging=false;this.launched=true;this.ball.SetActive(true);
    this.ball.SetLinearVelocity(new this.b.b2Vec2(0,-(9+15*this.launchPower)));
    this.events.push({type:'launch',power:this.charge});this.charge=0;
  }
  clearInputs(){this.inputs.left=this.inputs.right=false;this.charging=false;this.charge=0;}
  tick(dt=1/120){
    if(this.status!=='playing')return;
    this.elapsed+=dt;this.remaining=Math.max(0,this.layout.duration-this.elapsed);
    if(this.remaining===0){this.finish('time');return;}
    if(this.charging)this.charge=Math.min(1,this.charge+dt/1.2);
    for(const [i,f] of this.flippers.entries()){
      const pressed=this.inputs[f.id]&&this.elapsed>=this.tiltUntil;
      f.joint.SetMotorSpeed((pressed?-1:1)*(i?-1:1)*(pressed?34:40));
    }
    if(this.lossDelay){this.lossDelay=Math.max(0,this.lossDelay-dt);if(!this.lossDelay)this.respawn();}
    this.world.Step(dt,10,5);
    for(const o of this.pending.splice(0)){if(o.type==='ramp-entry'){if(this.launched&&this.travelState==='SHOOTER')this.enterRamp();}else if(this.travelState!=='RAMP_TRAVEL')this.hit(o);}
    if(this.travelState==='RAMP_TRAVEL'){this.advanceRamp(dt);return;}
    const p=this.ball.GetPosition(),v=this.ball.GetLinearVelocity();
    if(this.launched){
      if(!this.layout.ramp&&!this.entered&&p.x<8.45&&p.y<4.0){this.entered=true;this.events.push({type:'entry'});}
      const speed=Math.hypot(v.x,v.y);if(speed>22)this.ball.SetLinearVelocity(new this.b.b2Vec2(v.x*22/speed,v.y*22/speed));
      if(p.y>16.5){this.balls--;this.ball.SetActive(false);this.launched=false;this.clearInputs();this.events.push({type:'lost'});if(!this.balls)this.finish('balls');else this.lossDelay=.85;}
      // A ball that returns down the real shooter lane may be relaunched.
      else if(p.x>8.95&&p.y>14.45&&Math.abs(v.y)<1&&this.elapsed>(this.lastReturn||0)+.7){this.respawn();this.events.push({type:'return'});this.lastReturn=this.elapsed;}
    }
    this.detectStuck(dt);
  }
  enterRamp(){
    const route=this.layout.ramp,p=this.ball.GetPosition();let nearest=0,error=Infinity;
    for(let i=0;i<Math.min(40,route.samples.length);i++){const q=route.samples[i],e=Math.hypot(q[0]-p.x,q[1]-p.y);if(e<error){nearest=i;error=e;}}
    this.rampDistance=route.distances[nearest];this.rampSpeed=8+13*this.launchPower;
    // Weak pulls visibly climb the same channel, lose energy and roll back to the launcher.
    // A sufficiently charged plunger completes the route and enters the playfield.
    this.rampDirection=1;
    this.rampMaxDistance=this.launchPower>=.62?route.length:
      Math.min(route.length-1,1.6+Math.pow(this.launchPower/.62,1.5)*route.length*.68);
    this.travelState='RAMP_TRAVEL';this.ball.SetActive(false);this.pending=[];
    this.rampPose=rampPose(route,this.rampDistance);this.events.push({type:'ramp-enter'});
  }
  advanceRamp(dt){
    const route=this.layout.ramp;
    if(this.rampDirection<0){
      this.rampDistance=Math.max(0,this.rampDistance-(4+this.rampSpeed*.75)*dt);
      if(this.rampDistance===0){this.respawn();this.events.push({type:'return'});return;}
    }else{
      const remaining=this.rampMaxDistance-this.rampDistance;
      const speed=this.rampMaxDistance<route.length?
        Math.max(.6,this.rampSpeed*Math.min(1,Math.sqrt(Math.max(0,remaining)/1.2))):this.rampSpeed;
      this.rampDistance=Math.min(this.rampMaxDistance,this.rampDistance+speed*dt);
      if(this.rampDistance>=this.rampMaxDistance&&this.rampMaxDistance<route.length){
        this.rampDirection=-1;this.events.push({type:'weak-launch'});
      }
    }
    this.rampPose=rampPose(route,this.rampDistance);const p=this.rampPose;
    this.ball.SetPosition(new this.b.b2Vec2(p.x,p.y));this.ball.SetAngle(this.rampDistance/this.layout.ballRadius);
    if(this.rampDistance>=route.length&&this.rampDirection>0){
      const [dx,dy]=p.tangent,n=Math.hypot(dx,dy);
      const exitSpeed=route.exitSpeed*(.8+.75*this.launchPower);
      this.travelState='PLAYFIELD';this.entered=true;
      this.ball.SetActive(true);this.ball.SetLinearVelocity(new this.b.b2Vec2(dx/n*exitSpeed,dy/n*exitSpeed));
      this.ball.SetAngularVelocity(exitSpeed/this.layout.ballRadius);this.rampPose=null;
      this.events.push({type:'ramp-exit'},{type:'entry'});
    }
  }
  // Genuine movement of the physical Box2D ball. Never nudges an animated ramp ball.
  nudge(dx=0,dy=-1,strength=1){
    if(this.status!=='playing'||this.travelState!=='PLAYFIELD'||!this.launched||
      !this.ball.IsActive()||this.elapsed<this.tiltUntil)return false;
    this.nudgeHistory=this.nudgeHistory.filter(t=>this.elapsed-t<4);
    this.nudgeHistory.push(this.elapsed);
    if(this.nudgeHistory.length>=5){
      this.nudgeHistory=[];this.tiltUntil=this.elapsed+2.5;
      this.events.push({type:'tilt'});return false;
    }
    const v=this.ball.GetLinearVelocity(),mag=Math.hypot(dx,dy)||1;
    const kick=Math.max(1,Math.min(4.5,2.5*strength));
    const vx=v.x+dx/mag*kick,vy=v.y+dy/mag*kick;
    const speed=Math.hypot(vx,vy),scale=speed>22?22/speed:1;
    this.ball.SetLinearVelocity(new this.b.b2Vec2(vx*scale,vy*scale));
    this.stallSeconds=0;this.stallOrigin=null;
    this.events.push({type:'nudge'});return true;
  }
  // A ball wedged in a static fixture receives two gentle freeing kicks; after
  // repeated failed attempts it returns to a clear area without losing a life.
  detectStuck(dt){
    if(this.travelState!=='PLAYFIELD'||!this.launched||!this.ball.IsActive()||this.lossDelay){
      this.stallSeconds=0;this.stallOrigin=null;return;
    }
    const p=this.ball.GetPosition();
    if(!this.stallOrigin||Math.hypot(p.x-this.stallOrigin.x,p.y-this.stallOrigin.y)>.18){
      this.stallOrigin={x:p.x,y:p.y};this.stallSeconds=0;return;
    }
    this.stallSeconds+=dt;
    if(this.stallSeconds<3)return;
    this.stuckAttempts++;
    if(this.stuckAttempts>=3){
      this.ball.SetPosition(new this.b.b2Vec2(4.75,11.3));
      this.ball.SetLinearVelocity(new this.b.b2Vec2(1.3,-3.5));
      this.stuckAttempts=0;
    }else{
      const direction=p.x<4.75?1:-1;
      this.ball.SetLinearVelocity(new this.b.b2Vec2(direction*4,-5));
    }
    this.stallSeconds=0;this.stallOrigin=null;this.events.push({type:'unstuck'});
  }
  hit(o){
    if((this.cooldowns.get(o.id)||-1)>this.elapsed||!this.launched)return;
    this.cooldowns.set(o.id,this.elapsed+.13);this.lights.set(o.id,this.elapsed+.2);
    this.hits.set(o.id,(this.hits.get(o.id)||0)+1);this.score+=o.points;
    const p=this.ball.GetPosition(),v=this.ball.GetLinearVelocity();
    let dx,dy;
    if(o.type==='bumper'){dx=p.x-o.x;dy=p.y-o.y;}
    else if(o.type==='sling'){[dx,dy]=o.kick;}
    else {dx=p.x-o.x;dy=p.y<o.y?-1:1;}
    // Mechanisms transfer different energy: slings strongest, large bumpers
    // medium, small tank bumpers soft. Avoid a uniform, frantic rebound feel.
    const n=Math.hypot(dx,dy)||1,k=o.type==='sling'?10.5:o.type==='bumper'?(o.kind==='tank'?2.3:5.3):1.8;
    this.ball.SetLinearVelocity(new this.b.b2Vec2(v.x+dx/n*k,v.y+dy/n*k));
    this.events.push({type:'hit',id:o.id,kind:o.type,points:o.points});
  }
  respawn(){this.travelState='SHOOTER';this.rampPose=null;this.rampDistance=0;this.rampDirection=1;this.rampMaxDistance=0;
    this.stallOrigin=null;this.stallSeconds=0;this.stuckAttempts=0;this.tiltUntil=0;this.nudgeHistory=[];
    this.pending=[];this.ball.SetActive(false);this.ball.SetPosition(new this.b.b2Vec2(...this.layout.spawn));this.ball.SetLinearVelocity(new this.b.b2Vec2(0,0));this.ball.SetAngularVelocity(0);this.launched=false;this.entered=false;this.charge=0;this.charging=false;}
  finish(reason){this.travelState='FINISHED';this.rampPose=null;this.status='finished';this.ball.SetActive(false);this.clearInputs();this.events.push({type:'finish',reason});}
  snapshot(){const p=this.ball.GetPosition(),v=this.ball.GetLinearVelocity();return {travelState:this.travelState,ramp:this.rampPose,ballActive:this.ball.IsActive(),status:this.status,score:this.score,remaining:this.remaining,balls:this.balls,charge:this.charge,launched:this.launched,entered:this.entered,launchPower:this.launchPower,rampDirection:this.rampDirection,tilted:this.elapsed<this.tiltUntil,stuckAttempts:this.stuckAttempts,position:{x:p.x,y:p.y},velocity:{x:v.x,y:v.y},flippers:this.flippers.map(f=>({id:f.id,angle:f.body.GetAngle()})),hits:Object.fromEntries(this.hits),lights:Object.fromEntries([...this.lights].filter(([,t])=>t>this.elapsed))};}
}
