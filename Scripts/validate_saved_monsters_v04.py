import unreal
from pathlib import Path
unreal.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/Monsters/Refined_v04/Maps/Map_MonsterReview_v04')
source=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/validate_monsters_unreal_v04.py')
exec(compile(source.read_text(),str(source),'exec'))
