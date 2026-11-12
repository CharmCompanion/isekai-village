import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain59/Materials/MI_Gosain59_MI_Grass');parents=[]
while isinstance(mat,unreal.MaterialInstanceConstant):mat=mat.get_editor_property('parent');parents.append(mat.get_path_name())
out={'parents':parents,'use_material_attributes':mat.get_editor_property('use_material_attributes'),'property_methods':[x for x in dir(M) if 'property_input' in x],'static_switch_methods':[x for x in dir(M) if 'static_switch' in x]}
for prop in [unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialProperty.MP_EMISSIVE_COLOR,unreal.MaterialProperty.MP_SUBSURFACE_COLOR]:
 try:
  node=M.get_material_property_input_node(mat,prop);out[str(prop)]={'node':node.get_name() if node else None,'output':M.get_material_property_input_node_output_name(mat,prop)}
 except Exception as e:out[str(prop)]=str(e)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59/grass_graph.json').write_text(json.dumps(out,indent=2,default=str))
