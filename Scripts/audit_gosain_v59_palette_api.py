import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain59/Materials/MI_Gosain59_MI_Grass');out={'setter_doc':str(M.set_material_instance_vector_parameter_value.__doc__),'parameters':[str(x) for x in M.get_vector_parameter_names(mat)],'values':{}}
for p in M.get_vector_parameter_names(mat):
 c=M.get_material_instance_vector_parameter_value(mat,p);out['values'][str(p)]=[c.r,c.g,c.b,c.a]
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59/palette_api.json').write_text(json.dumps(out,indent=2))
