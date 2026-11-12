import unreal as u,time,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
level='/Game/Elrhun/Golems/Maps/Map_GolemSoulGems'
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.EditorLoadingAndSavingUtils.save_map(world,level)
world=u.EditorLoadingAndSavingUtils.load_map(level)
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
u.EditorLevelLibrary.editor_set_game_view(True)
pos,rot=u.EditorLevelLibrary.get_level_viewport_camera_info()
visible=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  c=a.get_editor_property('skeletal_mesh_component')
  visible.append({'actor':a.get_actor_label(),'mesh':c.get_editor_property('skeletal_mesh_asset').get_path_name(),'body':c.get_material(1).get_path_name(),'gem':c.get_material(3).get_path_name()})
(root/'Saved/golem_lighting_final_verify.json').write_text(json.dumps({'reloaded':True,'pitch':rot.pitch,'yaw':rot.yaw,'golems':visible,'count':len(visible)},indent=2))
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<7:return
 u.unregister_slate_post_tick_callback(handle);u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
