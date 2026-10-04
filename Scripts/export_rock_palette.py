import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');paths=['/Game/SoStylized/Environment/Rocks/Textures/Classic/T_RockClassic_Rocks_BC','/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC']
for path in paths:
 t=unreal.AssetExportTask();t.object=unreal.load_asset(path);t.filename=str(B/'Saved/AdventureWorldSource'/(path.split('/')[-1]+'.png'));t.automated=True;t.prompt=False;t.replace_identical=True;t.exporter=unreal.TextureExporterPNG();assert unreal.Exporter.run_asset_export_task(t)
