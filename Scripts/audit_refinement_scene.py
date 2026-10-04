import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in E.get_all_level_actors():
 l=a.get_actor_label();f=str(a.get_folder_path())
 if any(x in l.lower() for x in ['cloud','continent','sky','fog']) or f=='Refinement/Distant World':
  row={'label':l,'folder':f,'loc':str(a.get_actor_location()),'hidden':a.is_hidden() if hasattr(a,'is_hidden') else str(a.get_editor_property('hidden'))}
  if isinstance(a,unreal.StaticMeshActor):row.update(mesh=str(a.static_mesh_component.static_mesh),mat=str(a.static_mesh_component.get_material(0)),bounds=str(a.get_actor_bounds(False)))
  rows.append(row)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/refinement_scene_audit.json').write_text(json.dumps(rows,indent=2))
