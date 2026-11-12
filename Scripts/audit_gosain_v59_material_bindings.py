import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if c.static_mesh and c.static_mesh.get_name() in ['SM_Grass1','SM_Grass2']:
   rows.append({'component':c.get_name(),'mesh':c.static_mesh.get_name(),'count':c.get_instance_count(),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else '' for i in range(c.get_num_materials())]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain59/material_bindings.json').write_text(json.dumps(rows,indent=2))
