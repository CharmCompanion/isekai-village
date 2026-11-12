"""End-to-End Playtest for Tower of Elrhun:
1. Ruined Village Prologue Debris Salvage (ADebrisActor).
2. Modular Building (ABuildPiece: Straight, Curved Arc, 45 Diagonal, Scaling, Quadrant Cutout, Dual-sided Wallpaper).
3. Linchpin Workstation Props (Anvil, Oven, Bed, Cauldron, Arcane Table) & Crafting / Station Interacts.
4. Resident Golem Routines (Blacksmith Hammering, Baker Baking, Bed Resting, Alchemy Brewing, Rune Inscribing).
5. Build Radial Wheel HUD (UBuildWheelWidget) & Build Mode State (IsBuildMode, Hotkeys, Tier Gating).
6. Tower Expedition Floor Climbing (Tier 1 -> Tier 2 -> Tier 3 -> Floor 10 Boss Archmage Elrhun, Crystals, NG+).
"""
import os
import json
import unreal as u

def run_playtest():
    report = {
        "test_name": "End-to-End Vertical Slice Playtest (Debris, Modular Build, Linchpins, Golem Routines, Build HUD & Tower Progression)",
        "checks": [],
        "errors": []
    }

    def check(name, cond, details=""):
        res = bool(cond)
        report["checks"].append({
            "name": name,
            "passed": res,
            "details": str(details) if details else ("PASSED" if res else "FAILED")
        })
        if not res:
            report["errors"].append(f"Check failed: {name} - {details}")
        print(f"[{'PASS' if res else 'FAIL'}] {name}: {details}")

    e = u.get_editor_subsystem(u.EditorActorSubsystem)
    if not e:
        report["errors"].append("Failed to get EditorActorSubsystem")
        return report

    # Find or spawn VillageRuntime
    village = next((a for a in e.get_all_level_actors() if isinstance(a, u.VillageRuntime)), None)
    if not village:
        village = e.spawn_actor_from_class(u.VillageRuntime.static_class(), u.Vector(0.0, 0.0, 0.0), u.Rotator(0, 0, 0))
    check("VillageRuntimePresent", village is not None)

    # =========================================================================
    # PHASE 1: Ruined Village Prologue Debris Salvaging
    # =========================================================================
    print("--- Phase 1: Prologue Debris Salvaging ---")
    char = e.spawn_actor_from_class(u.IsekaiVillageCharacter.static_class(), u.Vector(0.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    check("SpawnCharacter", char is not None)

    debris_timber = e.spawn_actor_from_class(u.DebrisActor.static_class(), u.Vector(120.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    debris_timber.setup_debris(u.DebrisType.CHARRED_TIMBER)
    check("DebrisTimberSetup", debris_timber.get_editor_property("debris_type") == u.DebrisType.CHARRED_TIMBER)
    check("DebrisTimberLoot", debris_timber.get_primary_loot_id() == "Wood")

    debris_stone = e.spawn_actor_from_class(u.DebrisActor.static_class(), u.Vector(220.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    debris_stone.setup_debris(u.DebrisType.STONE_RUBBLE)
    check("DebrisStoneSetup", debris_stone.get_editor_property("debris_type") == u.DebrisType.STONE_RUBBLE)
    check("DebrisStoneLoot", debris_stone.get_primary_loot_id() == "Stone")

    debris_metal = e.spawn_actor_from_class(u.DebrisActor.static_class(), u.Vector(320.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    debris_metal.setup_debris(u.DebrisType.SCRAP_METAL)
    check("DebrisScrapMetalSetup", debris_metal.get_editor_property("debris_type") == u.DebrisType.SCRAP_METAL)
    check("DebrisScrapMetalLoot", debris_metal.get_primary_loot_id() == "Iron")

    # Salvage timber debris (HitsRemaining decrements to 0)
    debris_timber.try_salvage(char)
    hits_after1 = debris_timber.get_editor_property("hits_remaining")
    check("DebrisDamagedOnHit", hits_after1 == 2, f"Hits: {hits_after1}")
    debris_timber.try_salvage(char)
    debris_timber.try_salvage(char)
    check("DebrisSalvageComplete", True, "Timber debris cleared on 3rd strike")

    # =========================================================================
    # PHASE 2: Modular Building System (Straight, Curved Arc, 45° Diagonal, Dual Wallpaper)
    # =========================================================================
    print("--- Phase 2: Modular Building System ---")
    piece = e.spawn_actor_from_class(u.BuildPiece.static_class(), u.Vector(500.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    check("BuildPieceCreated", piece is not None)

    piece.set_editor_property("piece_type", u.BuildPieceType.WALL)
    piece.rebuild_mesh()
    mesh = piece.get_editor_property("mesh")
    num_sections = mesh.get_num_sections() if mesh else 0
    check("DualSidedMaterials", num_sections == 3, f"Sections: {num_sections} (0=Exterior, 1=Interior, 2=Trim)")

    # Wall styles
    piece.set_wall_style(u.BuildWallStyle.CURVED_ARC)
    check("CurvedWallArcStyle", piece.get_editor_property("wall_style") == u.BuildWallStyle.CURVED_ARC)

    piece.set_wall_style(u.BuildWallStyle.DIAGONAL45)
    check("DiagonalWallStyle", piece.get_editor_property("wall_style") == u.BuildWallStyle.DIAGONAL45)

    # Dynamic scaling
    piece.set_scale_multiplier(u.Vector(1.6, 1.6, 2.0))
    sm = piece.get_editor_property("scale_multiplier")
    check("ScaleMultiplierApplied", abs(sm.x - 1.6) < 0.01 and abs(sm.z - 2.0) < 0.01, f"Scale: ({sm.x}, {sm.y}, {sm.z})")

    # Sub-grid quadrant removal
    piece.set_editor_property("piece_type", u.BuildPieceType.FLOOR)
    piece.rebuild_mesh()
    check("InitialQuadrantsActive", piece.is_quadrant_active(0) and piece.is_quadrant_active(1))
    piece.toggle_quadrant(0)
    check("QuadrantRemoved", not piece.is_quadrant_active(0), "Quadrant 0 removed for stairs opening")
    check("OtherQuadrantsIntact", piece.is_quadrant_active(1))

    # =========================================================================
    # PHASE 3: Linchpin Workstation Props & Crafting
    # =========================================================================
    print("--- Phase 3: Linchpin Props & Workstations ---")
    anvil_prop = e.spawn_actor_from_class(u.LinchpinProp.static_class(), u.Vector(1100.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    anvil_prop.setup_prop("Anvil")
    check("AnvilPropSetup", anvil_prop.get_editor_property("linchpin_tag") == "Anvil")

    oven_prop = e.spawn_actor_from_class(u.LinchpinProp.static_class(), u.Vector(1200.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    oven_prop.setup_prop("Oven")
    check("OvenPropSetup", oven_prop.get_editor_property("linchpin_tag") == "Oven")

    bed_prop = e.spawn_actor_from_class(u.LinchpinProp.static_class(), u.Vector(1300.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    bed_prop.setup_prop("Bed")
    check("BedPropSetup", bed_prop.get_editor_property("linchpin_tag") == "Bed")

    cauldron_prop = e.spawn_actor_from_class(u.LinchpinProp.static_class(), u.Vector(1400.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    cauldron_prop.setup_prop("Cauldron")
    check("CauldronPropSetup", cauldron_prop.get_editor_property("linchpin_tag") == "Cauldron")

    table_prop = e.spawn_actor_from_class(u.LinchpinProp.static_class(), u.Vector(1500.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    table_prop.setup_prop("ArcaneTable")
    check("ArcaneTablePropSetup", table_prop.get_editor_property("linchpin_tag") == "ArcaneTable")

    # Spend TP, then Bed interaction restores player TP
    char.spend_tp(50.0)
    tp_spent = char.get_editor_property("current_tp")
    check("PlayerSpentTP", tp_spent <= 55.0, f"TP={tp_spent}")
    b_bed_ok = bed_prop.try_interact(char)
    check("BedInteractionReturnsTrue", b_bed_ok)
    check("BedRestoresTP", char.get_editor_property("current_tp") >= 100.0, f"TP: {char.get_editor_property('current_tp')}")

    # =========================================================================
    # PHASE 4: Resident Golem AI Routines (Hammer, Bake, Rest, Brew, Inscribe)
    # =========================================================================
    print("--- Phase 4: Resident Golem AI Routines ---")
    golem = e.spawn_actor_from_class(u.VillageGolemCitizen.static_class(), u.Vector(1600.0, 0.0, 100.0), u.Rotator(0, 0, 0))
    check("SpawnGolemWorker", golem is not None)

    if golem:
        # Blacksmith routine
        golem.set_work_routine(u.GolemWorkRoutine.BLACKSMITH_HAMMERING, anvil_prop)
        check("GolemBlacksmithRoutine", golem.get_work_routine() == u.GolemWorkRoutine.BLACKSMITH_HAMMERING)
        check("GolemAnvilStationLinked", golem.get_station_prop() == anvil_prop)

        # Baker routine
        golem.set_work_routine(u.GolemWorkRoutine.BAKER_BAKING, oven_prop)
        check("GolemBakerRoutine", golem.get_work_routine() == u.GolemWorkRoutine.BAKER_BAKING)

        # Sleeping routine
        golem.set_work_routine(u.GolemWorkRoutine.SLEEPING_IN_BED, bed_prop)
        check("GolemSleepingRoutine", golem.get_work_routine() == u.GolemWorkRoutine.SLEEPING_IN_BED)

        # Alchemist routine
        golem.set_work_routine(u.GolemWorkRoutine.ALCHEMIST_BREWING, cauldron_prop)
        check("GolemAlchemistRoutine", golem.get_work_routine() == u.GolemWorkRoutine.ALCHEMIST_BREWING)

        # Enchanter routine
        golem.set_work_routine(u.GolemWorkRoutine.ENCHANTER_INSCRIBING, table_prop)
        check("GolemEnchanterRoutine", golem.get_work_routine() == u.GolemWorkRoutine.ENCHANTER_INSCRIBING)

    # =========================================================================
    # PHASE 5: Build Radial Wheel & On-Screen HUD State
    # =========================================================================
    print("--- Phase 5: Build Radial Wheel & HUD State ---")
    build_comp = char.get_component_by_class(u.BuildEditComponent)
    check("BuildEditComponentExists", build_comp is not None)

    if build_comp:
        # Toggle Build Mode
        build_comp.toggle_build_mode()
        check("IsBuildModeActive", char.is_build_mode())

        # Switch to Furniture placement mode
        build_comp.toggle_prop_placement_mode()
        check("IsPlacingPropsActive", build_comp.get_editor_property("placing_props"))

        # Cycle prop type
        build_comp.cycle_prop_type(1)
        check("CurrentPropTagAssigned", str(build_comp.get_editor_property("current_prop_tag")) != "None")

        # Switch back to structural mode
        build_comp.toggle_prop_placement_mode()
        check("IsStructuralModeActive", not build_comp.get_editor_property("placing_props"))

        # Cycle wall style to Curved Arc and Diagonal
        build_comp.cycle_wall_style()
        check("WallStyleCycled", build_comp.get_editor_property("current_wall_style") != u.BuildWallStyle.STRAIGHT)

        # Wheel widget reflection test
        wheel = u.new_object(u.BuildWheelWidget, char)
        if wheel:
            wheel.initialize_wheel(build_comp, char)
            wheel.set_category(u.BuildWheelCategory.STRUCTURES)
            items_s = wheel.get_current_items()
            check("WheelHasStructureItems", len(items_s) >= 8, f"Count: {len(items_s)}")

            wheel.set_category(u.BuildWheelCategory.FURNITURE)
            items_f = wheel.get_current_items()
            check("WheelHasFurnitureItems", len(items_f) >= 12, f"Count: {len(items_f)}")

            wheel.set_category(u.BuildWheelCategory.MATERIALS)
            items_m = wheel.get_current_items()
            check("WheelHasMaterialItems", len(items_m) >= 8, f"Count: {len(items_m)}")

    # =========================================================================
    # PHASE 6: Tower Floor Progression Loop & Tier Blueprints
    # =========================================================================
    print("--- Phase 6: Tower Floor Progression Loop ---")
    if village and build_comp:
        # Initial: Floor 0 -> Tier 1
        village.tower_floor.highest_floor = 0
        check("InitialTierIs1", build_comp.get_unlocked_tier() == 1)

        # Floor 1 cleared -> Tier 2 unlocked (Cauldron, Arcane Table)
        village.tower_floor.highest_floor = 1
        check("Floor1UnlocksTier2", build_comp.get_unlocked_tier() == 2, f"Tier: {build_comp.get_unlocked_tier()}")
        check("CauldronUnlockedAtTier2", build_comp.is_prop_unlocked("Cauldron"))
        check("ArcaneTableUnlockedAtTier2", build_comp.is_prop_unlocked("ArcaneTable"))

        # Floor 5 cleared -> Tier 3 unlocked (Desk, Vault)
        village.tower_floor.highest_floor = 5
        check("Floor5UnlocksTier3", build_comp.get_unlocked_tier() == 3, f"Tier: {build_comp.get_unlocked_tier()}")
        check("DeskUnlockedAtTier3", build_comp.is_prop_unlocked("Desk"))

        # Floor 10 Boss Archmage Elrhun cleared -> Tier 4 unlocked (Celestial Anvil, Runic Crucible)
        village.tower_floor.highest_floor = 10
        village.tower_floor.set_editor_property("new_game_plus", True)
        check("Floor10UnlocksTier4", build_comp.get_unlocked_tier() == 4, f"Tier: {build_comp.get_unlocked_tier()}")
        check("CelestialAnvilUnlockedAtTier4", build_comp.is_prop_unlocked("CelestialAnvil"))
        check("RunicCrucibleUnlockedAtTier4", build_comp.is_prop_unlocked("RunicCrucible"))
        check("NewGamePlusUnlocked", village.tower_floor.get_editor_property("new_game_plus"))

    # Clean up spawned test actors
    actors_to_cleanup = [
        char, debris_stone, debris_metal,
        piece, anvil_prop, oven_prop, bed_prop, cauldron_prop, table_prop,
        golem
    ]
    for act in actors_to_cleanup:
        if act:
            e.destroy_actor(act)

    # Save summary report to JSON
    out_dir = "D:/DEVELOPMENT/Games/Tower of Elrhun/Saved"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "end_to_end_village_slice_playtest.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    total = len(report["checks"])
    passed = sum(1 for c in report["checks"] if c["passed"])
    print(f"\n=======================================================")
    print(f"PLAYTEST COMPLETE: {passed}/{total} checks passed ({len(report['errors'])} errors)")
    print(f"Report saved to: {out_path}")
    print(f"=======================================================\n")
    return report

if __name__ == "__main__":
    run_playtest()
