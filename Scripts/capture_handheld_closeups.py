import unreal as u,time,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs')
actors=u.get_editor_subsystem(u.EditorActorSubsystem);targets={a.get_actor_label():a for a in actors.get_all_level_actors() if isinstance(a,u.GolemEquipmentActor)}
sequence=[('Golem Evil_Crimson','Elrhun_Evil_Handheld_Closeup.png'),('Golem Tank','Elrhun_Tank_Handheld_Closeup.png'),('Golem Mage','Elrhun_Mage_Cloth_Closeup.png')]
index=0;phase='camera';deadline=0;results=[]
def tick(delta):
 global index,phase,deadline
 now=time.monotonic()
 if now<deadline:return
 try:
  if index==len(sequence):
   u.unregister_slate_post_tick_callback(handle);(root/'Saved/golem_closeup_capture.json').write_text(json.dumps(results,indent=2));return
  label,file=sequence[index];a=targets[label]
  if phase=='camera':
   loc=a.get_actor_location();eye=loc+u.Vector(-40,-150,130);look=loc+u.Vector(0,0,96)
   u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,look));phase='capture';deadline=now+4
  else:
   u.AutomationLibrary.take_high_res_screenshot(1300,1500,str(out/file),delay=1,force_game_view=False)
   results.append({'actor':label,'file':str(out/file)});index+=1;phase='camera';deadline=now+3
 except Exception:(root/'Saved/golem_closeup_capture_error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
