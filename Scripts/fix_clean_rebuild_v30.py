from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/prepare_civilized_world_v30.py');s=p.read_text().replace(".read_text().split('# Remaining branches')[0],'local water'", ".read_text().split('# Remaining branches')[0].replace('from world_reference_v30 import global_height',''),'local water'");p.write_text(s)
