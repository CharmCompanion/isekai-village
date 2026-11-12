import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 label=a.get_actor_label()
 if isinstance(a,u.DirectionalLight):
  c=a.get_component_by_class(u.DirectionalLightComponent)
  c.set_intensity(1.5 if label=='Review soft sun' else 0)
  if label!='Review soft sun':c.set_visibility(False)
 if isinstance(a,u.RectLight):
  c=a.get_component_by_class(u.RectLightComponent)
  c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
  c.set_intensity(250 if label=='Review key' else 120)
 if isinstance(a,u.SkyLight):a.get_component_by_class(u.SkyLightComponent).set_intensity(.35)
 if isinstance(a,u.PostProcessVolume):
  settings=a.get_editor_property('settings')
  settings.set_editor_property('auto_exposure_bias',-1)
  settings.set_editor_property('override_bloom_intensity',True);settings.set_editor_property('bloom_intensity',.12)
  a.set_editor_property('settings',settings)
# Neutral matte display floor.
T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;A=u.EditorAssetLibrary
mat=u.load_asset('/Game/Elrhun/Golems/Materials/M_ReviewFloor')
if not mat:
 mat=T.create_asset('M_ReviewFloor','/Game/Elrhun/Golems/Materials',u.Material,u.MaterialFactoryNew())
 color=M.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-200,0)
 color.set_editor_property('constant',u.LinearColor(.18,.20,.23,1));M.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
 M.recompile_material(mat);A.save_loaded_asset(mat)
for a in actors:
 if a.get_actor_label() in ('Review floor','Raised review platform'):a.get_editor_property('static_mesh_component').set_material(0,mat)
u.SystemLibrary.execute_console_command(world,'r.EyeAdaptationQuality 2')
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
if hasattr(u.EditorLevelLibrary,'editor_set_game_view'):u.EditorLevelLibrary.editor_set_game_view(True)
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle)
 u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
(root/'Saved/golem_light_calibrated.json').write_text(json.dumps({'saved':True,'manual_exposure_bias':-1,'sun_lux':1.5,'key_lumens':250,'fill_lumens':120}))
