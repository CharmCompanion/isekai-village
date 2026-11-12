"""Live PIE verification of T3: World Forest/Lake/Mine spots, DayBoardWidget, BuildingCatalogWidget, 5-Era Progression."""
from pathlib import Path
import json
import time
import uuid
import unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report_path = r / 'Saved/t3_world_ui_playtest.json'
slot = 'LiveT3Test_' + uuid.uuid4().hex[:8]
result = {'success': False, 'checks': [], 'slot': slot, 'errors': []}
release_key = None
handle = None
started = time.monotonic()
state = {'stage': 'boot', 'stamp': started}

def check(name, cond, detail=''):
    result['checks'].append({'name': name, 'ok': bool(cond), 'detail': detail})
    if not cond:
        result['errors'].append(f"{name}: {detail}" if detail else name)

def pulse(w, key):
    global release_key
    u.SystemLibrary.execute_console_command(w, 'Input.+key ' + key)
    release_key = key

def finish(err=None):
    global handle
    if err:
        result['errors'].append(str(err))
    result['success'] = (len(result['errors']) == 0) and all(c['ok'] for c in result['checks'])
    result['elapsed_s'] = round(time.monotonic() - started, 2)
    report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    try:
        u.EditorLevelLibrary.editor_end_play()
    except Exception:
        pass
    try:
        if u.GameplayStatics.does_save_game_exist(slot, 0):
            u.GameplayStatics.delete_game_in_slot(slot, 0)
    except Exception:
        pass
    if handle is not None:
        u.unregister_slate_post_tick_callback(handle)
        handle = None
    u.EditorPythonScripting.set_keep_python_script_alive(False)

