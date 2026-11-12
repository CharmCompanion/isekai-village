"""Recoverable Gosain kingdom conversion. Imports before changing the level."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain53';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain53'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();M=unreal.MaterialEditingLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN50 '+s)
actors=E.get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
terrain=bymesh('SM_IV_Continent_GosainLake52')
pairs=[(terrain,'SM_IV_Continent_GosainLake53')]
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


old=terrain.static_mesh_component.static_mesh
mesh=loadmesh('SM_IV_Continent_GosainLake53',{},terrain.static_mesh_component.get_material(0),True)
oldmat=terrain.static_mesh_component.get_material(0)
matpath=D+'/Materials/M_Gosain53_LakeBanks'
mat=unreal.load_asset(matpath) if A.does_asset_exist(matpath) else A.duplicate_asset(oldmat.get_path_name().split('.')[0],matpath)
found=0
for node in M.get_material_expressions(mat):
 if isinstance(node,unreal.MaterialExpressionCustom):
  code=node.get_editor_property('code')
  if 'float3 meadow=' in code:
   marker='float slope='
   addition="""float2 lakeDelta=q.xy-float2(27000.,36300.);
float2 lakeAxes=float2(lakeDelta.x-lakeDelta.y,lakeDelta.x+lakeDelta.y)*.70710678;
float lakeMask=1.-smoothstep(1.,1.35,length(lakeAxes/float2(1500.,1000.)));
float shore=(1.-smoothstep(3.,14.,abs(q.z+20545.)))*lakeMask;
float3 bank=lerp(float3(.14,.12,.075),D*.42,.30);
meadow=lerp(meadow,bank,shore*.78);
"""
   if 'float2 lakeDelta=' not in code:code=code.replace(marker,addition+marker)
   node.set_editor_property('code',code);found+=1
assert found==1
M.recompile_material(mat);A.save_loaded_asset(mat)
backup=B/'Saved/WorldBackups'/('BeforeGosain53_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
try:
 terrain.static_mesh_component.set_static_mesh(mesh)
 terrain.static_mesh_component.set_material(0,mat)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 terrain.static_mesh_component.set_static_mesh(old)
 terrain.static_mesh_component.set_material(0,oldmat)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'native_review':'pending'},indent=2))

