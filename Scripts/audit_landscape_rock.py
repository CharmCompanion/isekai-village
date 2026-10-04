import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Materials/M_IV_FloatingLandscape');rows=[]
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):rows.append({'name':n.get_name(),'code':n.get_editor_property('code')})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/landscape_shading_inspect.json').write_text(json.dumps(rows,indent=2))
