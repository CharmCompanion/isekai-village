"""
Headless Blueprint scaffolding for SpellCraft (Anime Mage spell system).
Run via: UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript -script=Scripts/generate_blueprints.py

Creates the Blueprint class shells + wires their components per
unreal_anime_mage_master_spec.md.

Run this FIRST, then Scripts/scaffold_blueprints.py, which adds the member
variables, event overrides, and function graphs to these classes.

Idempotent: re-running skips Blueprints that already exist, and only wires
components on classes it actually creates (never re-adds components to an
existing Blueprint, which would create duplicates).
"""
import unreal

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def create_blueprint(name, package_path, parent_class):
    """Returns (blueprint, was_created)."""
    full_path = f"{package_path}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        unreal.log(f"[skip] {full_path} already exists")
        return unreal.load_asset(full_path), False
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", parent_class)
    bp = asset_tools.create_asset(name, package_path, None, factory)
    unreal.log(f"[create] {full_path}")
    return bp, True


def add_component(bp, comp_class, comp_name):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root_handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
    if not root_handles:
        unreal.log_warning(f"    no root handle found on {bp.get_name()}, skipping component {comp_name}")
        return
    params = unreal.AddNewSubobjectParams(
        parent_handle=root_handles[0],
        new_class=comp_class,
        blueprint_context=bp
    )
    sub_handle, fail_reason = subsystem.add_new_subobject(params)
    if str(fail_reason):
        unreal.log_warning(f"    add_component {comp_name} failed: {fail_reason}")
        return
    subsystem.rename_subobject(sub_handle, unreal.Text(comp_name))
    unreal.log(f"    add_component {comp_name} ({comp_class.__name__})")


# --- 1. BP_MageCharacter -------------------------------------------------
mage_parent_bp = unreal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
mage_parent = mage_parent_bp.generated_class() if mage_parent_bp else unreal.Character
bp_mage, created_mage = create_blueprint("BP_MageCharacter", "/Game/SpellCraft/Blueprints/Character", mage_parent)
if bp_mage and created_mage:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp_mage)
    unreal.EditorAssetLibrary.save_loaded_asset(bp_mage)

# --- 2. BP_ProceduralMagicCircle -----------------------------------------
bp_circle, created_circle = create_blueprint("BP_ProceduralMagicCircle", "/Game/SpellCraft/Blueprints/MagicCircle", unreal.Actor)
if bp_circle and created_circle:
    add_component(bp_circle, unreal.SplineComponent, "MagicCircleSpline")
    add_component(bp_circle, unreal.NiagaraComponent, "MagicCircleVFX")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp_circle)
    unreal.EditorAssetLibrary.save_loaded_asset(bp_circle)

# --- 3. BP_SpellProjectile ------------------------------------------------
bp_proj, created_proj = create_blueprint("BP_SpellProjectile", "/Game/SpellCraft/Blueprints/Projectile", unreal.Actor)
if bp_proj and created_proj:
    add_component(bp_proj, unreal.SphereComponent, "CollisionSphere")
    add_component(bp_proj, unreal.ProjectileMovementComponent, "ProjectileMovement")
    add_component(bp_proj, unreal.NiagaraComponent, "ProjectileVFX")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp_proj)
    unreal.EditorAssetLibrary.save_loaded_asset(bp_proj)

# --- 4. WBP_RadialMenu -----------------------------------------------------
widget_factory = unreal.WidgetBlueprintFactory()
widget_path = "/Game/SpellCraft/UI/WBP_RadialMenu"
if unreal.EditorAssetLibrary.does_asset_exist(widget_path):
    unreal.log(f"[skip] {widget_path} already exists")
    bp_widget, created_widget = unreal.load_asset(widget_path), False
else:
    bp_widget = asset_tools.create_asset("WBP_RadialMenu", "/Game/SpellCraft/UI", None, widget_factory)
    created_widget = True
    unreal.log(f"[create] {widget_path}")
if bp_widget and created_widget:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp_widget)
    unreal.EditorAssetLibrary.save_loaded_asset(bp_widget)

unreal.log("=== SpellCraft blueprint scaffolding complete ===")
