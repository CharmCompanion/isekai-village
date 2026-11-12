import unreal as u,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
target=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Golem Mage')
comp=target.get_editor_property('skeletal_mesh_component');asset=comp.get_editor_property('skeletal_mesh_asset').get_editor_property('mesh_clothing_assets')[0]
asset.set_editor_property('PhysicsAsset',u.load_asset('/Game/Elrhun/Golems/Physics/PHYS_GolemBody_Cloth'))
comp.set_cloth_max_distance_scale(.1);comp.recreate_clothing_actors();comp.resume_clothing_simulation();comp.force_cloth_next_update_teleport_and_reset()
start=time.monotonic()
def capture(delta):
 if time.monotonic()-start<5:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1920,1200,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Cloth_Collision_Only.png',delay=1,force_game_view=False)
handle=u.register_slate_post_tick_callback(capture)
