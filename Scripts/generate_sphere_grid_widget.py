"""
Create WBP_SphereGrid parented to the C++ SphereGridWidget.
Run after the C++ module is compiled:

UnrealEditor-Cmd.exe IsekaiVillage.uproject -run=pythonscript -script=Scripts/generate_sphere_grid_widget.py
"""
import unreal

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
package_path = "/Game/IsekaiVillage/UI"
asset_name = "WBP_SphereGrid"
full_path = f"{package_path}/{asset_name}"

if unreal.EditorAssetLibrary.does_asset_exist(full_path):
    unreal.log(f"[skip] {full_path} already exists")
else:
    parent = unreal.load_class(None, "/Script/IsekaiVillage.SphereGridWidget")
    factory = unreal.WidgetBlueprintFactory()
    if parent:
        factory.set_editor_property("ParentClass", parent)
    widget = asset_tools.create_asset(asset_name, package_path, None, factory)
    if widget:
        unreal.BlueprintEditorLibrary.compile_blueprint(widget)
        unreal.EditorAssetLibrary.save_loaded_asset(widget)
        unreal.log(f"[create] {full_path}")
    else:
        unreal.log_warning("Failed to create WBP_SphereGrid")
