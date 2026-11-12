"""Preserve the source grass LOD parent chain and keep procedural roots on the ground."""
import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59');D='/Game/IsekaiVillage/AdventureWorld/Gosain59/Materials';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
assert (O/'grass_finish_applied.json').exists() and not (O/'grass_inheritance_applied.json').exists()
parent=unreal.load_asset(D+'/M_Gosain59_FoliageTone');rows=[]
for suffix in ['','_LOD1','_LOD2']:
 mat=unreal.load_asset(D+'/MI_Gosain59_MI_Grass'+suffix);M.set_material_instance_parent(mat,parent)
 for name in ['AdditionalX','AdditionalY','AdditionalZ']:M.set_material_instance_scalar_parameter_value(mat,name,0.)
 M.update_material_instance(mat);A.save_loaded_asset(mat);assert mat.get_editor_property('parent')==parent
 rows.append({'material':mat.get_path_name(),'parent':parent.get_path_name(),'additional_offsets_cm':[M.get_material_instance_scalar_parameter_value(mat,k) for k in ['AdditionalX','AdditionalY','AdditionalZ']]});parent=mat
assert all(abs(v)<1e-5 for q in rows for v in q['additional_offsets_cm'])
(O/'grass_inheritance_applied.json').write_text(json.dumps({'status':'saved','materials':rows,'original_lod_hierarchy_preserved_with_private_parents':True},indent=2))
