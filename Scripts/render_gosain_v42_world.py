import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain42';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
d=json.loads((O/'district.json').read_text());origin=d['mesh']['origin_m'];mesh=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain42/Meshes/'+d['mesh']['name'])
assert (O/'applied.json').exists()
output=B/'Docs/WorldDesign/Gosain42'
views=[('World_Aerial',(-140,-360,130),(-345,-100,15)),('World_Reverse',(-560,110,105),(-350,-95,15)),('World_Street',(-420,-180,4),(-384,-150,12))]
s={'i':0,'phase':0,'next':time.monotonic()+25,'done':[]};h={}
def tick(dt):
    if time.monotonic()<s['next']:return
    if s['i']>=len(views):
        unreal.unregister_slate_post_tick_callback(h['h']);(output/'in_context_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'mesh':mesh.get_path_name(),'temporary_actor_removed':True}));return
    name,eye,target=views[s['i']]
    if s['phase']==0:
        p=unreal.Vector(*[(origin[j]+eye[j])*100 for j in range(3)]);q=unreal.Vector(*[(origin[j]+target[j])*100 for j in range(3)]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,q));s.update(phase=1,next=time.monotonic()+10)
    elif s['phase']==1:
        path=output/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
    else:
        path=output/(name+'.png')
        if path.exists() and path.stat().st_mtime>s['old']:s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
        elif time.monotonic()-s['started']>60:s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
