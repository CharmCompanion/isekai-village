import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
results=[]
for i in range(1,15):
    path='/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_'+str(i)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(path)
    if not cls:continue
    a=E.spawn_actor_from_class(cls,unreal.Vector(0,0,1000000),transient=True)
    try:
        parts=[]
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            t=c.get_world_transform();p=t.translation;r=t.rotation.rotator();s=t.scale3d
            bb=c.static_mesh.get_bounding_box()
            parts.append({'mesh':c.static_mesh.get_path_name(),'position':[p.x,p.y,p.z-1000000],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z],'min':[bb.min.x,bb.min.y,bb.min.z],'max':[bb.max.x,bb.max.y,bb.max.z],'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
        center,extent=a.get_actor_bounds(False)
        results.append({'name':str(i),'parts':parts,'center':[center.x,center.y,center.z-1000000],'extent':[extent.x,extent.y,extent.z]})
    finally:E.destroy_actor(a)
(O/'native_house_kits.json').write_text(json.dumps(results,indent=2))
(O/'merge_api.txt').write_text(str(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).merge_static_mesh_actors.__doc__))
