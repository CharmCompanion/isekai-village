import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain52';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert (O/'applied.json').exists()
origin=[0,0,0];mesh=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain52/Meshes/SM_IV_Continent_GosainLake52')
output=B/'Docs/WorldDesign/Gosain52';output.mkdir(exist_ok=True)
views=[('Southern_Lake',(29500,32500,-17600),(27000,36300,-20545)),('Lake_Shore',(27400,35000,-20200),(27000,36300,-20545)),('Restored_Forest',(27000,34500,-18100),(24950,37800,-20520))]
views.append(('Grotto',(26289.78042433247, 37281.17120985487, -20505.1556108403),(26254.61186449179, 37366.39545757072, -20519.1556108403)))
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
