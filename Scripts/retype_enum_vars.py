"""
Retypes the placeholder `byte` variables to the real EElement / EFusionType
enums, and adds GrimoireSlots as an array of FSpellCircleConfig.
Run with the editor CLOSED.

  UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript ^
     -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\retype_enum_vars.py"
"""
import unreal

BEL = unreal.BlueprintEditorLibrary

P_ELEMENT = "/Game/SpellCraft/EElement"
P_FUSION = "/Game/SpellCraft/EFusionType"
P_CONFIG = "/Game/SpellCraft/FSpellCircleConfig"

report = []


def enum_pin(enum_asset):
    """Blueprint enum variables are PinCategory=byte + PinSubCategoryObject=<enum>."""
    path = enum_asset.get_path_name()
    p = unreal.EdGraphPinType()
    ok = p.import_text(
        f'(PinCategory="byte",PinSubCategoryObject='
        f'/Script/Engine.UserDefinedEnum\'"{path}"\')'
    )
    if not ok or 'PinSubCategoryObject=None' in p.export_text():
        return None
    return p


elem = unreal.load_asset(P_ELEMENT)
fusion = unreal.load_asset(P_FUSION)
config = unreal.load_asset(P_CONFIG)
report.append(f"EElement: {elem}")
report.append(f"EFusionType: {fusion}")
report.append(f"FSpellCircleConfig: {config}")

pin_elem = enum_pin(elem) if elem else None
pin_fusion = enum_pin(fusion) if fusion else None
report.append(f"pin_elem built: {pin_elem is not None}")
report.append(f"pin_fusion built: {pin_fusion is not None}")

RETYPE = [
    ("/Game/SpellCraft/Blueprints/Character/BP_MageCharacter", "PrimaryElement", pin_elem),
    ("/Game/SpellCraft/Blueprints/Character/BP_MageCharacter", "SecondaryElement", pin_elem),
    ("/Game/SpellCraft/Blueprints/Projectile/BP_SpellProjectile", "ElementType", pin_elem),
    ("/Game/SpellCraft/Blueprints/Projectile/BP_SpellProjectile", "FusionType", pin_fusion),
]

touched = set()

for path, var, new_type in RETYPE:
    if new_type is None:
        report.append(f"SKIP {var}: pin type unavailable")
        continue
    bp = unreal.load_asset(path)
    try:
        # NOTE: change_member_variable_type returns void, not a success bool --
        # verify by reading the type back instead of trusting a return value.
        BEL.change_member_variable_type(bp, var, new_type)
        after = BEL.get_member_variable_type(bp, var)
        txt = after.export_text() if after else ""
        applied = "PinSubCategoryObject=" in txt and "PinSubCategoryObject=None" not in txt
        sub = txt.split("PinSubCategoryObject=")[1].split(",")[0] if applied else "<not applied>"
        report.append(f"{'OK ' if applied else 'FAIL'} retype {var} -> {sub}")
        touched.add(path)
    except Exception as e:
        report.append(f"FAIL retype {var}: {e}")

# GrimoireSlots : Array<FSpellCircleConfig>
P_MAGE = "/Game/SpellCraft/Blueprints/Character/BP_MageCharacter"
if config:
    bp = unreal.load_asset(P_MAGE)
    existing = {str(n) for n in BEL.list_member_variable_names(bp)}
    if "GrimoireSlots" in existing:
        report.append("SKIP GrimoireSlots: already exists")
    else:
        try:
            arr = BEL.get_array_type(BEL.get_struct_type(config))
            ok = BEL.add_member_variable(bp, "GrimoireSlots", arr)
            report.append(f"{'OK ' if ok else 'FAIL'} add GrimoireSlots (Array<FSpellCircleConfig>)")
            touched.add(P_MAGE)
        except Exception as e:
            report.append(f"FAIL GrimoireSlots: {e}")

for path in touched:
    bp = unreal.load_asset(path)
    BEL.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    report.append(f"--- saved {path}")

with open("F:/DEVELOPMENT/Games/SpellCraft/Scripts/retype_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(str(r) for r in report))
print("done")
