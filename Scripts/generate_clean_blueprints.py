import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
ATH = unreal.AssetToolsHelpers.get_asset_tools()

BLUEPRINTS_TO_CREATE = [
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

for bp_info in BLUEPRINTS_TO_CREATE:
    full_path = f"{bp_info['path']}/{bp_info['name']}"
    unreal.log(f"Creating Blueprint: {full_path}")

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", bp_info["parent"])

    new_bp = ATH.create_asset(bp_info["name"], bp_info["path"], unreal.Blueprint, factory)
    if new_bp:
        BEL.compile_blueprint(new_bp)
        EAL.save_loaded_asset(new_bp)
        unreal.log(f"  Successfully created, compiled, and saved: {full_path}")
    else:
        unreal.log_error(f"  Failed to create: {full_path}")

unreal.log("=== All Blueprints successfully generated without errors! ===")
