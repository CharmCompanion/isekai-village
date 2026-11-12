"""Read-only baseline of the actual world; capture assets and actor state."""
import unreal, json, hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O=B/'Saved/Gosain43'; O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
actors=[]; foliage=[]
def vec(v): return [v.x,v.y,v.z]
for a in E.get_all_level_actors():
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),'rotation':str(a.get_actor_rotation()),'tags':[str(t) for t in a.tags],'hidden':a.is_hidden_ed(),'folder':str(a.get_folder_path())}
    comps=[]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        q={'name':c.get_name(),'mesh':m.get_path_name() if m else None,'materials':[x.get_path_name() if x else None for x in c.get_materials()]}
        if isinstance(c,unreal.InstancedStaticMeshComponent):
            q['count']=c.get_instance_count()
            rows=[]
            for i in range(q['count']):
                t=c.get_instance_transform(i,True)
                rows.append([*vec(t.translation),*vec(t.scale3d),t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
            q['transforms_sha256']=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
            foliage.append({'actor':a.get_name(),**q,'transforms':rows})
        comps.append(q)
    row['components']=comps;actors.append(row)
(O/'baseline_actors.json').write_text(json.dumps(actors,indent=1))
(O/'baseline_foliage.json').write_text(json.dumps(foliage,separators=(',',':')))

