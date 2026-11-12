"""Temporary native comparison; restore original shared sky transform, never save it."""
import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/Gosain58_AtmosphereStudy';O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkyAtmosphere));original=a.get_actor_location()
p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());j=len(p['xy'])-35;eye=(*p['xy'][j],p['z'][j]+3.5);target=(*p['xy'][j+12],p['z'][j+12]+2.5)
views=[('Gosain_Current',False,eye,target),('ElRuhn_Current',False,(1000,-1500,750),(0,0,150)),('Gosain_CorrectedSky',True,eye,target),('ElRuhn_CorrectedSky',True,(1000,-1500,750),(0,0,150))]
state={'i':0,'phase':0,'next':time.monotonic()+2,'done':[]};handle={}
def finish(error=None):
 a.set_actor_location(original,False,False);unreal.unregister_slate_post_tick_callback(handle['id']);now=a.get_actor_location()
 (O/'comparison_complete.json').write_text(json.dumps({'files':state['done'],'original_sky_location_cm':[original.x,original.y,original.z],'restored_location_cm':[now.x,now.y,now.z],'restored':now==original,'saved':False,'error':error},indent=2))
def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  if state['i']>=len(views):finish();return
  name,correct,eye,target=views[state['i']]
  if state['phase']==0:
   a.set_actor_location(unreal.Vector(original.x,original.y,-2060000.) if correct else original,False,False)
   p=unreal.Vector(*[x*100 for x in eye]);t=unreal.Vector(*[x*100 for x in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,t));state.update(phase=1,next=time.monotonic()+15)
  elif state['phase']==1:
   path=O/(name+'.png');state.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
  else:
   path=O/(name+'.png')
   if path.exists() and path.stat().st_mtime>state['old']:state['done'].append(str(path));state.update(i=state['i']+1,phase=0,next=time.monotonic()+2)
   elif time.monotonic()-state['started']>60:finish('Screenshot timeout')
 except Exception as error:finish(str(error));raise
handle['id']=unreal.register_slate_post_tick_callback(tick)
