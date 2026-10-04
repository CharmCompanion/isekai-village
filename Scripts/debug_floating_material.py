import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;R='/Game/IsekaiVillage/AdventureWorld';out={}
for name in ['M_IV_Landscape_Layered','M_IV_FloatingLandscape','M_IV_CaveStone']:
 mat=unreal.load_asset(R+'/Materials/'+name);out[name]={'nodes':[(n.get_class().get_name(),n.get_editor_property('code') if isinstance(n,unreal.MaterialExpressionCustom) else '') for n in M.get_material_expressions(mat)]}
 for p in ['MP_BASE_COLOR','MP_OPACITY_MASK']:
  try:out[name][p]=str(M.get_material_property_input_node(mat,getattr(unreal.MaterialProperty,p)))
  except Exception as e:out[name][p]=str(e)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));out['landscape']={'material':str(land.get_editor_property('landscape_material')),'layers':str(land.get_editor_property('target_layers'))}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/floating_material_audit.json').write_text(json.dumps(out,indent=2))

