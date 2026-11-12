import unreal,time,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Docs/WorldDesign/Gosain37');O.mkdir(exist_ok=True)
views=[
('Before_Capital_Context',(27700,35500,-15500),(23200,39600,-19500)),
('Before_Cathedral',(22650,40900,-19200),(22174,41625,-19580)),
('Before_Street',(22225,41525,-19622),(22174,41630,-19610)),
('Before_Wall',(25600,35200,-19800),(25100,36300,-20080)),
('Before_Monastery',(17800,34100,-16700),(14250,39000,-19350))]
state={'i':0,'phase':0,'next':time.monotonic()+12,'done':[]};h={}
def tick(dt):
    if time.monotonic()<state['next']:return
    if state['i']>=len(views):
        unreal.unregister_slate_post_tick_callback(h['h']);(O/'before_renders.json').write_text(json.dumps(state['done'],indent=2));return
    name,eye,target=views[state['i']];p=O/(name+'.png')
    if state['phase']==0:
        a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target])
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b))
        state.update(phase=1,next=time.monotonic()+12)
    elif state['phase']==1:
        state['old']=p.stat().st_mtime if p.exists() else 0
        unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(p),delay=.5)
        state.update(phase=2,next=time.monotonic()+2,start=time.monotonic())
    elif p.exists() and p.stat().st_mtime>state['old']:
        state['done'].append(str(p));state.update(i=state['i']+1,phase=0)
    elif time.monotonic()-state['start']>45:
        state['done'].append('FAILED '+name);state.update(i=state['i']+1,phase=0)
h['h']=unreal.register_slate_post_tick_callback(tick)
