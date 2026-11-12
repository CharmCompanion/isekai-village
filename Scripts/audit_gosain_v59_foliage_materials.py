import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59');data=json.loads((O/'understory.json').read_text());M=unreal.MaterialEditingLibrary;rows=[]
for q in data['assets']:
 mesh=unreal.load_asset(q['path']);entry={'key':q['key'],'materials':[]}
 for slot in mesh.static_materials:
  mat=slot.material_interface;r={'path':mat.get_path_name(),'type':mat.get_class().get_name(),'vectors':{},'scalars':{}}
  for p in M.get_vector_parameter_names(mat):
   try:
    c=M.get_material_instance_vector_parameter_value(mat,p);r['vectors'][str(p)]=[c.r,c.g,c.b,c.a]
   except Exception:pass
  for p in M.get_scalar_parameter_names(mat):
   try:r['scalars'][str(p)]=M.get_material_instance_scalar_parameter_value(mat,p)
   except Exception:pass
  entry['materials'].append(r)
 rows.append(entry)
(O/'material_audit.json').write_text(json.dumps(rows,indent=2))
