"""Native evidence of this milestone, using the actual saved scene."""
import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/Gosain40';O.mkdir(exist_ok=True)
cx,cy=22173.92809189915,41624.713312447166
views=[
('After_Capital',(cx+640,cy-970,-19160),(cx,cy-60,-19600)),
('After_Precinct',(cx+245,cy-325,-19480),(cx,cy+8,-19590)),
('After_Market',(cx+72,cy-363,-19616),(cx+20,cy-282,-19625)),
('After_Gate',(cx+12,cy-236,-19612),(cx,cy-133,-19605)),
('After_Terraces',(cx-730,cy-610,-19425),(cx-40,cy-90,-19618)),
('After_Reverse',(cx-510,cy+645,-19320),(cx,cy,-19600)),
('After_ElRuhn_Protected',(850,-1280,440),(0,30,-190))]
views=[(name,tuple(v-(683.48164 if j==2 else 0) for j,v in enumerate(eye)),tuple(v-(683.48164 if j==2 else 0) for j,v in enumerate(target))) if name!='After_ElRuhn_Protected' else (name,eye,target) for name,eye,target in views]
views.extend([('Both_Islands',(18500,21500,-6500),(19000,38000,-20350)),('Imperial_Bridge',(20500,41400,-20035),(19640,42600,-20555))])
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

