import unreal,json
from pathlib import Path
m=unreal.load_asset('/Game/StylizedCharacters/BodyA/Eyes/Eyes_01/MI_Eyes_01_a')
r={}
for n in unreal.MaterialEditingLibrary.get_vector_parameter_names(m):
 c=unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(m,n);r[str(n)]=[c.r,c.g,c.b,c.a]
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/monster_eye_parameters_v02.json').write_text(json.dumps(r,indent=2))
