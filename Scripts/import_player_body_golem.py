import unreal as u,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();report={'success':False}
try:
 skeleton=u.load_asset('/Game/StylizedCharacters/BodyA/Body/SK_BodyA');physics=u.load_asset('/Game/StylizedCharacters/BodyA/Body/PA_BodyA');world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 task=u.AssetImportTask();task.filename=str(r/'ArtSource/Golems/PlayerBody/SK_Golem_PlayerBody.fbx');task.destination_path=base+'/PlayerBody/Mesh';task.destination_name='SK_Golem_PlayerBody';task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory()
 opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=True;opt.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;opt.import_mesh=True;opt.import_animations=False;opt.import_materials=False;opt.import_textures=False;opt.create_physics_asset=False;opt.set_editor_property('skeleton',skeleton);opt.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;opt.skeletal_mesh_import_data.set_editor_property('bImportMorphTargets',True);task.options=opt
 T.import_asset_tasks([task]);mesh=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh))
 slots=list(mesh.get_editor_property('materials'));names=[];gem_slot=None
 for i,slot in enumerate(slots):
  name=str(slot.material_slot_name);names.append(name)
  if 'SoulGem' in name:mat=u.load_asset(base+'/Materials/MI_SoulGem_Mage');gem_slot=i
  elif 'Shadow' in name:mat=u.load_asset(base+'/Materials/MI_GripLeather')
  elif 'Dark' in name or 'glossy' in name:mat=u.load_asset(base+'/Materials/MI_DarkEyes')
  else:mat=u.load_asset(base+'/Materials/M_ClayBody')
  slot.set_editor_property('material_interface',mat);slots[i]=slot
 mesh.set_editor_property('materials',slots);mesh.set_editor_property('physics_asset',physics);A.save_loaded_asset(mesh,only_if_is_dirty=False);assert gem_slot is not None,names
 animations=[];anim=None
 for path in ['/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle','/Game/StylizedCharacters/Demo_Levels/Third_Person/RetargetedAnimations/BodyA/BodyA_Idle_Retargeted','/Game/MageSet01/Third_Person/RetargetedAnimations/BodyA/BodyA_Idle_Retargeted']:
  a=u.load_asset(path)
  if not a:continue
  sk=a.get_editor_property('skeleton');animations.append({'path':a.get_path_name(),'skeleton':sk.get_path_name()})
  if sk==skeleton and anim is None:anim=a
 assert anim,animations
 folder=base+'/PlayerBody/Blueprints';path=folder+'/BP_Golem_PlayerBodyBase';bp=u.load_asset(path)
 if not bp:
  factory=u.BlueprintFactory();factory.set_editor_property('parent_class',u.GolemEquipmentActor);bp=T.create_asset('BP_Golem_PlayerBodyBase',folder,u.Blueprint,factory)
 u.BlueprintEditorLibrary.compile_blueprint(bp);cdo=u.get_default_object(bp.generated_class());comp=cdo.get_editor_property('skeletal_mesh_component');comp.set_skeletal_mesh_asset(mesh);comp.set_physics_asset(physics,True);comp.set_editor_property('override_materials',[]);comp.set_collision_profile_name('Pawn');comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data);cdo.set_editor_property('equipped_items',[]);A.save_loaded_asset(bp,only_if_is_dirty=False)
 # New review copy preserves the earlier class models and their outfit work.
 review=base+'/Maps/Map_GolemPlayerBody'
 if not A.does_asset_exist(review):assert A.duplicate_asset(base+'/Maps/Map_GolemSoulGems',review)
 world=u.EditorLoadingAndSavingUtils.load_map(review);actors=u.get_editor_subsystem(u.EditorActorSubsystem);origin=None
 for a in list(actors.get_all_level_actors()):
  if a.get_actor_label()=='Golem Tank':origin=a.get_actor_transform()
  if isinstance(a,u.GolemEquipmentActor) or isinstance(a,u.TextRenderActor):actors.destroy_actor(a)
 origin=origin or u.Transform(location=u.Vector(0,0,5));actor=actors.spawn_actor_from_class(bp.generated_class(),origin.translation,origin.rotation.rotator());actor.set_actor_scale3d(u.Vector(1,1,1));actor.set_actor_label('Golem - Original Player Body');c=actor.get_editor_property('skeletal_mesh_component');c.play_animation(anim,True);c.set_position(0,False);c.set_update_animation_in_editor(True)
 loc=actor.get_actor_location();eye=loc+u.Vector(-100,-320,140);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,loc+u.Vector(0,0,102)))
 u.EditorLoadingAndSavingUtils.save_map(world,review);report.update({'success':True,'mesh':mesh.get_path_name(),'blueprint':bp.get_path_name(),'map':review,'skeleton':skeleton.get_path_name(),'animation':anim.get_path_name(),'materials':names,'gem_slot':gem_slot,'original_body_unchanged':json.loads((r/'ArtSource/Golems/PlayerBody/body_integrity.json').read_text())})
except Exception:report['error']=traceback.format_exc()
finally:u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1')
(r/'Saved/golem_player_body_import.json').write_text(json.dumps(report,indent=2))
