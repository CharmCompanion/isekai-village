"""Native exterior/interior review of the applied mine."""
import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57'
assert (O/'applied.json').exists()
plan=json.loads((O/'site_plan.json').read_text());C=plan['center'];F=plan['forward'];S=plan['side'];Z=plan['yard_floor_z']
output=B/'Docs/WorldDesign/Gosain57';output.mkdir(exist_ok=True)
def local(d,l,z):return (C[0]+F[0]*d+S[0]*l,C[1]+F[1]*d+S[1]*l,Z+z)
views=[('Mine_Yard',local(-58,-65,38),local(28,0,5)),('Mine_Entrance',local(-15,0,3),local(39,0,4)),('Mine_Interior',local(36,0,2),local(75,0,3)),('Mine_Looking_Out',local(55,0,2),local(-15,0,2)),('Mine_Hillside',local(-165,145,110),local(45,0,7)),('Mountain_Context',(14900,40800,-19400),(15950,41900,-20300)),('Mine_Rear',local(175,65,42),local(72,0,8))]
s={'i':0,'phase':0,'next':time.monotonic()+20,'done':[]};h={}
def tick(dt):
 if time.monotonic()<s['next']:return
 if s['i']>=len(views):
  unreal.unregister_slate_post_tick_callback(h['h']);(output/'native_views_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'views':views},indent=2));return
 name,eye,target=views[s['i']]
 if s['phase']==0:
  p=unreal.Vector(*[v*100 for v in eye]);q=unreal.Vector(*[v*100 for v in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,q));s.update(phase=1,next=time.monotonic()+10)
 elif s['phase']==1:
  path=output/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
 else:
  path=output/(name+'.png')
  if path.exists() and path.stat().st_mtime>s['old']:s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
  elif time.monotonic()-s['started']>60:s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
