/**
 * Ferrisariato IN-STORE: calibrated planar-projection preview for the fixed
 * 900x1420 corridor photograph. This is NOT segmentation or tracking of an
 * arbitrary image/camera frame. Geometry and occluders were traced for THIS
 * photograph only. Live AR uses the separate webxr-floor.js implementation.
 *
 * A flat ground plane maps to the photo through a pinhole perspective
 * homography. The old horizontal row-strip distortion is intentionally gone.
 * Floor bounds exclude shelves; foreground masks leave people and cart intact.
 */
const IMAGE_SIZE={width:900,height:1420};
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const makeCanvas=()=>{const c=document.createElement('canvas');c.width=IMAGE_SIZE.width;c.height=IMAGE_SIZE.height;return c;};

// Floor limits follow the converging aisle margins. Non-floor displays are
// intentionally outside this path, including the bath fixtures at the right.
const AISLE="M 340 782 L 554 783 L 564 822 L 589 893 L 627 960 L 699 1034 L 794 1105 L 900 1155 L 900 1420 L 0 1420 L 0 1123 L 111 1053 L 232 978 L 305 887 L 325 827 Z";

// Foreground figures traced from THIS static image only (original image pixels).
// Keeping the original pixels on top of the floor is a true 2D occlusion mask;
// it does not fabricate replacements for the shoppers or the cart.
const FOREGROUND=[
 // Left shopper: head, shirt, exposed arms, trousers, shoes.
 "M 225 615 Q 249 610 259 627 L 265 644 L 260 659 Q 284 669 297 690 L 312 724 L 320 777 Q 325 797 312 807 Q 300 813 296 800 L 293 791 L 289 838 L 290 875 L 285 928 L 278 996 L 277 1045 Q 276 1062 261 1067 Q 249 1066 246 1055 L 244 1006 L 229 937 L 224 997 L 219 1050 Q 214 1069 197 1065 Q 189 1061 190 1044 L 197 972 L 201 904 L 198 858 L 195 825 L 181 815 L 175 788 L 176 751 L 185 714 L 191 693 L 204 674 L 216 663 L 211 647 Q 210 626 225 615 Z",
 // Center woman, including shoes.
 "M 415 676 Q 439 673 445 690 L 445 720 L 453 732 Q 467 736 474 756 L 480 798 L 485 834 Q 486 852 477 858 L 468 844 L 466 814 L 467 859 L 460 924 L 460 970 L 469 984 Q 470 1000 451 1003 L 440 994 L 435 944 L 429 883 L 425 943 L 428 984 Q 438 1004 420 1005 Q 407 1005 404 990 L 406 936 L 400 866 L 397 822 L 394 856 Q 385 867 381 852 L 385 803 L 391 766 L 400 745 L 410 731 Q 408 713 408 697 Q 405 681 415 676 Z",
 // Blue-shirt shopper behind the woman.
 "M 509 708 Q 524 708 530 723 L 530 741 L 545 752 Q 555 767 557 799 L 558 833 L 548 850 L 542 836 L 540 866 L 540 915 L 532 957 Q 541 974 527 977 L 518 964 L 515 894 L 510 929 L 507 965 Q 508 978 494 977 L 489 960 L 492 899 L 493 851 L 483 848 L 478 819 L 480 780 Q 483 757 496 749 L 501 736 Q 500 715 509 708 Z",
 // Distant shopper immediately to the left of the central pair.
 "M 324 747 Q 338 744 344 756 L 345 780 L 356 790 L 363 830 L 355 848 L 350 830 L 350 877 L 347 931 L 348 954 L 337 958 L 332 929 L 330 868 L 326 931 L 322 950 L 314 948 L 313 911 L 311 850 L 310 810 L 314 783 L 322 778 Z"
];

// Thin metal trolley bars must remain in front of the newly installed floor;
// restoring a rectangular photo patch would visibly reintroduce the old floor.
const CART_BARS=[
 "M 186 795 L 179 854 L 188 998 L 202 1054",
 "M 314 794 L 336 842 L 340 1005 L 327 1060",
 "M 186 797 L 312 800 L 326 810",
 "M 181 840 L 332 841",
 "M 192 910 L 333 912",
 "M 194 999 L 329 1003",
 "M 213 828 L 212 1019",
 "M 294 830 L 296 1037",
 "M 203 1051 Q 212 1064 219 1056",
 "M 318 1051 Q 325 1064 335 1056"
];

