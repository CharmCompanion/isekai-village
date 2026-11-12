"""Coordinated Gosain-only relief update; prepare every asset before scene mutation."""
import unreal,json,shutil
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain43';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain43'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
report={'stage':'preflight'}
def status(s):
    report['stage']=s;(O/'apply_progress.json').write_text(json.dumps(report,indent=2));unreal.log('GOSAIN43 '+s)
actors=E.get_all_level_actors();components={c.get_name():c for a in actors for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)}
plans=[]
for q in json.loads((O/'foliage_moves.json').read_text()):
    c=components[q['component']];ft=unreal.load_asset(q['foliage_type']);assert ft and ft.get_editor_property('mesh')==c.static_mesh
    assert c.get_instance_count()==q['count']
    old=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())];new=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())]
    for i,dz in zip(q['indices'],q['delta_cm']):
        p=new[i].translation;new[i].translation=unreal.Vector(p.x,p.y,p.z+dz)
    plans.append((ft,old,new))
entries=json.loads((O/'structure_sources.json').read_text());entries.append({'old_name':'SM_IV_Continent_GosainRelief40','name':'SM_IV_Continent_GosainTerraces43'})
for q in json.loads((O/'defenses.json').read_text())['meshes']:entries.append({'old_name':q['name'].replace('Gosain43','Gosain40'),'name':q['name']})
replacements=[]
for q in entries:
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==q['old_name']]
    assert len(found)==1,(q['old_name'],len(found));a=found[0];replacements.append([a,a.static_mesh_component.static_mesh,q])
backup=B/'Saved/WorldBackups/BeforeGosain43_20261016';backup.mkdir(exist_ok=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
for a,old,q in replacements:
    name=q['name'];status('importing '+name);task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
    T.import_asset_tasks([task]);m=unreal.load_asset(D+'/Meshes/'+name);assert m,name
    slots={str(s.material_slot_name):s.material_interface for s in old.static_materials}
    updated=list(m.static_materials)
    for i,s in enumerate(updated):
        if len(old.static_materials)==1:mat=old.static_materials[0].material_interface
        else:assert str(s.material_slot_name) in slots,(name,str(s.material_slot_name),list(slots));mat=slots[str(s.material_slot_name)]
        s.set_editor_property('material_interface',mat)
        updated[i]=s
    m.set_editor_property('static_materials',updated)
    A.save_loaded_asset(m);q['new_mesh']=m
status('assets prepared; applying coordinated terrain and placements')
try:
    for a,old,q in replacements:a.static_mesh_component.set_static_mesh(q['new_mesh'])
    for ft,old,new in plans:
        unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,new)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    for a,old,q in replacements:a.static_mesh_component.set_static_mesh(old)
    for ft,old,new in plans:
        unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,old)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();raise
result={'status':'saved','meshes':[{'actor':a.get_name(),'old':old.get_path_name(),'new':q['new_mesh'].get_path_name()} for a,old,q in replacements],'foliage_types':len(plans),'backup':str(backup),'validation':'pending'}
(O/'applied.json').write_text(json.dumps(result,indent=2));status('saved')
