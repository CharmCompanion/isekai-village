"""Unique authored UV/color/AO maps; keeps the existing UV0 normal and skin maps."""
import bpy,json,sys
import numpy as np
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v05')
manifest=json.loads((root/'model_manifest.json').read_text())
only=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for model in manifest['models']:
    name=model['id']
    if only and name not in only:continue
    if model.get('authored_color_texture') and Path(model['authored_color_texture']).exists():
        print('AUTHORED_SURFACE_ALREADY_SAVED',name,flush=True);continue
    bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
    mesh=bpy.data.objects['SK_'+name];arm=mesh.parent
    for o in bpy.data.objects:o.hide_render=o!=mesh
    mesh.hide_render=False;mesh.hide_set(False)
    arm.animation_data.action=None
    for p in arm.pose.bones:p.rotation_euler=(0,0,0);p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
    bpy.context.scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
    original=mesh.data.uv_layers[0].name
    if mesh.data.uv_layers.get('AuthoredSurface'):mesh.data.uv_layers.remove(mesh.data.uv_layers['AuthoredSurface'])
    uv=mesh.data.uv_layers.new(name='AuthoredSurface');mesh.data.uv_layers.active=uv
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.003,area_weight=.8)
    bpy.ops.object.mode_set(mode='OBJECT')
    color=bpy.data.images.new('T_IV_'+name+'_Authored_v05',2048,2048,alpha=True)
    ao=bpy.data.images.new('AO_'+name,2048,2048,alpha=True);ao.colorspace_settings.name='Non-Color'
    nodes=[]
    for mat in mesh.data.materials:
        if not mat.use_nodes:continue
        nt=mat.node_tree;uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map=original
        for n in list(nt.nodes):
            if n.type=='TEX_IMAGE':nt.links.new(uvnode.outputs['UV'],n.inputs['Vector'])
        active=nt.nodes.new('ShaderNodeTexImage');active.image=color;nt.nodes.active=active;nodes.append((mat,active))
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.bake.margin=10
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    bpy.ops.object.bake(type='DIFFUSE')
    for mat,n in nodes:n.image=ao;mat.node_tree.nodes.active=n
    bpy.ops.object.bake(type='AO')
    rgb=np.empty(2048*2048*4,dtype=np.float32);occlusion=np.empty_like(rgb)
    color.pixels.foreach_get(rgb);ao.pixels.foreach_get(occlusion)
    rgb=rgb.reshape(-1,4);occlusion=occlusion.reshape(-1,4)
    rgb[:,:3]*=(.72+.28*np.clip(occlusion[:,:3],0,1))
    color.pixels.foreach_set(rgb.ravel());color.filepath_raw=str(root/'Textures'/(color.name+'.png'));color.file_format='PNG';color.save()
    for mat,n in nodes:
        n.image=color;uvnode=mat.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='AuthoredSurface'
        mat.node_tree.links.new(uvnode.outputs['UV'],n.inputs['Vector'])
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:mat.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
    mesh.data.uv_layers.active_index=0
    for i,u in enumerate(mesh.data.uv_layers):u.active_render=i==0
    # Keep legacy skeleton and animation settings while exporting the new second UV channel.
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm
    bpy.ops.export_scene.fbx(filepath=model['fbx'],use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,use_armature_deform_only=False,mesh_smooth_type='FACE',bake_anim=False)
    model['authored_color_texture']=str(color.filepath_raw);model['authored_color_uv_channel']=1
    model['surface_bake']='2048 diffuse color and restrained geometry AO; original normals on UV0'
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/(name+'.blend')))
    (root/'model_manifest.json').write_text(json.dumps(manifest,indent=2));print('AUTHORED_SURFACE_COMPLETE',name,flush=True)
print('SURFACE_BAKE_COMPLETE',flush=True)
