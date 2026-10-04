import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage'); A=unreal.EditorAssetLibrary; M=unreal.MaterialEditingLibrary
paths=[ '/Game/SoStylized/Environment/Sky/Meshes/SM_StylizedSkyDome_Clouds','/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Spire01','/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClump01','/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1','/Game/SoStylized/Environment/Trees/Oak/SM_OakBranch1','/Game/SoStylized/Environment/Sky/Materials/MI_StylizedClouds_Lite','/Game/StylizedIsland/StylizedVFX/Fog/Materials/FogCard/MI_FogCard_01']
d={}
for p in paths:
 a=unreal.load_asset(p); row={'exists':bool(a)};d[p]=row
 if not a:continue
 if isinstance(a,unreal.StaticMesh):row.update(bounds=str(a.get_bounding_box()),materials=[str(m.material_interface) for m in a.static_materials])
 if isinstance(a,unreal.MaterialInstanceConstant):
  row.update(scalars={str(n):M.get_material_instance_scalar_parameter_value(a,n) for n in M.get_scalar_parameter_names(a)},vectors={str(n):str(M.get_material_instance_vector_parameter_value(a,n)) for n in M.get_vector_parameter_names(a)},textures={str(n):str(M.get_material_instance_texture_parameter_value(a,n)) for n in M.get_texture_parameter_names(a)})
(B/'Saved/refinement_asset_audit.json').write_text(json.dumps(d,indent=2))
