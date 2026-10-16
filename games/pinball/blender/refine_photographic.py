"""Second visual review: glazing, mounted cabinet edges, target artwork."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector

def refine(g):
    globals().update({k:v for k,v in g.items() if not k.startswith('__')})
    scene=bpy.context.scene
    # Anti-reflection coated glass, photographed through a polarizer: retain
    # softbox reflections at 10% intensity so the ball remains clearly visible.
    m=bpy.data.materials['Protective glass / thin pane Fresnel'];n=m.node_tree.nodes;l=m.node_tree.links
    fres=next(o for o in n if o.type=='FRESNEL');mix=next(o for o in n if o.type=='MIX_SHADER')
    attenuation=n.new('ShaderNodeMath');attenuation.operation='MULTIPLY';attenuation.inputs[1].default_value=.10;l.new(fres.outputs[0],attenuation.inputs[0]);l.new(attenuation.outputs[0],mix.inputs[0])
    # Refit the glass to a sloped upper cabinet, clear of the tallest house/ramps.
    # Move visual cover vertices only; functional camera and guides are untouched.
    for o in cover.objects:
        if o.type=='MESH':
            if o.name.startswith('Protective glass / uninterrupted'):
                for v in o.data.vertices:v.co.z=3.0-.13*(8-v.co.y)
            else:o.location.z+=3.0-.13*(8-o.location.y)-2.72
        elif o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:p.co.z+=3.0-.13*(8-p.co.y)-2.72
    for x in [.43,9.7]:
        pts=[pt(x,.35,.35),pt(x,15.72,.35),pt(x,15.72,.91),pt(x,.35,2.95)]
        mesh=bpy.data.meshes.new('Cabinet sloped side cheek');mesh.from_pydata(pts,[],[(0,1,2,3)]);mesh.update()
        obj=bpy.data.objects.new('Cabinet / glazed cover mounting cheek',mesh);cover.objects.link(obj);mesh.materials.append(blue)
        solid=obj.modifiers.new('Folded sheet thickness','SOLIDIFY');solid.thickness=.035
        for y in [.42,15.60]:
            line('Cabinet / glass corner bracket',[(x,y,.35),(x,y,3-.13*y)],.028,steel,cover)
    # Softer mineral variation retains pores without a camouflage-like pattern.
    nodes=floor.node_tree.nodes
    ramp=next(o for o in nodes if o.type=='VALTORGB')
    ramp.color_ramp.elements[0].color=(.17,.18,.18,1);ramp.color_ramp.elements[1].color=(.31,.32,.30,1)
    for o in nodes:
        if o.type=='TEX_NOISE' and o.inputs['Scale'].default_value==5:o.inputs['Scale'].default_value=9
    # Printed lacquered halo graphics occupy empty gray areas, entirely flush.
    for b in DATA['bumpers']:
        x,y,r=b['x'],b['y'],b['radius']
        for j in range(24):
            a=j*math.tau/24;end=a+math.tau/24*.87
            vertices=[(x+rr*math.cos(t),y+rr*math.sin(t)) for rr,t in [(r+.29,a),(r+.41,a),(r+.41,end),(r+.29,end)]]
            o=polygon('Playfield / printed bumper halo',vertices,.037,gold if j%4==0 else blue)
            for c in list(o.users_collection):c.objects.unlink(o)
            photo.objects.link(o)
    # Same category paths as the live canvas, placed on physical target faces.
    paths=[
      [[(-10+c*7+(row%2)*3.5,-9+row*6),(-4+c*7+(row%2)*3.5,-9+row*6),(-4+c*7+(row%2)*3.5,-4+row*6),(-10+c*7+(row%2)*3.5,-4+row*6)] for row in range(3) for c in range(3) if -10+c*7+(row%2)*3.5<8],
      [[(-8,9),(2,-1),(5,-1),(10,-6),(9,-10),(5,-6),(2,-8),(6,-12),(1,-12),(-3,-8),(-3,-4),(-11,6)]],
      [[(-10,-10),(6,-10),(6,-3),(-10,-3)],[(6,-8),(10,-8),(10,0),(0,0),(0,11)]],
      [[(1,-12),(-8,1),(-1,1),(-5,13),(9,-3),(2,-3),(7,-12)]],
      [[(-10,2),(-6,2),(-6,-3),(4,-3),(4,3),(10,3),(10,8)],[(-6,-3),(-6,-7)],[(-10,-7),(-2,-7)]],
      [[(-9,10),(-12,0),(-6,-6),(11,-12),(8,4),(2,10)]],
      [[(-12,-9),(-8,-9),(-4,5),(8,5),(11,-5),(-7,-5)]]]
    for idx,target in enumerate(DATA['targets']):
        x,y=target['x'],target['y'];z=.49
        for k,path in enumerate(paths[idx]):
            pts=[pt(x+xx*.020,y+.237,z-zz*.020) for xx,zz in path]
            fill=idx in [0,1,3,5] or idx==2 and k==0
            if fill:
                mesh=bpy.data.meshes.new('Category symbol');mesh.from_pydata(pts,[],[list(range(len(pts)))]);mesh.update()
                obj=bpy.data.objects.new('Target / engraved category '+str(idx),mesh);interactive.objects.link(obj);mesh.materials.append(leaf if idx==5 else white if idx==2 else gold)
            else:line('Target / category line '+str(idx),[(p[0]+5,8-p[1],p[2]) for p in pts],.016,gold,interactive)
        if idx==6:
            for dx in [-.06,.14]:sphere('Target / cart wheel',x+dx,y+.244,z-.2,.034,gold,interactive)
    scene['photographic_pass']='2.1'

if __name__=='__main__':
    # Reuse geometry helpers/material names from the base source, no reset.
    import ast
    ROOT=Path(__file__).resolve().parents[1]
    source=ast.parse((ROOT/'blender/generate.py').read_text())
    scene=bpy.context.scene
    for node in source.body:
        if isinstance(node,ast.FunctionDef) and node.name in {'mat','place','pt','bevel','cube','cyl','sphere','line','polygon'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
    for k,name in {'blue':'Ferrisariato cobalt enamel','gold':'Safety yellow enamel','steel':'Polished chrome','floor':'Mineral concrete','leaf':'Palm leaf light side','white':'Ivory paint'}.items():globals()[k]=bpy.data.materials[name]
    cover=bpy.data.collections['Protective glass reflections'];interactive=bpy.data.collections['Interactive bumper tank target sling art'];photo=bpy.data.collections['Photographic workshop miniatures'];DATA=json.loads((ROOT/'layout.json').read_text())
    refine(dict(globals()))
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/ferrisariato-photographic.blend'))
