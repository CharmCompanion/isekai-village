import unreal as u,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
mesh=u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem')
base='/Game/Elrhun/Golems/Materials/'
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  c=a.get_editor_property('skeletal_mesh_component');c.set_skeletal_mesh_asset(mesh)
  for i,name in enumerate(['MI_DarkEyes','M_ClayBody','MI_PolishedClay']):c.set_material(i,u.load_asset(base+name))
  role=a.get_actor_label().replace('Golem ','')
  c.set_material(3,u.load_asset(base+'MI_SoulGem_'+role));c.set_visibility(True)
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle);u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
