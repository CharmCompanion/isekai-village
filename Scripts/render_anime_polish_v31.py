"""Ground-level and rim review renders for the v31 anime polish pass.

Run inside the editor with Map_AnimeAdventure open, or via
  UnrealEditor.exe <uproject> /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure -ExecCmds="py Scripts/render_anime_polish_v31.py"
Captures go to Docs/WorldDesign/AnimePolish31_*.png. Set IV_RENDER_QUIT=1 in the environment to quit the editor when done.
"""
import unreal, time, json, os
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
MAP = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure'
WS = [unreal.ObjectTypeQuery.ECC_WORLD_STATIC]

# (name, eye_xy_m, eye_z_m or None=ground+1.7, target (x, y, z_or_None=ground+1.5))
VIEWS = [
    ('Village', (0, -20), None, (0, 200, None)),
    ('Meadow', (60, -60), None, (90, -40, None)),
    ('Inn', (-20, -45), None, (-38, -26, None)),
    ('Farm', (130, -110), None, (110, -181, None)),
    ('Lake', (-220, -300), None, (-300, -340, None)),
    ('LakeBank', (-250, -400), None, (-300, -460, None)),
    ('Forest', (-120, 150), None, (-200, 260, None)),
    ('DungeonPath', (200, 400), None, (230, 445, None)),
    ('FrontEdge', (120, -555), None, (-250, -560, None)),
    ('RimFront', (0, -900), 60, (0, -520, 15)),
    ('RimEast', (700, -150), 90, (430, -100, 30)),
    ('RimWest', (-750, 60), 110, (-470, 20, 50)),
    ('RimNorth', (0, 820), 150, (0, 500, 130)),
    ('Aerial', (250, -350), 260, (0, 0, 30)),
    ('Island', (900, -1300), 650, (0, 30, 0)),
]


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def ground_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single_for_objects(world(), unreal.Vector(x * 100, y * 100, 60000), unreal.Vector(x * 100, y * 100, -60000), WS, True, [], unreal.DrawDebugTrace.NONE, True)
    if hit and hit.to_tuple()[0]:
        return hit.to_tuple()[5].z / 100.0
    return None


def start_render(prefix='AnimePolish31_', out_dir=B / 'Docs/WorldDesign', views=VIEWS, warmup=20.0, on_complete=None, quit_when_done=None):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    if quit_when_done is None:
        quit_when_done = os.environ.get('IV_RENDER_QUIT') == '1'
    state = {'i': 0, 'stage': 'warm', 'next': time.monotonic() + warmup, 'done': []}
    holder = {}

    def tick(delta):
        if time.monotonic() < state['next']:
            return
        if state['stage'] == 'warm':
            state['stage'] = 'camera'
        if state['i'] >= len(views):
            unreal.unregister_slate_post_tick_callback(holder['h'])
            (out_dir / (prefix + 'renders.json')).write_text(json.dumps(state['done'], indent=1))
            unreal.log('RENDER_COMPLETE %d views' % len(state['done']))
            if on_complete:
                on_complete()
            if quit_when_done:
                unreal.SystemLibrary.execute_console_command(world(), 'QUIT_EDITOR')
            return
        name, exy, ez, tgt = views[state['i']]
        path = out_dir / (prefix + name + '.png')
        if state['stage'] == 'camera':
            gz = ground_z(*exy)
            ezm = ez if ez is not None else ((gz if gz is not None else 30) + 1.7)
            tz = tgt[2]
            if tz is None:
                g2 = ground_z(tgt[0], tgt[1]); tz = (g2 if g2 is not None else ezm) + 1.5
            a = unreal.Vector(exy[0] * 100, exy[1] * 100, ezm * 100); b = unreal.Vector(tgt[0] * 100, tgt[1] * 100, tz * 100)
            unreal.EditorLevelLibrary.set_level_viewport_camera_info(a, unreal.MathLibrary.find_look_at_rotation(a, b))
            state['stage'] = 'capture'; state['next'] = time.monotonic() + 5
        elif state['stage'] == 'capture':
            state['mtime'] = path.stat().st_mtime if path.exists() else 0
            unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, str(path), delay=0.5)
            state['stage'] = 'waiting'; state['t0'] = time.monotonic(); state['next'] = time.monotonic() + 2
        elif path.exists() and path.stat().st_mtime > state['mtime']:
            state['done'].append(str(path)); state['i'] += 1; state['stage'] = 'camera'; unreal.log('SHOT ' + name)
        elif time.monotonic() - state['t0'] > 40:
            state['i'] += 1; state['stage'] = 'camera'
        else:
            state['next'] = time.monotonic() + 1

    holder['h'] = unreal.register_slate_post_tick_callback(tick)
    return holder


if __name__ == '__main__':
    assert world().get_path_name().startswith(MAP + '.'), 'open Map_AnimeAdventure first'
    start_render()
