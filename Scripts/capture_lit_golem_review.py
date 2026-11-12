import unreal as u,time
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.get_editor_subsystem(u.EditorActorSubsystem).set_selected_level_actors([])
for command in ('showflag.BillboardSprites 0','showflag.CompositeEditorPrimitives 0','showflag.Grid 0','showflag.SelectionOutline 0'):
 u.SystemLibrary.execute_console_command(world,command)
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<3:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png',force_game_view=False)
handle=u.register_slate_post_tick_callback(snap)
