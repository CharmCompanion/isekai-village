import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 if isinstance(a,u.SkeletalMeshActor):a.set_actor_rotation(u.Rotator(pitch=0,yaw=180,roll=0),False)
 if a.get_actor_label()=='Review soft sun':a.get_component_by_class(u.DirectionalLightComponent).set_intensity(6)
 if isinstance(a,u.RectLight):a.get_component_by_class(u.RectLightComponent).set_intensity(800 if a.get_actor_label()=='Review key' else 400)
mesh=u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem')
sys=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
slots=[sys.get_lod_material_slot(mesh,0,i) for i in range(sys.get_num_sections(mesh,0))]
mat=u.load_asset('/Game/Elrhun/Golems/Materials/M_ClayBody')
color=u.MaterialEditingLibrary.get_material_default_vector_parameter_value(mat,'BodyColor')
(root/'Saved/golem_material_debug.json').write_text(json.dumps({'section_slots':slots,'default_color':[color.r,color.g,color.b]}))
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
