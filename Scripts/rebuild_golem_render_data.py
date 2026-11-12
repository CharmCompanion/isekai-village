import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
mesh=u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem')
sys=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
settings=sys.get_lod_build_settings(mesh,0)
sys.set_lod_build_settings(mesh,0,settings)
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
(root/'Saved/golem_rebuild.json').write_text(json.dumps({'vertices':sys.get_num_verts(mesh,0),'sections':sys.get_num_sections(mesh,0),'saved':True}))
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  c=a.get_editor_property('skeletal_mesh_component')
  c.set_skeletal_mesh_asset(None);c.set_skeletal_mesh_asset(mesh)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle);u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
