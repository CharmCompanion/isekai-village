import unreal as u,json,time,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
target=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Golem Mage')
comp=target.get_editor_property('skeletal_mesh_component');mesh=comp.get_editor_property('skeletal_mesh_asset')
asset=mesh.get_editor_property('mesh_clothing_assets')[0]
for name,config in asset.get_editor_property('cloth_configs').items():
 if config.get_class().get_name()=='ChaosClothConfig':
  config.set_editor_property('bUseSelfCollisions',False);config.set_editor_property('GravityScale',.2);config.set_editor_property('CollisionThickness',.7)
asset.set_editor_property('PhysicsAsset',None)
comp.set_cloth_max_distance_scale(.1);comp.set_editor_property('cloth_blend_weight',1);comp.resume_clothing_simulation();comp.recreate_clothing_actors();comp.force_cloth_next_update_teleport_and_reset()
started=time.monotonic()
def check(delta):
 if time.monotonic()-started<4:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1920,1200,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Cloth_Stability_Test.png',delay=1,force_game_view=False)
 info={'head':str(comp.get_socket_location('Head')),'hips':str(comp.get_socket_location('Hips')),'root':str(comp.get_socket_transform('Elrhun_Clay_Mannequin'))}
 (root/'Saved/golem_cloth_stability_test.json').write_text(json.dumps(info,indent=2))
handle=u.register_slate_post_tick_callback(check)
