"""Resolve trim separation introduced when tapering the authored cuirass."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v05')
manifest=json.loads((root/'model_manifest.json').read_text());records=[]
for model in manifest['models']:
    if model['id'] not in ['SkeletonKnight','OgreChampion']:continue
    name=model['id'];original=root/(name+'_before_trim_v05.blend')
    if not original.exists():
        import shutil
        shutil.copy2(root/(name+'.blend1'),original)
    bpy.ops.wm.open_mainfile(filepath=str(original))
    mesh=bpy.data.objects['SK_'+name];arm=mesh.parent;gi=mesh.vertex_groups['spine_04'].index
    def weighted(i):return any(g.group==gi and g.weight>.9 for g in mesh.data.vertices[i].groups)
    faces=[list(p.vertices) for p in mesh.data.polygons if mesh.data.materials[p.material_index].name=='Steel' and all(weighted(i) for i in p.vertices)]
    tree=BVHTree.FromPolygons([v.co for v in mesh.data.vertices],faces)
    selected={i for p in mesh.data.polygons if mesh.data.materials[p.material_index].name=='Gold' for i in p.vertices if weighted(i)}
    # Preserve round trim cross-sections. Move the old borders with exactly the
    # same taper/keel field as the cuirass; newly authored small inlays stay put.
    neighbors={i:set() for i in selected}
    for e in mesh.data.edges:
        a,b=e.vertices
        if a in selected and b in selected:neighbors[a].add(b);neighbors[b].add(a)
    seen=set();changed=0;og=name.startswith('Ogre');cz=arm.data.bones['spine_04'].head_local.z
    for first in selected:
        if first in seen:continue
        component=set();todo=[first]
        while todo:
            i=todo.pop()
            if i in seen:continue
            seen.add(i);component.add(i);todo.extend(neighbors[i]-seen)
        if len(component)<35:continue
        for i in component:
            v=mesh.data.vertices[i];t=max(0,min(1,(v.co.z-(cz-.20))/(.54 if og else .30)))
            v.co.x*=.80+.20*t
            v.co.y-=((.026 if og else .010)*max(0,1-abs(v.co.x)/(.42 if og else .15)))
            changed+=1
    mesh.data.update()
    arm.animation_data.action=None
    for b in arm.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
    bpy.context.scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm
    bpy.ops.export_scene.fbx(filepath=model['fbx'],use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,use_armature_deform_only=False,mesh_smooth_type='FACE',bake_anim=False)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/(name+'.blend')))
    records.append({'id':name,'fitted_trim_vertices':changed,'weights_uvs_actions':'preserved'})
(root/'armor_trim_fit.json').write_text(json.dumps(records,indent=2));print('ARMOR_TRIM_FIT_COMPLETE',records)
