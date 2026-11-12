"""Street-level and aerial review cameras for v34 towns."""
import unreal, time, json, os
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
OUT = B / 'Docs/WorldDesign'
data = json.loads((B / 'Saved/AdventureWorldSource/civilization_instances_v34.json').read_text())
land = data['landmarks']
views = []


def find(part=None, culture=None):
    for q in land:
        if part and part not in q['name']:
            continue
        if culture and q.get('culture') != culture:
            continue
        return q
    return land[0]


def aerial(q, name, dist=420):
    x, y, z = q['xy_m'][0], q['xy_m'][1], q['z']
    views.append((name, (x + dist * .85, y - dist * 1.15, z + dist * .55), (x, y, z + 18)))


def street(q, name):
    x, y, z = q['xy_m'][0], q['xy_m'][1], q['z']
    views.append((name, (x + 28, y - 36, z + 7.5), (x, y + 4, z + 4)))


cit = find('island capital')
aerial(cit, 'Civ34_GosainAerial', 520)
street(cit, 'Civ34_GosainStreet')
views.append(('Civ34_GosainPlaza', (cit['xy_m'][0] + 22, cit['xy_m'][1] - 32, cit['z'] + 9), (cit['xy_m'][0], cit['xy_m'][1] + 6, cit['z'] + 12)))
ple = find('pleasure')
aerial(ple, 'Civ34_PleasureAerial', 480)
street(ple, 'Civ34_PleasureStreet')
for name, culture in [('KelsinStreet', 'arcane'), ('YozuanStreet', 'nomad'), ('RabaricStreet', 'farming')]:
    q = find(culture=culture)
    street(q, 'Civ34_' + name)
    aerial(q, 'Civ34_' + name.replace('Street', 'Aerial'), 380)
views.append(('Civ34_Island', (850, -1280, 440), (0, 30, -190)))

state = {'index': 0, 'stage': 'warm', 'next': time.monotonic() + 70, 'completed': []}
holder = {}


def tick(delta):
    if time.monotonic() < state['next']:
        return
    if state['stage'] == 'warm':
        state['stage'] = 'camera'
    if state['index'] >= len(views):
        unreal.unregister_slate_post_tick_callback(holder['handle'])
        (OUT / 'Civ34_renders.json').write_text(json.dumps(state['completed'], indent=1))
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
