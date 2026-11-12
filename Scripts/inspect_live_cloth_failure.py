import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');r={}
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if not isinstance(a,u.GolemEquipmentActor):continue
 comp=a.get_editor_property('skeletal_mesh_component');mesh=comp.get_editor_property('skeletal_mesh_asset')
 comp.suspend_clothing_simulation();comp.set_editor_property('cloth_blend_weight',0)
 row={'bounds':str(mesh.get_bounds()),'head':str(comp.get_socket_location('Head')),'hips':str(comp.get_socket_location('Hips')),'config':[]}
 for asset in mesh.get_editor_property('mesh_clothing_assets'):
  for name,config in asset.get_editor_property('cloth_configs').items():
   row['config'].append({'type':config.get_class().get_name(),'text':config.export_text() if hasattr(config,'export_text') else str(config)})
 r[a.get_actor_label()]=row
(root/'Saved/golem_cloth_failure_inspection.json').write_text(json.dumps(r,indent=2))
