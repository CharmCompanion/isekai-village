"""
Adds the generator-derived layer model to BP_ProceduralMagicCircle
(see Docs/magic_circle_system.md sections 2-4 and 8).

Run with the editor CLOSED:
  UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript ^
     -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\add_circle_layer_vars.py"

Idempotent: skips variables that already exist.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
CIRCLE = "/Game/SpellCraft/Blueprints/MagicCircle/BP_ProceduralMagicCircle"
P_ELEMENT = "/Game/SpellCraft/EElement"

report = []


def pin(text):
    p = unreal.EdGraphPinType()
    if not p.import_text(text):
        return None
    return p


BOOL = '(PinCategory="bool")'
INT = '(PinCategory="int")'
DOUBLE = '(PinCategory="real",PinSubCategory="double")'
INT_ARRAY = '(PinCategory="int",ContainerType=Array)'


def enum_pin(asset):
    return pin(
        f'(PinCategory="byte",PinSubCategoryObject='
        f'/Script/Engine.UserDefinedEnum\'"{asset.get_path_name()}"\')'
    )


# name -> pin type text (or callable returning a pin)
VARS = [
    # --- layer geometry (Docs section 2) ---
    ("SymmetryCount", INT),
    ("ConnectPointsSkip", INT),
    ("SectionSize", DOUBLE),
    ("LineWidth", DOUBLE),
    ("Rotation", DOUBLE),
    ("RotationSpeed", DOUBLE),
    ("ParentPointIndex", INT),
    # --- feature toggles (Docs section 4) ---
    ("bOuterRing", BOOL),
    ("bConnectBorder", BOOL),
    ("bConnectPoints", BOOL),
    ("bConnectMidPoints", BOOL),
    ("bLinesToCenter", BOOL),
    ("bInscribePoints", BOOL),
    ("bDoubleInscribedPoints", BOOL),
    ("bSymbolsAtPoints", BOOL),
    ("bDrawTextRing", BOOL),
    # --- element -> shape lookup (Docs section 8) ---
    ("ElementSymmetry", INT_ARRAY),
    ("ElementSkip", INT_ARRAY),
]

bp = unreal.load_asset(CIRCLE)
elem_asset = unreal.load_asset(P_ELEMENT)
existing = {str(n) for n in BEL.list_member_variable_names(bp)}

# Element enum var, so the circle knows which shape to build.
if "Element" in existing:
    report.append("skip Element (exists)")
else:
    ep = enum_pin(elem_asset)
    if ep:
        BEL.add_member_variable(bp, "Element", ep)
        report.append("add  Element (EElement)")
    else:
        report.append("FAIL Element: could not build enum pin")

for name, spec in VARS:
    if name in existing:
        report.append(f"skip {name} (exists)")
        continue
    p = pin(spec)
    if not p:
        report.append(f"FAIL {name}: bad pin spec")
        continue
    BEL.add_member_variable(bp, name, p)
    report.append(f"add  {name}")

BEL.compile_blueprint(bp)

# --- defaults -------------------------------------------------------------
# Lookup tables are indexed by EElement value:
#   Fire 0, Earth 1, Water 2, Wind 3, Light 4, Dark 5, Lightning 6, Arcane 7
DEFAULTS = {
    "SymmetryCount": 6,
    "ConnectPointsSkip": 1,
    "SectionSize": 94.0,
    "LineWidth": 7.0,
    "Rotation": 0.0,
    "RotationSpeed": 1.0,
    "ParentPointIndex": -1,
    "bOuterRing": True,
    "bConnectBorder": False,
    "bConnectPoints": True,
    "bConnectMidPoints": False,
    "bLinesToCenter": False,
    "bInscribePoints": False,
    "bDoubleInscribedPoints": False,
    "bSymbolsAtPoints": False,
    "bDrawTextRing": False,
    "ElementSymmetry": [3, 4, 6, 5, 10, 8, 7, 9],
    "ElementSkip": [1, 1, 1, 1, 1, 1, 3, 1],
}

cdo = unreal.get_default_object(bp.generated_class())
for name, value in DEFAULTS.items():
    try:
        cdo.set_editor_property(name, value)
        got = cdo.get_editor_property(name)
        got = list(got) if hasattr(got, "__iter__") and not isinstance(got, str) else got
        report.append(f"{'OK  ' if got == value else f'MISMATCH({got!r})'} {name} = {value!r}")
    except Exception as e:
        report.append(f"FAIL default {name}: {e}")

BEL.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
report.append("--- saved")

with open("F:/DEVELOPMENT/Games/SpellCraft/Scripts/circle_vars_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(str(r) for r in report))
print("done")
