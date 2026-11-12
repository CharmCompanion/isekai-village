import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
report={}
for name in ['M_IV_MonsterSurface_v01','M_IV_MonsterGel_v01']:
    mat=unreal.load_asset('/Game/IsekaiVillage/Monsters/Materials/'+name)
    report[name]={'usage_before':mat.get_editor_property('used_with_skeletal_mesh')}
    mat.set_editor_property('used_with_skeletal_mesh',True)
    if 'Gel' in name:
        mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    M.recompile_material(mat);A.save_loaded_asset(mat)
manifest=json.loads((B/'ArtSource/Monsters/Models_v01/model_manifest.json').read_text())
for model in manifest['models']:
    mesh=unreal.load_asset('/Game/IsekaiVillage/Monsters/'+model['family']+'/SK_'+model['id'])
    slots=mesh.get_editor_property('materials')
    for i,spec in enumerate(model['materials']):
        path='/Game/StylizedCharacters/BodyA/Eyes/Eyes_01/MI_Eyes_01_a' if spec['name'].startswith('EyeExisting') else '/Game/IsekaiVillage/Monsters/Materials/MI_IV_'+spec['name']+'_v01'
        material=unreal.load_asset(path);assert material,path
        slot=slots[i];slot.set_editor_property('material_interface',material);slots[i]=slot
    mesh.set_editor_property('materials',slots);A.save_loaded_asset(mesh)
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(actor,unreal.SkeletalMeshActor):
        comp=actor.get_editor_property('skeletal_mesh_component')
        comp.set_forced_lod(1)
        report[actor.get_actor_label()]=[comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())]
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for cmd in ['viewmode lit','ShowFlag.LightingOnlyOverride 0','ShowFlag.OverrideDiffuseAndSpecular 0','ShowFlag.Materials 1']:
    unreal.SystemLibrary.execute_console_command(world,cmd)
(B/'Saved/monster_material_check.json').write_text(json.dumps(report,indent=2))
exec(compile((B/'Scripts/render_monsters_unreal_v01.py').read_text(),'native monster previews','exec'),{'__name__':'__main__'})
