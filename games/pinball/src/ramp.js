// Arc-length interpolation uses the exact sampled Blender construction spline.
export function rampPose(route,distance){
 const ds=route.distances,ps=route.samples,d=Math.max(0,Math.min(route.length,distance));
 let lo=0,hi=ds.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(ds[m]<=d)lo=m;else hi=m;}
 const a=ps[lo],b=ps[hi],t=(d-ds[lo])/(ds[hi]-ds[lo]||1),v=b.map((n,k)=>n-a[k]),n=Math.hypot(...v)||1;
 return {x:a[0]+v[0]*t,y:a[1]+v[1]*t,z:a[2]+v[2]*t,tangent:v.map(x=>x/n),distance:d,progress:d/route.length};
}
