import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 label=a.get_actor_label()
 if isinstance(a,u.TextRenderActor):a.set_actor_rotation(u.Rotator(pitch=0,yaw=-90,roll=0),False)
 if isinstance(a,u.DirectionalLight):a.set_actor_rotation(u.Rotator(pitch=-45,yaw=-65,roll=0),False)
 if label=='Review key':a.set_actor_rotation(u.Rotator(pitch=-25,yaw=65,roll=0),False)
 if label=='Review fill':a.set_actor_rotation(u.Rotator(pitch=-20,yaw=125,roll=0),False)
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<8:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
pos,rot=u.EditorLevelLibrary.get_level_viewport_camera_info()
(root/'Saved/golem_camera_fixed.json').write_text(json.dumps({'pitch':rot.pitch,'yaw':rot.yaw,'roll':rot.roll,'saved':True}))
