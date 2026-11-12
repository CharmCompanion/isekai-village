"""Recoverable Gosain kingdom conversion. Imports before changing the level."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain51';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain51'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();M=unreal.MaterialEditingLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert (O/'applied.json').exists()
assert not (O/'refined.json').exists()
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN50 '+s)
actors=E.get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
terrain=bymesh('SM_IV_Continent_GosainKingdom51')
pairs=[(bymesh('SM_Gosain51_RoyalLake'),'SM_Gosain51_RoyalLakeRefined')]
lake=unreal.load_asset('/Game/AdvancedVillagePack/Materials/M_Inst_Water');assert lake
def loadmesh(name,mats,single=None,collision=False):
    if A.does_asset_exist(D+'/Meshes/'+name):return unreal.load_asset(D+'/Meshes/'+name)
    status('importing '+name);task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
    T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
    slots=list(mesh.static_materials)
    for s in slots:s.set_editor_property('material_interface',single if single else mats[str(s.material_slot_name)])
    mesh.set_editor_property('static_materials',slots)
    if collision:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    A.save_loaded_asset(mesh);return mesh

new={}
for actor,name in pairs:
 old=actor.static_mesh_component.static_mesh
 mats={str(v.material_slot_name):v.material_interface for v in old.static_materials}
 new[name]=loadmesh(name,mats,actor.static_mesh_component.get_material(0) if actor==terrain or name.endswith('RoyalLake') else None,actor==terrain)
waterpath=D+'/Materials/MI_Gosain51_RoyalLake'
water=unreal.load_asset(waterpath) if A.does_asset_exist(waterpath) else A.duplicate_asset('/Game/AdvancedVillagePack/Materials/M_Inst_Water',waterpath)
M.set_material_instance_vector_parameter_value(water,'BaseColor',unreal.LinearColor(.025,.15,.19,1))
M.set_material_instance_vector_parameter_value(water,'FresnelColor',unreal.LinearColor(.07,.26,.23,1))
A.save_loaded_asset(water)
oldwater=pairs[0][0].static_mesh_component.get_material(0)
backup=B/'Saved/WorldBackups'/('BeforeGosain51_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
plans=json.loads((O/'foliage_changes.json').read_text())
components={c.get_name():c for a in E.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)}
def transform(row):
 return unreal.Transform(location=unreal.Vector(*row[:3]),rotation=unreal.Quat(*row[3:7]).rotator(),scale=unreal.Vector(*row[7:10]))
changes=[]
for p in plans:
 ft=unreal.load_asset(p['foliage_type']);assert ft,p['foliage_type']
 matching=[c for c in components.values() if c.static_mesh==ft.get_editor_property('mesh')]
 assert len(matching)==1,(p['foliage_type'],len(matching))
 c=matching[0];assert c.get_instance_count()==p['old_count']
 old=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())]
 changes.append((ft,old,[transform(r) for r in p['new']]))
rollback=[(a,a.static_mesh_component.static_mesh) for a,n in pairs]
try:
 for a,n in pairs:a.static_mesh_component.set_static_mesh(new[n])
 pairs[0][0].static_mesh_component.set_material(0,water)
 for ft,old,rows in changes:
  unreal.InstancedFoliageActor.remove_all_instances(W,ft)
  unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for a,m in rollback:a.static_mesh_component.set_static_mesh(m)
 pairs[0][0].static_mesh_component.set_material(0,oldwater)
 for ft,old,rows in changes:
  unreal.InstancedFoliageActor.remove_all_instances(W,ft)
  unreal.InstancedFoliageActor.add_instances(W,ft,old)
 raise
(O/'refined.json').write_text(json.dumps({'status':'saved','backup':str(backup),'meshes':[n for a,n in pairs],'foliage_types_updated':len(changes),'native_review':'pending'},indent=2))

