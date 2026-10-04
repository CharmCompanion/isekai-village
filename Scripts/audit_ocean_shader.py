import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;a=unreal.load_asset('/Game/SoStylized/Environment/Water/Materials/MI_Ocean')
out={'parent':str(a.get_editor_property('parent')),'switch_names':[str(n) for n in M.get_static_switch_parameter_names(a)],'textures':{str(n):str(M.get_material_instance_texture_parameter_value(a,n)) for n in M.get_texture_parameter_names(a)}}
out['switch_values']={str(n):M.get_material_instance_static_switch_parameter_value(a,n) for n in M.get_static_switch_parameter_names(a)}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/ocean_shader_audit.json').write_text(json.dumps(out,indent=2))
