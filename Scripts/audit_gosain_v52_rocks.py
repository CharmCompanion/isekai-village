import unreal,json
from pathlib import Path
out=[];M=unreal.MaterialEditingLibrary
for i in [2,3,4]:
 m=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB0'+str(i))
 for slot in m.static_materials:
  mat=slot.material_interface;r={'mesh':m.get_path_name(),'material':mat.get_path_name(),'vectors':{},'scalars':{}}
  if isinstance(mat,unreal.MaterialInstanceConstant):
   for n in M.get_vector_parameter_names(mat):
    v=M.get_material_instance_vector_parameter_value(mat,n);r['vectors'][str(n)]=[v.r,v.g,v.b,v.a]
   for n in M.get_scalar_parameter_names(mat):r['scalars'][str(n)]=M.get_material_instance_scalar_parameter_value(mat,n)
  out.append(r)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain52/rock_materials.json').write_text(json.dumps(out,indent=2))
