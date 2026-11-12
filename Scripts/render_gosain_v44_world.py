import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain44';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert (O/'applied.json').exists()
origin=[0,0,0];mesh=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain44/Meshes/SM_IV_Continent_GosainWallInfill44')
output=B/'Docs/WorldDesign/Gosain44';output.mkdir(exist_ok=True)
views=[('Both_Islands',(32000,23000,-9200),(19500,38000,-20470)),('Capital_Tiers',(24500,38900,-18600),(22400,41800,-20440)),('Castle_Terrace',(23600,41200,-19600),(22474,42275,-20376))]
plan=json.loads((B/'ArtSource/World/Gosain38/whole_island_plan.json').read_text());ends=plan['bridge_endpoints_m'];cx=(ends[0][0]+ends[1][0])/2;cy=(ends[0][1]+ends[1][1])/2
views.append(('Walls_And_Bridge',(cx+900,cy-950,-19950),(cx,cy,-20535)))
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
