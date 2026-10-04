"""
Clean and recreate SpellCraft Blueprints to properly inherit from C++ classes without variable/function conflicts.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
ATH = unreal.AssetToolsHelpers.get_asset_tools()

BLUEPRINTS_TO_RECREATE = [
    {
        "name": "BP_MageCharacter",
        "path": "/Game/SpellCraft/Blueprints/Character",
        "parent": unreal.SpellCraftCharacter
    },
    {
        "name": "BP_ProceduralMagicCircle",
        "path": "/Game/SpellCraft/Blueprints/MagicCircle",
        "parent": unreal.ProceduralMagicCircle
    },
    {
        "name": "BP_SpellProjectile",
        "path": "/Game/SpellCraft/Blueprints/Projectile",
        "parent": unreal.SpellProjectile
    }
]

for bp_info in BLUEPRINTS_TO_RECREATE:
    full_path = f"{bp_info['path']}/{bp_info['name']}"
    unreal.log(f"Processing: {full_path}")
    
    # If asset exists, delete it so we can create a clean fresh Blueprint inheriting directly from C++
    if EAL.does_asset_exist(full_path):
        EAL.delete_asset(full_path)
        unreal.log(f"  Deleted old conflicting asset: {full_path}")

    # Create fresh Blueprint factory
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", bp_info["parent"])

    new_bp = ATH.create_asset(bp_info["name"], bp_info["path"], unreal.Blueprint, factory)
    if new_bp:
        BEL.compile_blueprint(new_bp)
        EAL.save_loaded_asset(new_bp)
        unreal.log(f"  Successfully created and compiled clean C++ child blueprint: {full_path}")
    else:
        unreal.log_error(f"  Failed to create blueprint: {full_path}")

unreal.log("=== Blueprint cleanup and recreation complete! ===")
