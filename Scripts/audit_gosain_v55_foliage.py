import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain55';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if not c.static_mesh:continue
  transforms=[]
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,True);p=t.translation;r=t.rotation;s=t.scale3d
   transforms.append([p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z])
  rows.append({'name':c.get_name(),'mesh':c.static_mesh.get_path_name(),'transforms':transforms,'count':len(transforms)})
(O/'baseline_foliage.json').write_text(json.dumps(rows))
(O/'audit_ready.json').write_text(json.dumps({'status':'ready','components':len(rows)}))
