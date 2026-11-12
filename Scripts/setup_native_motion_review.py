import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');motion=r/'ArtSource/Golems/NativeMotion';manifest=json.loads((motion/'manifest.json').read_text());A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();base='/Game/Elrhun/Golems';folder=base+'/PlayerBody';dest=base+'/Maps/Map_GolemMotionReview';source=base+'/Maps/Map_GolemPlayerBody';review={'success':False,'map':dest,'actors':{},'playlists':{}}
mapfile=r/'Content/Elrhun/Golems/Maps/Map_GolemMotionReview.umap'
if not mapfile.exists():assert u.EditorLevelLibrary.new_level(dest)
world=u.EditorLoadingAndSavingUtils.load_map(dest);assert world and world.get_name()=='Map_GolemMotionReview';E=u.get_editor_subsystem(u.EditorActorSubsystem)
for actor in E.get_all_level_actors():
 if isinstance(actor,(u.SkeletalMeshActor,u.StaticMeshActor,u.TextRenderActor,u.SceneCapture2D,u.Light,u.PostProcessVolume)):E.destroy_actor(actor)
floor=E.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,-140,-5),u.Rotator());floor.set_actor_label('Motion review floor');fc=floor.get_editor_property('static_mesh_component');fc.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));fc.set_material(0,u.load_asset(base+'/Materials/M_ReviewFloor'));floor.set_actor_scale3d(u.Vector(11,10,.1))
roles=['Tank','Mage','Ranger','Healer']
for body,row in [('BodyA',100),('BodyB',-260)]:
 for i,role in enumerate(roles):
  clips=[body+'_'+s for s in ['Idle','Walk_InPlace','Run_Fwd','Jump']]+[body+'_'+s for s in (['NinjaLeftJab','NinjaRightCross'] if role in ['Tank','Ranger'] else ['AS_CastSpell','AS_StaffStrike+CastSpell'])];anims=[u.load_asset(manifest['animations'][s]['path']) for s in clips];skeleton=anims[0].get_editor_property('skeleton');assert all(a.get_editor_property('skeleton')==skeleton for a in anims)
  preview_key=body+'_'+{'Tank':'Run_Fwd','Mage':'AS_CastSpell','Ranger':'NinjaRightCross','Healer':'AS_StaffStrike+CastSpell'}[role];composite=u.load_asset(manifest['animations'][preview_key]['path'])
  if role=='Tank':
   dest_anim=folder+'/Animations/Review/'+body+'_Run_InPlace';composite=u.load_asset(dest_anim) or A.duplicate_asset(composite.get_path_name(),dest_anim);composite.set_editor_property('force_root_lock',True);A.save_loaded_asset(composite,only_if_is_dirty=False)
  cls=A.load_blueprint_class(folder+'/Blueprints/Wardrobe/BP_Native_'+body+'_'+role);actor=E.spawn_actor_from_class(cls,u.Vector((i-1.5)*240,row,0),u.Rotator());actor.set_actor_label('Motion - '+body+' '+role);comp=actor.get_editor_property('skeletal_mesh_component');comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',composite);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data);comp.play_animation(composite,True);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);comp.recreate_clothing_actors()
  text=E.spawn_actor_from_class(u.TextRenderActor,u.Vector((i-1.5)*240-60,row,208),u.Rotator(0,90,0));tc=text.get_component_by_class(u.TextRenderComponent);tc.set_text(role+' / '+('Male' if body=='BodyA' else 'Female'));tc.set_world_size(16.)
  review['actors'][body+'_'+role]=actor.get_actor_label();review['playlists'][body+'_'+role]={'path':composite.get_path_name(),'duration':composite.get_play_length(),'preview_clip':preview_key,'validated_clips':[manifest['animations'][key]['path'] for key in clips]}
# A bright, even setup for judging garment motion.
for a in E.get_all_level_actors():
 if isinstance(a,u.RectLight):E.destroy_actor(a)
for label,pos,power in [('Motion key',u.Vector(-400,500,650),1500),('Motion fill',u.Vector(500,300,500),1000)]:
 a=E.spawn_actor_from_class(u.RectLight,pos,u.MathLibrary.find_look_at_rotation(pos,u.Vector(0,-80,100)));a.set_actor_label(label);c=a.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(power);c.set_editor_property('attenuation_radius',2500);c.set_editor_property('source_width',800);c.set_editor_property('source_height',500)
sun=E.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,600),u.Rotator(-40,-90,0));sun.get_component_by_class(u.DirectionalLightComponent).set_mobility(u.ComponentMobility.MOVABLE);sun.get_component_by_class(u.DirectionalLightComponent).set_intensity(1.5)
pp=E.spawn_actor_from_class(u.PostProcessVolume,u.Vector(),u.Rotator());pp.set_editor_property('unbound',True);settings=pp.get_editor_property('settings')
for key,value in {'override_auto_exposure_method':True,'auto_exposure_method':u.AutoExposureMethod.AEM_MANUAL,'override_auto_exposure_apply_physical_camera_exposure':True,'auto_exposure_apply_physical_camera_exposure':False,'override_auto_exposure_bias':True,'auto_exposure_bias':-.5}.items():settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings);world.get_world_settings().set_editor_property('default_game_mode',u.GameModeBase)
eye=u.Vector(180,1240,760);target=u.Vector(0,-80,95);camera=E.spawn_actor_from_class(u.SceneCapture2D,eye,u.MathLibrary.find_look_at_rotation(eye,target));camera.set_actor_label('Motion test camera');cap=camera.get_component_by_class(u.SceneCaptureComponent2D);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('capture_on_movement',False);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,target));assert u.EditorLoadingAndSavingUtils.save_map(world,dest);assert mapfile.exists();review['success']=True;(r/'Saved/native_motion_review.json').write_text(json.dumps(review,indent=2))
