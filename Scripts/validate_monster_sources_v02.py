"""Check actual skinned deformations in the saved Blender model sources."""
import bpy,json,math
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v02')
manifest=json.loads((root/'model_manifest.json').read_text());rows=[]
for model in manifest['models']:
    name=model['id'];bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
    obj=bpy.data.objects.get('SK_'+name);arm=next(m.object for m in obj.modifiers if m.type=='ARMATURE');scene=bpy.context.scene
    assert len([b for b in arm.data.bones if b.parent is None])==1,(name,'multiple rig roots')
    row={'id':name,'root_count':1,'clips':{},'weights_valid':True}
    assert max(abs(arm.matrix_world[i][i]-1) for i in range(3))<.001,(name,'unapplied rig scale')
    head_height=(arm.matrix_world@arm.data.bones['head'].head_local).z if 'head' in arm.data.bones else None
    if model['family']=='Goblin':assert 1.0<head_height<1.35,(name,'incorrect goblin units',head_height)
    if model['family']=='Ogre':assert 2.4<head_height<3.1,(name,'incorrect ogre units',head_height)
    assert len(obj.data.uv_layers)==1,(name,'inconsistent accessory UV layers')
    uv=obj.data.uv_layers.active.data
    for p in obj.data.polygons:
        spec=model['materials'][p.material_index];cell=spec['palette_index']
        if cell is not None:
            for li in p.loop_indices:
                u,v=uv[li].uv
                assert int(u*8)==cell%8 and int(v*4)==cell//8,(name,spec['name'],'wrong texture tile')
    for v in obj.data.vertices:
        assert abs(sum(g.weight for g in v.groups)-1)<.01,(name,v.index,'weights')
        assert all(obj.vertex_groups[g.group].name in arm.data.bones for g in v.groups),(name,v.index,'unknown bone')
    for kind in model['animations']:
        action=bpy.data.actions.get('AN_'+name+'_'+kind);assert action,(name,kind)
        arm.animation_data.action=action;checks=[]
        frames=int(action.frame_range[1]);frames=max(frames,2)
        for frame in [1,max(1,frames//2),frames]:
            scene.frame_set(frame);dep=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(dep);mesh=evaluated.to_mesh();verts=[evaluated.matrix_world@v.co for v in mesh.vertices]
            assert all(math.isfinite(c) for v in verts for c in v),(name,kind,frame,'invalid deformation')
            low=[min(v[a] for v in verts) for a in range(3)];high=[max(v[a] for v in verts) for a in range(3)]
            assert max(high[a]-low[a] for a in range(3))<8,(name,kind,frame,'exploded rig')
            checks.append({'frame':frame,'min':low,'max':high});evaluated.to_mesh_clear()
        row['clips'][kind]=checks
    for kind in model['animations']:assert (root/'FBX'/name/('AN_'+name+'_'+kind+'.fbx')).stat().st_size>1000
    rows.append(row)
(root/'source_validation.json').write_text(json.dumps({'passed':True,'models_checked':len(rows),'clips_checked':sum(len(r['clips']) for r in rows),'checks':rows},indent=2));print('MONSTER_SOURCE_VALIDATION_PASSED',len(rows))

