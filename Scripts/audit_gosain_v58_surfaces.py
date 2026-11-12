import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain58');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in E.get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 c=a.static_mesh_component;m=c.static_mesh
 if not m:continue
 name=m.get_name();label=a.get_actor_label()
 if not any(s in (name+' '+label).lower() for s in ['continent','terrain','ocean','fog','shoulder','roadbed']):continue
 p=a.get_actor_location();s=a.get_actor_scale3d();rows.append({'label':label,'actor':a.get_name(),'mesh':m.get_path_name(),'visible':c.is_visible(),'hidden':a.get_editor_property('hidden'),'location':[p.x,p.y,p.z],'scale':[s.x,s.y,s.z],'material':[c.get_material(i).get_path_name() if c.get_material(i) else '' for i in range(c.get_num_materials())]})
(O/'surface_actor_audit.json').write_text(json.dumps(rows,indent=2))
fog=[]
for a in E.get_all_level_actors():
 if not isinstance(a,unreal.ExponentialHeightFog):continue
 c=a.get_component_by_class(unreal.ExponentialHeightFogComponent);p=a.get_actor_location();row={'actor':a.get_name(),'location':[p.x,p.y,p.z]}
 for key in ['fog_density','fog_height_falloff','fog_max_opacity','start_distance','volumetric_fog_enabled','volumetric_fog_distance','fog_cutoff_distance']:
  try:row[key]=c.get_editor_property(key)
  except Exception:pass
 fog.append(row)
(O/'fog_audit.json').write_text(json.dumps(fog,indent=2))
sky=[]
for a in E.get_all_level_actors():
 if not isinstance(a,unreal.SkyAtmosphere):continue
 c=a.get_component_by_class(unreal.SkyAtmosphereComponent);p=a.get_actor_location();row={'actor':a.get_name(),'location':[p.x,p.y,p.z]}
 for key in ['aerial_perspective_start_depth','aerial_perspective_view_distance_scale','height_fog_contribution','bottom_radius','atmosphere_height']:
  try:row[key]=c.get_editor_property(key)
  except Exception:pass
 sky.append(row)
(O/'sky_audit.json').write_text(json.dumps(sky,indent=2))
