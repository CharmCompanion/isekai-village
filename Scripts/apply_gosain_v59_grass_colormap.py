"""Reduce the pack's active grass colormap contribution on private Gosain instances."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain59';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;report=[]
assert (O/'palette_applied.json').exists() and not (O/'colormap_applied.json').exists()
for suffix in ['','_LOD1','_LOD2']:
 mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain59/Materials/MI_Gosain59_MI_Grass'+suffix);assert mat;old=M.get_material_instance_scalar_parameter_value(mat,'Colormap Multiply');M.set_material_instance_scalar_parameter_value(mat,'Colormap Multiply',.40);M.update_material_instance(mat);actual=M.get_material_instance_scalar_parameter_value(mat,'Colormap Multiply');assert abs(actual-.4)<1e-5;A.save_loaded_asset(mat);report.append({'material':mat.get_path_name(),'old_colormap_multiply':old,'new_colormap_multiply':actual})
(O/'colormap_applied.json').write_text(json.dumps({'status':'saved','materials':report},indent=2))
