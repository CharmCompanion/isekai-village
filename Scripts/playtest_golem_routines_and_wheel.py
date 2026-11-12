import unreal
import json
import os

def run_playtest():
    report = {
        "test_name": "Golem Routines, Tower Progression & Build HUD Wheel Verification",
        "checks": [],
        "errors": []
    }

    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        report["errors"].append("Failed to get editor world")
        return report

    def check(name, condition, details=""):
        res = bool(condition)
        report["checks"].append({
            "name": name,
            "passed": res,
            "details": details if details else ("PASSED" if res else "FAILED")
        })
        if not res:
            report["errors"].append(f"Check failed: {name} - {details}")
        print(f"[{'PASS' if res else 'FAIL'}] {name}: {details}")

    # -------------------------------------------------------------
    # 1. OPTION A: Resident Golem Routine Behaviors
    # -------------------------------------------------------------
    print("=== Testing Option A: Resident Golem Routine Behaviors ===")
    golem_loc = unreal.Vector(0, 0, 100)
    golem = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.VillageGolemCitizen, golem_loc)
    check("SpawnGolemCitizen", golem is not None, f"Spawned golem at {golem_loc}")

    anvil_prop = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LinchpinProp, unreal.Vector(120, 0, 100))
    anvil_prop.setup_prop("Anvil")

    counter_prop = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LinchpinProp, unreal.Vector(240, 0, 100))
    counter_prop.setup_prop("Counter")

    bed_prop = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LinchpinProp, unreal.Vector(360, 0, 100))
    bed_prop.setup_prop("Bed")

    oven_prop = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LinchpinProp, unreal.Vector(480, 0, 100))
    oven_prop.setup_prop("Oven")

    bench_prop = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LinchpinProp, unreal.Vector(600, 0, 100))
    bench_prop.setup_prop("Workbench")

    if golem:
        # A1: Blacksmith Hammering
        golem.set_work_routine(unreal.GolemWorkRoutine.BLACKSMITH_HAMMERING, anvil_prop)
        check("BlacksmithRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.BLACKSMITH_HAMMERING)
        check("StationPropLinked", golem.get_station_prop() == anvil_prop)
        line = str(golem.offer_line())
        check("BlacksmithOfferLine", "Blacksmith" in line and "anvil" in line.lower(), f"Line: {line}")

        # A2: Innkeeper Hosting
        golem.set_work_routine(unreal.GolemWorkRoutine.INNKEEPER_HOSTING, counter_prop)
        check("InnkeeperRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.INNKEEPER_HOSTING)
        line = str(golem.offer_line())
        check("InnkeeperOfferLine", "Innkeeper" in line, f"Line: {line}")

        # A3: Shopkeeper Trading
        golem.set_work_routine(unreal.GolemWorkRoutine.SHOPKEEPER_TRADING, counter_prop)
        check("ShopkeeperRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.SHOPKEEPER_TRADING)
        line = str(golem.offer_line())
        check("ShopkeeperOfferLine", "Merchant" in line, f"Line: {line}")

        # A4: Baker Baking
        golem.set_work_routine(unreal.GolemWorkRoutine.BAKER_BAKING, oven_prop)
        check("BakerRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.BAKER_BAKING)
        line = str(golem.offer_line())
        check("BakerOfferLine", "Baker" in line, f"Line: {line}")

        # A5: Craftsman Working
        golem.set_work_routine(unreal.GolemWorkRoutine.CRAFTSMAN_WORKING, bench_prop)
        check("CraftsmanRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.CRAFTSMAN_WORKING)
        line = str(golem.offer_line())
        check("CraftsmanOfferLine", "Artisan" in line, f"Line: {line}")

        # A6: Sleeping in Bed
        golem.set_work_routine(unreal.GolemWorkRoutine.SLEEPING_IN_BED, bed_prop)
        check("SleepingRoutineActive", golem.get_work_routine() == unreal.GolemWorkRoutine.SLEEPING_IN_BED)
        line = str(golem.offer_line())
        check("SleepingOfferLine", "Resting" in line and "bed" in line.lower(), f"Line: {line}")

    # -------------------------------------------------------------
    # 2. OPTION B: Tower Floor Progression & Recipe Unlocks
    # -------------------------------------------------------------
    print("=== Testing Option B: Tower Floor Progression & Unlocks ===")
    recipes = unreal.LinchpinRecipe.get_default_recipes_list()
    recipe_ids = [r.get_editor_property("recipe_id") for r in recipes if r is not None]
    check("Tier2AlchemistLabRecipe", "AlchemistLab" in recipe_ids, f"Recipes: {recipe_ids}")
    check("Tier2EnchanterRecipe", "Enchanter" in recipe_ids)
    check("Tier4ArcaneForgeRecipe", "ArcaneForge" in recipe_ids)

    # Spawn character with BuildEditComponent
    char = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.IsekaiVillageCharacter, unreal.Vector(1000, 0, 100))
    check("SpawnCharacter", char is not None)

    build_comp = char.get_component_by_class(unreal.BuildEditComponent) if char else None
    check("HasBuildEditComponent", build_comp is not None)

    if build_comp:
        tier0 = build_comp.get_unlocked_tier()
        check("DefaultTier1", tier0 >= 1, f"Initial tier: {tier0}")

        # Tier unlock queries
        check("Tier1AnvilUnlocked", build_comp.is_prop_unlocked("Anvil"))
        check("Tier1BedUnlocked", build_comp.is_prop_unlocked("Bed"))
        check("Tier1CounterUnlocked", build_comp.is_prop_unlocked("Counter"))

        # Verification of prop costs
        res1, c1, res2, c2 = unreal.BuildEditComponent.get_prop_craft_cost("Cauldron")
        check("CauldronCraftCost", str(res1) == "Stone" and c1 == 4 and str(res2) == "Iron" and c2 == 2, f"{res1}:{c1}, {res2}:{c2}")

        res1, c1, res2, c2 = unreal.BuildEditComponent.get_prop_craft_cost("ArcaneTable")
        check("ArcaneTableCraftCost", str(res1) == "Wood" and c1 == 6 and str(res2) == "Crystal" and c2 == 2, f"{res1}:{c1}, {res2}:{c2}")

        res1, c1, res2, c2 = unreal.BuildEditComponent.get_prop_craft_cost("CelestialAnvil")
        check("CelestialAnvilCraftCost", str(res1) == "Iron" and c1 == 10 and str(res2) == "Crystal" and c2 == 5, f"{res1}:{c1}, {res2}:{c2}")

    # -------------------------------------------------------------
    # 3. OPTION C: In-Game Build HUD / Wheel
    # -------------------------------------------------------------
    print("=== Testing Option C: In-Game Build HUD / Wheel ===")
    if char and build_comp:
        wheel_widget = unreal.new_object(unreal.BuildWheelWidget, char)
        check("ConstructBuildWheelWidget", wheel_widget is not None)

        if wheel_widget:
            wheel_widget.initialize_wheel(build_comp, char)

            # Test Structures Category
            wheel_widget.set_category(unreal.BuildWheelCategory.STRUCTURES)
            struct_items = wheel_widget.get_current_items()
            check("StructuresCategoryItemCount", len(struct_items) >= 9, f"Count: {len(struct_items)}")

            # Equip Curved Arc Wall via Wheel
            wheel_widget.select_item_index(1) # Wall_Curved
            check("EquipCurvedWallViaWheel", build_comp.get_editor_property("current_wall_style") == unreal.BuildWallStyle.CURVED_ARC)

            # Equip 45 Diagonal Wall via Wheel
            wheel_widget.select_item_index(2) # Wall_Diagonal
            check("EquipDiagonalWallViaWheel", build_comp.get_editor_property("current_wall_style") == unreal.BuildWallStyle.DIAGONAL45)

            # Test Furniture Category
            wheel_widget.set_category(unreal.BuildWheelCategory.FURNITURE)
            furn_items = wheel_widget.get_current_items()
            check("FurnitureCategoryItemCount", len(furn_items) >= 14, f"Count: {len(furn_items)}")

            # Equip Bed via Wheel
            wheel_widget.select_item_index(2) # Bed
            check("EquipBedViaWheel", str(build_comp.get_editor_property("current_prop_tag")) == "Bed")
            check("PropPlacementModeActive", build_comp.get_editor_property("placing_props") == True)

            # Test Materials Category
            wheel_widget.set_category(unreal.BuildWheelCategory.MATERIALS)
            mat_items = wheel_widget.get_current_items()
            check("MaterialsCategoryItemCount", len(mat_items) >= 9, f"Count: {len(mat_items)}")

            # Close Wheel
            wheel_widget.close_wheel()
            check("CloseWheelCleanly", True)

    # Clean up spawned test actors
    if golem: golem.destroy_actor()
    if anvil_prop: anvil_prop.destroy_actor()
    if counter_prop: counter_prop.destroy_actor()
    if bed_prop: bed_prop.destroy_actor()
    if oven_prop: oven_prop.destroy_actor()
    if bench_prop: bench_prop.destroy_actor()
    if char: char.destroy_actor()

    # Save report
    out_dir = "D:/DEVELOPMENT/Games/Tower of Elrhun/Saved"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "golem_routines_and_wheel_playtest.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    passed = sum(1 for c in report["checks"] if c["passed"])
    total = len(report["checks"])
    print(f"\nPLAYTEST SUMMARY: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    return report

if __name__ == "__main__":
    run_playtest()
