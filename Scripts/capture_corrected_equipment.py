import unreal as u,json
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for cmd in ['showflag.BillboardSprites 0','showflag.CompositeEditorPrimitives 0','showflag.Grid 0']:u.SystemLibrary.execute_console_command(world,cmd)
u.AutomationLibrary.take_high_res_screenshot(1920,1200,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Clothing_Collision_Review.png',delay=1,force_game_view=False)
