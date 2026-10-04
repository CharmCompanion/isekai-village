import unreal,json
from pathlib import Path
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.InstancedFoliageActor):
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   m=c.static_mesh
   if m and m.get_name()=='SM_OakTree2':
    for i in range(c.get_instance_count()):
     t=c.get_instance_transform(i,world_space=True);p=t.translation
     if p.z<-1800000 and p.x*p.x+p.y*p.y<190000**2:
      rows.append({'mesh':m.get_name(),'transform':str(t),'bounds':str(m.get_bounding_box())})
      if len(rows)>=3:break
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/remnant_tree_audit.json').write_text(json.dumps(rows,indent=2))
