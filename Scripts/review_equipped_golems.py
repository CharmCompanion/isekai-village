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
  mesh=a.get_editor_property('skeletal_mesh_component').get_editor_property('skeletal_mesh_asset')
  bounds=mesh.get_bounds();loc.z=(220 if loc.y>0 else -1)-(bounds.origin.z-bounds.box_extent.z)
  comp=a.get_editor_property('skeletal_mesh_component')
  data=comp.get_editor_property('animation_data')
  anim=data.get_editor_property('anim_to_play')
  if anim:
   comp.play_animation(anim,True);comp.set_position(0,False);comp.set_update_animation_in_editor(True)

  a.set_actor_location(loc,False,False)
if not any(a.get_actor_label()=='Raised review platform' for a in actors):
 platform=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,150,210))
 platform.set_actor_label('Raised review platform')
 platform.get_editor_property('static_mesh_component').set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
 platform.set_actor_scale3d(u.Vector(14,3,.2))
u.EditorLoadingAndSavingUtils.save_map(u.EditorLevelLibrary.get_editor_world(),level)
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
u.SystemLibrary.execute_console_command(u.EditorLevelLibrary.get_editor_world(),'r.ScreenPercentage 100')
for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(actor,u.SkyLight):actor.get_component_by_class(u.SkyLightComponent).recapture_sky()
started=time.monotonic()
def capture(delta):
 if time.monotonic()-started<25:return
 u.unregister_slate_post_tick_callback(handle)
 try:
  u.get_editor_subsystem(u.EditorActorSubsystem).set_selected_level_actors([])
  for command in ('showflag.BillboardSprites 0','showflag.CompositeEditorPrimitives 0','showflag.Grid 0'):
   u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),command)
  u.AutomationLibrary.take_high_res_screenshot(1920,1200,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Equipped_Golems_Unreal.png',delay=1,force_game_view=False)
  (root/'Saved/golem_review_capture.json').write_text(json.dumps({'requested':True}))
 except Exception:(root/'Saved/golem_review_capture.json').write_text(json.dumps({'error':traceback.format_exc()}))
handle=u.register_slate_post_tick_callback(capture)


review_last_job=None
def review_poll(delta):
 global review_last_job
 request=root/'Saved/golem_equipment_review_job.json'
 if not request.exists():return
 job=json.loads(request.read_text())
 if review_last_job==job['id']:return
 review_last_job=job['id']
 try:
  script=root/'Scripts'/job['script']
  exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
 except Exception:(root/'Saved/golem_equipment_review_error.txt').write_text(traceback.format_exc())
review_poll_handle=u.register_slate_post_tick_callback(review_poll)
