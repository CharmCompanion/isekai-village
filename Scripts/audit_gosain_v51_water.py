import unreal,json
from pathlib import Path
m=unreal.load_asset('/Game/AdvancedVillagePack/Materials/M_Inst_Water');M=unreal.MaterialEditingLibrary
out={}
for n in M.get_vector_parameter_names(m):
 v=M.get_material_instance_vector_parameter_value(m,n);out[str(n)]=[v.r,v.g,v.b,v.a]
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain51/water_parameters.json').write_text(json.dumps(out))
