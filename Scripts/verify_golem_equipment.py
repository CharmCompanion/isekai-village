import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
report={}
try:
 expected=json.loads((root/'Saved/golem_equipment_setup.json').read_text());assert expected['success'],expected
 roles=json.loads((root/'Saved/golem_setup_report.json').read_text())['blueprints']
 for role,path in roles.items():
  bp=u.load_asset(path);c=u.get_default_object(bp.generated_class()).get_editor_property('skeletal_mesh_component')
  mesh=c.get_editor_property('skeletal_mesh_asset')
  assert mesh.get_path_name()==expected['roles'][role]['mesh'],role
  assert c.get_material(expected['roles'][role]['gem_slot']).get_name()=='MI_SoulGem_'+role,role
  anim=c.get_editor_property('animation_data').get_editor_property('anim_to_play');assert anim,role
  report[role]={'mesh':mesh.get_name(),'animation':anim.get_name(),'gem':c.get_material(expected['roles'][role]['gem_slot']).get_name(),'material_slots':len(mesh.get_editor_property('materials'))}
 report['success']=True
except Exception:report['success']=False;report['error']=traceback.format_exc()
(root/'Saved/golem_equipment_verify.json').write_text(json.dumps(report,indent=2))
