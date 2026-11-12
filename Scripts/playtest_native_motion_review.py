import unreal as u,json,time,traceback,math
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');output='C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs';manifest=json.loads((r/'ArtSource/Golems/NativeMotion/manifest.json').read_text());result={'success':False,'mode':'Live Simulate In Editor, real animation and Chaos cloth ticks','phases':[]};started=time.monotonic();state='waiting';phase=-1;phase_start=0.;captured=False;handle=None
def finish(error=None):
 global handle,state
 state='finished'
 if handle:u.unregister_slate_post_tick_callback(handle);handle=None
 if error:result['error']=error
 try:u.EditorLevelLibrary.editor_end_play()
 except Exception:pass
 (r/'Saved/native_motion_playtest.json').write_text(json.dumps(result,indent=2))
 if not error:u.EditorPythonScripting.set_keep_python_script_alive(False)
 else:
  deadline=time.monotonic()+600
  def poll(delta):
   p=r/'Saved/native_motion_live_job.json'
   if p.exists():
    job=json.loads(p.read_text());u.unregister_slate_post_tick_callback(poll_handle)
    if job.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
    else:
     script=Path(job['script']);exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
   elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(poll_handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
  poll_handle=u.register_slate_post_tick_callback(poll)
def capture(world,actors,label,eye,target):
 actor=u.GameplayStatics.get_all_actors_of_class(world,u.SceneCapture2D)[0];actor.set_actor_location_and_rotation(eye,u.MathLibrary.find_look_at_rotation(eye,target),False,False);cap=actor.get_component_by_class(u.SceneCaptureComponent2D);rt=u.RenderingLibrary.create_render_target2d(world,2000,1350,u.TextureRenderTargetFormat.RTF_RGBA8);cap.set_editor_property('texture_target',rt);cap.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('fov_angle',48.);cap.capture_scene();u.RenderingLibrary.export_render_target(world,rt,output,label+'.png')
def tick(delta):
 global state,phase,phase_start,captured,started
 try:
  now=time.monotonic()
  if now-started>150:return finish('Playtest timed out')
  if state=='waiting':
   if now-started<4:return
   u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemMotionReview');u.EditorLevelLibrary.editor_play_simulate();state='starting';return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  world=worlds[0];actors=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.SkeletalMeshActor) if a.get_actor_label().startswith('Motion - ')]
  if len(actors)!=8:return
  if state=='starting' or now-phase_start>3.0:
   phase+=1
   if phase==6:
    result['success']=True;return finish()
   state='playing';phase_start=now;captured=False
   for actor in actors:
    label=actor.get_actor_label();body='BodyB' if 'BodyB' in label else 'BodyA';role=label.split()[-1];suffix=['Idle','Walk_InPlace','Run_Fwd','Jump',('NinjaLeftJab' if role in ['Tank','Ranger'] else 'AS_CastSpell'),('NinjaRightCross' if role in ['Tank','Ranger'] else 'AS_StaffStrike+CastSpell')][phase];anim=u.load_asset(manifest['animations'][body+'_'+suffix]['path']);comp=actor.get_editor_property('skeletal_mesh_component');assert anim.get_editor_property('skeleton')==comp.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton');comp.play_animation(anim,True)
   return
  if captured or now-phase_start<1.8:return
  captured=True;sample={'phase':phase,'actors':{}}
  for actor in actors:
   comp=actor.get_editor_property('skeletal_mesh_component');origin,extent=actor.get_actor_bounds(False);hand=comp.get_socket_location('hand_r');head=comp.get_socket_location('head');assert all(math.isfinite(v) for v in [*origin.to_tuple(),*extent.to_tuple(),*hand.to_tuple(),*head.to_tuple()]);assert max(extent.to_tuple())<800,(actor.get_actor_label(),extent)
   sample['actors'][actor.get_actor_label()]={'animation_time':comp.get_position(),'bounds_extent':extent.to_tuple(),'hand_r':hand.to_tuple(),'head':head.to_tuple()}
  capture(world,actors,'Elrhun_Live_Motion_'+str(phase),u.Vector(180,1240,760),u.Vector(0,-80,95))
  if phase in [3,4,5]:
   chosen=[a for a in actors if a.get_actor_label()=='Motion - BodyB Healer'][0]
   for a in actors:a.set_actor_hidden_in_game(a!=chosen)
   pos=chosen.get_actor_location();capture(world,[chosen],'Elrhun_Live_Healer_'+str(phase),pos+u.Vector(80,420,130),pos+u.Vector(0,0,100))
   for a in actors:a.set_actor_hidden_in_game(False)
  result['phases'].append(sample);(r/'Saved/native_motion_playtest_progress.json').write_text(json.dumps(result,indent=2))
 except Exception:finish(traceback.format_exc())
try:
 p=r/'Scripts/tune_native_coat_cloth.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 p=r/'Scripts/setup_native_motion_review.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 p=r/'Scripts/export_native_motion_poses.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
except Exception:(r/'Saved/native_pose_export_error.txt').write_text(traceback.format_exc())
started=time.monotonic();handle=u.register_slate_post_tick_callback(tick)
