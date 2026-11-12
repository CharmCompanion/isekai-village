import unreal
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
