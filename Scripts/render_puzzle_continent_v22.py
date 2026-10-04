import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');OUT=B/'Docs/WorldDesign'
views=[('RemnantWorld_Rim',(1400,-2000,-18500),(0,20,-20100)),('RemnantWorld_River',(-200,-3800,-17900),(-2400,300,-19950)),('RemnantWorld_Context',(4300,-26000,4500),(0,20,-9500)),('RemnantWorld_Valley',(0,-1050,560),(0,100,35))]

state={'index':0,'stage':'camera','next':0,'completed':[]};holder={}
def write():(B/'Saved/remnant_world_render.json').write_text(json.dumps(state,indent=2))
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