function shadowOnFloor(ctx,x,y,rx,ry,strength){
 ctx.save();ctx.translate(x,y);ctx.scale(rx,ry);
 const g=ctx.createRadialGradient(0,0,.15,0,0,1);
 g.addColorStop(0,'rgba(14,17,18,'+strength+')');
 g.addColorStop(1,'rgba(14,17,18,0)');
 ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,1,0,Math.PI*2);ctx.fill();ctx.restore();
}
// Photographic ground plane: vanishing point ~ (450,630), camera-side plane
// extends outside the photo. This *rational* projection is perspective-correct.
function project(u,v){
 const perspective=1+3.75*v;
 return {x:450+(u-.5)*1100/perspective,
         y:630+790/perspective};
}
function tri(ctx,pattern,src,dst){
 const [s0,s1,s2]=src,[d0,d1,d2]=dst;
 const sx1=s1.x-s0.x,sy1=s1.y-s0.y,sx2=s2.x-s0.x,sy2=s2.y-s0.y;
 const det=sx1*sy2-sx2*sy1;if(Math.abs(det)<.00001)return;
 const dx1=d1.x-d0.x,dy1=d1.y-d0.y,dx2=d2.x-d0.x,dy2=d2.y-d0.y;
 const a=(dx1*sy2-dx2*sy1)/det;
 const b=(dy1*sy2-dy2*sy1)/det;
 const c=(sx1*dx2-sx2*dx1)/det;
 const d=(sx1*dy2-sx2*dy1)/det;
 const e=d0.x-a*s0.x-c*s0.y,f=d0.y-b*s0.x-d*s0.y;
 ctx.save();
 ctx.beginPath();ctx.moveTo(d0.x,d0.y);ctx.lineTo(d1.x,d1.y);ctx.lineTo(d2.x,d2.y);ctx.closePath();
 ctx.clip();ctx.setTransform(a,b,c,d,e,f);
 ctx.fillStyle=pattern;
 const minx=Math.min(s0.x,s1.x,s2.x)-3,maxx=Math.max(s0.x,s1.x,s2.x)+3;
 const miny=Math.min(s0.y,s1.y,s2.y)-3,maxy=Math.max(s0.y,s1.y,s2.y)+3;
 ctx.fillRect(minx,miny,maxx-minx,maxy-miny);ctx.restore();
}

