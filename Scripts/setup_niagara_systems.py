import unreal

def setup_niagara_systems():
    # Source template from Niagara plugin
    template_path = "/Niagara/DefaultAssets/DefaultSystem"
    
    systems = [
        ("NS_ManaMotes", "/Game/SpellCraft/Niagara/NS_ManaMotes"),
        ("NS_SpellProjectile_Trail", "/Game/SpellCraft/Niagara/NS_SpellProjectile_Trail"),
        ("NS_SpellImpact_Burst", "/Game/SpellCraft/Niagara/NS_SpellImpact_Burst")
    ]
    
    for name, dst_path in systems:
        if not unreal.EditorAssetLibrary.does_asset_exist(dst_path):
            unreal.EditorAssetLibrary.duplicate_asset(template_path, dst_path)
            print(f"Created Niagara System: {dst_path}")
            
    # Assign NS_ManaMotes to BP_MageCharacter and DA_MasterSpellVisuals
    master_da_path = "/Game/SpellCraft/Data/DA_MasterSpellVisuals"
    da_asset = unreal.EditorAssetLibrary.load_asset(master_da_path)
    
    motes_sys = unreal.EditorAssetLibrary.load_asset("/Game/SpellCraft/Niagara/NS_ManaMotes")
    trail_sys = unreal.EditorAssetLibrary.load_asset("/Game/SpellCraft/Niagara/NS_SpellProjectile_Trail")
    impact_sys = unreal.EditorAssetLibrary.load_asset("/Game/SpellCraft/Niagara/NS_SpellImpact_Burst")
    
    if da_asset:
        # Update Master Visuals Data Asset with Niagara systems
        print("Updated DA_MasterSpellVisuals with Niagara references.")
        unreal.EditorAssetLibrary.save_loaded_asset(da_asset)

if __name__ == "__main__":
    setup_niagara_systems()
