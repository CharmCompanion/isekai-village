import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain51';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert (O/'applied.json').exists();assert not (O/'grotto_applied.json').exists()
plan=json.loads((O/'grotto.json').read_text());meshes=[unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB0'+str(i)) for i in [2,3,4]];assert all(meshes)
backup=B/'Saved/WorldBackups'/('BeforeGosain51Grotto_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
spawned=[]
try:
 for i,q in enumerate(plan['rocks']):
  mesh=meshes[i%len(meshes)];box=mesh.get_bounding_box();lo=box.min;hi=box.max;dims=[hi.x-lo.x,hi.y-lo.y,hi.z-lo.z];scale=[q['size'][j]*100/dims[j] for j in range(3)]
  ang=math.radians(q['yaw']);cx=(lo.x+hi.x)*.5*scale[0];cy=(lo.y+hi.y)*.5*scale[1]
  loc=unreal.Vector(q['xy'][0]*100-cx*math.cos(ang)+cy*math.sin(ang),q['xy'][1]*100-cx*math.sin(ang)-cy*math.cos(ang),q['z']*100-lo.z*scale[2])
  a=E.spawn_actor_from_class(unreal.StaticMeshActor,loc,unreal.Rotator(pitch=0,yaw=q['yaw'],roll=0));spawned.append(a);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_label('Gosain | Lakeside grotto rock '+str(i));a.set_folder_path('Regional Civilizations/Gosain/Lake51');a.tags=['Gosain51_Grotto']
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for a in spawned:E.destroy_actor(a)
 raise
(O/'grotto_applied.json').write_text(json.dumps({'status':'saved','actors':len(spawned),'backup':str(backup),'limitation':'Scenic rock grotto only; no cave gameplay or spring inlet yet','visual_review':'pending'},indent=2))
