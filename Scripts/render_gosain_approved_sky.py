import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/Gosain58_ApprovedSky';O.mkdir(exist_ok=True)
p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());j=len(p['xy'])-35
views=[('Gosain_Saved',(*p['xy'][j],p['z'][j]+3.5),(*p['xy'][j+12],p['z'][j+12]+2.5)),('ElRuhn_Saved',(1000,-1500,750),(0,0,150))]
S={'i':0,'phase':0,'next':time.monotonic()+1};H={}
def tick(dt):
 if time.monotonic()<S['next']:return
 if S['i']>=len(views):
  unreal.unregister_slate_post_tick_callback(H['h']);(O/'complete.json').write_text(json.dumps({'status':'captured','saved_sky_z_cm':-2060000}));return
 name,eye,target=views[S['i']]
 if S['phase']==0:
  p=unreal.Vector(*[v*100 for v in eye]);t=unreal.Vector(*[v*100 for v in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,t));S.update(phase=1,next=time.monotonic()+14)
 elif S['phase']==1:
  unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(O/(name+'.png')),delay=.5);S.update(phase=2,next=time.monotonic()+4)
 else:S.update(i=S['i']+1,phase=0,next=time.monotonic()+1)
H['h']=unreal.register_slate_post_tick_callback(tick)
