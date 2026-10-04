"""
SpellCraft Blueprint scaffolding -- variables, event nodes, function graph stubs.
Run with the editor CLOSED:

  UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript ^
     -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\scaffold_blueprints.py"

What this does (all of it is scriptable in UE 5.8):
  * adds typed member variables to the 4 Blueprints
  * adds event override nodes (BeginPlay / Tick)
  * creates named, empty function graphs

What it deliberately does NOT do:
  * fill function graphs with logic nodes -- UE 5.8 exposes no generic node-spawn
    API to Python, so the bodies must be built in-editor. See
    Docs/blueprint_setup_checklist.md for the node-by-node instructions.
  * populate EElement / EFusionType / FSpellCircleConfig -- UserDefinedEnum and
    UserDefinedStruct have no Python API for adding entries/members. Element
    variables are typed `byte` here; retype them once the enums are filled in.

Idempotent: re-running skips anything that already exists.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary

# --- pin type helpers -----------------------------------------------------
# NOTE: get_basic_type_by_name silently returns `int` for "double"/"float"/
# "vector"/etc, so only use it for names verified to resolve correctly.
_SAFE_BASIC = {"bool", "int", "int64", "byte", "name", "string", "text"}


def pin(type_name):
    """Return an EdGraphPinType for a scalar type."""
    if type_name in _SAFE_BASIC:
        return BEL.get_basic_type_by_name(type_name)
    if type_name == "double":
        p = unreal.EdGraphPinType()
        p.import_text('(PinCategory="real",PinSubCategory="double")')
        return p
    raise ValueError(f"unhandled pin type: {type_name}")


def array_of(type_name):
    return BEL.get_array_type(pin(type_name))


def add_vars(bp, bp_label, specs):
    existing = {str(n) for n in BEL.list_member_variable_names(bp)}
    for var_name, pin_type in specs:
        if var_name in existing:
            unreal.log(f"  [skip var] {bp_label}.{var_name}")
            continue
        ok = BEL.add_member_variable(bp, var_name, pin_type)
        unreal.log(f"  [{'var' if ok else 'FAIL'}] {bp_label}.{var_name}")


def add_events(bp, bp_label, event_names):
    for ev in event_names:
        node = BEL.add_event_override(bp, ev, unreal.IntPoint(0, 0))
        unreal.log(f"  [{'event' if node else 'FAIL event'}] {bp_label}.{ev}")


def add_functions(bp, bp_label, func_names):
    existing = {str(n) for n in BEL.list_graph_names(bp)}
    for fn in func_names:
        if fn in existing:
            unreal.log(f"  [skip fn] {bp_label}.{fn}")
            continue
        graph = BEL.add_function_graph(bp, fn)
        unreal.log(f"  [{'fn' if graph else 'FAIL fn'}] {bp_label}.{fn}")


def finish(bp, path):
    BEL.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    unreal.log(f"  saved {path}")


# --- 1. BP_MageCharacter --------------------------------------------------
P_MAGE = "/Game/SpellCraft/Blueprints/Character/BP_MageCharacter"
bp = unreal.load_asset(P_MAGE)
if bp:
    unreal.log("BP_MageCharacter")
    add_vars(bp, "Mage", [
        ("bIsCharging",      pin("bool")),
        ("bHasSecondary",    pin("bool")),
        ("bIsCtrlHeld",      pin("bool")),
        ("ChargeTime",       pin("double")),
        ("MaxChargeTime",    pin("double")),
        ("ChargeRatio",      pin("double")),
        ("SpellTier",        pin("int")),
        ("MulticastCount",   pin("int")),
        ("SpreadAngle",      pin("double")),
        # byte until EElement enum is populated in-editor
        ("PrimaryElement",   pin("byte")),
        ("SecondaryElement", pin("byte")),
        ("ActiveSymbols",    array_of("name")),
    ])
    add_events(bp, "Mage", ["ReceiveBeginPlay", "ReceiveTick"])
    add_functions(bp, "Mage", [
        "FireMulticastBarrage",
        "UpdateMagicCircle",
        "GetAimDirectionFromMouse",
        "GetCompositeColor",
        "ComputeSpellTier",
        "AttachSymbol",
        "SaveGrimoireSlot",
        "LoadGrimoireSlot",
    ])
    finish(bp, P_MAGE)

# --- 2. BP_ProceduralMagicCircle -----------------------------------------
P_CIRCLE = "/Game/SpellCraft/Blueprints/MagicCircle/BP_ProceduralMagicCircle"
bp = unreal.load_asset(P_CIRCLE)
if bp:
    unreal.log("BP_ProceduralMagicCircle")
    add_vars(bp, "Circle", [
        ("Radius",             pin("double")),
        ("OuterRadius",        pin("double")),
        ("InnerRadius",        pin("double")),
        ("OffsetDist",         pin("double")),
        ("NumPoints",          pin("int")),
        ("StarPoints",         pin("int")),
        ("EmissivePower",      pin("double")),
        ("ParticleSpeed",      pin("double")),
        ("SpinRateMultiplier", pin("double")),
    ])
    add_functions(bp, "Circle", [
        "GenerateCircleSpline",
        "GenerateStarSpline",
        "GenerateDualCoreSplines",
        "UpdateNiagaraBindings",
    ])
    finish(bp, P_CIRCLE)

# --- 3. BP_SpellProjectile ------------------------------------------------
P_PROJ = "/Game/SpellCraft/Blueprints/Projectile/BP_SpellProjectile"
bp = unreal.load_asset(P_PROJ)
if bp:
    unreal.log("BP_SpellProjectile")
    add_vars(bp, "Proj", [
        ("ElementType",  pin("byte")),   # -> EElement later
        ("FusionType",   pin("byte")),   # -> EFusionType later
        ("Speed",        pin("double")),
        ("Damage",       pin("double")),
        ("ChargeRatio",  pin("double")),
        ("bHasImpacted", pin("bool")),
    ])
    add_events(bp, "Proj", ["ReceiveBeginPlay"])
    add_functions(bp, "Proj", [
        "ApplyElementalPhysics",
        "HandleImpact",
        "SpawnImpactFX",
    ])
    finish(bp, P_PROJ)

# --- 4. WBP_RadialMenu ----------------------------------------------------
P_UI = "/Game/SpellCraft/UI/WBP_RadialMenu"
bp = unreal.load_asset(P_UI)
if bp:
    unreal.log("WBP_RadialMenu")
    add_vars(bp, "UI", [
        ("HoveredSlot", pin("int")),
        ("PageIndex",   pin("int")),
        ("DeadZone",    pin("double")),
    ])
    add_functions(bp, "UI", [
        "UpdateHoveredSlot",
        "CyclePage",
        "RefreshSlotIcons",
    ])
    finish(bp, P_UI)

unreal.log("=== SpellCraft scaffolding complete ===")
