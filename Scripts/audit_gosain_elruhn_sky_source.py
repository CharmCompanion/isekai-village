"""Read-only inventory for an isolated El Ruhn sky map."""
import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[];fol=[]
for a in E.get_all_level_actors():
 p=a.get_actor_location();row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'folder':str(a.get_folder_path()),'p':[p.x/100,p.y/100,p.z/100],'tags':[str(t) for t in a.tags],'hidden':a.get_editor_property('hidden')}
 cs=a.get_components_by_class(unreal.StaticMeshComponent)
 row['meshes']=[{'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'visible':c.is_visible(),'mats':[m.get_path_name() if m else None for m in c.get_materials()]} for c in cs if not isinstance(c,unreal.InstancedStaticMeshComponent)]
 if math.hypot(p.x,p.y)<500000 or not isinstance(a,unreal.StaticMeshActor):rows.append(row)
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  n=c.get_instance_count();near=0;lo=[1e30]*3;hi=[-1e30]*3
  for i in range(n):
   q=c.get_instance_transform(i,True).translation
   if abs(q.x)<180000 and abs(q.y)<180000 and q.z>-180000:near+=1
   for j,v in enumerate([q.x/100,q.y/100,q.z/100]):lo[j]=min(lo[j],v);hi[j]=max(hi[j],v)
  fol.append({'actor':a.get_name(),'component':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'n':n,'near_island':near,'min':lo,'max':hi})
(O/'scene_audit.json').write_text(json.dumps({'actors':rows,'instances':fol},indent=2))
api={'save_map':str(unreal.EditorLoadingAndSavingUtils.save_map.__doc__),'remove_instances':str(unreal.InstancedStaticMeshComponent.remove_instances.__doc__)}
(O/'api.json').write_text(json.dumps(api,indent=2))
exec(compile((B/'Scripts/elruhn_sky_editor_session.py').read_text(),'elruhn_sky_editor_session','exec'),{'__name__':'__main__'})
