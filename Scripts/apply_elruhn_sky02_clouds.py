"""Set the cloud deck below the lowest visible rock and soften the painted accents."""
from pathlib import Path
import json,unreal
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
cloud=next(a for a in actors if a.get_actor_label()=='Cloud Sea | continuous sculpted volume')
component=cloud.get_component_by_class(unreal.VolumetricCloudComponent)
component.set_editor_property('layer_bottom_altitude',3.5)
component.set_editor_property('layer_height',1.38)
mat=component.get_editor_property('material'); editing=unreal.MaterialEditingLibrary
for name,value in [('Cloud_GlobalCoverage',.10),('Cloud_GlobalDensity',.016),('Layout_CloudGlobalScale',88.)]:
 editing.set_material_instance_scalar_parameter_value(mat,name,value)
editing.set_material_instance_vector_parameter_value(mat,'Cloud_AlbedoColor',unreal.LinearColor(.76,.84,.95,1))
editing.update_material_instance(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
for i in range(1,4):
 paint=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/ElRuhnSky01/Materials/MI_ES01_Cloud'+str(i))
 editing.set_material_instance_scalar_parameter_value(paint,'Opacity',.57)
 editing.set_material_instance_vector_parameter_value(paint,'Tint',unreal.LinearColor(.60,.72,.87,1));editing.update_material_instance(paint);unreal.EditorAssetLibrary.save_loaded_asset(paint)
bed=next(a for a in actors if a.get_actor_label()=='Cloud Sea | distant horizon haze')
bed.set_actor_location(unreal.Vector(0,0,-276000),False,False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(root/'ArtSource/World/ElRuhnSky02/clouds.json').write_text(json.dumps({'volume_top_m':-1120,'volume_bottom_m':-2500,'rock_tip_m':-884,'clearance_m':236},indent=2))
