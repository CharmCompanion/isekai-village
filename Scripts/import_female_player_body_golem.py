import unreal as u,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();report={'success':False}
try:
 world=u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemPlayerBody')
 source_info=json.loads((r/'Saved/golem_female_body_source.json').read_text());skeleton=u.load_asset(source_info['skeleton']);physics=u.load_asset(source_info['physics']);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 task=u.AssetImportTask();task.filename=str(r/'ArtSource/Golems/PlayerBody/SK_Golem_PlayerBodyFemale.fbx');task.destination_path=base+'/PlayerBody/Mesh';task.destination_name='SK_Golem_PlayerBodyFemale';task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory()
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
 for path in ['/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle','/Game/StylizedCharacters/Demo_Levels/Third_Person/RetargetedAnimations/BodyB/BodyB_Idle_Retargeted','/Game/MageSet01/Third_Person/RetargetedAnimations/BodyB/BodyB_Idle_Retargeted']:
  a=u.load_asset(path)
  if not a:continue
  sk=a.get_editor_property('skeleton');animations.append({'path':a.get_path_name(),'skeleton':sk.get_path_name()})
  if sk==skeleton and anim is None:anim=a
 assert anim,animations
 folder=base+'/PlayerBody/Blueprints';path=folder+'/BP_Golem_PlayerBodyFemale';bp=u.load_asset(path)
 if not bp:
  factory=u.BlueprintFactory();factory.set_editor_property('parent_class',u.load_asset(folder+'/BP_Golem_PlayerBodyBase').generated_class());bp=T.create_asset('BP_Golem_PlayerBodyFemale',folder,u.Blueprint,factory)
 u.BlueprintEditorLibrary.compile_blueprint(bp);cdo=u.get_default_object(bp.generated_class());comp=cdo.get_editor_property('skeletal_mesh_component');comp.set_skeletal_mesh_asset(mesh);comp.set_physics_asset(physics,True);comp.set_editor_property('override_materials',[]);comp.set_collision_profile_name('Pawn');comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data);cdo.set_editor_property('equipped_items',[]);A.save_loaded_asset(bp,only_if_is_dirty=False)
 actors=u.get_editor_subsystem(u.EditorActorSubsystem);allactors=list(actors.get_all_level_actors());male=next(a for a in allactors if a.get_actor_label()=='Golem - Original Player Body');female=next((a for a in allactors if a.get_actor_label()=='Golem - Original Female Player Body'),None)
 center=(male.get_actor_location()+female.get_actor_location())*.5 if female else male.get_actor_location();male.set_actor_location(center+u.Vector(-60,0,0),False,False)
 if not female:female=actors.spawn_actor_from_class(bp.generated_class(),center+u.Vector(60,0,0),male.get_actor_rotation());female.set_actor_label('Golem - Original Female Player Body')
 female.set_actor_location(center+u.Vector(60,0,0),False,False);c=female.get_editor_property('skeletal_mesh_component');c.set_skeletal_mesh_asset(mesh);c.set_physics_asset(physics,True);c.set_editor_property('override_materials',[]);c.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);c.set_editor_property('animation_data',data);c.play_animation(anim,True);c.set_position(0,False);c.set_update_animation_in_editor(True)
 malecomp=male.get_editor_property('skeletal_mesh_component');maleanim=malecomp.get_editor_property('animation_data').get_editor_property('anim_to_play');malecomp.play_animation(maleanim,True);malecomp.set_update_animation_in_editor(True)
 gem_a=next(i for i,s in enumerate(malecomp.get_editor_property('skeletal_mesh_asset').get_editor_property('materials')) if 'SoulGem' in str(s.material_slot_name));assert str(malecomp.get_editor_property('skeletal_mesh_asset').get_editor_property('materials')[gem_a].material_slot_name)==str(slots[gem_slot].material_slot_name);assert malecomp.get_material(gem_a)==c.get_material(gem_slot)
 actors.set_selected_level_actors([]);eye=center+u.Vector(150,520,140);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,center+u.Vector(0,0,100)));u.EditorLoadingAndSavingUtils.save_map(world,base+'/Maps/Map_GolemPlayerBody')
 report['male_base_blueprint']=folder+'/BP_Golem_PlayerBodyBase';report['review_map']=base+'/Maps/Map_GolemPlayerBody';report['shared_gem_material']=c.get_material(gem_slot).get_path_name();report['body_integrity']=json.loads((r/'ArtSource/Golems/PlayerBody/body_integrity_female.json').read_text())
 report.update({'success':True,'mesh':mesh.get_path_name(),'blueprint':bp.get_path_name(),'skeleton':skeleton.get_path_name(),'animation':anim.get_path_name(),'gem_slot':gem_slot})
except Exception:report['error']=traceback.format_exc()
finally:u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1')
(r/'Saved/golem_female_body_import.json').write_text(json.dumps(report,indent=2))
if not report['success']:raise RuntimeError(report['error'])
