import unreal,json
from pathlib import Path
out={};M=unreal.MaterialEditingLibrary
for path in ['/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2','/Game/SoStylized/Environment/Trees/Pine/SM_Pine01']:
 m=unreal.load_asset(path);row={'bounds':str(m.get_bounding_box()),'materials':[]}
 for sm in m.get_editor_property('static_materials'):
  mat=sm.material_interface;d={'path':mat.get_path_name(),'params':{}}
  try:
   for name in M.get_scalar_parameter_names(mat):d['params'][str(name)]=M.get_material_instance_scalar_parameter_value(mat,name)
  except Exception as e:d['error']=str(e)
  row['materials'].append(d)
 out[path]=row
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/continent_foliage_audit.json').write_text(json.dumps(out,indent=2))
