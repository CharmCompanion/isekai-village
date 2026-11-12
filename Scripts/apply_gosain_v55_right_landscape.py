"""Recoverable Gosain kingdom conversion. Imports before changing the level."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain55';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain55'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();M=unreal.MaterialEditingLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
assert json.loads((O/'countryside_report.json').read_text())['mine_route_max_grade'] < .15
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN50 '+s)
actors=E.get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
terrain=bymesh('SM_IV_Continent_GosainLake53')
pairs=[(terrain,'SM_IV_Continent_GosainKingdom55'),(bymesh('SM_Gosain54_KingdomRoutes'),'SM_Gosain55_KingdomRoutes')]
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
for a,n in pairs:
 mats={str(v.material_slot_name):v.material_interface for v in a.static_mesh_component.static_mesh.static_materials}
 new[n]=loadmesh(n,mats,a.static_mesh_component.get_material(0) if a==terrain else None,a==terrain)
fts=[]
for i in range(5):
 path=D+'/Meshes/SM_RightForestTree'+str(i);mesh=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(R+'/Gosain50/Meshes/SM_Gosain50_Tree'+str(i),path);assert mesh
 path=D+'/Foliage/FT_RightForestTree'+str(i);ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_RightForestTree'+str(i),D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',mesh);A.save_loaded_asset(ft);fts.append(ft)
groups=[[] for _ in range(5)]
for x,y,z,yaw,scale,i in json.loads((O/'forest_instances.json').read_text()):groups[int(i)].append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(scale,scale,scale)))
backup=B/'Saved/WorldBackups'/('BeforeGosain55_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
rollback=[(a,a.static_mesh_component.static_mesh) for a,n in pairs]
try:
 for a,n in pairs:a.static_mesh_component.set_static_mesh(new[n])
 for ft,rows in zip(fts,groups):unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for a,m in rollback:a.static_mesh_component.set_static_mesh(m)
 for ft in fts:unreal.InstancedFoliageActor.remove_all_instances(W,ft)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'meshes':[n for a,n in pairs],'right_forest_trees':sum(map(len,groups)),'existing_foliage_retained':True,'native_review':'pending'},indent=2))

