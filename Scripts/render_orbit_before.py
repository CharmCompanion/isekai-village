import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');OUT=B/'Docs/WorldDesign'
views=[]
import math
for i in range(8):
 a=math.tau*i/8
 views.append(('Orbit_Before_%02d'%i,(1550*math.cos(a),1550*math.sin(a),80),(0,20,-270)))
views.extend([('Orbit_Before_Bottom',(0,-300,-1600),(0,20,-250)),('Orbit_Before_Top',(0,-1200,1000),(0,20,0))])

state={'index':0,'stage':'camera','next':0,'completed':[]};holder={}
def write():(B/'Saved/orbit_before_review.json').write_text(json.dumps(state,indent=2))
def tick(delta):
 if time.monotonic()<state['next']:return
 if state['index']>=len(views):
  state['stage']='complete';write();unreal.unregister_slate_post_tick_callback(holder['handle']);return
 name,eye,target=views[state['index']];path=OUT/(name+'.png')
 if state['stage']=='camera':
  a=unreal.Vector(*(v*100 for v in eye));b=unreal.Vector(*(v*100 for v in target));unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));state['next']=time.monotonic()+5;state['stage']='capture'
 elif state['stage']=='capture':
  state['mtime']=path.stat().st_mtime if path.exists() else 0;unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(path),delay=.5);state['stage']='waiting';state['next']=time.monotonic()+2
 elif path.exists() and path.stat().st_mtime>state['mtime']:state['completed'].append(str(path));state['index']+=1;state['stage']='camera'
 else:state['next']=time.monotonic()+1
 write()
holder['handle']=unreal.register_slate_post_tick_callback(tick)
