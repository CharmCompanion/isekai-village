"""Private final grass color attenuation, retaining the pack's geometry, masking and wind."""
import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59');D='/Game/IsekaiVillage/AdventureWorld/Gosain59/Materials';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
assert not (O/'grass_finish_applied.json').exists()
path=D+'/M_Gosain59_FoliageTone';assert not A.does_asset_exist(path)
base=A.duplicate_asset('/Game/SoStylized/Environment/Foliage/Materials/M_Foliage',path);assert base and not base.get_editor_property('use_material_attributes')
for prop,factor in [(unreal.MaterialProperty.MP_BASE_COLOR,.42),(unreal.MaterialProperty.MP_SUBSURFACE_COLOR,.42),(unreal.MaterialProperty.MP_EMISSIVE_COLOR,.15)]:
 node=M.get_material_property_input_node(base,prop);output=M.get_material_property_input_node_output_name(base,prop);assert node
 mul=M.create_material_expression(base,unreal.MaterialExpressionMultiply);mul.set_editor_property('const_b',factor);assert M.connect_material_expressions(node,output,mul,'A');assert M.connect_material_property(mul,'',prop)
M.recompile_material(base);A.save_loaded_asset(base);parents=[]
for suffix in ['','_LOD1','_LOD2']:
 mat=unreal.load_asset(D+'/MI_Gosain59_MI_Grass'+suffix);assert mat;parents.append({'instance':mat.get_path_name(),'previous_parent':mat.get_editor_property('parent').get_path_name()});M.set_material_instance_parent(mat,base);M.update_material_instance(mat);A.save_loaded_asset(mat);assert mat.get_editor_property('parent')==base
(O/'grass_finish_applied.json').write_text(json.dumps({'status':'saved','private_parent':base.get_path_name(),'instances':parents,'base_and_subsurface_multiplier':.42,'emissive_multiplier':.15,'original_pack_materials_unchanged':True},indent=2))
