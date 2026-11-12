"""Verify saved native monster assets and preserve the review level."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
A=unreal.EditorAssetLibrary
SS=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
report=json.loads((B/'Saved/monster_import_v05.json').read_text())
assert report['stage']=='complete' and len(report['models'])==9
assert report['animation_count']==45
assert not report['errors'],report['errors']
manifest_path=B/'ArtSource/Monsters/Models_v05/model_manifest.json'
manifest=json.loads(manifest_path.read_text());source_models={m['id']:m for m in manifest['models']}
rows=[]
for row in report['models']:
    mesh=unreal.load_asset(row['asset'])
    assert isinstance(mesh,unreal.SkeletalMesh)
    assert SS.get_lod_count(mesh)==3,(row['id'],'LOD count')
    verts=[SS.get_num_verts(mesh,i) for i in range(3)]
    assert verts[0]>=verts[1]>=verts[2]>0,(row['id'],verts)
    assert all(s.get_editor_property('material_interface') for s in mesh.get_editor_property('materials'))
    spec=source_models[row['id']]
    expected=unreal.load_asset('/Game/IsekaiVillage/Monsters/Refined_v05/Textures/'+Path(spec['authored_color_texture']).stem)
    assert isinstance(expected,unreal.Texture2D),(row['id'],'missing authored color map')
    for slot,source in zip(mesh.get_editor_property('materials'),spec['materials']):
        if source['name'].startswith('EyeExisting'):continue
        parameter='CreaturePaint' if source['name'].endswith('Skin') else 'Palette'
        material=slot.get_editor_property('material_interface')
        assert unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(material,parameter)==expected,(row['id'],source['name'],'wrong unique surface map')
    sk=mesh.get_editor_property('skeleton')
    for kind,path in row['animations'].items():
        an=unreal.load_asset(path)
        assert isinstance(an,unreal.AnimSequence) and an.get_editor_property('skeleton')==sk
        assert A.does_asset_exist(path)
    rows.append({'id':row['id'],'lod_vertices':verts,'clips':len(row['animations']),'authored_material_assignments':True})
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.EditorLevelLibrary.eject_pilot_level_actor()
eye=unreal.Vector(1700,3300,1500)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,650,110)))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,report['review_map'])
out={'passed':True,'models':9,'clips':45,'review_map':report['review_map'],'details':rows}
(B/'Saved/monster_unreal_validation_v05.json').write_text(json.dumps(out,indent=2))
manifest['unreal_import']='verified: 9 skeletal meshes, 45 animation sequences, 3 LODs each, individual surface maps assigned';manifest['review_map']=report['review_map'];manifest_path.write_text(json.dumps(manifest,indent=2))
unreal.log('MONSTER_UNREAL_VALIDATION_PASSED 9 45')

