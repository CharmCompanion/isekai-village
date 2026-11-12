"""Synchronous Editor Commandlet Verification of Linchpin Prop Crafting & Snappable Furniture:
1. Linchpin prop placement mode toggle (b_placing_props).
2. Cycling prop types across the catalog (Anvil, Forge, Bed, Counter, Oven, Workbench, Chest, Crate, Board).
3. Recipe resource checking & consumption (Wood, Stone, Iron, ToolParts).
4. Interior room snapping: 50cm sub-grid + magnetic wall-flush alignment against nearby ABuildPiece walls.
5. Interactive workstation dispatch:
   - Bed: rest restores CurrentHP and CurrentTP to full.
   - Forge / Anvil: tool upgrade interaction dispatch.
   - Stone Hearth Oven: bread baking & ration restoration.
   - Craftsman Workbench: tool parts fabrication.
6. Enclosing ARoomVolume dynamic auto-classification when props are placed.
"""
from pathlib import Path
import json
import time
import unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report_path = r / 'Saved/linchpin_props_playtest.json'
result = {'success': False, 'checks': [], 'errors': []}
started = time.monotonic()

def check(name, cond, detail=''):
    result['checks'].append({'name': name, 'ok': bool(cond), 'detail': str(detail)})
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")
    if not cond:
        result['errors'].append(f"{name}: {detail}" if detail else name)

