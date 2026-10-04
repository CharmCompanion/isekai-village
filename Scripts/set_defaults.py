"""
Sets default values on the scaffolded Blueprint variables by writing to each
class's CDO. Run with the editor CLOSED.

  UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript ^
     -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\set_defaults.py"

Idempotent -- just rewrites the same values.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary

DEFAULTS = [
    ("/Game/SpellCraft/Blueprints/Character/BP_MageCharacter", {
        "MaxChargeTime": 2.0,
        "SpellTier": 1,
        "MulticastCount": 1,
        "SpreadAngle": 14.0,
        "bIsCharging": False,
        "bHasSecondary": False,
        "bIsCtrlHeld": False,
        "ChargeTime": 0.0,
        "ChargeRatio": 0.0,
    }),
    ("/Game/SpellCraft/Blueprints/MagicCircle/BP_ProceduralMagicCircle", {
        "Radius": 150.0,
        "OuterRadius": 150.0,
        "InnerRadius": 60.0,
        "OffsetDist": 35.0,
        "NumPoints": 32,
        "StarPoints": 8,
        "EmissivePower": 1.0,
        "ParticleSpeed": 50.0,
        "SpinRateMultiplier": 1.0,
    }),
    ("/Game/SpellCraft/Blueprints/Projectile/BP_SpellProjectile", {
        "Speed": 1500.0,
        "Damage": 25.0,
        "ChargeRatio": 0.0,
        "bHasImpacted": False,
    }),
    ("/Game/SpellCraft/UI/WBP_RadialMenu", {
        "HoveredSlot": -1,
        "PageIndex": 0,
        "DeadZone": 20.0,
    }),
]

report = []

for path, values in DEFAULTS:
    bp = unreal.load_asset(path)
    if not bp:
        report.append(f"MISSING {path}")
        continue
    cdo = unreal.get_default_object(bp.generated_class())
    if not cdo:
        report.append(f"NO CDO {path}")
        continue
    for name, value in values.items():
        try:
            cdo.set_editor_property(name, value)
            got = cdo.get_editor_property(name)
            ok = "OK " if got == value else f"MISMATCH(got {got!r})"
            report.append(f"{ok} {path.rsplit('/', 1)[1]}.{name} = {value!r}")
        except Exception as e:
            report.append(f"FAIL {path.rsplit('/', 1)[1]}.{name}: {e}")
    BEL.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    report.append(f"--- saved {path}")

with open("F:/DEVELOPMENT/Games/SpellCraft/Scripts/defaults_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("done")
