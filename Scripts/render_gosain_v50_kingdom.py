import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain50';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert (O/'applied.json').exists()
origin=[0,0,0];mesh=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain50/Meshes/SM_IV_Continent_GosainKingdom50')
output=B/'Docs/WorldDesign/Gosain50';output.mkdir(exist_ok=True)
views=[('Kingdom_Overview',(32000,25000,-9000),(19500,38000,-20400)),('Royal_Forest_Lake',(28000,33500,-16700),(25000,37800,-20534)),('Twin_Towns',(24500,37000,-17000),(18500,41000,-20350)),('Mountain_Tower',(18000,36000,-18000),(13500,42000,-20300)),('Knight_School',(16200,39100,-19900),(15784,39745,-20470))]
s={'i':0,'phase':0,'next':time.monotonic()+25,'done':[]};h={}
def tick(dt):
    if time.monotonic()<s['next']:return
    if s['i']>=len(views):
        unreal.unregister_slate_post_tick_callback(h['h']);(output/'native_views_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'mesh':mesh.get_path_name(),'temporary_actor_removed':True}));return
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
