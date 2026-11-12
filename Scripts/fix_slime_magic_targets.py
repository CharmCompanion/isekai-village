import unreal
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=E.get_all_level_actors();by_name={a.get_actor_label():a for a in actors}
for a in actors:
 if a.get_actor_label().startswith('Target visual '):
  prefix=a.get_actor_label().removeprefix('Target visual ');target=by_name['Target_'+prefix+'Slime']
  a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
  a.attach_to_actor(target,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/IsekaiVillage/Magic/Slimes/Map_SlimeMagic')
