"""Render an individual layer of the saved editable scene, reusing geometry.
blender -b games/pinball/blender/ferrisariato-pinball.blend -t 4 \
  --python games/pinball/blender/render_existing.py -- interactives
"""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
selected=args[0]
scene=bpy.context.scene
layers={'interactives':bpy.data.collections['Interactive bumper tank target sling art'],
        'foreground':bpy.data.collections['Foreground decorative raised channels']}
dynamic=bpy.data.collections['Movable elements'];dynamic.hide_render=True
for name in (['table','interactives','foreground'] if selected=='all' else [selected]):
    if name not in ['table',*layers]:raise ValueError('Unknown layer: '+name)
    layers['interactives'].hide_render=name=='table'
    layers['foreground'].hide_render=name!='foreground'
    hidden=[]
    if name!='table':
        for o in scene.objects:
            if o.type not in {'LIGHT','CAMERA'} and o.name not in layers[name].objects and hasattr(o,'visible_camera'):
                hidden.append(o);o.visible_camera=False
    scene.render.filepath=str(ROOT/'assets'/(name+'.png'));bpy.ops.render.render(write_still=True)
    for o in hidden:o.visible_camera=True
print('LAYER_RENDER_COMPLETE')
