"""Capture the current tower village and cloud island from the Unreal viewport."""
import json, time, unreal
from pathlib import Path

root = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
output = root / 'Docs/WorldDesign/ElRuhnSky02'
output.mkdir(exist_ok=True)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert 'Map_ElRuhnSky.' in world.get_path_name()
views = [
    ('Tower_Village', (235,-380,205), (5,13,82)),
    ('Village_Parcels', (25,-180,550), (0,15,12)),
    ('Fountain_Approach', (20,-165,32), (0,20,86)),
    ('Sky_Island', (1180,-1550,655), (0,25,-140)),
]
state = {'index':0,'phase':'camera','next':time.monotonic()+1,'files':[]}
handle = {}

def tick(_):
    if time.monotonic()<state['next']:
        return
    if state['index']==len(views):
        (output/'complete.json').write_text(json.dumps({'status':'captured','files':state['files']},indent=2))
        unreal.unregister_slate_post_tick_callback(handle['callback'])
        return
    name,eye,target=views[state['index']]
    path=output/(name+'.png')
    if state['phase']=='camera':
        eye=unreal.Vector(*[v*100 for v in eye]);target=unreal.Vector(*[v*100 for v in target])
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
        state.update(phase='capture',next=time.monotonic()+11)
    elif state['phase']=='capture':
        state.update(old=path.stat().st_mtime if path.exists() else 0,started=time.monotonic(),phase='file',next=time.monotonic()+2)
        unreal.AutomationLibrary.take_high_res_screenshot(1800,1100,str(path),delay=.5)
    elif path.exists() and path.stat().st_mtime>state['old']:
        state['files'].append(str(path));state.update(index=state['index']+1,phase='camera',next=time.monotonic()+1)
    elif time.monotonic()-state['started']>60:
        (output/'complete.json').write_text(json.dumps({'status':'failed','view':name}))
        unreal.unregister_slate_post_tick_callback(handle['callback'])

(output/'complete.json').write_text(json.dumps({'status':'capturing'}))
handle['callback']=unreal.register_slate_post_tick_callback(tick)
