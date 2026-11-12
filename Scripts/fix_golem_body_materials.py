import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
base='/Game/Elrhun/Golems'
mesh=u.load_asset(base+'/Mesh/SK_ElrhunGolem')
body=u.load_asset(base+'/Materials/M_ClayBody')
ink=u.load_asset(base+'/Materials/MI_DarkEyes')
joint=u.load_asset(base+'/Materials/MI_PolishedClay')
tank=u.load_asset(base+'/Materials/MI_SoulGem_Tank')
materials=list(mesh.get_editor_property('materials'))
for i,mat in enumerate([ink,body,joint,tank]):
 slot=materials[i];slot.set_editor_property('material_interface',mat);materials[i]=slot
mesh.modify();mesh.set_editor_property('materials',materials)
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
r=json.loads((root/'Saved/golem_setup_report.json').read_text())
for role,path in r['blueprints'].items():
 bp=u.load_asset(path);cdo=u.get_default_object(bp.generated_class());comp=cdo.get_editor_property('skeletal_mesh_component')
 for i,mat in enumerate([ink,body,joint]):comp.set_material(i,mat)
 u.BlueprintEditorLibrary.compile_blueprint(bp);u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  comp=a.get_editor_property('skeletal_mesh_component')
  for i,mat in enumerate([ink,body,joint]):comp.set_material(i,mat)
u.EditorLoadingAndSavingUtils.save_map(world,base+'/Maps/Map_GolemSoulGems')
(root/'Saved/golem_body_material_fixed.json').write_text(json.dumps({'mesh_slots':[str(m.material_interface) for m in mesh.get_editor_property('materials')],'saved':True},indent=2))
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
