import unreal,json,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain53';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
actors=[a for a in E.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainLake53'];assert len(actors)==1
c=actors[0].static_mesh_component;old=c.get_material(0);path='/Game/IsekaiVillage/AdventureWorld/Gosain53/Materials/M_Gosain53_ShoreMaskFixed';assert not A.does_asset_exist(path)
mat=A.duplicate_asset(old.get_path_name().split('.')[0],path);found=0
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  marker='float lakeMask=1.-smoothstep(1.,1.35,length(lakeAxes/float2(1500.,1000.)));'
  if marker in code:
   replacement='''float2 lakeNorm=lakeAxes/float2(1000.,490.);
float lakeAngle=atan2(lakeNorm.y,lakeNorm.x);
float lakeRadius=1.+.14*sin(3.*lakeAngle+.7)+.075*cos(5.*lakeAngle-.4);
float lakeSigned=(length(lakeNorm)-lakeRadius)*length(lakeAxes)/max(length(lakeNorm),.001);
float lakeMask=1.-smoothstep(200.,280.,abs(lakeSigned));'''
   n.set_editor_property('code',code.replace(marker,replacement));found+=1
assert found==1;M.recompile_material(mat);A.save_loaded_asset(mat)
backup=B/'Saved/WorldBackups'/('BeforeGosain53ShoreMask_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
try:
 c.set_material(0,mat);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 c.set_material(0,old);raise
(O/'shore_mask_fixed.json').write_text(json.dumps({'status':'saved','backup':str(backup),'material':mat.get_path_name()},indent=2))
