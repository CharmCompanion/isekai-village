import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(a for a in E.get_all_level_actors() if a.get_name()=='StaticMeshActor_1128')
m=a.static_mesh_component.get_material(0);M=unreal.MaterialEditingLibrary
rows=[]
for n in M.get_material_expressions(m):
    row={'name':n.get_name(),'class':n.get_class().get_name()}
    if isinstance(n,unreal.MaterialExpressionCustom):row['code']=n.get_editor_property('code')
    if isinstance(n,unreal.MaterialExpressionWorldPosition):row['mode']=str(n.get_editor_property('world_position_shader_offset'))
    if isinstance(n,unreal.MaterialExpressionTextureSample):row['texture']=n.texture.get_path_name() if n.texture else None
    rows.append(row)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/Gosain37/live_material.json').write_text(json.dumps({'material':m.get_path_name(),'base':M.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR).get_name(),'nodes':rows},indent=2))
