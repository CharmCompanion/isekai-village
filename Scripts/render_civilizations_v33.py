"""Review cameras for v33 kingdom capitals and the Gosain island city."""
import unreal, time, json, os
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
OUT = B / 'Docs/WorldDesign'
data = json.loads((B / 'Saved/AdventureWorldSource/civilization_instances_v33.json').read_text())
land = data['landmarks']
views = []


def find(name_part=None, culture=None, tier=None):
    for q in land:
        if name_part and name_part not in q['name']:
            continue
        if culture and q.get('culture') != culture:
            continue
        if tier and q.get('tier') != tier:
            continue
        return q
    return next(q for q in land if not culture or q.get('culture') == culture)


cit = find('island capital') or find(culture='citadel')
x, y, z, r = cit['xy_m'][0], cit['xy_m'][1], cit['z'], cit['radius']
views.append(('Civ33_GosainCapital', (x + r * .55, y - r * .7, z + r * .45), (x, y, z + 180)))
views.append(('Civ33_GosainWalls', (x + 2800, y - 4200, z + 2400), (x, y, z + 80)))
views.append(('Civ33_GosainCourtyard', (x + 240, y - 380, z + 160), (x, y + 80, z + 120)))
mon = find('monastery quarter')
if mon:
    mx, my, mz = mon['xy_m'][0], mon['xy_m'][1], mon['z']
    views.append(('Civ33_GosainBridges', ((x + mx) * .5 + 900, (y + my) * .5 - 1400, z + 700), ((x + mx) * .5, (y + my) * .5, z + 40)))
for name, culture in [('KelsinCapital', 'arcane'), ('YozuanCapital', 'nomad'), ('RabaricCapital', 'farming'), ('VylfodCapital', 'wetland')]:
    q = find(culture=culture, tier='capital') or find(culture=culture)
    x, y, z, r = q['xy_m'][0], q['xy_m'][1], q['z'], min(q['radius'], 900)
    views.append(('Civ33_' + name, (x + r * 1.4, y - r * 1.8, z + r * 1.1), (x, y, z + 80)))
views.append(('Civ33_Island', (850, -1280, 440), (0, 30, -190)))

state = {'index': 0, 'stage': 'warm', 'next': time.monotonic() + 70, 'completed': []}
holder = {}


def tick(delta):
    if time.monotonic() < state['next']:
        return
    if state['stage'] == 'warm':
        state['stage'] = 'camera'
    if state['index'] >= len(views):
        unreal.unregister_slate_post_tick_callback(holder['handle'])
        (OUT / 'Civ33_renders.json').write_text(json.dumps(state['completed'], indent=1))
        unreal.log('RENDER_COMPLETE %d views' % len(state['completed']))
        if os.environ.get('IV_RENDER_QUIT') == '1':
            unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), 'QUIT_EDITOR')
        return
    name, eye, target = views[state['index']]
    path = OUT / (name + '.png')
    if state['stage'] == 'camera':
        a = unreal.Vector(*(v * 100 for v in eye))
        b = unreal.Vector(*(v * 100 for v in target))
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(a, unreal.MathLibrary.find_look_at_rotation(a, b))
        state['next'] = time.monotonic() + 6
        state['stage'] = 'capture'
    elif state['stage'] == 'capture':
        state['mtime'] = path.stat().st_mtime if path.exists() else 0
        unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, str(path), delay=.5)
        state['stage'] = 'waiting'
        state['t0'] = time.monotonic()
        state['next'] = time.monotonic() + 2
    elif path.exists() and path.stat().st_mtime > state['mtime']:
        state['completed'].append(str(path))
        state['index'] += 1
        state['stage'] = 'camera'
        unreal.log('SHOT ' + name)
    elif time.monotonic() - state['t0'] > 40:
        state['index'] += 1
        state['stage'] = 'camera'
    else:
        state['next'] = time.monotonic() + 1


holder['handle'] = unreal.register_slate_post_tick_callback(tick)
