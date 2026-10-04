import unreal
import os

def reimport_and_update_all():
    elements = ["Master", "Fire", "Earth", "Wind", "Water", "Lightning", "DarkArcane", "Light", "Fusion"]
    tasks = []
    
    for el in elements:
        png_path = f"F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/T_MagicCircle_{el}.png"
        if os.path.exists(png_path):
            task = unreal.AssetImportTask()
            task.filename = png_path
            task.destination_path = "/Game/SpellCraft/Textures"
            task.destination_name = f"T_MagicCircle_{el}"
            task.replace_existing = True
            task.automated = True
            task.save = True
            tasks.append(task)

    if tasks:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        print(f"Successfully re-imported {len(tasks)} element textures with distinctive center symbols!")

if __name__ == "__main__":
    reimport_and_update_all()