def tick(dt):
    global release_key
    try:
        now = time.monotonic()
        if now - started > 120.0:
            return finish('Timeout in t3_world_ui playtest')

        if state['stage'] == 'boot':
            state['stage'] = 'wait_pie'
            state['stamp'] = now
            u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play()
            return

        worlds = u.EditorLevelLibrary.get_pie_worlds(False)
        if not worlds:
            return
        w = worlds[0]
        if release_key:
            u.SystemLibrary.execute_console_command(w, 'Input.-key ' + release_key)
            release_key = None
            state['stamp'] = now
            return

        if now - state['stamp'] < 0.35:
            return

        v = next(iter(u.GameplayStatics.get_all_actors_of_class(w, u.VillageRuntime)), None)
        p = u.GameplayStatics.get_player_character(w, 0)
        if not v or not p or not p.gather or not p.party_reserve:
            return

        if state['stage'] == 'wait_pie':
            if now - started < 4.0:
                return
            v.set_editor_property('window_seconds', 10000.0)

            # 1. Verify world supply sites & new actors in Map_ElRuhnSky
            tags = {str(s.site_tag): str(s.item) for s in v.supply_sites}
            check('3 World supply sites configured', len(v.supply_sites) == 3, str(tags))
            check('Forest, Lake & Mine supply tags set',
                  tags.get('Whispering Forest') == 'Wood'
                  and tags.get('SkyLake Pier') == 'Fish'
                  and tags.get('Whisperwood Mine') == 'Stone', str(tags))

            spots = list(u.GameplayStatics.get_all_actors_of_class(w, u.LakeFishingSpot))
            veins = list(u.GameplayStatics.get_all_actors_of_class(w, u.MineOreVein))
            mine_returns = [
                ps for ps in u.GameplayStatics.get_all_actors_of_class(w, u.PlayerStart)
                if str(ps.get_editor_property('player_start_tag')) == 'MineReturn'
            ]
            check('LakeFishingSpots spawned in Map_ElRuhnSky', len(spots) >= 2, str(len(spots)))
            check('Respawning MineOreVeins spawned in Map_ElRuhnSky', len(veins) >= 2, str(len(veins)))
            check('MineReturn PlayerStart present in Map_ElRuhnSky', len(mine_returns) >= 1, str(len(mine_returns)))

            # 2. Player fishing via T at SkyLake Fishing Spot
            spot = next((s for s in spots if 'SkyLake' in s.spot_title), spots[0])
            p.set_actor_location(spot.get_actor_location() + u.Vector(0, 0, 100), False, True)
            p.character_movement.stop_movement_immediately()
            state['spot'] = spot
            state['fish_before'] = p.gather.get_count('Fish')
            state['stage'] = 'fish_cast_1'
            state['stamp'] = now
            return

        if state['stage'] == 'fish_cast_1':
            pulse(w, 'T')
            state['stage'] = 'fish_cast_2'
            return

        if state['stage'] == 'fish_cast_2':
            pulse(w, 'T')
            state['stage'] = 'verify_fish_and_mine'
            return

        if state['stage'] == 'verify_fish_and_mine':
            spot = state['spot']
            fish_after = p.gather.get_count('Fish')
            check('T at SkyLake Fishing Spot catches Fish', fish_after > state['fish_before'], f"Before={state['fish_before']} After={fish_after}")

            # Check respawning Copper vein at Whisperwood Mine
            vein = next(iter(u.GameplayStatics.get_all_actors_of_class(w, u.MineOreVein)), None)
            p.gather.set_editor_property('pickaxe_tier', u.AxeTier.STEEL)
            p.set_actor_location(vein.get_actor_location() + u.Vector(0, 0, 100), False, True)
            p.character_movement.stop_movement_immediately()
            check('Copper/Iron Vein present & visible before mine', vein.mesh.is_visible())
            check('Vein TryMine executes cleanly', vein.try_mine(p))
            check('Respawning MineOreVein hides instead of destroying', u.SystemLibrary.is_valid(vein) and not vein.mesh.is_visible())

            # 3. Walk to DayBoard (check existing or place/find) & press U to open UDayBoardWidget
            board = next(iter(u.GameplayStatics.get_all_actors_of_class(w, u.DayBoard)), None)
            check('DayBoard actor present in world', board is not None)
            p.gather.add_item('Wood', 250)
            p.gather.add_item('Iron', 80)
            p.gather.add_item('Crystal', 20)
            p.gather.add_item('Bread', 80)
            p.gather.add_item('ToolParts', 4)
            p.set_actor_location(board.get_actor_location() + u.Vector(0, 0, 80), False, True)
            p.character_movement.stop_movement_immediately()
            state['stage'] = 'press_board_u'
            state['stamp'] = now
            return

        if state['stage'] == 'press_board_u':
            pulse(w, 'U')
            state['stage'] = 'verify_board_ui'
            return

        if state['stage'] == 'verify_board_ui':
            bw = p.board_widget
            check('U at DayBoard opens DayBoardWidget', bw is not None and bw.is_in_viewport(), f"bNearDayBoard={p.near_day_board}")
            if bw:
                missions = list(v.today_missions)
                done_any = False
                for idx in range(len(missions)):
                    if bw.submit_mission(idx):
                        done_any = True
                        break
                check('DayBoardWidget can submit/progress a mission', done_any or len(missions) == 0, str(len(missions)))
                wall_before = v.wall_integrity
                if wall_before < 100:
                    check('DayBoardWidget FortifyWall works', bw.fortify_wall() and v.wall_integrity > wall_before, f"{wall_before}->{v.wall_integrity}")
                bw.close_board()
                check('DayBoardWidget closes cleanly', not bw.is_in_viewport())

            # 4. Press B to toggle UBuildingCatalogWidget (non-blocking dock)
            pulse(w, 'B')
            state['stage'] = 'verify_catalog_ui'
            return

        if state['stage'] == 'verify_catalog_ui':
            cw = p.catalog_widget
            check('B opens BuildingCatalogWidget', v.building_catalog_open and cw is not None and cw.is_in_viewport())
            check('CatalogWidget stays non-blocking for mouselook placement', not p.has_blocking_modal_ui())
            if cw:
                check('CatalogWidget select_catalog_index works', cw.select_catalog_index(2))
            pulse(w, 'B')
            state['stage'] = 'verify_catalog_close_and_eras'
            return

        if state['stage'] == 'verify_catalog_close_and_eras':
            cw = p.catalog_widget
            check('B closes BuildingCatalogWidget', not v.building_catalog_open and (cw is None or not cw.is_in_viewport()))

            # 5. Verify 5-Era progression & NextEraRequirementText
            next_txt = v.get_next_era_requirement_text(p)
            check('NextEraRequirementText reports next settlement milestone', len(next_txt) > 0, next_txt)
            start_era = v.get_settlement_era_name(p)
            check('Starting Settlement Era is Homestead or Village', start_era in ('Homestead', 'Village'), start_era)

            blocker_locs = [pl.location + pl.stake_offset for pl in v.plots if pl.built and pl.kind in (u.TownBuilding.SHOP, u.TownBuilding.SMITH)]
            free = [
                pl for pl in v.plots
                if pl.flexible_use and not pl.built and pl.buildable_size >= 2000.0
                and all(((pl.location.x + pl.stake_offset.x - b.x)**2 + (pl.location.y + pl.stake_offset.y - b.y)**2) >= 700.0**2 for b in blocker_locs)
            ]
            free.sort(key=lambda pl: (pl.location.x - 10000)**2 + (pl.location.y - 2000)**2)
            def build_on(idx, cid):
                p.set_actor_location(free[idx].location + free[idx].stake_offset + u.Vector(0, 0, 110), False, True)
                v.select_building(cid)
                v.try_build_plot(free[idx].id, p)
            build_on(0, 'Inn')
            build_on(1, 'Cottage')
            build_on(2, 'Chapel')

            unlocked = {str(x) for x in p.unlocked_sphere_nodes}
            for nid in ['CA_Life_HP1', 'CA_Life_HP2', 'CA_Life_HP3', 'CA_Life_HP4', 'CA_Life_TP1', 'CA_Life_TP2', 'CA_Life_TP3', 'CA_Life_Inv1', 'CA_Life_Inv2']:
                if nid not in unlocked and len(unlocked) < 9:
                    if p.unlock_sphere_node(nid):
                        unlocked.add(nid)
            feasts = 0
            while (v.trust + p.sphere_trust_bonus) < 80 and feasts < 25:
                if not v.execute_service_action(u.TownBuilding.INN, 'Feast', p):
                    break
                feasts += 1
            build_on(3, 'Manor')
            check('Reached Barony before Castle if < 80 Trust or >=4 plots', v.get_settlement_era_name(p) in ('Barony', 'Kingdom'), v.get_settlement_era_name(p))
            build_on(4, 'Castle')
            if v.building_catalog_open:
                v.toggle_building_catalog()
            check('Reached Kingdom Era after 8 Sphere Nodes + 80 Trust + Castle', v.get_settlement_era_name(p) == 'Kingdom',
                  f"Era={v.get_settlement_era_name(p)} Trust={v.trust + p.sphere_trust_bonus} Nodes={len(p.unlocked_sphere_nodes)} Dev={v.developed_plot_count()}")
            return finish()
    except Exception as ex:
        return finish(ex)

try:
    u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
    ed_v = next(x for x in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(x, u.VillageRuntime))
    ed_v.set_editor_property('construction_save_slot', slot)
    ed_v.set_editor_property('use_golem_village', True)
    ed_v.set_editor_property('use_organic_golem_needs', True)
    u.EditorPythonScripting.set_keep_python_script_alive(True)
    handle = u.register_slate_post_tick_callback(tick)
except Exception as ex:
    finish(ex)
