import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';stage='After' if (O/'applied.json').exists() else 'Before';output=B/('Docs/WorldDesign/Gosain58_'+stage);output.mkdir(exist_ok=True)
p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());j=len(p['xy'])-35;eye=(*p['xy'][j],p['z'][j]+3.5);target=(*p['xy'][j+12],p['z'][j+12]+2.5)
views=[('Right_Mountains',(21000,37000,-17000),(16400,42500,-20200)),('Right_Coast',(18500,41000,-19600),(17400,42600,-20300)),('Mine_Road',eye,target),('Lake_Shore',(27400,35000,-20200),(27000,36300,-20545)),('Kingdom',(32000,25000,-9000),(19500,38000,-20400)),('Mine_Yard',(15863.6616778,41888.3942205,-20257.5454744),(15971.2591849,41881.7778415,-20290.5454744))]
s={'i':0,'phase':0,'next':time.monotonic()+20,'done':[]};h={}
def tick(dt):
 if time.monotonic()<s['next']:return
 if s['i']>=len(views):unreal.unregister_slate_post_tick_callback(h['h']);(output/'native_views_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'stage':stage},indent=2));return
 name,eye,target=views[s['i']]
 if s['phase']==0:
  a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));s.update(phase=1,next=time.monotonic()+10)
 elif s['phase']==1:
  path=output/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
 else:
  path=output/(name+'.png')
  if path.exists() and path.stat().st_mtime>s['old']:s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
  elif time.monotonic()-s['started']>60:s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
