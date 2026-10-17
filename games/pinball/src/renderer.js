export class Renderer {
  constructor(canvas,projection,layout,background,interactives,foreground,glass,ballSprite,depth,flipperAtlas,flipperFrames){Object.assign(this,{canvas,projection,layout,background,interactives,foreground,glass,ballSprite,flipperAtlas,flipperFrames});this.ctx=canvas.getContext('2d',{alpha:false});this.debug=false;
    if(depth){const dc=document.createElement('canvas');dc.width=depth.width;dc.height=depth.height;const dx=dc.getContext('2d',{willReadFrequently:true});dx.drawImage(depth,0,0);this.depth=dx.getImageData(0,0,dc.width,dc.height).data;}
    this.ballCanvas=document.createElement('canvas');this.ballCanvas.width=this.ballCanvas.height=128;this.ballContext=this.ballCanvas.getContext('2d',{willReadFrequently:true});this.ballContext.drawImage(ballSprite,0,0,128,128);this.ballPixels=this.ballContext.getImageData(0,0,128,128);
  }
  depthAt(x,y){if(!this.depth||x<0||y<0||x>=this.canvas.width||y>=this.canvas.height)return 100;const i=(Math.floor(y)*this.canvas.width+Math.floor(x))*4;return (this.depth[i]*256+this.depth[i+1])/65535*100;}
  // Cycles Z is camera-axis depth, not Euclidean distance along an oblique ray.
  distance(x,y,z){const v=[x-5,8-y,z,1];return this.projection.matrix[3].reduce((sum,n,i)=>sum+n*v[i],0);}
  display(game){
    const c=this.ctx,values={score:String(game.score).padStart(6,'0').replace(/(\d{3})$/,'.$1'),time:String(Math.floor(Math.ceil(game.remaining)/60)).padStart(2,'0')+':'+String(Math.ceil(game.remaining)%60).padStart(2,'0')};
    for(const [i,uv] of (this.projection.ballIndicators||[]).entries()){const x=uv[0]*this.canvas.width,y=uv[1]*this.canvas.height;c.beginPath();c.arc(x,y,2.8,0,Math.PI*2);c.fillStyle=i<game.balls?'#ffe294':'#203247';c.shadowColor='#ffa218';c.shadowBlur=i<game.balls?5:0;c.fill();c.shadowBlur=0;}
    for(const [key,uv] of Object.entries(this.projection.displays||{})){
      const q=uv.map(([x,y])=>({x:x*this.canvas.width,y:y*this.canvas.height}));
      c.save();c.setTransform((q[1].x-q[0].x)/400,(q[1].y-q[0].y)/400,(q[3].x-q[0].x)/64,(q[3].y-q[0].y)/64,q[0].x,q[0].y);
      c.font='78px PinballSegment';c.textAlign='center';c.textBaseline='middle';c.fillStyle='#ffe4a0';c.shadowColor='#ff9400';c.shadowBlur=7;const tw=c.measureText(values[key]).width;c.translate(200,34);c.scale(370/tw,1);c.fillText(values[key],0,0);c.restore();
    }
  }
  rampLights(game){
    this.activeRampLights=[];if(!game.rampPose)return;const c=this.ctx,ps=this.layout.ramp.samples,ds=this.layout.ramp.distances,d=game.rampDistance;
    for(let i=8;i<ps.length-5;i+=16){if(Math.abs(ds[i]-d)>1.3)continue;const a=ps[Math.max(0,i-1)],b=ps[Math.min(ps.length-1,i+1)],l=Math.hypot(b[0]-a[0],b[1]-a[1]);
      for(const side of [-1,1]){const x=ps[i][0]+side*.35*(b[1]-a[1])/l,y=ps[i][1]-side*.35*(b[0]-a[0])/l,z=ps[i][2]+.29,p=this.point(x,y,z);
       if(this.depthAt(p.x,p.y)+.12<this.distance(x,y,z))continue;this.activeRampLights.push({sample:i,side});c.save();c.globalCompositeOperation='screen';c.shadowColor='#ffc42b';c.shadowBlur=12;c.fillStyle='#fff3b1';c.beginPath();c.arc(p.x,p.y,2.6,0,Math.PI*2);c.fill();c.restore();
      }
    }
  }
  point(x,y,z=0){const v=[x-5,8-y,z,1],m=this.projection.matrix,r=m.map(row=>row.reduce((a,n,i)=>a+n*v[i],0));return {x:(r[0]/r[3]+1)*this.canvas.width/2,y:(1-r[1]/r[3])*this.canvas.height/2};}
  poly(points,z,fill,stroke=null,width=2){const c=this.ctx;c.beginPath();points.forEach(([x,y],i)=>{const p=this.point(x,y,z);i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y);});c.closePath();if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}}
  ellipse(x,y,z,r,color){const p=this.point(x,y,z),a=this.point(x+r,y,z),b=this.point(x,y+r,z),c=this.ctx;c.beginPath();c.ellipse(p.x,p.y,Math.abs(a.x-p.x),Math.abs(b.y-p.y),0,0,Math.PI*2);c.fillStyle=color;c.fill();}
  icon(index,p,lit){
    const c=this.ctx;c.save();c.translate(p.x,p.y);c.scale(1.25,1.25);c.strokeStyle=lit?'#fff9c4':index===2?'#eaf5ff':'#ffcd1c';c.fillStyle=c.strokeStyle;c.lineWidth=2;c.lineCap='round';c.lineJoin='round';
    if(lit){c.shadowColor='#ffd41f';c.shadowBlur=18;}
    const path=(points,fill=false)=>{c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));if(fill){c.closePath();c.fill();}else c.stroke();};
    if(index===0){for(let row=0;row<3;row++)for(let col=0;col<3;col++){const x=-10+col*7+(row%2)*3.5;if(x<9)c.fillRect(x,-9+row*6,Math.min(6,10-x),5);}}
    if(index===1){path([[-8,9],[2,-1],[5,-1],[10,-6],[9,-10],[5,-6],[2,-8],[6,-12],[1,-12],[-3,-8],[-3,-4],[-11,6]],true);}
    if(index===2){c.strokeRect(-10,-10,16,7);path([[7,-8],[10,-8],[10,0],[0,0],[0,5]]);c.fillRect(-2,4,4,9);}
    if(index===3)path([[1,-12],[-8,1],[-1,1],[-5,13],[9,-3],[2,-3],[7,-12]],true);
    if(index===4){path([[-10,2],[-6,2],[-6,-3],[4,-3],[4,3],[10,3],[10,8]]);path([[-6,-3],[-6,-7]]);path([[-10,-7],[-2,-7]]);c.fillRect(-12,0,4,6);c.beginPath();c.arc(10,11,1.4,0,Math.PI*2);c.fill();}
    if(index===5){c.fillStyle=lit?'#fbffd2':'#b7df79';c.beginPath();c.moveTo(-9,10);c.bezierCurveTo(-15,-5,0,-9,11,-12);c.bezierCurveTo(10,4,3,13,-9,10);c.fill();c.strokeStyle='#f3ffe4';path([[-10,12],[5,-5]]);}
    if(index===6){path([[-12,-9],[-8,-9],[-4,5],[8,5],[11,-5],[-7,-5]]);for(const x of [-3,7]){c.beginPath();c.arc(x,10,2,0,Math.PI*2);c.fill();}}
    c.restore();
  }
  draw(game){
    const c=this.ctx;c.fillStyle='#07203a';c.fillRect(0,0,this.canvas.width,this.canvas.height);c.drawImage(this.background,0,0,this.canvas.width,this.canvas.height);c.drawImage(this.interactives,0,0,this.canvas.width,this.canvas.height);
    for(const o of this.layout.bumpers){const lit=(game.lights.get(o.id)||0)>game.elapsed;if(lit){c.save();c.globalCompositeOperation='screen';const p=this.point(o.x,o.y,.45);const r=Math.abs(this.point(o.x+o.radius*2,o.y,.45).x-p.x);const gr=c.createRadialGradient(p.x,p.y,2,p.x,p.y,r);gr.addColorStop(0,'#ffffcbbb');gr.addColorStop(.4,'#ffd22b99');gr.addColorStop(1,'#ffad0000');c.fillStyle=gr;c.fillRect(p.x-r,p.y-r,r*2,r*2);this.ellipse(o.x,o.y,o.kind==='tank'?1.0:.77,o.radius*.9,'#ffdb4344');c.restore();}}
    for(const [i,o] of this.layout.targets.entries()){
      const pulse=(game.lights.get(o.id)||0)>game.elapsed;
      const active=game.targetsActivated?.has(o.id)===true;
      const p=this.point(o.x,o.y+.23,.49);
      if(pulse||active)this.icon(i,p,true);
      // The seven lamps stay visibly lit after each distinct hit.
      // A larger glow chases across them during the completion celebration.
      if(pulse||active){
        const lamp=this.point(o.x,o.y+.25,.18);
        c.save();c.shadowColor='#ffce00';c.shadowBlur=pulse?32:12;
        c.fillStyle=pulse?'#fff0a0':'#eec548';
        c.beginPath();c.arc(lamp.x,lamp.y,pulse?8:4,0,Math.PI*2);c.fill();c.restore();
      }
    }
    for(const s of this.layout.slings)if((game.lights.get(s.id)||0)>game.elapsed){c.save();c.globalCompositeOperation='screen';this.poly(s.vertices,.42,'#ffe84a66','#fff4aa',3);c.restore();}
    c.drawImage(this.foreground,0,0,this.canvas.width,this.canvas.height);this.rampLights(game);
    this.flipperRenderFrames={};
    for(const f of game.flippers){
      const frames=this.flipperFrames.frames[f.id],angle=f.body.GetAngle();
      const frame=frames.reduce((best,p)=>Math.abs(p.angle-angle)<Math.abs(best.angle-angle)?p:best,frames[0]);
      // These are the actual modeled blue body, rubber, white cap and fittings,
      // rendered by Cycles from the same camera at each motor angle.
      this.flipperRenderFrames[f.id]={angle:frame.angle,physicalAngle:angle};
      const root=this.layout.flipperRadius,tip=this.layout.flipperTipRadius,q=Math.acos((root-tip)/f.length);
      const contour=[];
      for(let i=0;i<=16;i++){const t=-q+2*q*i/16;contour.push([f.length+tip*Math.cos(t),tip*Math.sin(t)]);}
      for(let i=0;i<=20;i++){const t=q+(Math.PI*2-2*q)*i/20;contour.push([root*Math.cos(t),root*Math.sin(t)]);}
      this.poly(contour.map(([x,y])=>[f.x+x*Math.cos(angle)-y*Math.sin(angle)+.025,f.y+x*Math.sin(angle)+y*Math.cos(angle)+.04]),.025,'#0006');
      this.ellipse(f.x,f.y,.025,.25,'#0007');
      const sx=this.canvas.width/this.flipperFrames.width,sy=this.canvas.height/this.flipperFrames.height;
      c.drawImage(this.flipperAtlas,frame.sx,frame.sy,frame.width,frame.height,frame.x*sx,frame.y*sy,frame.width*sx,frame.height*sy);
    }
    const b=game.rampPose||game.ball.GetPosition(),z=game.rampPose?b.z+this.layout.ballRadius+.01:this.layout.ballRadius+.05;
    const p=this.point(b.x,b.y,z),r=Math.abs(this.point(b.x+this.layout.ballRadius,b.y,z).x-p.x),size=r*2.3125;
    if(!game.rampPose)this.ellipse(b.x+.08,b.y+.10,.02,.18,'#0008');
    let eligiblePixels=0,visiblePixels=0;const pixels=new ImageData(new Uint8ClampedArray(this.ballPixels.data),128,128),depth=this.distance(b.x,b.y,z);
    for(let yy=0;yy<128;yy++)for(let xx=0;xx<128;xx++){
      const i=(yy*128+xx)*4;if(!pixels.data[i+3])continue;eligiblePixels++;
      const u=(xx-64)/55.35,v=(yy-64)/55.35,front=depth-this.layout.ballRadius*Math.sqrt(Math.max(0,1-u*u-v*v));
      if(front>this.depthAt(p.x-size/2+xx/128*size,p.y-size/2+yy/128*size)+.035)pixels.data[i+3]=0;
      if(pixels.data[i+3])visiblePixels++;
      // A minute rolling witness mark moves over the sphere; reflections stay world-fixed.
      if(game.rampPose&&Math.abs(u-Math.sin(game.rampDistance/this.layout.ballRadius)*.65)<.025&&Math.abs(v-.15)<.035){pixels.data[i]*=.65;pixels.data[i+1]*=.65;pixels.data[i+2]*=.65;}
    }
    this.ballVisibleFraction=eligiblePixels?visiblePixels/eligiblePixels:0;this.ballContext.putImageData(pixels,0,0);c.drawImage(this.ballCanvas,p.x-size/2,p.y-size/2,size,size);
    // Moving shooter rod and steel spring, aligned to the same camera plane.
    const rodTop=14.78+game.charge*.42;const top=this.point(9.25,rodTop,.19),bottom=this.point(9.25,16,.19);
    const chrome=c.createLinearGradient(top.x-7,0,top.x+7,0);
    for(const [stop,color] of [[0,'#08192a'],[.18,'#66829e'],[.36,'#f5faff'],[.48,'#9ab4c9'],[.62,'#183350'],[.83,'#d8e8f1'],[1,'#172a3e']])chrome.addColorStop(stop,color);
    c.lineWidth=13;c.strokeStyle='#020b17';c.beginPath();c.moveTo(top.x+2,top.y+3);c.lineTo(bottom.x+2,bottom.y+3);c.stroke();
    c.lineWidth=9;c.strokeStyle=chrome;c.beginPath();c.moveTo(top.x,top.y);c.lineTo(bottom.x,bottom.y);c.stroke();
    // Continuous helical coil follows the charged rod, with front/back highlights.
    for(let i=0;i<216;i++){
      const a=i*Math.PI/12,b=(i+1)*Math.PI/12;
      const y=rodTop+.16+i/216*(15.87-rodTop-.16),yy=rodTop+.16+(i+1)/216*(15.87-rodTop-.16);
      const p=this.point(9.25+Math.cos(a)*.17,y,.22+Math.sin(a)*.12),q=this.point(9.25+Math.cos(b)*.17,yy,.22+Math.sin(b)*.12);
      c.beginPath();c.moveTo(p.x,p.y);c.lineTo(q.x,q.y);c.lineWidth=2.4;c.strokeStyle=Math.sin(a)>.15?'#e7eef3':Math.sin(a)>-.3?'#8197ad':'#23384e';c.stroke();
    }
    const cap=this.point(9.25,rodTop,.22),rr=Math.abs(this.point(9.48,rodTop,.22).x-cap.x);
    const capMetal=c.createLinearGradient(cap.x-rr,cap.y-4,cap.x+rr,cap.y+4);capMetal.addColorStop(0,'#284464');capMetal.addColorStop(.32,'#faf8e8');capMetal.addColorStop(.47,'#a8b9c9');capMetal.addColorStop(.65,'#243b53');capMetal.addColorStop(.86,'#dce9f3');capMetal.addColorStop(1,'#18334d');
    this.ellipse(9.25,rodTop,.22,.23,capMetal);
    // The protective pane remains above all live pieces, never intercepting input.
    c.drawImage(this.glass,0,0,this.canvas.width,this.canvas.height);
    this.display(game);
    if(this.debug){c.beginPath();this.layout.ramp.samples.forEach(([x,y,z],i)=>{const p=this.point(x,y,z+.17);i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y);});c.strokeStyle='#ff33dd';c.lineWidth=3;c.stroke();for(const w of this.layout.walls){c.beginPath();w.forEach(([x,y],i)=>{const p=this.point(x,y,.02);i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y);});c.strokeStyle='#3cff8e';c.lineWidth=2;c.stroke();}for(const o of this.layout.posts||[])this.ellipse(o.x,o.y,.02,o.radius,'#ff916c');for(const o of this.layout.bumpers)this.ellipse(o.x,o.y,.02,o.radius,'#00ff4444');for(const o of this.layout.targets)this.poly([[o.x-.31,o.y-.17],[o.x+.31,o.y-.17],[o.x+.31,o.y+.17],[o.x-.31,o.y+.17]],.02,null,'#3cff8e');}
  }
}
