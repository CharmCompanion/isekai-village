import unreal as u,time,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs')
actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors.set_selected_level_actors([])
items={a.get_actor_label():a for a in actors.get_all_level_actors() if isinstance(a,u.GolemEquipmentActor)}
camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector());camera.set_actor_label('Temporary refined hand review');camera.get_component_by_class(u.CameraComponent).set_field_of_view(34)
def norm(v):
 return v/max((v.x*v.x+v.y*v.y+v.z*v.z)**.5,.000001)
def cross(a,b):
 return u.Vector(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)
shots=['open','profile','grip'];index=0;phase='camera';deadline=0;busy=False;report=[]
def tick(delta):
 global index,phase,deadline,busy
 if busy or time.monotonic()<deadline:return
 busy=True
 try:
  if index==len(shots):
   editor.eject_pilot_level_actor();actors.destroy_actor(camera);u.unregister_slate_post_tick_callback(handle)
   a=items['Golem Tank'];p=a.get_actor_location();eye=p+u.Vector(-40,-150,130);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,p+u.Vector(0,0,96)))
   (root/'Saved/golem_slim_hand_captures.json').write_text(json.dumps(report,indent=2));return
  shot=shots[index];a=items['Golem Tank' if shot=='grip' else 'Golem Mage'];comp=a.get_editor_property('skeletal_mesh_component');side='Right' if shot=='grip' else 'Left'
  if phase=='camera':
   wrist=comp.get_socket_location(side+'Hand');knuckle=u.Vector()
   for digit in ['Index','Middle','Ring','Pinky']:knuckle+=comp.get_socket_location(side+'Hand'+digit+'1')*.25
   forward=norm(knuckle-wrist);width=norm(comp.get_socket_location(side+'HandPinky1')-comp.get_socket_location(side+'HandIndex1'));normal=norm(cross(forward,width))
   center=wrist+(knuckle-wrist)*1.15
   eye=center+normal*54+width*22-forward*7 if shot=='open' else center+width*60+normal*14 if shot=='profile' else center+u.Vector(-35,-50,30)
   camera.set_actor_location(eye,False,False);camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(eye,center),False);editor.pilot_level_actor(camera);phase='capture';deadline=time.monotonic()+4
  else:
   file=out/('Elrhun_Slim_Hand_'+shot.title()+'.png');index+=1;phase='camera';deadline=time.monotonic()+3
   u.AutomationLibrary.take_high_res_screenshot(1500,1100,str(file),delay=1,force_game_view=False);report.append(str(file))
 except Exception:
  (root/'Saved/golem_slim_hand_capture_error.txt').write_text(traceback.format_exc());editor.eject_pilot_level_actor();actors.destroy_actor(camera);u.unregister_slate_post_tick_callback(handle)
 finally:busy=False
handle=u.register_slate_post_tick_callback(tick)
