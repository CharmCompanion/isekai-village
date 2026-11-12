import unreal as u,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/NativeWeapons';fitting=json.loads((out/'fitting.json').read_text());clips=json.loads((out/'manifest.json').read_text())['clips'];assert fitting['success'];A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;folder='/Game/Elrhun/Golems/PlayerBody';report=json.loads((r/'Saved/native_weapon_setup.json').read_text()) if globals().get('only_keys') else {'success':False,'meshes':{},'animations':{},'blueprints':{}}
def simple_material(name,color,roughness=.55):
 path=folder+'/Materials/Weapons/'+name;mat=u.load_asset(path)
 if mat:return mat
 mat=T.create_asset(name,folder+'/Materials/Weapons',u.Material,u.MaterialFactoryNew());mat.set_editor_property('two_sided',True);node=M.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-200,0);node.set_editor_property('constant',u.LinearColor(*color,1));M.connect_material_property(node,'',u.MaterialProperty.MP_BASE_COLOR);rough=M.create_material_expression(mat,u.MaterialExpressionConstant,-200,120);rough.set_editor_property('r',roughness);M.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
special={'ELR_ArrowSteel':simple_material('M_ArrowSteel',(.38,.42,.48),.32),'ELR_ArrowWood':u.load_asset('/Game/Elrhun/Golems/Materials/MI_GripLeather'),'ELR_ArrowFeather':simple_material('M_ArrowFeather',(.70,.68,.50))}
u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 0')
assets={name:spec for name,spec in fitting['assets'].items() if not globals().get('only_keys') or any(name in fitting['bodies'][key.split('_',1)[0]][key.split('_',1)[1]]['items'] for key in only_keys)}
if not globals().get('only_keys'):assets['SM_Native_NockedArrow']={'file':str(out/'SM_Native_NockedArrow.fbx'),'materials':['ELR_ArrowWood','ELR_ArrowSteel','ELR_ArrowFeather']}
for name,info in assets.items():
 task=u.AssetImportTask();task.filename=info['file'];task.destination_path=folder+'/Weapons';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory();opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=opt;T.import_asset_tasks([task]);mesh=u.load_asset(folder+'/Weapons/'+name);assert isinstance(mesh,u.StaticMesh),name
 for i,path in enumerate(info['materials']):
  mat=special.get(path) or u.load_asset(path);assert mat,path;mesh.set_material(i,mat)
 collision_editor=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
 if collision_editor:collision_editor.remove_collisions(mesh)
 else:
  body_setup=mesh.get_editor_property('body_setup');geometry=body_setup.get_editor_property('agg_geom')
  for field in ['sphere_elems','box_elems','sphyl_elems','convex_elems','tapered_capsule_elems']:geometry.set_editor_property(field,[])
  body_setup.set_editor_property('agg_geom',geometry)
 u.GolemClothTools.ensure_weapon_collision(mesh);A.save_loaded_asset(mesh,only_if_is_dirty=False);report['meshes'][name]=mesh.get_path_name()
u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1')
def transform(t):
 value=u.Transform();value.translation=u.Vector(*t['p']);value.rotation=u.Quat(*t['q']);value.scale3d=u.Vector(*t['s']);return value
def posed_copy(body,role,label,source,pose,freeze=False,curve=None):
 name='A_'+body+'_'+role+'_'+label;path=folder+'/Animations/Equipped/'+name;anim=u.load_asset(path) or A.duplicate_asset(source,path);assert anim;assert u.GolemClothTools.apply_held_bone_pose(anim,{n:transform(t) for n,t in pose.items()}),(body,role,label);anim.set_editor_property('force_root_lock',True)
 if curve:
  phases,values=curve;assert u.GolemClothTools.set_equipment_curve(anim,'ElrhunBowDraw',[float(p*anim.get_play_length()) for p in phases],[float(v) for v in values])
 assert u.GolemClothTools.normalize_equipment_root(anim,label!='Ready',role in ['Tank','Ranger'] and label in ['Ready','Action1','Action2'])
 A.save_loaded_asset(anim,only_if_is_dirty=False);return anim
for body,roles in fitting['bodies'].items():
 for role,info in roles.items():
  if globals().get('only_keys') and body+'_'+role not in only_keys:continue
  held={n:t for n,t in info['grip_local_pose'].items() if (n.endswith('_r') or role in ['Tank','Ranger'])};held.update(info.get('free_hand_local_pose',{}));source=clips[body+'_'+info['ready_source']]['path'];ready=posed_copy(body,role,'Ready',source,info['ready_local_pose'],True,([0,1],[1,1]) if role=='Ranger' else None);anims={'Ready':ready.get_path_name()}
  actions={'Tank':['Sword','Shield'],'Mage':['Staff','Staff'],'Ranger':['BowDraw','BowRelease'],'Healer':['Staff','Staff']}[role]
  for index,kind in enumerate(actions):
   draw_side=info.get('bow_draw_hand','hand_r')[-1];finger_pose={n:t for n,t in held.items() if not(role=='Ranger' and kind=='BowRelease' and n.endswith('_'+draw_side))};curve=([0,.15,.65,1],[0,.05,1,1]) if kind=='BowDraw' else ([0,.065,.08,.25,1],[1,1,0,0,0]) if kind=='BowRelease' else None;anim=posed_copy(body,role,'Action'+str(index+1),clips[body+'_'+kind]['path'],finger_pose,curve=curve);anims['Action'+str(index+1)]=anim.get_path_name()
  for motion,stem in [('Walk','Walk_InPlace'),('Run','Run_Fwd')]:
   source='/Game/StylizedCharacters/Demo_Levels/Third_Person/RetargetedAnimations/'+body+'/'+body+'_'+stem+'_Retargeted';anim=posed_copy(body,role,motion,source,held,curve=([0,1],[0,0]) if role=='Ranger' else None);anims[motion]=anim.get_path_name()
  report['animations'][body+'_'+role]=anims
