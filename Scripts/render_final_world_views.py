"""Nonblocking renderer review queue for the saved environment; no desktop capture."""
import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');OUT=B/'Docs/WorldDesign';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
views=[
 ('Trade_Pass_Review',(-328,-61,67.5),(-364,-85,59.5),False),
 ('Mine_Entrance_Review',(-293,275,84),(-331,295,71),False),
 ('Dungeon_Entrance_Review',(205,410,136),(230,450,120),False),
 ('Village_Ground_Review',(0,-21,26.8),(0,22,28),False),
 ('Farm_Final_Review',(200,-255,115),(128,-140,24.5),False),
 ('Harbor_Ocean_Review',(80,-460,26),(-35,-390,9),False),
 ('Layered_World_Review',(450,-600,390),(0,40,40),False),
 ('Large_Town_Defenses_Review',(410,-420,340),(40,40,35),True)]
future=[a for a in E.get_all_level_actors() if 'IVFutureLargeTown' in [str(t) for t in a.tags]]
def preview(show):
    for a in future:a.static_mesh_component.set_visibility(show);a.set_actor_hidden_in_game(not show)
state={'index':0,'stage':'camera','next':0,'completed':[]};holder={}
def write():
    (B/'Saved/world_render_review.json').write_text(json.dumps(state,indent=2))
def tick(delta):
    if time.monotonic()<state['next']:return
    i=state['index']
    if i>=len(views):
        preview(False)
        eye=unreal.Vector(45000,-60000,39000);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,4000,4000)))
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();state['stage']='complete';write();unreal.unregister_slate_post_tick_callback(holder['handle']);return
    name,eye,target,show=views[i];path=OUT/(name+'.png')
    if state['stage']=='camera':
        preview(show);a=unreal.Vector(*(v*100 for v in eye));b=unreal.Vector(*(v*100 for v in target));unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));state['next']=time.monotonic()+4;state['stage']='capture';write()
    elif state['stage']=='capture':
        state['old_mtime']=path.stat().st_mtime if path.exists() else 0;state['started']=time.monotonic();unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(path),delay=.5);state['stage']='waiting';state['next']=time.monotonic()+2;write()
    elif path.exists() and path.stat().st_mtime>state['old_mtime']:
        state['completed'].append(str(path));state['index']+=1;state['stage']='camera';state['next']=time.monotonic()+1;write()
    elif time.monotonic()-state['started']>180:
        preview(False);state['stage']='capture timeout';write();unreal.unregister_slate_post_tick_callback(holder['handle'])
    else:state['next']=time.monotonic()+1
holder['handle']=unreal.register_slate_post_tick_callback(tick)
