"""Modular reference props. Linked mesh instances keep repeated details light.
Coordinates are the shared playfield coordinates, never collider definitions.
"""
import bpy, math, random
from mathutils import Vector

class Props:
    def __init__(self,api):self.__dict__.update(api)
    def copy(self,source,name,dx=0,dy=0,dz=0):
        o=source.copy();o.data=source.data;o.name=name;bpy.context.scene.collection.objects.link(o)
        o.location.x+=dx;o.location.y-=dy;o.location.z+=dz;return o
    def mesh(self,name,points,faces,material):
        m=bpy.data.meshes.new(name);m.from_pydata([self.pt(*p) for p in points],[],faces);m.update()
        o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.data.materials.append(material);return o
    def text(self,name,text,x,y,z,size,material,front=False):
        c=bpy.data.curves.new(name,'FONT');c.body=text;c.align_x='CENTER';c.size=size;c.extrude=.001
        o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=self.pt(x,y,z)
        if front:o.rotation_euler.x=math.pi/2
        c.materials.append(material);return o
    def pallet(self,x,y,w=1.05,d=.75,z=0):
        for xx in [-w*.37,0,w*.37]:
            for yy in [-d*.34,d*.34]:self.cube('Pallet / spacer block',x+xx,y+yy,z+.10,w*.15,d*.2,.18,self.wood)
        bottom=self.cube('Pallet / bottom skid',x-w*.37,y,z+.025,w*.16,d,.05,self.wood)
        self.copy(bottom,'Pallet / linked bottom skid',w*.37);self.copy(bottom,'Pallet / linked bottom skid',w*.74)
        plank=self.cube('Pallet / deck slat',x,y-d*.4,z+.22,w,d*.14,.08,self.wood)
        for i in range(1,5):self.copy(plank,'Pallet / linked deck slat',dy=d*.2*i)
        nail=self.cyl('Pallet / nail',x-w*.37,y-d*.4,z+.265,.014,.008,self.steel)
        for i in range(5):
            for xx in [0,w*.37,w*.74]:
                if i or xx:self.copy(nail,'Pallet / linked nail',xx,d*.2*i)
    def crate(self,x,y,w=.75,d=.65,h=.65,z=0):
        for xx in [-w*.44,w*.44]:
            for yy in [-d*.43,d*.43]:self.cube('Crate / timber corner',x+xx,y+yy,z+h/2,.07,.07,h,self.wood)
        for row in range(4):
            zz=z+(row+.5)*h/4
            for yy in [-d*.48,d*.48]:self.cube('Crate / face slat',x,y+yy,zz,w,.045,h*.2,self.wood)
            for xx in [-w*.48,w*.48]:self.cube('Crate / side slat',x+xx,y,zz,.045,d,h*.2,self.wood)
        self.cube('Crate / paper label',x,y+d*.51,z+h*.55,w*.6,.012,h*.42,self.white)
        self.text('Crate / handling mark','↑  ↑',x,y+d*.53,z+h*.42,h*.28,self.navy,True)
    def timber(self,x,y,z=.3):
        board=self.cube('Timber / cut plank',x-.25,y,z,.14,1.05,.11,self.wood)
        for layer in range(4):
            for col in range(4):
                if layer or col:self.copy(board,'Timber / linked stacked plank',col*.16,layer*.025,layer*.125)
        for yy in [-.31,.31]:self.cube('Timber / steel retaining band',x,y+yy,z+.25,.67,.035,.58,self.steel)
        for col in range(4):
            self.line('Timber / end grain',[(x-.25+col*.16-.04,y+.532,z+.1),(x-.25+col*.16+.04,y+.532,z+.1)],.005,self.navy)
    def bricks(self,x,y,z=.28,rows=3):
        brick=self.cube('Brick stack / chamfered brick',x-.24,y-.16,z,.28,.22,.17,self.brick)
        for row in range(rows):
            for col in range(3):
                for depth in range(2):
                    if row or col or depth:self.copy(brick,'Brick stack / linked brick',col*.30+(row%2)*.055,depth*.24,row*.185)
    def block(self,x,y,z=.3):
        # Hollow concrete masonry unit assembled from walls and a central web.
        for dx in [-.27,0,.27]:self.cube('Concrete block / cross web',x+dx,y,z,.065,.40,.28,self.concrete)
        for dy in [-.18,.18]:self.cube('Concrete block / longitudinal wall',x,y+dy,z,.60,.065,.28,self.concrete)
    def blocks(self,x,y,z=.25,count=5):
        positions=[(-.305,0,0),(.305,0,0),(-.27,.04,.3),(.34,.04,.3),(-.235,.08,.6)]
        for dx,dy,dz in positions[:count]:self.block(x+dx,y+dy,z+dz)
    def box(self,x,y,z=.5,w=.65,h=.65):
        self.cube('Cardboard carton',x,y,z,w,w*.8,h,self.cardboard)
        self.cube('Carton / packing tape',x,y,z+h/2+.005,.08,w*.8,.012,self.gold)
        self.text('Carton / shipping text','FRÁGIL',x,y+w*.405,z,.09,self.navy,True)
        self.text('Carton / orientation','↑  ↑',x,y+w*.405,z+.15,.15,self.navy,True)
    def tape(self,x,y,z=.3):
        self.cube('Tape measure / rubber shell',x,y,z+.23,.49,.32,.47,self.black)
        self.cube('Tape measure / yellow inset',x,y+.17,z+.24,.39,.028,.34,self.gold)
        self.cyl('Tape measure / steel hub',x,y,z+.49,.10,.025,self.steel)
        self.cube('Tape measure / thumb lock',x,y+.06,z+.49,.16,.11,.05,self.black)
        self.text('Tape measure / 5m label','5 m',x,y+.19,z+.20,.11,self.navy,True)
        self.cube('Tape measure / extended tape',x+.30,y+.12,z+.06,.32,.11,.016,self.gold)
        for i in range(7):self.cube('Tape measure / graduations',x+.18+i*.038,y+.12,z+.073,.008,.07,.005,self.navy)
        self.cube('Tape measure / hook',x+.47,y+.12,z+.025,.03,.13,.1,self.steel)
    def toolbox(self,x,y,z=.26):
        self.cube('Toolbox / ribbed yellow body',x,y,z+.28,1.05,.6,.5,self.gold)
        self.cube('Toolbox / hinged lid',x,y,z+.56,1.1,.64,.13,self.gold)
        self.line('Toolbox / folding black handle',[(x-.23,y,z+.64),(x-.23,y,z+.80),(x+.23,y,z+.80),(x+.23,y,z+.64)],.055,self.black)
        for dx in [-.33,.33]:
            self.cube('Toolbox / black latch',x+dx,y+.32,z+.43,.11,.05,.27,self.black)
            self.cube('Toolbox / latch pin',x+dx,y+.36,z+.49,.07,.02,.05,self.steel)
        for dx in [-.43,-.36,.36,.43]:self.cube('Toolbox / molded rib',x+dx,y+.31,z+.25,.025,.035,.34,self.navy)
    def drill(self,x,y,z=.85):
        self.cube('Cordless drill / battery pack',x,y,z+.08,.46,.34,.17,self.black)
        self.cube('Cordless drill / yellow battery edge',x,y,z+.15,.48,.36,.09,self.gold)
        grip=self.cube('Cordless drill / handle',x+.07,y,z+.39,.19,.22,.48,self.gold);grip.rotation_euler.y=-.16
        for dz in [.25,.31,.37,.43]:self.cube('Cordless drill / rubber grip ridge',x+.16,y+.12,z+dz,.08,.025,.032,self.black)
        self.cube('Cordless drill / trigger',x-.04,y,z+.53,.11,.23,.08,self.black)
        self.cube('Cordless drill / motor housing',x,y,z+.70,.59,.30,.30,self.gold)
        for xx in [.09,.15,.21]:self.cube('Cordless drill / cooling vent',x+xx,y+.155,z+.72,.025,.012,.16,self.black)
        chuck=self.cyl('Cordless drill / black chuck',x-.36,y,z+.70,.135,.22,self.black);chuck.rotation_euler.y=math.pi/2
        ring=self.cyl('Cordless drill / torque ring',x-.25,y,z+.70,.15,.065,self.steel);ring.rotation_euler.y=math.pi/2
        self.line('Cordless drill / steel bit',[(x-.46,y,z+.70),(x-.71,y,z+.70)],.022,self.steel)
    def bucket(self,x,y,z=0,r=.28,h=.55):
        self.cyl('Paint bucket / white body',x,y,z+h/2,r,h,self.white)
        for zz in [z+.04,z+h-.03]:self.cyl('Paint bucket / blue band',x,y,zz,r+.018,.08,self.blue)
        self.cyl('Paint bucket / chrome rolled rim',x,y,z+h+.02,r+.025,.035,self.steel)
        self.cyl('Paint bucket / blue sealed lid',x,y,z+h+.04,r*.93,.03,self.blue)
        self.line('Paint bucket / wire bail',[(x+r*math.cos(a),y-.04,z+h*.65+r*math.sin(a)) for a in [i*math.pi/20 for i in range(21)]],.012,self.steel)
        self.text('Paint bucket / house label','⌂',x,y+r+.012,z+h*.27,h*.5,self.blue,True)
    def cone(self,x,y,z=0):
        self.cube('Cone / square rubber foot',x,y,z+.06,.53,.53,.12,self.black)
        self.cube('Cone / orange base',x,y,z+.13,.47,.47,.07,self.orange)
        bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.21,radius2=.05,depth=.62,location=self.pt(x,y,z+.46));o=bpy.context.object;o.name='Cone / tapered orange body';o.data.materials.append(self.orange)
        for zz,rr in [(z+.35,.166),(z+.55,.113)]:
            bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=rr+.013,radius2=rr-.013,depth=.10,location=self.pt(x,y,zz));o=bpy.context.object;o.name='Cone / reflective white band';o.data.materials.append(self.white)
    def plant(self,x,y,z=0,scale=1):
        bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.19*scale,radius2=.27*scale,depth=.37*scale,location=self.pt(x,y,z+.185*scale));o=bpy.context.object;o.name='Ornamental plant / terracotta pot';o.data.materials.append(self.brick)
        self.cyl('Pot / rolled lip',x,y,z+.35*scale,.28*scale,.07*scale,self.brick)
        self.cyl('Pot / soil',x,y,z+.38*scale,.245*scale,.02*scale,self.soil)
        for i in range(24):
            a=i*2.39996;r=(.34+.15*(i%3))*scale;h=(.55+.12*(i%4))*scale
            ux,uy=math.cos(a),math.sin(a);nx,ny=-uy*.065*scale,ux*.065*scale
            base=(x,y,z+.36*scale);mid=(x+ux*r*.5,y+uy*r*.5,z+h)
            tip=(x+ux*r,y+uy*r,z+h*.8)
            pts=[base,(mid[0]+nx,mid[1]+ny,mid[2]),tip,(mid[0]-nx,mid[1]-ny,mid[2]),(mid[0],mid[1],mid[2]+.04)]
            self.mesh('Ornamental plant / pointed folded leaf',pts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],self.leaf if i%3 else self.green)
    def palm(self,x,y,z=0):
        self.cyl('Palm / garden soil bed',x,y,z+.06,.39,.11,self.soil)
        for i in range(10):
            self.cyl('Palm / trunk segment',x+.025*math.sin(i*.3),y,z+.12+i*.10,.09-i*.003,.12,self.wood)
        crown=z+1.13
        for j in range(10):
            a=j*math.tau/10;dx,dy=math.cos(a),math.sin(a);reach=.85 if j%2 else .72
            path=[]
            for i in range(10):
                t=i/9;path.append((x+dx*t*reach,y+dy*t*reach,crown+.32*math.sin(t*math.pi)-.2*t))
            self.line('Palm / curved frond midrib',path,.016,self.green)
            for i in range(1,9):
                t=i/9;xx,yy,zz=path[i];length=.22*math.sin(t*math.pi)+.05
                for sign in [-1,1]:
                    tip=(xx-dy*length*sign+dx*.10,yy+dx*length*sign+dy*.10,zz-.08)
                    self.mesh('Palm / linked style narrow leaflet',[(xx,yy,zz),(xx+dx*.06,yy+dy*.06,zz+.02),tip],[(0,1,2)],self.leaf if i%2 else self.green)
    def wheelbarrow(self,x,y,z=0):
        # Open steel tray: tapered bottom and flared upper edges.
        pts=[(x-.25,y-.45,z+.45),(x+.25,y-.45,z+.45),(x+.25,y+.35,z+.45),(x-.25,y+.35,z+.45),
             (x-.47,y-.62,z+.82),(x+.47,y-.62,z+.82),(x+.42,y+.52,z+.82),(x-.42,y+.52,z+.82)]
        o=self.mesh('Wheelbarrow / open blue steel tub',pts,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],self.blue)
        solid=o.modifiers.new('Tray sheet metal','SOLIDIFY');solid.thickness=.025
        self.line('Wheelbarrow / rolled tray lip',[pts[i] for i in [4,5,6,7,4]],.03,self.blue)
        for xx in [-.3,.3]:
            self.line('Wheelbarrow / tubular handle',[(x+xx,y-1.12,z+.73),(x+xx,y+.65,z+.27)],.04,self.steel)
            self.line('Wheelbarrow / black handle grip',[(x+xx,y-1.12,z+.73),(x+xx,y-.89,z+.67)],.06,self.black)
            self.line('Wheelbarrow / support leg',[(x+xx,y-.25,z+.47),(x+xx,y-.15,z+.06),(x+xx,y+.1,z+.06),(x+xx,y+.25,z+.46)],.035,self.steel)
        bpy.ops.mesh.primitive_torus_add(major_radius=.20,minor_radius=.07,major_segments=32,minor_segments=12,location=self.pt(x,y+.70,z+.26),rotation=(0,math.pi/2,0));o=bpy.context.object;o.name='Wheelbarrow / rubber tire';o.data.materials.append(self.black)
        hub=self.cyl('Wheelbarrow / steel wheel hub',x,y+.70,z+.26,.14,.13,self.steel);hub.rotation_euler.y=math.pi/2
        for i in range(95):
            xx=x+random.uniform(-.32,.32);yy=y+random.uniform(-.42,.35)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.035,.075),location=self.pt(xx,yy,z+.70+random.uniform(0,.07)));o=bpy.context.object;o.name='Wheelbarrow / angular gravel';o.scale.z=.65;o.data.materials.append(self.concrete)
    def hand_tools(self,x,y,z=.7):
        self.line('Hammer / wooden handle',[(x-.12,y-.22,z),(x+.15,y+.22,z)],.035,self.wood)
        head=self.cube('Hammer / steel head',x-.12,y-.22,z,.31,.09,.10,self.steel);head.rotation_euler.z=-.45
        self.line('Wrench / steel shaft',[(x+.15,y-.18,z+.03),(x+.4,y+.22,z+.03)],.035,self.steel)
        self.cyl('Wrench / ring head',x+.4,y+.22,z+.03,.075,.04,self.steel)
        self.line('Screwdriver / steel shaft',[(x+.3,y-.18,z+.08),(x+.55,y-.1,z+.08)],.012,self.steel)
        self.line('Screwdriver / yellow grip',[(x+.55,y-.1,z+.08),(x+.70,y-.05,z+.08)],.035,self.gold)
