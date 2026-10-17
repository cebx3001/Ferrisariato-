"""Articulated miniature palms: ringed trunks, arching fronds and curved leaflets."""
import bpy,math,json,bmesh
from mathutils import Matrix,Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);C=bpy.data.collections['Reference V5 / workshop assets']
for o in list(s.objects):
 if o.name.startswith(('Palm /','Garden tree /','Garden / dense crown','Reference V5 / miniature palm')):bpy.data.objects.remove(o,do_unlink=True)
def p(x,y,z):return B@Vector((x-5,8-y,z))
def mesh(name,ps,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(ps,[],fs);me.materials.append(m);me.update();o=bpy.data.objects.new('Reference V5 / miniature palm / '+name,me);C.objects.link(o);o['reference_asset']='miniature palms';return o
wood=bpy.data.materials['Cut pine'];greens=[bpy.data.materials['Reference V5 / leaf '+str(i)] for i in range(4)]
for x,y,z in [(2.65,2.18,.67),(6.75,2.18,.67)]:
 ps=[];n=24;rows=20
 for j in range(rows):
  zz=z+j*.053;r=.067*(1-j/rows*.3)*(1.12 if j%2 else .94)
  for i in range(n):a=i*math.tau/n;ps.append(p(x+math.cos(a)*r+.015*math.sin(j*.2),y+math.sin(a)*r,zz))
 mesh('segmented fibrous trunk',ps,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rows-1) for i in range(n)],wood)
 crown=z+1.08
 for j in range(16):
  a=j*2.39996;reach=.50+.10*(j%3);rise=.22+.06*(j%3)
  for k in range(1,13):
   t=k/13;xx=x+math.cos(a)*reach*t;yy=y+math.sin(a)*reach*t;zz=crown+rise*math.sin(math.pi*t)-.18*t
   length=.13*math.sin(math.pi*t)+.035
   for side in [-1,1]:
    tip=(xx-math.sin(a)*length*side+math.cos(a)*.07,yy+math.cos(a)*length*side+math.sin(a)*.07,zz-.055)
    mid=((xx+tip[0])*.5,(yy+tip[1])*.5,zz+.015)
    ps=[p(xx,yy,zz),p(mid[0]+.018*math.cos(a),mid[1]+.018*math.sin(a),mid[2]),p(*tip),p(mid[0]-.018*math.cos(a),mid[1]-.018*math.sin(a),mid[2])]
    mesh('individual arching leaflet',ps,[(0,1,2),(0,2,3)],greens[(j+k)%4])
# Move the upper-left planter onto the block top, with a readable contact point.
for o in s.objects:
 if o.get('reference_asset')=='rear corner miniature plants':
  c=B.inverted()@o.matrix_world.translation
  if c.x+5<3 and 8-c.y<1.5:o.location+=B.to_3x3()@Vector((0,0,.26))
s['miniature_palms_version']='5.0';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
