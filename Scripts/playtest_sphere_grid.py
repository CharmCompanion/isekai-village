"""Live PIE verification of all 12 Sphere Grid discs, K/N UI cycling, town perks (+2 lofts, shop haggle), combat artes, and persistence."""
from pathlib import Path
import json, time, traceback, uuid, unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report_path = r / 'Saved/sphere_grid_playtest.json'
slot = 'VerifySphereGrid_' + uuid.uuid4().hex
report = {'success': False, 'slot': slot, 'checks': []}
stage = 'start'
stamp = time.monotonic()
started = stamp
handle = None
release = None
state = {}
u.EditorPythonScripting.set_keep_python_script_alive(True)


def write():
    report_path.write_text(json.dumps(report, indent=2))


def check(name, yes):
    assert yes, name
    report['checks'].append(name)


def pulse(w, key):
    global release
    u.SystemLibrary.execute_console_command(w, 'Input.+key ' + key)
    release = key


def finish(error=None):
    global stage, stamp
    report['success'] = not bool(error)
    if error:
        report['error'] = error
    write()
    u.EditorLevelLibrary.editor_end_play()
    stage = 'ending'
    stamp = time.monotonic()


def face_order(grid, disc, flipped):
    if disc == 0:
        return list(grid.flip_node_order if flipped else grid.life_node_order)
    if disc == 1:
        return list(grid.villager_node_order if flipped else grid.work_node_order)
    return list(grid.extra_discs[disc - 2].node_order)


def unlock_face(p, grid, disc, flipped):
    for nid in face_order(grid, disc, flipped):
        p.unlock_sphere_node(nid)