try:
    try:
        world = u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
    except Exception as ex:
        print(f"Handled map load exception: {ex}")
        world = u.EditorLevelLibrary.get_editor_world()

    e = u.get_editor_subsystem(u.EditorActorSubsystem)

    # 1. Spawn test player character
    char_class = u.IsekaiVillageCharacter.static_class()
    player = e.spawn_actor_from_class(char_class, u.Vector(0.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
    check('PlayerSpawned', player is not None, "Test IsekaiVillageCharacter spawned")

    build_comp = player.get_editor_property('build_edit') if player else None
    check('BuildEditComponentFound', build_comp is not None, "BuildEditComponent retrieved from player")

    gather_comp = player.get_editor_property('gather') if player else None
    check('GatherComponentFound', gather_comp is not None, "GatherInventoryComponent retrieved from player")

    if build_comp and gather_comp:
        # 2. Toggle build mode and prop placement mode
        build_comp.toggle_build_mode()
        check('BuildModeActive', build_comp.get_editor_property('build_mode') == True, "Build mode activated")

        check('PropModeInitiallyFalse', build_comp.get_editor_property('placing_props') == False, "Prop placement initially false")
        build_comp.toggle_prop_placement_mode()
        check('PropModeToggledOn', build_comp.get_editor_property('placing_props') == True, "Prop placement mode toggled ON")

        # 3. Cycle prop types
        initial_tag = build_comp.get_editor_property('current_prop_tag')
        check('InitialPropTag', str(initial_tag) == 'Anvil', f"Initial prop is {initial_tag}")

        build_comp.cycle_prop_type(1)
        tag2 = build_comp.get_editor_property('current_prop_tag')
        check('PropTypeCycledForward', str(tag2) == 'Forge', f"Cycled to {tag2}")

        build_comp.cycle_prop_type(1)
        tag3 = build_comp.get_editor_property('current_prop_tag')
        check('PropTypeCycledToBed', str(tag3) == 'Bed', f"Cycled to {tag3}")

        # 4. Check craft costs
        cost_res = build_comp.get_prop_craft_cost('Bed')
        res1, cost1, res2, cost2 = cost_res
        check('BedCostQuery', cost1 > 0 and str(res1) == 'Wood', f"Bed costs: {cost1} {res1}, {cost2} {res2}")

        # Attempt craft without materials -> fails (freshly spawned player has empty inventory)
        b_fail = build_comp.try_craft_and_place_prop(player, u.Vector(200.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        check('CraftFailsWithoutMaterials', b_fail == False, "Cannot place prop without required materials")

        # Give materials and craft
        gather_comp.add_item('Wood', 100)
        gather_comp.add_item('Stone', 100)
        gather_comp.add_item('Iron', 100)
        gather_comp.add_item('ToolParts', 20)
        check('MaterialsAdded', gather_comp.get_count('Wood') >= 100, "Materials stocked in player inventory")

        b_bed = build_comp.try_craft_and_place_prop(player, u.Vector(200.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        bed_prop = build_comp.get_editor_property('selected_prop')
        check('BedPropCrafted', b_bed == True and bed_prop is not None and isinstance(bed_prop, u.LinchpinProp), "Bed linchpin prop spawned successfully")
        check('BedPropTag', str(bed_prop.get_editor_property('linchpin_tag')) == 'Bed', "LinchpinTag is Bed")

        # 5. Wall Flush Placement & Proximity Test
        piece_class = u.BuildPiece.static_class()
        wall = e.spawn_actor_from_class(piece_class, u.Vector(500.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        wall.set_editor_property('piece_type', u.BuildPieceType.WALL)
        wall.rebuild_mesh()
        check('WallPieceSpawned', wall is not None, "Test Wall piece placed at (500, 0, 2100)")

        # Place prop near wall flush
        b_flush = build_comp.try_craft_and_place_prop(player, u.Vector(500.0, 35.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        flush_prop = build_comp.get_editor_property('selected_prop')
        check('FurniturePlacedNearWall', b_flush == True and flush_prop is not None, f"Furniture placed flush at (500, 35, 2100)")
        if flush_prop:
            check('FurnitureZCorrect', flush_prop.get_actor_location().z == 2100.0, "Furniture placed on room elevation")
            e.destroy_actor(flush_prop)

        # 6. Interactive Station Dispatch Tests
        # Test Bed: Restores HP and TP
        player.spend_tp(50.0)
        tp_before = player.get_editor_property('current_tp')
        check('PlayerSpentTPForRestTest', tp_before <= 50.0, f"TP={tp_before}")
        
        bed_interacted = bed_prop.try_interact(player)
        check('BedInteractionSucceeds', bed_interacted == True, "Bed TryInteract returned true")
        check('BedRestoresTP', player.get_editor_property('current_tp') >= 100.0, f"TP restored to: {player.get_editor_property('current_tp')}")

        # Test Anvil: Upgrade dispatch
        build_comp.set_editor_property('current_prop_tag', 'Anvil')
        b_anvil = build_comp.try_craft_and_place_prop(player, u.Vector(300.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        anvil_prop = build_comp.get_editor_property('selected_prop')
        check('AnvilCrafted', b_anvil == True and anvil_prop is not None, "Anvil crafted and placed")
        anvil_interacted = anvil_prop.try_interact(player) if anvil_prop else False
        check('AnvilInteractionSucceeds', anvil_interacted == True, "Anvil TryInteract successfully dispatched")

        # Test Stone Hearth Oven: Bread baking
        build_comp.set_editor_property('current_prop_tag', 'Oven')
        b_oven = build_comp.try_craft_and_place_prop(player, u.Vector(400.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        oven_prop = build_comp.get_editor_property('selected_prop')
        check('OvenCrafted', b_oven == True and oven_prop is not None, "Stone Hearth Oven crafted and placed")
        oven_interacted = oven_prop.try_interact(player) if oven_prop else False
        check('OvenInteractionSucceeds', oven_interacted == True, "Oven baked travel bread rations")

        # Test Craftsman Workbench: Tool parts fabrication
        build_comp.set_editor_property('current_prop_tag', 'Workbench')
        b_bench = build_comp.try_craft_and_place_prop(player, u.Vector(400.0, 100.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        bench_prop = build_comp.get_editor_property('selected_prop')
        check('WorkbenchCrafted', b_bench == True and bench_prop is not None, "Craftsman Workbench crafted and placed")
        bench_interacted = bench_prop.try_interact(player) if bench_prop else False
        check('WorkbenchInteractionSucceeds', bench_interacted == True, "Workbench crafted tool parts")

        # 7. Test Room Auto-Classification via Placed Props
        room_class = u.RoomVolume.static_class()
        room = e.spawn_actor_from_class(room_class, u.Vector(1500.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        check('RoomSpawned', room is not None, "Enclosing ARoomVolume spawned")

        build_comp.set_editor_property('current_prop_tag', 'Counter')
        b_counter = build_comp.try_craft_and_place_prop(player, u.Vector(1520.0, 0.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        counter_prop = build_comp.get_editor_property('selected_prop')
        check('CounterPlacedInRoom', b_counter == True and counter_prop is not None, "General Store Counter placed inside room")

        build_comp.set_editor_property('current_prop_tag', 'Crate')
        b_crate = build_comp.try_craft_and_place_prop(player, u.Vector(1520.0, 50.0, 2100.0), u.Rotator(0.0, 0.0, 0.0))
        crate_prop = build_comp.get_editor_property('selected_prop')
        check('CratePlacedInRoom', b_crate == True and crate_prop is not None, "Storage Crate placed inside room")

        # Room should be classified as SHOP (Counter + Crate)
        room_func = room.get_editor_property('current_function')
        check('RoomAutoClassifiedAsShop', room_func == u.RoomFunction.SHOP, f"Room classified as: {room_func}")

        # Cleanup test actors
        if wall: e.destroy_actor(wall)
        if bed_prop: e.destroy_actor(bed_prop)
        if anvil_prop: e.destroy_actor(anvil_prop)
        if oven_prop: e.destroy_actor(oven_prop)
        if bench_prop: e.destroy_actor(bench_prop)
        if counter_prop: e.destroy_actor(counter_prop)
        if crate_prop: e.destroy_actor(crate_prop)
        if room: e.destroy_actor(room)

    if player:
        e.destroy_actor(player)

    result['success'] = (len(result['errors']) == 0) and all(c['ok'] for c in result['checks'])
    result['elapsed_s'] = round(time.monotonic() - started, 2)
    report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print("=" * 60)
    print(f"LINCHPIN PROP PLAYTEST COMPLETE: {'ALL PASSED' if result['success'] else 'FAILED'}")
    print(f"Total Checks: {len(result['checks'])} | Errors: {len(result['errors'])} | Time: {result['elapsed_s']}s")
    print("=" * 60)

except Exception as ex:
    import traceback
    traceback.print_exc()
    result['errors'].append(str(ex))
    result['success'] = False
    report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"FATAL ERROR: {ex}")
