import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain56';M=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain53/Materials/M_Gosain53_ShoreMaskFixed');rows=[]
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):rows.append({'code':n.get_editor_property('code')})
(O/'terrain_material.json').write_text(json.dumps(rows,indent=2))
(O/'trace_api.txt').write_text(str(unreal.SystemLibrary.line_trace_single.__doc__))