def configure(actor,body,role,live=False):
 role_type={'Necromancer':'Healer','Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Healer'}.get(role,role);info=fitting['bodies'][body][role_type];comp=actor.get_editor_property('skeletal_mesh_component');anim=u.load_asset(report['animations'][body+'_'+role_type]['Ready']);assert anim.get_editor_property('skeleton')==comp.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton');actor.set_editor_property('animate_bow_string',False);equipment=[]
 for name in info['items']:
  spec=fitting['assets'][name];item=u.GolemEquipmentItem();item.set_editor_property('mesh',u.load_asset(report['meshes'][name]));item.set_editor_property('bone',spec['bone']);item.set_editor_property('adjustment',u.Transform());equipment.append(item)
 if role_type=='Ranger':
  bow=fitting['assets'][info['items'][0]];actor.set_editor_property('bow_equipment_index',0);actor.set_editor_property('bow_upper_tip',u.Vector(*bow['bow_upper_tip']));actor.set_editor_property('bow_lower_tip',u.Vector(*bow['bow_lower_tip']));actor.set_editor_property('bow_draw_hand',info.get('bow_draw_hand','hand_r'));actor.set_editor_property('bow_draw_hand_offset',u.Vector(*info['bow_draw_hand_offset']));actor.set_editor_property('bow_string_segment_mesh',u.load_asset('/Engine/BasicShapes/Cylinder'));actor.set_editor_property('bow_string_material',u.load_asset('/Game/Elrhun/Golems/Materials/MI_GripLeather'));actor.set_editor_property('nocked_arrow_mesh',u.load_asset(report['meshes']['SM_Native_NockedArrow']));actor.set_editor_property('bow_draw_override',-1.)
 actor.set_editor_property('equipped_items',equipment);actor.set_editor_property('animate_bow_string',role_type=='Ranger');comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data)
 if live:comp.play_animation(anim,True);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);actor.rebuild_equipment()
roles=['Tank','Mage','Ranger','Healer','Necromancer','Evil_Crimson','Evil_Blight','Evil_Void']
for body in ['BodyA','BodyB']:
 for role in roles:
  path=folder+'/Blueprints/Wardrobe/BP_Native_'+body+'_'+role;bp=u.load_asset(path);assert bp;u.BlueprintEditorLibrary.compile_blueprint(bp);configure(u.get_default_object(bp.generated_class()),body,role);A.save_loaded_asset(bp,only_if_is_dirty=False);report['blueprints'][body+'_'+role]=path
 basebp=u.load_asset(folder+'/Blueprints/'+('BP_Golem_PlayerBodyBase' if body=='BodyA' else 'BP_Golem_PlayerBodyFemale'));configure(u.get_default_object(basebp.generated_class()),body,'Mage');A.save_loaded_asset(basebp,only_if_is_dirty=False)
world=u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemPlayerBody');assert world;E=u.get_editor_subsystem(u.EditorActorSubsystem)
for actor in E.get_all_level_actors():
 label=actor.get_actor_label()
 if label in ['Golem - Original Player Body','Golem - Original Female Player Body']:configure(actor,'BodyB' if 'Female' in label else 'BodyA','Mage',True)
assert u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemPlayerBody')
# Keep the earlier clothing-only motion lab free of equipment.
world=u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemMotionReview');assert world
for actor in E.get_all_level_actors():
 if actor.get_actor_label().startswith('Motion - '):actor.set_editor_property('animate_bow_string',False);actor.set_editor_property('equipped_items',[]);actor.rebuild_equipment()
assert u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemMotionReview');report['success']=True;report['hand_geometry_changed']=False;report['arrow_is_visual_preview']=True;(r/'Saved/native_weapon_setup.json').write_text(json.dumps(report,indent=2))
# Save inherited equipment defaults from the base classes down to the role classes.
scope={'__name__':'weapon_configuration'};script=r/'Scripts/native_weapon_config.py';exec(compile(script.read_text(),str(script),'exec'),scope);scope['apply_weapon_defaults']()
if (r/'ArtSource/Golems/NativeClipping/safe_animation_tracks.json').exists():
 script=r/'Scripts/apply_native_clearance_poses.py';exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
