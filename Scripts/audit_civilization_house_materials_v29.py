import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;r={}
for name in ['SM_House_Var01','SM_House_Var02']:
 mesh=unreal.load_asset('/Game/AdvancedVillagePack/Meshes/'+name);mat=mesh.static_materials[0].material_interface
 r[name]={'material':mat.get_path_name(),'class':mat.get_class().get_name(),'parent':str(mat.get_editor_property('parent')) if isinstance(mat,unreal.MaterialInstanceConstant) else None,'scalars':{str(n):M.get_material_instance_scalar_parameter_value(mat,n) for n in M.get_scalar_parameter_names(mat)},'vectors':{str(n):str(M.get_material_instance_vector_parameter_value(mat,n)) for n in M.get_vector_parameter_names(mat)},'textures':{str(n):str(M.get_material_instance_texture_parameter_value(mat,n)) for n in M.get_texture_parameter_names(mat)}}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/civilization_house_materials_v29.json').write_text(json.dumps(r,indent=2))
