import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
d={'actors':[(a.get_actor_label(),str(a.get_folder_path())) for a in E.get_all_level_actors() if 'Harbor' in str(a.get_folder_path()) or 'Sea' in a.get_actor_label()],'cloud':{},'landscape':{}}
mesh=unreal.load_asset('/Game/StylizedSkymap/meshes/sky/SM_cloud');b=mesh.get_bounding_box();d['cloud']['bounds']=str(b);d['cloud']['materials']=[str(m.material_interface) for m in mesh.static_materials]
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
for p in ['target_layers','editor_layer_settings']:
 try:d['landscape'][p]=str(land.get_editor_property(p))
 except Exception as e:d['landscape'][p]=str(e)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/floating_asset_audit.json').write_text(json.dumps(d,indent=2))
