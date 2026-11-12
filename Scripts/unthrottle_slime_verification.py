import unreal,builtins
# Session-only: do not save the user's editor preferences.
settings=unreal.load_object(None,'/Script/UnrealEd.Default__EditorPerformanceSettings')
builtins.slime_original_background_throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground')
settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'t.IdleWhenNotForeground 0')
