import unreal as u,time,json,traceback
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
level='/Game/Elrhun/Golems/Maps/Map_GolemSoulGems'
u.EditorLoadingAndSavingUtils.load_map(level)
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 loc=a.get_actor_location()
 if isinstance(a,u.TextRenderActor):
  a.set_actor_rotation(u.Rotator(pitch=0,yaw=-90,roll=0),False)
  if loc.y>0:loc.z=420
  else:loc.z=200
  a.set_actor_location(loc,False,False)
 elif isinstance(a,u.SkeletalMeshActor):
  loc.z=218.4 if loc.y>0 else -2.6
  a.set_actor_location(loc,False,False)
if not any(a.get_actor_label()=='Raised review platform' for a in actors):
 platform=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,150,210))
 platform.set_actor_label('Raised review platform')
 platform.get_editor_property('static_mesh_component').set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
 platform.set_actor_scale3d(u.Vector(14,3,.2))
u.EditorLoadingAndSavingUtils.save_map(u.EditorLevelLibrary.get_editor_world(),level)
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
u.SystemLibrary.execute_console_command(u.EditorLevelLibrary.get_editor_world(),'r.ScreenPercentage 100')
started=time.monotonic()
def capture(delta):
 if time.monotonic()-started<40:return
 u.unregister_slate_post_tick_callback(handle)
 try:
  u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_Unreal.png')
  (root/'Saved/golem_review_capture.json').write_text(json.dumps({'requested':True}))
 except Exception:(root/'Saved/golem_review_capture.json').write_text(json.dumps({'error':traceback.format_exc()}))
handle=u.register_slate_post_tick_callback(capture)

