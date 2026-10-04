import unreal
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in E.get_all_level_actors():
 if a.get_actor_label() in ['SM_IV_SkyLake','SM_IV_SkyRiver','Skyfall - river spilling into clouds'] or str(a.get_folder_path())=='Floating Island/Cloud Sea':
  for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_editor_property('cast_shadow',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