def tick(dt):
    global stage, stamp, release
    try:
        now = time.monotonic()
        if stage == 'ending':
            if now - stamp < 3:
                return
            if u.GameplayStatics.does_save_game_exist(slot, 0):
                u.GameplayStatics.delete_game_in_slot(slot, 0)
            u.unregister_slate_post_tick_callback(handle)
            u.EditorPythonScripting.set_keep_python_script_alive(False)
            return

        if now - started > 180:
            return finish('Timeout at ' + stage)

        if stage == 'start':
            if now - stamp < 3:
                return
            u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play()
            stage = 'load'
            stamp = now
            return

        worlds = u.EditorLevelLibrary.get_pie_worlds(False)
        if not worlds:
            return
        w = worlds[0]
        v = next(iter(u.GameplayStatics.get_all_actors_of_class(w, u.VillageRuntime)), None)
        p = u.GameplayStatics.get_player_character(w, 0)
        if not v or not p:
            return

        if release:
            u.SystemLibrary.execute_console_command(w, 'Input.-key ' + release)
            release = None
            return

        if stage == 'load':
            if now - stamp < 8:
                return
            v.set_editor_property('construction_save_slot', slot)
            v.set_editor_property('window_seconds', 10000.)
            v.initialize_construction()
            grid = p.sphere_grid
            check('SphereGrid loaded with 12 discs', grid is not None and grid.disc_count() == 12)
            check('4 starter EquippedArtes initialized on BeginPlay', len(p.equipped_artes) == 4 and p.equipped_artes[0] is not None)

            p.set_editor_property('sphere_points', 220)
            # Progress Center A (Life -> Adventurer)
            unlock_face(p, grid, 0, False)
            check('Flip Center A -> Adventurer', p.flip_sphere_grid())
            unlock_face(p, grid, 0, True)
            check('Center B unlocked after Adventurer', p.center_b_unlocked and grid.is_disc_unlocked(1, p.unlocked_sphere_nodes))

            # Progress Center B (Work -> Town Main unlocked; Villager -> Combat Main unlocked)
            p.select_sphere_disc(1)
            unlock_face(p, grid, 1, False)
            check('Town Main unlocked after Work', grid.is_disc_unlocked(3, p.unlocked_sphere_nodes))
            check('Combat Main locked before Villager complete', not grid.is_disc_unlocked(5, p.unlocked_sphere_nodes))
            check('Flip Center B -> Villager', p.flip_sphere_grid())
            unlock_face(p, grid, 1, True)
            check('Combat Main unlocked after Villager complete', grid.is_disc_unlocked(5, p.unlocked_sphere_nodes) and grid.is_disc_unlocked(6, p.unlocked_sphere_nodes))

            # Unlock all Main + Endgame discs
            for d in range(2, 12):
                check(f'Disc {d} unlocked for progression', grid.is_disc_unlocked(d, p.unlocked_sphere_nodes))
                p.select_sphere_disc(d)
                unlock_face(p, grid, d, False)

            check('Domain LoftBeds+2 & Economy ShopHaggle active', p.has_sphere_skill('LoftBeds+2') and p.has_sphere_skill('ShopHaggle'))
            check('Soulsmith VesselAnchor & Artificer SanctuaryCamp active', p.has_sphere_skill('VesselAnchor') and p.has_sphere_skill('SanctuaryCamp'))

            # Verify +2 bed loft upgrade on a built Cottage
            p.gather.add_item('Wood', 60)
            p.gather.add_item('Stone', 20)
            free = [x for x in v.plots if x.flexible_use and not x.built]
            free.sort(key=lambda x: (x.location.x - 10000)**2 + (x.location.y - 2000)**2)
            house_plot = free[0]
            state['house_id'] = str(house_plot.id)
            p.set_actor_location(house_plot.location + house_plot.stake_offset + u.Vector(0, 0, 110), False, True)
            check('Select Cottage', v.select_building('Cottage'))
            v.try_build_plot(house_plot.id, p)
            built_plot = next(x for x in v.plots if str(x.id) == state['house_id'])
            base_beds = built_plot.bed_bonus
            v.try_build_plot(house_plot.id, p)  # loft upgrade
            upgraded_plot = next(x for x in v.plots if str(x.id) == state['house_id'])
            check('Expanded Lofts adds +2 beds on upgrade', upgraded_plot.bed_bonus == base_beds + 2)
            if v.building_catalog_open:
                v.toggle_building_catalog()

            # Test UI open (K) and cycle disc (N)
            p.select_sphere_disc(0)
            pulse(w, 'K')
            stage = 'grid_opened'
            stamp = now
            return

        if stage == 'grid_opened':
            if not p.sphere_grid_open:
                if now - stamp < 3:
                    return
                raise AssertionError('K did not open Sphere Grid')
            check('K opens Sphere Grid UI', p.sphere_grid_open)
            state['disc_before'] = p.sphere_disc
            pulse(w, 'N')
            stage = 'grid_cycled'
            stamp = now
            return

        if stage == 'grid_cycled':
            if p.sphere_disc == state['disc_before']:
                if now - stamp < 3:
                    return
                raise AssertionError('N did not cycle Sphere Grid disc')
            check('N cycles unlocked Sphere Grid discs', p.sphere_disc != state['disc_before'])
            p.select_sphere_disc(9)  # non-center disc (Summons)
            pulse(w, 'K')
            stage = 'grid_closed'
            stamp = now
            return

        if stage == 'grid_closed':
            if p.sphere_grid_open:
                if now - stamp < 3:
                    return
                raise AssertionError('K did not close Sphere Grid')
            check('K closes Sphere Grid UI', not p.sphere_grid_open)

            # Cast SpreadFan projectile in live PIE
            p.activate_focus_mode()
            p.trigger_arte(0)
            u.GameplayStatics.set_global_time_dilation(w, 1.0)
            projs = list(u.GameplayStatics.get_all_actors_of_class(w, u.SpellProjectile))
            check('Live PIE SpreadFan spawns >= 3 projectiles', len(projs) >= 3)

            # Save and reload verification (confirm Disc 9 & +2 beds persist)
            check('Save Village State succeeds', v.save_village_state(p))
            p.select_sphere_disc(0)
            v.reload_village_state(p)
            check('Reload preserves Disc >= 2 (Disc 9)', p.sphere_disc == 9)
            reloaded_plot = next(x for x in v.plots if str(x.id) == state['house_id'])
            check('Reload preserves Expanded Loft +2 beds', reloaded_plot.bed_bonus >= 4)

            return finish()

    except Exception as ex:
        finish(traceback.format_exc())


handle = u.register_slate_post_tick_callback(tick)
