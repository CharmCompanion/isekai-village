import unreal,json,collections
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');rows={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 c=a.static_mesh_component;m=c.static_mesh
 if not m or not c.is_visible():continue
 loc=a.get_actor_location()
 if abs(loc.x)>150000 or abs(loc.y)>150000 or loc.z<-95000:continue
 if not any(k in m.get_name().lower() for k in ['rock','cliff','spire']):continue
 path=m.get_path_name();q=rows.setdefault(path,{'count':0,'labels':[]});q['count']+=1
 if len(q['labels'])<2:q['labels'].append(a.get_actor_label())
(B/'Saved/stylized_content_audit_v28.json').write_text(json.dumps(rows,indent=2))
