import unreal,random,math,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
rng=random.Random(260930)
clouds=sorted([a for a in E.get_all_level_actors() if a.get_actor_label()=='Painted drifting cloudbank'],key=lambda a:a.get_path_name())
for i,a in enumerate(clouds):
 active=i<24;a.static_mesh_component.set_visibility(active,True);a.set_actor_hidden_in_game(not active)
 if not active:continue
 bx,by=[(-7600,4500),(6500,7300),(2400,-5800)][i%3]
 x=bx+rng.gauss(0,2200);y=by+rng.gauss(0,1350)
 if math.hypot(x,y)<2200:x+=3500
 z=rng.uniform(-3000,-1250);size=rng.uniform(580,1600)
 a.set_actor_location(unreal.Vector(x*100,y*100,z*100),False,False);a.set_actor_scale3d(unreal.Vector(size,size*rng.uniform(.52,.90),1));a.set_actor_rotation(unreal.Rotator(pitch=rng.uniform(-12,12),yaw=rng.uniform(0,360),roll=rng.uniform(-9,9)),False)
 old=a.static_mesh_component.get_material(0);name=old.get_name().removesuffix('_Polish26')+'_Polish26';path=R+'/Materials/'+name
 mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(old.get_path_name(),path)
 M.set_material_instance_scalar_parameter_value(mat,'Opacity',.59);M.set_material_instance_scalar_parameter_value(mat,'AlphaPower',1.08);M.set_material_instance_vector_parameter_value(mat,'Tint',unreal.LinearColor(.73,.81,.88,1));A.save_loaded_asset(mat);a.static_mesh_component.set_material(0,mat)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/cloud_polish_v26.json').write_text(json.dumps({'cloud_banks_found':len(clouds),'visible':min(24,len(clouds)),'distribution':'three irregular drifting groups; central opening retained'}))
