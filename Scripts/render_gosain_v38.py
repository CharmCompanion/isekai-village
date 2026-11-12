"""Native evidence of this milestone, using the actual saved scene."""
import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/Gosain38'
cx,cy=22173.92809189915,41624.713312447166
views=[
('Both_Islands',(18500,21500,-6500),(19000,38000,-20000)),
('Imperial_Bridge',(20500,41400,-20020),(19640,42600,-20540)),
('Capital_Bridge_Gate',(20120,42650,-20500),(19929,42839,-20570)),
('Western_Coast',(11000,35500,-19750),(12700,37000,-20400))]
s={'i':0,'phase':0,'next':time.monotonic()+25,'done':[]};h={}
def tick(dt):
    if time.monotonic()<s['next']:return
    if s['i']>=len(views):
        eye,target=views[0][1:]
        a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target])
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b))
        unreal.unregister_slate_post_tick_callback(h['h']);(O/'after_renders.json').write_text(json.dumps(s['done'],indent=2));return
    name,eye,target=views[s['i']];p=O/(name+'.png')
    if s['phase']==0:
        a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target])
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));s.update(phase=1,next=time.monotonic()+12)
    elif s['phase']==1:
        s['old']=p.stat().st_mtime if p.exists() else 0;unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(p),delay=.5);s.update(phase=2,next=time.monotonic()+2,start=time.monotonic())
    elif p.exists() and p.stat().st_mtime>s['old']:
        s['done'].append(str(p));s.update(i=s['i']+1,phase=0)
    elif time.monotonic()-s['start']>50:
        s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0)
h['h']=unreal.register_slate_post_tick_callback(tick)
