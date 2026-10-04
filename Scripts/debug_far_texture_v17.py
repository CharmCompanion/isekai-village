import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');M=unreal.MaterialEditingLibrary;R='/Game/IsekaiVillage/AdventureWorld';mat=unreal.load_asset(R+'/Materials/M_IV_LivingContinent_v17');rows=[]
for node in M.get_material_expressions(mat):
 r={'class':node.get_class().get_name(),'name':node.get_name()}
 for p in ['inputs','coordinates','texture','code']:
  try:r[p]=str(node.get_editor_property(p))
  except:pass
 rows.append(r)
tex=unreal.load_asset(R+'/Textures/T_IV_ContinentFar17');task=unreal.AssetExportTask();task.object=tex;task.filename=str(B/'Saved/far_texture_export.png');task.automated=True;task.prompt=False;task.replace_identical=True
try:rows.append({'export':unreal.Exporter.run_asset_export_task(task)})
except Exception as e:rows.append({'export_error':str(e)})
(B/'Saved/far_graph.json').write_text(json.dumps(rows,indent=2))
