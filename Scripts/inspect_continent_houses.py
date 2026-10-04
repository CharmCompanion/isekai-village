import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;rows=[]
for path in ['/Game/AdvancedVillagePack/Meshes/SM_House_Var01','/Game/AdvancedVillagePack/Meshes/SM_House_Var02']:
 m=unreal.load_asset(path);d={'mesh':path,'materials':[]}
 for sm in m.get_editor_property('static_materials'):
  mat=sm.material_interface;r={'name':mat.get_path_name(),'textures':{}}
  try:
   for k in M.get_texture_parameter_names(mat):
    t=M.get_material_instance_texture_parameter_value(mat,k);r['textures'][str(k)]=t.get_path_name() if t else None
  except:pass
  d['materials'].append(r)
 rows.append(d)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/continent_houses.json').write_text(json.dumps(rows,indent=2))
