import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/ElRuhnSky01');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in E.get_all_level_actors():
 label=a.get_actor_label()
 if not (isinstance(a,unreal.Landscape) or any(t in label.lower() for t in ['matching rock foundation','rim rock collar','island levitation ring','island covenant','levitation stone','horizontal wind seal'])):continue
 origin,extent=a.get_actor_bounds(False);p=a.get_actor_location();s=a.get_actor_scale3d();row={'name':a.get_name(),'label':label,'origin_m':[v/100 for v in [origin.x,origin.y,origin.z]],'extent_m':[v/100 for v in [extent.x,extent.y,extent.z]],'location_m':[v/100 for v in [p.x,p.y,p.z]],'scale':[s.x,s.y,s.z]}
 if isinstance(a,unreal.StaticMeshActor):
  b=a.static_mesh_component.static_mesh.get_bounding_box();row['local_bounds_m']=[[b.min.x/100,b.min.y/100,b.min.z/100],[b.max.x/100,b.max.y/100,b.max.z/100]]
 rows.append(row)
(O/'center_audit.json').write_text(json.dumps(rows,indent=2))
