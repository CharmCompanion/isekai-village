import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain40';O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
info={}
for name in dir(unreal.InstancedFoliageActor):
    if any(s in name for s in ['foliage_type','instance_transform','used_foliage']):info[name]=str(getattr(unreal.InstancedFoliageActor,name).__doc__)
(O/'foliage_api.json').write_text(json.dumps(info,indent=2))
actors=[]
for a in E.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    c=a.static_mesh_component
    if not c.static_mesh:continue
    p=a.get_actor_location();sc=a.get_actor_scale3d();r=a.get_actor_rotation()
    actors.append({'name':a.get_name(),'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'location':[p.x,p.y,p.z],'scale':[sc.x,sc.y,sc.z],'rotation':[r.pitch,r.yaw,r.roll],'tags':[str(t) for t in a.tags]})
(O/'static_actors.json').write_text(json.dumps(actors,indent=2))
