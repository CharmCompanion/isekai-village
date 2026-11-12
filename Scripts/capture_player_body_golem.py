import unreal as u,time,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs');actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.LevelEditorSubsystem);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();actor=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Golem - Original Player Body');comp=actor.get_editor_property('skeletal_mesh_component');loc=actor.get_actor_location()
cam=actors.spawn_actor_from_class(u.CameraActor,u.Vector());cam.set_actor_label('Temporary player body camera');cc=cam.get_component_by_class(u.CameraComponent);cc.set_field_of_view(34);cc.set_editor_property('constrain_aspect_ratio',True)
fill=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Player body review fill'),None)
if not fill:
 fill=actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,400));fill.set_actor_label('Player body review fill');fill.get_editor_property('light_component').set_intensity(2.5);fill.get_editor_property('light_component').set_cast_shadows(False)
shots=['Body','Hands'];i=0;phase='camera';deadline=time.monotonic()+4;busy=False;images=[]
def tick(delta):
 global i,phase,deadline,busy
 if busy or time.monotonic()<deadline:return
 busy=True
 try:
  if i==len(shots):
   editor.eject_pilot_level_actor();actors.destroy_actor(cam);eye=loc+u.Vector(150,400,140);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,loc+u.Vector(0,0,100)));u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemPlayerBody');u.unregister_slate_post_tick_callback(handle);(r/'Saved/golem_player_body_captures.json').write_text(json.dumps({'images':images,'saved':True},indent=2));return
  shot=shots[i]
  if phase=='camera':
   center=loc+u.Vector(0,0,99) if shot=='Body' else (comp.get_socket_location('hand_l')+comp.get_socket_location('middle_02_l'))*.5
   eye=loc+u.Vector(150,400,140) if shot=='Body' else center+u.Vector(23,42,12);cc.set_aspect_ratio(.8 if shot=='Body' else 1.2);cam.set_actor_location(eye,False,False);cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(eye,center),False);fill.set_actor_rotation(u.MathLibrary.find_look_at_rotation(eye,center),False);editor.pilot_level_actor(cam);phase='capture';deadline=time.monotonic()+6
  else:
   file=out/('Elrhun_PlayerBody_Golem_'+shot+'.png');i+=1;phase='camera';deadline=time.monotonic()+4;u.AutomationLibrary.take_high_res_screenshot(1600,2000 if shot=='Body' else 1300,str(file),camera=cam,delay=1,force_game_view=True);images.append(str(file))
 except Exception:
  (r/'Saved/golem_player_body_capture_error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle)
 finally:busy=False
handle=u.register_slate_post_tick_callback(tick)
