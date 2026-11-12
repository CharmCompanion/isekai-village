import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for filename,result in [('import_refined_hands.py','golem_refined_hands_import.json'),('setup_corrected_equipment.py','golem_corrected_setup.json'),('verify_corrected_equipment.py','golem_corrected_verify.json')]:
  p=root/'Scripts'/filename;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','roles_to_import':['Tank','Mage','Ranger','Healer','Necromancer']})
  report=json.loads((root/'Saved'/result).read_text());assert report['success'],report.get('error',report)
 (root/'Saved/golem_refined_hands_apply_error.txt').write_text('')
except Exception:(root/'Saved/golem_refined_hands_apply_error.txt').write_text(traceback.format_exc())
finally:
 u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
 for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
  if not isinstance(a,u.GolemEquipmentActor):continue
  comp=a.get_editor_property('skeletal_mesh_component');anim=comp.get_editor_property('animation_data').get_editor_property('anim_to_play');comp.play_animation(anim,True);comp.set_position(0,False);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);comp.recreate_clothing_actors();a.rebuild_equipment()
