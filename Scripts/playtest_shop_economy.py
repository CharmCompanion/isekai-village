"""Live PIE verification of T1: Multi-item General Store (U), ShopWidget/ForgeWidget UI, and ToolParts economy/temper/wall loop."""
from pathlib import Path
import json
import time
import uuid
import unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report_path = r / 'Saved/shop_economy_playtest.json'
slot = 'LiveShopTest_' + uuid.uuid4().hex[:8]
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
        if now - started > 90.0:
            return finish('Timeout in shop_economy playtest')

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
        pc = u.GameplayStatics.get_player_controller(w, 0)
        if not v or not p or not pc or not p.gather or not p.party_reserve:
            return

        if state['stage'] == 'wait_pie':
            if now - started < 4.0:
                return
            v.set_editor_property('window_seconds', 10000.0)
            v.set_editor_property('use_golem_village', True)
            v.set_editor_property('use_organic_golem_needs', True)
            p.gather.add_item('Wood', 100)
            p.gather.add_item('Stone', 40)
            p.gather.add_item('Iron', 20)
            p.gather.add_item('Coin', 60)
            p.gather.add_item('ToolParts', 6)

            free = [pl for pl in v.plots if pl.flexible_use and not pl.built and pl.buildable_size >= 2000.0]
            free.sort(key=lambda pl: (pl.location.x - 10000)**2 + (pl.location.y - 2000)**2)
            check('Enough free plots in Map_ElRuhnSky', len(free) >= 5, str(len(free)))
            for idx, cid in enumerate(['Guild', 'Townhouse', 'Townhouse', 'Shop', 'Smith']):
                p.set_actor_location(free[idx].location + free[idx].stake_offset + u.Vector(0, 0, 110), False, True)
                v.select_building(cid)
                v.try_build_plot(free[idx].id, p)
                built = any(x.id == free[idx].id and x.built and str(x.catalog_id) == cid for x in v.plots)
                check(f'Build {cid}_{idx}', built, f"{cid} size={free[idx].buildable_size}")
            if v.building_catalog_open:
                v.toggle_building_catalog()
            state['guild_id'] = free[0].id
            state['shop_id'] = free[3].id
            state['smith_id'] = free[4].id
            state['guild_plot'] = next(pl for pl in v.plots if pl.id == free[0].id)
            state['shop_plot'] = next(pl for pl in v.plots if pl.id == free[3].id)

            gp = state['guild_plot']
            p.set_actor_location(gp.location + gp.stake_offset + u.Vector(0, 0, 110), False, True)
            check('Create golem Tank at Hall', v.create_golem_adventurer(p, 'Tank', False, u.Text('Kael StoreTest')), v.last_hall_message)
            state['adv_id'] = p.party_reserve.reserve[-1].adventurer_id

            state['keeper'] = next((g for g in u.GameplayStatics.get_all_actors_of_class(w, u.VillageGolemCitizen) if g.work_plot == state['shop_id']), None)
            check('Shopkeeper golem assigned', state['keeper'] is not None)
            if state['keeper']:
                state['stage'] = 'wait_keeper'
                state['stamp'] = now
                return
            return finish('Shopkeeper golem missing')

        if state['stage'] == 'wait_keeper':
            g = state['keeper']
            if not v.is_shop_staffed(state['shop_id']):
                goal = g.get_editor_property('goal')
                if g.get_editor_property('goal_place') == u.VillagePlace.SHOP and goal.length() > 1.0:
                    g.set_actor_location(goal + u.Vector(0, 0, 99), False, True)
                return
            check('Shop is staffed', v.is_shop_staffed(state['shop_id']))
            sp = state['shop_plot']
            p.set_actor_location(sp.location + sp.stake_offset + u.Vector(0, 0, 110), False, True)
            p.character_movement.stop_movement_immediately()
            state['stage'] = 'press_shop_u'
            state['stamp'] = now
            return

        if state['stage'] == 'press_shop_u':
            pulse(w, 'U')
            state['stage'] = 'shop_open'
            return

        if state['stage'] == 'shop_open':
            sw = p.shop_widget
            check('U opens ShopWidget near Shop', sw is not None and sw.is_in_viewport())
            if sw:
                k = state['keeper']
                dr = next((r.drives for r in v.golem_residents if r.id == k.golem_id), None)
                d2 = (k.get_actor_location() - k.get_editor_property('goal')).length()
                shop_diag = f"msg={v.last_shop_message} staffed={v.is_shop_staffed(state['shop_id'])} act={dr.activity if dr else '?'} place={k.get_editor_property('goal_place')} d={d2:.1f} win={v.window_index}"
                coin_before = p.gather.get_count('Coin')
                check('ShopWidget buy Bread succeeds', sw.execute_trade('Bread', True), shop_diag)
                check('Bought 1 Bread for pack', p.gather.get_count('Bread') == 1, str(p.gather.get_count('Bread')))
                check('Coin charged 5 for Bread', p.gather.get_count('Coin') == coin_before - 5, str(p.gather.get_count('Coin')))
                check('ShopWidget sell ToolParts succeeds', sw.execute_trade('ToolParts', False), v.last_shop_message)
                check('ToolParts sell pays +6 Coin', p.gather.get_count('Coin') == coin_before + 1, str(p.gather.get_count('Coin')))
                sw.close_shop()
                check('ShopWidget closes cleanly', not sw.is_in_viewport())

            state['wood_before'] = p.gather.get_count('Wood')
            state['stage'] = 'press_quick_sell'
            state['stamp'] = now
            return

        if state['stage'] == 'press_quick_sell':
            pulse(w, 'T')
            state['stage'] = 'quick_sell_done'
            return

        if state['stage'] == 'quick_sell_done':
            check('T quick-sell Wood works', p.gather.get_count('Wood') == state['wood_before'] - 1, f"{v.last_shop_message} staffed={v.is_shop_staffed(state['shop_id'])}")
            pulse(w, 'Y')
            state['stage'] = 'quick_buy_done'
            return

        if state['stage'] == 'quick_buy_done':
            check('Y quick-buy Wood works', p.gather.get_count('Wood') == state['wood_before'])
            forge = next(iter(u.GameplayStatics.get_all_actors_of_class(w, u.BlacksmithForge)), None)
            check('BlacksmithForge present in world', forge is not None)
            if forge:
                p.set_actor_location(forge.get_actor_location() + u.Vector(40, 0, 0), False, True)
                state['wall_before'] = v.wall_integrity
                state['stage'] = 'press_forge_u'
                state['stamp'] = now
                return
            return finish()

        if state['stage'] == 'press_forge_u':
            pulse(w, 'U')
            state['stage'] = 'forge_open'
            return

        if state['stage'] == 'forge_open':
            fw = p.forge_widget
            check('U opens ForgeWidget near Forge', fw is not None and fw.is_in_viewport())
            if fw:
                parts_before = p.gather.get_count('ToolParts')
                check('Temper Rank 1 via ForgeWidget', fw.temper_adventurer(state['adv_id']))
                check('Temper Rank 2 via ForgeWidget', fw.temper_adventurer(state['adv_id']))
                check('4 ToolParts consumed for +2 temper', p.gather.get_count('ToolParts') == parts_before - 4)
                check('Fortify Wall via ForgeWidget', fw.reinforce_walls())
                check('Wall boosted +50', v.wall_integrity == min(100, state['wall_before'] + 50))
                fw.close_forge()
                check('ForgeWidget closes cleanly', not fw.is_in_viewport())

            v.save_village_state(p)
            p.gather.consume('Bread', 1)
            check('Temporary consume drops Bread to 0 before reload', p.gather.get_count('Bread') == 0)
            v.reload_village_state(p)
            adv = next(a for a in p.party_reserve.reserve if a.adventurer_id == state['adv_id'])
            check('TemperLevel +2 persists after live reload', adv.temper_level == 2)
            check('Bread purchase restores from save on live reload', p.gather.get_count('Bread') == 1)
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
