import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
opts=unreal.MergeStaticMeshActorsOptions()
(O/'merge_options.txt').write_text(str(opts))
