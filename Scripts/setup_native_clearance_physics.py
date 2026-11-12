import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');shapes=json.loads((r/'ArtSource/Golems/NativeClipping/geometry_audit.json').read_text())['head_shapes'];A=u.EditorAssetLibrary;folder='/Game/Elrhun/Golems/PlayerBody';report={'success':False,'bodies':{}}
for body,shape in shapes.items():
 source='/Game/StylizedCharacters/'+body+'/Body/PA_'+body;dest=folder+'/Physics/PA_Golem_'+body;physics=u.load_asset(dest) or A.duplicate_asset(source,dest);mesh=u.load_asset(folder+'/Outfits/SK_Native_'+body+'_Mage');assert u.GolemClothTools.fit_native_head_collision(mesh,physics,u.Vector(*shape['center_reference_cm']),shape['radius_cm']+.35);A.save_loaded_asset(physics,only_if_is_dirty=False)
 for role in ['Tank','Mage','Ranger','Healer']:
  mesh=u.load_asset(folder+'/Outfits/SK_Native_'+body+'_'+role);mesh.set_editor_property('physics_asset',physics)
  for cloth in mesh.get_editor_property('mesh_clothing_assets'):cloth.set_editor_property('PhysicsAsset',physics)
  A.save_loaded_asset(mesh,only_if_is_dirty=False)
 report['bodies'][body]={'physics':physics.get_path_name(),'head_radius_cm':shape['radius_cm']+.35,'original_player_physics_unchanged':True}
scope={'__name__':'native_clearance_configuration'};p=r/'Scripts/native_weapon_config.py';exec(compile(p.read_text(),str(p),'exec'),scope);scope['apply_weapon_defaults']();report['success']=True;(r/'Saved/native_clearance_physics.json').write_text(json.dumps(report,indent=2))
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
if world and world.get_name()=='Map_GolemPlayerBody':
 for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
  label=actor.get_actor_label()
  if label in ['Golem - Original Player Body','Golem - Original Female Player Body']:scope['configure_weapon_actor'](actor,'BodyB' if 'Female' in label else 'BodyA','Mage',True)
 assert u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemPlayerBody')
