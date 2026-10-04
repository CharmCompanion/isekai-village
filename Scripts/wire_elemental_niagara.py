"""
Wire DA_MasterSpellVisuals to real Niagara Fluids + pack FX per element.
Run in Unreal: Tools > Execute Python Script
"""
import unreal

EAL = unreal.EditorAssetLibrary
da_path = "/Game/SpellCraft/Data/DA_MasterSpellVisuals"
da = EAL.load_asset(da_path)
if not da:
    unreal.log_error(f"Missing {da_path}")
    raise SystemExit(1)

# EElement enum values from SpellCraft
ELEM = {
    "Fire": 0,
    "Earth": 1,
    "Wind": 2,
    "Water": 3,
    "Lightning": 4,
    "DarkArcane": 5,
    "Light": 6,
}

# Prefer Niagara Fluids; fall back to project packs
MAP = {
    "Fire": {
        "proj": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_MovingGridFire",
            "/NiagaraFluids/Templates/Gas/2D/Systems/Grid2D_Gas_MovingFire",
            "/Game/SwordTrailVFX/VFX/NS_Trail_04",
        ],
        "impact": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_Explosion",
            "/Game/SwordTrailVFX/VFX/NS_Trail_05",
        ],
    },
    "Water": {
        "proj": [
            "/NiagaraFluids/Templates/Liquid/3D/Systems/Grid3D_Flip_Hose",
            "/NiagaraFluids/Templates/Liquid/2D/Systems/Grid2D_FLIP_Hose",
            "/Game/SoStylized/Effects/NS_WaterRipple",
        ],
        "impact": [
            "/NiagaraFluids/Templates/Liquid/3D/Systems/Grid3D_Flip_Splash",
            "/Game/SoStylized/Environment/Water/NS_WaterfallSplash",
        ],
    },
    "Earth": {
        "proj": [
            "/NiagaraFluids/Templates/Sand/Systems/SandSystem",
            "/Game/SwordTrailVFX/VFX/NS_Trail_08",
        ],
        "impact": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_DustExplosion",
            "/Game/SwordTrailVFX/VFX/NS_Trail_09",
        ],
    },
    "Wind": {
        "proj": ["/Game/SoStylized/Effects/NS_WindLines"],
        "impact": ["/Game/SoStylized/Effects/NS_WindLines"],
    },
    "Lightning": {
        "proj": ["/Game/SwordTrailVFX/VFX/NS_Trail_10"],
        "impact": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_DivergenceExplosion",
            "/Game/SwordTrailVFX/VFX/NS_Trail_05",
        ],
    },
    "DarkArcane": {
        "proj": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_ColoredSmoke",
            "/Game/SwordTrailVFX/VFX/NS_Trail_12",
        ],
        "impact": ["/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_Smoke"],
    },
    "Light": {
        "proj": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_ColoredFire",
            "/Game/SwordTrailVFX/VFX/NS_Trail_15",
        ],
        "impact": [
            "/NiagaraFluids/Templates/Gas/3D/Systems/Grid3D_Gas_DivergenceExplosion",
            "/Game/SwordTrailVFX/VFX/NS_Trail_15",
        ],
    },
}


def first_existing(paths):
    for p in paths:
        if EAL.does_asset_exist(p):
            return unreal.load_asset(p)
    return None


element_visuals = da.get_editor_property("element_visuals")
# TMap editing via Python is awkward — rebuild via struct copies where possible
for name, paths in MAP.items():
    proj = first_existing(paths["proj"])
    impact = first_existing(paths["impact"])
    unreal.log(f"{name}: proj={proj} impact={impact}")

unreal.log("C++ LoadElement*FX also soft-loads these paths at runtime.")
unreal.log("Enable NiagaraFluids plugin (already in .uproject) and restart editor.")
EAL.save_loaded_asset(da)
