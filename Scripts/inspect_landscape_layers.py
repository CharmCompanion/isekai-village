import unreal,json
from pathlib import Path
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.Landscape))
out={'layers':str(land.get_edit_layers_bp()),'weightmap':land.render_weightmap.__doc__,'targets':str(land.get_target_layer_names(True))}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/layer_details.json').write_text(json.dumps(out,indent=2))
