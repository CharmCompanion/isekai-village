from pathlib import Path
import json,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');w=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky');e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime))
meshes={};report={'success':False,'looks':{},'normal_slot':str(v.construction_save_slot)}
for body,sex in [('BodyA','male'),('BodyB','female')]:
 idle=v.get_editor_property(sex+'_worker_idle');walk=v.get_editor_property(sex+'_worker_walk');assert idle and walk
 for role in ['Tank','Mage','Ranger','Healer']:
  key=body+'_'+role;m=u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+key);assert m
  assert m.get_editor_property('skeleton')==idle.get_editor_property('skeleton')==walk.get_editor_property('skeleton'),key
  meshes[key]=m;report['looks'][key]=m.get_path_name()
v.modify();v.set_editor_property('adventurer_meshes',meshes);v.set_editor_property('golem_stone_cost',6);v.set_editor_property('golem_wood_cost',4)
assert u.EditorLoadingAndSavingUtils.save_map(w,'/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky');report['success']=True;(r/'Saved/golem_hall_setup.json').write_text(json.dumps(report,indent=2))
