import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.is_visible():
  o,b=a.get_actor_bounds(False)
  if o.y>23000 and o.z>-10000 and max(b.x,b.y,b.z)>4000:
   rows.append({'label':a.get_actor_label(),'folder':str(a.get_folder_path()),'origin':[o.x/100,o.y/100,o.z/100],'extent':[b.x/100,b.y/100,b.z/100],'mesh':a.static_mesh_component.static_mesh.get_path_name(),'materials':[a.static_mesh_component.get_material(i).get_path_name() if a.static_mesh_component.get_material(i) else None for i in range(a.static_mesh_component.get_num_materials())]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/rear_join_actors.json').write_text(json.dumps(rows,indent=2))