export class FloorPreview {
 constructor(canvas){
  this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});
  this.images=new Map();this.floorLayers=new Map();this.base=null;
  this.current=null;this.previous=null;this.start=0;this.duration=1200;
  this.r=0;this.cx=IMAGE_SIZE.width*.50;this.cy=IMAGE_SIZE.height*.81;
  this.before=false;this.active=false;this.raf=0;
  this.revealLayer=makeCanvas();this.revealCtx=this.revealLayer.getContext('2d');
 }
 async init(){
  if(this.canvas.width!==900||this.canvas.height!==1420)
   throw Error('La simulación requiere el encuadre original 900×1420, sin deformación.');
  const load=url=>new Promise((resolve,reject)=>{const im=new Image();
   im.onload=()=>resolve(im);im.onerror=()=>reject(Error('No se pudo cargar '+url));im.src=url;});
  const MATERIALS=[
   ['roble-natural','./assets/instore-e1f65608d.jpg'],
   ['porcelanato-piedra','./assets/instore-a941ebd35.jpg'],
   ['cemento-urbano','./assets/instore-c300b854c.jpg'],
   ['arena-mate','./assets/instore-ed819f1ba.jpg']
  ];
  const [base,...mats]=await Promise.all([
   load('./assets/instore-e94f4a91c.jpg'),...MATERIALS.map(x=>load(x[1]))
  ]);
  if(base.naturalWidth!==900||base.naturalHeight!==1420)
   throw Error('La fotografía del pasillo ha cambiado; se debe recalibrar la perspectiva y las máscaras.');
  this.base=base;
  MATERIALS.forEach((m,i)=>this.images.set(m[0],mats[i]));
  this.active=true;this.render();
 }
 _layer(id){
  if(this.floorLayers.has(id))return this.floorLayers.get(id);
  const texture=this.images.get(id);
  if(!texture)return null;
  const result=makeCanvas(),ctx=result.getContext('2d');
  ctx.save();ctx.clip(new Path2D(AISLE));
  const pattern=ctx.createPattern(texture,'repeat');
  // Regular ground cells in 3D, not horizontal screen-image strips.
  // Source coords map to a repeated physical texture on the ground plane.
  const nx=22,ny=38,tw=texture.width*3.2,th=texture.height*6.6;
  for(let j=0;j<ny;j++){
   const v0=j/ny,v1=(j+1)/ny;
   for(let i=0;i<nx;i++){
    const u0=i/nx,u1=(i+1)/nx;
    const src=[{x:u0*tw,y:v0*th},{x:u1*tw,y:v0*th},
      {x:u1*tw,y:v1*th},{x:u0*tw,y:v1*th}];
    const dst=[project(u0,v0),project(u1,v0),project(u1,v1),project(u0,v1)];
    tri(ctx,pattern,[src[0],src[1],src[2]],[dst[0],dst[1],dst[2]]);
    tri(ctx,pattern,[src[0],src[2],src[3]],[dst[0],dst[2],dst[3]]);
   }
  }
  // Slight exposure response to the photographed aisle, without repainting
  // the people or removing the original light cues entirely.
  ctx.globalCompositeOperation='multiply';
  const shade=ctx.createLinearGradient(0,755,0,1420);
  shade.addColorStop(0,'rgba(153,166,180,.34)');
  shade.addColorStop(.42,'rgba(219,217,210,.14)');
  shade.addColorStop(1,'rgba(242,235,220,.10)');
  ctx.fillStyle=shade;ctx.fillRect(0,760,900,660);
  ctx.globalCompositeOperation='source-over';
  shadowOnFloor(ctx,242,1064,48,17,.43);
  shadowOnFloor(ctx,439,1005,30,10,.28);
  shadowOnFloor(ctx,516,974,25,8,.27);
  ctx.restore();
  // Replace no pixels belonging to the shoppers or the trolley.
  // Original photo remains visible through these transparencies.
  ctx.save();ctx.globalCompositeOperation='destination-out';
  for(const svg of FOREGROUND){const p=new Path2D(svg);ctx.fill(p);}
  ctx.lineCap='round';ctx.lineJoin='round';
  ctx.strokeStyle='#000';ctx.lineWidth=5;
  for(const svg of CART_BARS)ctx.stroke(new Path2D(svg));
  ctx.restore();
  this.floorLayers.set(id,result);return result;
 }
 setMaterial(id,origin){
  if(!this.images.has(id))return;
  this.previous=this.current;this.current=id;this.reveal(origin);
 }
 reveal(origin={x:IMAGE_SIZE.width*.5,y:IMAGE_SIZE.height*.83}){
  if(!this.current)this.current='roble-natural';
  this._layer(this.current); // prepare geometry once, not every animation frame
  this.cx=clamp(origin?.x??450,0,900);this.cy=clamp(origin?.y??1150,0,1420);
  this.start=performance.now();this.r=0;this.tick();
 }
 setBefore(value){this.before=value;this.render();}
 tick(){
  cancelAnimationFrame(this.raf);if(!this.active)return;
  const t=clamp((performance.now()-this.start)/this.duration,0,1);
  this.r=(1-Math.pow(1-t,2.2))*Math.hypot(900,1420)*1.35;
  this.render();
  if(t<1)this.raf=requestAnimationFrame(()=>this.tick());
  else{this.start=0;this.previous=null;}
 }
 render(){
  if(!this.active||!this.base)return;
  const ctx=this.ctx;ctx.setTransform(1,0,0,1,0,0);
  ctx.clearRect(0,0,900,1420);
  ctx.drawImage(this.base,0,0,900,1420);
  if(this.before||!this.current)return;
  if(this.previous)ctx.drawImage(this._layer(this.previous),0,0);
  if(!this.start){ctx.drawImage(this._layer(this.current),0,0);return;}
  const t=this.revealCtx;t.setTransform(1,0,0,1,0,0);t.clearRect(0,0,900,1420);
  t.drawImage(this._layer(this.current),0,0);
  t.globalCompositeOperation='destination-in';
  const g=t.createRadialGradient(this.cx,this.cy,Math.max(0,this.r-24),this.cx,this.cy,Math.max(1,this.r));
  g.addColorStop(0,'rgba(0,0,0,1)');g.addColorStop(1,'rgba(0,0,0,0)');
  t.fillStyle=g;t.fillRect(0,0,900,1420);t.globalCompositeOperation='source-over';
  ctx.drawImage(this.revealLayer,0,0);
 }
 /** Account for CSS object-fit:contain when a landscape desktop presents the portrait photo. */
 pointFromClient(clientX,clientY){
  const r=this.canvas.getBoundingClientRect(),canvasAR=900/1420,boxAR=r.width/r.height;
  const dw=boxAR>canvasAR?r.height*canvasAR:r.width;
  const dh=boxAR>canvasAR?r.height:r.width/canvasAR;
  const x0=r.left+(r.width-dw)/2,y0=r.top+(r.height-dh)/2;
  if(clientX<x0||clientX>x0+dw||clientY<y0||clientY>y0+dh)return null;
  return {x:(clientX-x0)/dw*900,y:(clientY-y0)/dh*1420};
 }
 stop(){this.active=false;cancelAnimationFrame(this.raf);}
}