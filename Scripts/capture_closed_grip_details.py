import unreal as u,time,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs')
system=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.LevelEditorSubsystem)
targets={a.get_actor_label():a for a in system.get_all_level_actors() if isinstance(a,u.GolemEquipmentActor)}
camera=system.spawn_actor_from_class(u.CameraActor,u.Vector(0,0,0));camera.set_actor_label('Temporary hand grip inspection camera');camera.get_component_by_class(u.CameraComponent).set_field_of_view(30)
sequence=[('Golem Tank','Right','Elrhun_Corrected_Sword_Grip.png',u.Vector(-35,-50,30)),('Golem Tank','Left','Elrhun_Corrected_Shield_Grip.png',u.Vector(-40,50,28)),('Golem Mage','Right','Elrhun_Corrected_Wand_Grip.png',u.Vector(-35,-50,30))]
index=0;phase='camera';deadline=0;results=[];busy=False
def tick(delta):
 global index,phase,deadline,busy
 if busy or time.monotonic()<deadline:return
 busy=True
 try:
  if index==len(sequence):
   editor.eject_pilot_level_actor();system.destroy_actor(camera);u.unregister_slate_post_tick_callback(handle)
   a=targets['Golem Evil_Crimson'];p=a.get_actor_location();eye=p+u.Vector(-40,-150,130);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,p+u.Vector(0,0,96)))
   (root/'Saved/golem_closed_grip_captures.json').write_text(json.dumps(results,indent=2));return
  label,side,filename,offset=sequence[index];comp=targets[label].get_editor_property('skeletal_mesh_component')
  if phase=='camera':
   center=u.Vector(0,0,0)
   for digit in ['Index','Middle','Ring','Pinky']:center+=comp.get_socket_location(side+'Hand'+digit+'2')*.25
   eye=center+offset;camera.set_actor_location(eye,False,False);camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(eye,center),False)
   editor.pilot_level_actor(camera);phase='capture';deadline=time.monotonic()+4
  else:
   u.AutomationLibrary.take_high_res_screenshot(1400,1100,str(out/filename),delay=1,force_game_view=False);results.append({'actor':label,'hand':side,'file':str(out/filename)});index+=1;phase='camera';deadline=time.monotonic()+3
 except Exception:
  (root/'Saved/golem_closed_grip_capture_error.txt').write_text(traceback.format_exc());editor.eject_pilot_level_actor();system.destroy_actor(camera);u.unregister_slate_post_tick_callback(handle)
 finally:busy=False
handle=u.register_slate_post_tick_callback(tick)
