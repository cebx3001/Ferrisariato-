"""Authoritative continuous route, sampled identically by Blender and runtime."""
import json, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'layout.json';d=json.loads(p.read_text())
knots=[[9.25,14.5,.045],[9.25,12,.18],[9.25,8,.95],[9.2,4.5,1.75],[8.5,2,1.95],[7,.65,1.95],[4.7,.5,1.95],[2.5,.85,1.95],[1.45,2.7,1.7],[1.4,4.8,1.1],[1.55,6.3,.28],[2.05,6.98,.045],[2.65,7.05,.045]]
# Cubic Hermite XY; monotone harmonic tangents in Z prevent floor undershoot.
samples=[]
for i in range(len(knots)-1):
 a,b=knots[i:i+2];prev=knots[max(0,i-1)];nxt=knots[min(len(knots)-1,i+2)]
 def slope(l,r):return 2*l*r/(l+r) if l*r>0 else 0
 ma=[(b[k]-prev[k])/(1 if i==0 else 2) for k in range(3)]
 mb=[(nxt[k]-a[k])/(1 if i==len(knots)-2 else 2) for k in range(3)]
 ma[2]=slope(a[2]-prev[2],b[2]-a[2]);mb[2]=slope(b[2]-a[2],nxt[2]-b[2])
 for j in range(40):
  t=j/40;h00=2*t**3-3*t*t+1;h10=t**3-2*t*t+t;h01=-2*t**3+3*t*t;h11=t**3-t*t
  samples.append([round(h00*a[k]+h10*ma[k]+h01*b[k]+h11*mb[k],6) for k in range(3)])
samples.append(knots[-1]);dist=[0]
for a,b in zip(samples,samples[1:]):dist.append(round(dist[-1]+math.dist(a,b),6))
d['ramp']={'state':'RAMP_TRAVEL','innerWidth':.7,'floorHeight':.045,'sensor':[9.25,14.13],'exitSpeed':8,'knots':knots,'samples':samples,'distances':dist,'length':dist[-1]}
d['flipperRadius']=.21
# Close scenery bays while preserving the existing mechanical field.
d['walls']=d['walls'][:4]+[[[1.65,3.8],[1.65,10.9],[1.7,11.55]],[[7.85,3.8],[7.85,10.9],[7.8,11.55]],[[1.65,3.8],[7.85,3.8]]]
posts=[]
for wall in d['walls'][4:]:
 for a,b in zip(wall,wall[1:]):
  n=max(2,int(math.dist(a,b)/.8))
  for j in range(n+1):
   t=j/n;posts.append({'id':f'guide-post-{len(posts)}','x':a[0]*(1-t)+b[0]*t,'y':a[1]*(1-t)+b[1]*t,'radius':.055})
for i in range(8,len(samples)-5,16):
 a=samples[max(0,i-1)];b=samples[min(len(samples)-1,i+1)];dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy)
 for side in [-1,1]:
  x=samples[i][0]+side*.35*dy/l;y=samples[i][1]-side*.35*dx/l
  if 1.65<x<7.85 and 4.4<y<14:posts.append({'id':f'channel-support-{i}-{side}','x':round(x,6),'y':round(y,6),'radius':.065})
d['posts']=posts
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Shared route:',len(samples),'samples;',dist[-1],'units; clear width .70 vs ball diameter .32')
