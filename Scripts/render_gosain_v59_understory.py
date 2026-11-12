import unreal,json,time,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/Gosain59';O.mkdir(exist_ok=True)
assert (B/'ArtSource/World/Gosain59/applied.json').exists()
p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());j=len(p['xy'])-35;eye=(*p['xy'][j],p['z'][j]+3.5);target=(*p['xy'][j+12],p['z'][j+12]+2.5)
j2=len(p['xy'])-65;eye2=(*p['xy'][j2],p['z'][j2]+1.8);target2=(*p['xy'][j2+5],p['z'][j2+5]+1.6)
views=[('Mine_Road',eye,target),('Woodland_Approach',eye2,target2),('Understory_Aerial',(eye[0]+160,eye[1]-200,eye[2]+150),(eye[0],eye[1],eye[2]-3.5))]
s={'i':0,'phase':0,'next':time.monotonic()+15,'done':[]};h={}
def tick(dt):
 if time.monotonic()<s['next']:return
 if s['i']>=len(views):unreal.unregister_slate_post_tick_callback(h['h']);(O/'native_views_complete.json').write_text(json.dumps({'files':s['done'],'status':'captured'},indent=2));return
 name,eye,target=views[s['i']]
 if s['phase']==0:
  a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));s.update(phase=1,next=time.monotonic()+12)
 elif s['phase']==1:
  path=O/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
 else:
  path=O/(name+'.png')
  if path.exists() and path.stat().st_mtime>s['old']:s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
  elif time.monotonic()-s['started']>60:s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
