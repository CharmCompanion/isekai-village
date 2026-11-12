import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
a=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Golem Healer');a.rebuild_equipment()
(r/'Saved/final_hand_attachments.json').write_text(json.dumps({'items':[{'bone':str(i.bone),'mesh':i.mesh.get_path_name() if i.mesh else None} for i in a.get_editor_property('equipped_items')],'parts':[str(p.get_name()) for p in a.get_components_by_class(u.StaticMeshComponent)]}))
p=r/'Scripts/verify_corrected_equipment.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.GolemEquipmentActor):
  c=a.get_editor_property('skeletal_mesh_component');c.play_animation(c.get_editor_property('animation_data').get_editor_property('anim_to_play'),True);c.set_position(0,False);c.set_update_animation_in_editor(True);c.set_update_cloth_in_editor(True);c.recreate_clothing_actors();a.rebuild_equipment()
