"""Live PIE verification of T2: Town service buildings (U UI + T quick-use), Bank compounding, Academy research, Inn rest, Guild Rank progression & reload."""
from pathlib import Path
import json
import time
import uuid
import unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report_path = r / 'Saved/town_services_playtest.json'
slot = 'LiveTownSvc_' + uuid.uuid4().hex[:8]
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
            return finish('Timeout in town_services playtest')

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
            p.gather.add_item('Wood', 160)
            p.gather.add_item('Stone', 40)
            p.gather.add_item('Iron', 40)
            p.gather.add_item('Crystal', 12)
            p.gather.add_item('Bread', 60)
            p.gather.add_item('Coin', 120)

            # Ensure 4+ Center A Sphere nodes are unlocked (Start / CA_Life_HP1 may already be active)
            unlocked = {str(x) for x in p.unlocked_sphere_nodes}
            for nid in ['CA_Life_HP1', 'CA_Life_HP2', 'CA_Life_HP3', 'CA_Life_HP4', 'CA_Life_TP1']:
                if nid not in unlocked:
                    check(f'Unlock {nid}', p.unlock_sphere_node(nid), nid)
            check('4+ Sphere nodes unlocked', len(p.unlocked_sphere_nodes) >= 4, str(len(p.unlocked_sphere_nodes)))

            # Pick free plots well clear (>700cm) of Shop/Blacksmith so U opens TownServiceWidget reliably
            blocker_locs = [
                pl.location + pl.stake_offset
                for pl in v.plots
                if pl.built and pl.kind in (u.TownBuilding.SHOP, u.TownBuilding.SMITH)
            ]
            for fg in u.GameplayStatics.get_all_actors_of_class(w, u.BlacksmithForge):
                blocker_locs.append(fg.get_actor_location())

            def clear_of_shop_or_forge(pl):
                pos = pl.location + pl.stake_offset
                return all(((pos.x - b.x)**2 + (pos.y - b.y)**2) >= 700.0**2 for b in blocker_locs)

            free = [
                pl for pl in v.plots
                if pl.flexible_use and not pl.built and pl.buildable_size >= 2000.0 and clear_of_shop_or_forge(pl)
            ]
            free.sort(key=lambda pl: (pl.location.x - 10000)**2 + (pl.location.y - 2000)**2)
            check('Enough free plots in Map_ElRuhnSky', len(free) >= 6, str(len(free)))

            def build_on(idx, cid):
                p.set_actor_location(free[idx].location + free[idx].stake_offset + u.Vector(0, 0, 110), False, True)
                v.select_building(cid)
                v.try_build_plot(free[idx].id, p)
                built = any(x.id == free[idx].id and x.built and str(x.catalog_id) == cid for x in v.plots)
                check(f'Build {cid}', built, f"{cid} Trust={v.trust} Bread={p.gather.get_count('Bread')}")

            # Build Village-era services first, then host Inn Feasts until Trust reaches LargeTown threshold (50)
            build_on(0, 'Inn')
            build_on(4, 'Chapel')
            feasts = 0
            while (v.trust + p.sphere_trust_bonus) < 50 and feasts < 15:
                if not v.execute_service_action(u.TownBuilding.INN, 'Feast', p):
                    break
                feasts += 1
            check('Trust reaches >= 50 via Inn Feasts for LargeTown', (v.trust + p.sphere_trust_bonus) >= 50, f"EffectiveTrust={v.trust + p.sphere_trust_bonus} Feasts={feasts}")

            for idx, cid in [(1, 'Bank'), (2, 'Bath'), (3, 'Academy'), (5, 'Manor')]:
                build_on(idx, cid)
            if v.building_catalog_open:
                v.toggle_building_catalog()

            state['inn_plot'] = next(pl for pl in v.plots if pl.id == free[0].id)
            state['bank_plot'] = next(pl for pl in v.plots if pl.id == free[1].id)
            state['acad_plot'] = next(pl for pl in v.plots if pl.id == free[3].id)

            # Stand at Bank and open UTownServiceWidget via U
            bp = state['bank_plot']
            p.set_actor_location(bp.location + bp.stake_offset + u.Vector(0, 0, 110), False, True)
            p.character_movement.stop_movement_immediately()
            state['stage'] = 'press_bank_u'
            state['stamp'] = now
            return

        if state['stage'] == 'press_bank_u':
            pulse(w, 'U')
            state['stage'] = 'bank_open'
            return

        if state['stage'] == 'bank_open':
            sw = p.service_widget
            check('U opens TownServiceWidget at Bank', sw is not None and sw.is_in_viewport())
            if sw:
                check('Bank Deposit10 works via ServiceWidget', sw.trigger_action('Deposit10'))
                check('BankVaultCoins == 10', v.bank_vault_coins == 10)
                sw.close_service()
                check('TownServiceWidget closes cleanly', not sw.is_in_viewport())

            # Stand at Academy and advance research with T quick-interact
            ap = state['acad_plot']
            p.set_actor_location(ap.location + ap.stake_offset + u.Vector(0, 0, 110), False, True)
            p.character_movement.stop_movement_immediately()
            state['stage'] = 'press_acad_t'
            state['stamp'] = now
            return

        if state['stage'] == 'press_acad_t':
            pulse(w, 'T')
            state['stage'] = 'acad_done'
            return

        if state['stage'] == 'acad_done':
            check('T at Academy advances research Tier 1', v.academy_research_level == 1, v.last_service_message)
            # Stand at Inn and rest via U modal
            ip = state['inn_plot']
            p.set_actor_location(ip.location + ip.stake_offset + u.Vector(0, 0, 110), False, True)
            p.character_movement.stop_movement_immediately()
            state['stage'] = 'press_inn_u'
            state['stamp'] = now
            return

        if state['stage'] == 'press_inn_u':
            pulse(w, 'U')
            state['stage'] = 'inn_open'
            return

        if state['stage'] == 'inn_open':
            sw = p.service_widget
            check('U opens TownServiceWidget at Inn', sw is not None and sw.is_in_viewport())
            day_before = v.day_index
            if sw:
                check('Inn Rest advances day via ServiceWidget', sw.trigger_action('Rest'))
                check('DayIndex incremented', v.day_index == day_before + 1)
                check('Bank Vault compounded > 10', v.bank_vault_coins > 10, str(v.bank_vault_coins))
                sw.close_service()

            check('Guild Rank promoted >= C (1)', v.town_guild_rank >= 1, f"Rank={v.get_guild_rank_name()} Score={v.get_guild_standing_score()}")
            saved_vault = v.bank_vault_coins
            saved_rank = v.town_guild_rank
            saved_coin = p.gather.get_count('Coin')
            v.save_village_state(p)
            p.gather.consume('Coin', min(10, saved_coin))
            v.reload_village_state(p)
            check('Reload restores BankVaultCoins', v.bank_vault_coins == saved_vault)
            check('Reload restores AcademyResearchLevel == 1', v.academy_research_level == 1)
            check('Reload restores TownGuildRank', v.town_guild_rank == saved_rank)
            check('Reload restores Coin count', p.gather.get_count('Coin') == saved_coin)
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
