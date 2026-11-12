import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain50';O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def state(a):
    t=a.get_actor_transform();p=t.translation;q=t.rotation;s=t.scale3d
    return {'name':a.get_name(),'label':a.get_actor_label(),'transform':[p.x,p.y,p.z,q.x,q.y,q.z,q.w,s.x,s.y,s.z],'hidden':a.is_hidden_ed(),'mesh':a.static_mesh_component.static_mesh.get_path_name() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh else None}
assert not (O/'baseline.json').exists(),'Do not overwrite baseline'
result={'actors':[state(a) for a in E.get_all_level_actors()],'trees':[]}
for i in range(1,6):
    path='/Game/AdvancedVillagePack/Meshes/SM_Tree_Var0'+str(i);m=unreal.load_asset(path)
    if m:
        box=m.get_bounding_box();result['trees'].append({'path':path,'min':[box.min.x,box.min.y,box.min.z],'max':[box.max.x,box.max.y,box.max.z]})
(O/'baseline.json').write_text(json.dumps(result,indent=2))
