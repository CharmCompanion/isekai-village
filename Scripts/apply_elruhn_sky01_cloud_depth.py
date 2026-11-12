"""Continuous volume beneath the stylized cloud accents, private new-map settings."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';D='/Game/IsekaiVillage/AdventureWorld/ElRuhnSky01';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
path=D+'/Materials/MI_ES01_CloudVolume';mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst',path)
for name,value in [('Cloud_GlobalCoverage',.62),('Cloud_GlobalDensity',.045),('Layout_CloudGlobalScale',32.)]:M.set_material_instance_scalar_parameter_value(mat,name,value)
M.set_material_instance_vector_parameter_value(mat,'Cloud_AlbedoColor',unreal.LinearColor(.89,.94,1,1));M.set_material_instance_vector_parameter_value(mat,'Layout_WindControls',unreal.LinearColor(.3,.1,.1,.3));A.save_loaded_asset(mat)
a=next((a for a in E.get_all_level_actors() if isinstance(a,unreal.VolumetricCloud)),None)
if not a:a=E.spawn_actor_from_class(unreal.VolumetricCloud,unreal.Vector(0,0,0))
a.set_actor_label('Cloud Sea | continuous sculpted volume');a.set_folder_path('El Ruhn Sky/Cloud Sea');a.tags=['ElRuhnSkyVolume01'];c=a.get_component_by_class(unreal.VolumetricCloudComponent)
for key,val in [('material',mat),('layer_bottom_altitude',4.3),('layer_height',.85),('tracing_start_max_distance',100.),('tracing_max_distance',60.),('view_sample_count_scale',2.),('shadow_view_sample_count_scale',1.),('sky_light_cloud_bottom_occlusion',.4)]:c.set_editor_property(key,val)
for a in E.get_all_level_actors():
 if a.get_actor_label().startswith('Cloud Sea | painted bank '):
  # Painted silhouettes become accents within the deeper cloud layer, never opaque cover plates.
  a.static_mesh_component.set_cast_shadow(False)
  p=a.get_actor_location();a.set_actor_location(unreal.Vector(p.x,p.y,p.z-13000),False,False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'cloud_depth.json').write_text(json.dumps({'status':'saved','volume_bottom_world_m':-1700,'volume_top_world_m':-850,'material':path,'cloud_coverage':.62,'depth_km':.85},indent=2))
