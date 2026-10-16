"""Render preview/hero/web layers/ball from the enhanced scene with external OIDN.
PINBALL_PYTHON and OIDN_BIN can override external tools. Raw EXRs stay in /tmp.
"""
import bpy,sys,os,subprocess,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['preview']
mode=args[0];scene=bpy.context.scene
layers={'interactives':bpy.data.collections['Interactive bumper tank target sling art'],'foreground':bpy.data.collections['Foreground decorative raised channels'],'glass':bpy.data.collections['Protective glass reflections']}
dynamic=bpy.data.collections['Movable elements']
work=Path('/tmp/ferrisariato-premium');work.mkdir(exist_ok=True)
scene.view_layers[0].cycles.denoising_store_passes=True
scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';scene.use_nodes=False
post=bpy.data.scenes.new('Photographic export compositor');post.render.engine='CYCLES';post.cycles.samples=1;post.cycles.use_denoising=False;post.render.film_transparent=True
post.render.threads_mode='FIXED';post.render.threads=5
camdata=bpy.data.cameras.new('Export camera');cam=bpy.data.objects.new('Export camera',camdata);post.collection.objects.link(cam);post.camera=cam
post.view_settings.view_transform='AgX';post.view_settings.look='AgX - Medium High Contrast';post.view_settings.exposure=scene.view_settings.exposure
post.use_nodes=True;n=post.node_tree.nodes;n.clear();im=n.new('CompositorNodeImage');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2;gl.size=7;gl.mix=-.93
out=n.new('CompositorNodeComposite');background=n.new('CompositorNodeAlphaOver');background.inputs[1].default_value=(.003,.008,.017,1);post.node_tree.links.new(im.outputs[0],background.inputs[2]);post.node_tree.links.new(im.outputs[0],gl.inputs[0]);post.node_tree.links.new(gl.outputs[0],out.inputs[0])
post.render.image_settings.file_format='PNG';post.render.image_settings.color_mode='RGBA';post.render.resolution_percentage=100
selected=['table','interactives','foreground','glass','ball'] if mode=='web' else [mode]
for name in selected:
    hero=name in {'hero','preview'};ball=name=='ball'
    scene.render.resolution_x=1760 if name=='hero' else 660 if name=='preview' else 128 if ball else 880
    scene.render.resolution_y=2200 if name=='hero' else 825 if name=='preview' else 128 if ball else 1100
    scene.render.resolution_percentage=100;scene.cycles.samples=int(os.environ.get('PINBALL_SAMPLES',96 if name=='hero' else 32 if name=='preview' else 64))
    dynamic.hide_render=not(hero or ball)
    for key,collection in layers.items():collection.hide_render=not(hero or key==name or name=='ball')
    # Preserve bumper AND ramp shadows/reflections in the static layer.
    # Camera-invisible raised channels still occlude light on the props below.
    if name=='table':
        layers['interactives'].hide_render=False
        layers['foreground'].hide_render=False
    holdouts=[]
    use_holdout=name=='foreground'
    if use_holdout:layers['interactives'].hide_render=False
    hidden=[]
    if not hero:
        keep=set(layers[name].objects) if name in layers else set()
        if ball:keep={bpy.data.objects['Editable chrome ball']}
        for o in scene.objects:
            if o.type in {'LIGHT','CAMERA'} or not hasattr(o,'visible_camera'):continue
            hide=any(o.name in layers[k].objects for k in ['interactives','foreground']) if name=='table' else o not in keep
            if hide and o.visible_camera:
                if use_holdout:o.is_holdout=True;holdouts.append(o)
                else:hidden.append(o);o.visible_camera=False
    original_camera=scene.camera
    if ball:
        b=bpy.data.objects['Editable chrome ball'];data=original_camera.data.copy();data.type='ORTHO';data.ortho_scale=.37;data.shift_x=0;data.shift_y=0
        camera=bpy.data.objects.new('Ball sprite export camera',data);scene.collection.objects.link(camera)
        camera.rotation_euler=original_camera.rotation_euler;direction=original_camera.rotation_euler.to_quaternion()@Vector((0,0,1));camera.location=b.location+direction*3;scene.camera=camera
    raw=work/(name+'-raw.exr');clean=work/(name+'-clean.exr');scene.render.filepath=str(raw)
    bpy.ops.render.render(write_still=True,scene=scene.name)
    env=os.environ.copy();env['PYTHONPATH']=os.environ.get('PINBALL_PYTHONPATH','/workspace/.cache/ferrisariato-python');env['OIDN_BIN']=os.environ.get('OIDN_BIN','/workspace/.cache/oidn-2.3.3.x86_64.linux/bin/oidnDenoise')
    subprocess.run([os.environ.get('PINBALL_PYTHON',shutil.which('python3')),str(ROOT/'scripts/denoise.py'),str(raw),str(clean)],check=True,env=env)
    im.image=bpy.data.images.load(str(clean));post.node_tree.links.new(background.outputs[0] if hero else im.outputs[0],gl.inputs[0]);post.render.resolution_x=scene.render.resolution_x;post.render.resolution_y=scene.render.resolution_y
    # Preserve alpha for overlay layers; glare is already physically bright in the base.
    gl.mix=-1 if name in {'glass','ball','interactives','foreground'} else -.93
    dest=ROOT/'docs'/('premium-'+name+'.png') if hero else Path(os.environ.get('PINBALL_ASSET_STAGE',str(ROOT/'assets')))/(name+'.png')
    post.render.filepath=str(dest);bpy.ops.render.render(write_still=True,scene=post.name)
    for o in hidden:o.visible_camera=True
    for o in holdouts:o.is_holdout=False
    scene.camera=original_camera
    print('PHOTOGRAPHIC_RENDER_COMPLETE',name,flush=True)
