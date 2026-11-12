import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out=[]
for a in E.get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 c=a.static_mesh_component
 if not c.static_mesh or not c.get_editor_property('visible'):continue
 p,e=a.get_actor_bounds(False)
 if p.x+e.x<2550000 or p.x-e.x>2870000 or p.y+e.y<3480000 or p.y-e.y>3820000:continue
 if p.z+e.z<-2061000 or p.z-e.z>-2010000:continue
 out.append({'actor':a.get_name(),'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'center':[p.x/100,p.y/100,p.z/100],'extent':[e.x/100,e.y/100,e.z/100]})
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain54');O.mkdir(exist_ok=True);(O/'lake_actors.json').write_text(json.dumps(out,indent=2))
