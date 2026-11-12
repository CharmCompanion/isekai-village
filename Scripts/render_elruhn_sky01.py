"""Native editor views, including full support system and the tower entrance."""
import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Docs/WorldDesign/ElRuhnSky01';O.mkdir(exist_ok=True);q=json.loads((B/'ArtSource/World/ElRuhnSky01/source.json').read_text());cx,cy,cz=q['tower_origin_m']
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
views=[('Sky_Kingdom',(1500,-2100,850),(0,0,-120)),('Five_Stones',(0,-700,1700),(0,0,-120)),('Tower_Approach',(cx+65,cy-160,cz+40),(cx,cy,cz+83)),('Grand_Entrance',(cx+18,cy-97,cz+8),(cx,cy-25,cz+23)),('Underside',(-1350,-1850,-100),(0,0,-180))]
center_path=B/'ArtSource/World/ElRuhnSky01/centering_applied.json'
if center_path.exists():
 ix,iy=json.loads(center_path.read_text())['island_center_m'];views.insert(1,('Centered_Top',(ix,iy,1800),(ix,iy,-120)))
S={'i':0,'phase':0,'next':time.monotonic()+2,'files':[]};H={}
(O/'complete.json').write_text(json.dumps({'status':'capturing'}))
def tick(dt):
 if time.monotonic()<S['next']:return
 if S['i']>=len(views):
  unreal.unregister_slate_post_tick_callback(H['h']);(O/'complete.json').write_text(json.dumps({'status':'captured','files':S['files']},indent=2));return
 name,eye,target=views[S['i']];p=O/(name+'.png')
 if S['phase']==0:
  a=unreal.Vector(*[v*100 for v in eye]);b=unreal.Vector(*[v*100 for v in target]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));S.update(phase=1,next=time.monotonic()+16)
 elif S['phase']==1:
  S.update(old=p.stat().st_mtime if p.exists() else 0,started=time.monotonic(),phase=2,next=time.monotonic()+3);unreal.AutomationLibrary.take_high_res_screenshot(1800,1100,str(p),delay=.5)
 else:
  if p.exists() and p.stat().st_mtime>S['old']:S['files'].append(str(p));S.update(i=S['i']+1,phase=0,next=time.monotonic()+1)
  elif time.monotonic()-S['started']>70:S['files'].append('FAILED '+name);S.update(i=S['i']+1,phase=0,next=time.monotonic()+1)
H['h']=unreal.register_slate_post_tick_callback(tick)
