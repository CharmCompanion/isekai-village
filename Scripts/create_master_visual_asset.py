"""
Creates DA_MasterSpellVisuals in /Game/SpellCraft/Data/ and assigns it to BP_MageCharacter.
"""
import unreal

EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary
AssetTools = unreal.AssetToolsHelpers.get_asset_tools()

folder_path = "/Game/SpellCraft/Data"
asset_name = "DA_MasterSpellVisuals"
package_path = f"{folder_path}/{asset_name}"

# Create Data Asset if not already existing
if not EAL.does_asset_exist(package_path):
    data_asset_class = unreal.load_class(None, "/Script/SpellCraft.SpellVisualDataAsset")
    if data_asset_class:
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", data_asset_class)
        new_asset = AssetTools.create_asset(asset_name, folder_path, data_asset_class, factory)
        if new_asset:
            unreal.log(f"Successfully created Master Data Asset at {package_path}")
            EAL.save_loaded_asset(new_asset)

# Assign to BP_MageCharacter
bp_path = "/Game/SpellCraft/Blueprints/Character/BP_MageCharacter"
bp = unreal.load_asset(bp_path)
da = unreal.load_asset(package_path)

if bp and da:
    gen_class = bp.generated_class()
    cdo = unreal.get_default_object(gen_class)
    if cdo:
        try:
            cdo.set_editor_property("spell_visuals", da)
            unreal.log("Assigned DA_MasterSpellVisuals to BP_MageCharacter!")
        except Exception as e:
            unreal.log(f"Property assign notice: {e}")
            
    BEL.compile_blueprint(bp)
    EAL.save_loaded_asset(bp)

unreal.log("=== Master Visual Data Asset Ready ===")
