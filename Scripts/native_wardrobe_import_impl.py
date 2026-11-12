import unreal as u,json,traceback,hashlib,os
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';folder=base+'/PlayerBody';A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;S=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem);report={'success':False,'meshes':{},'blueprints':{},'materials':{},'errors':[]}
try:
 built=json.loads((r/'ArtSource/Golems/NativeWardrobe/Built/build_report.json').read_text());manifest=json.loads((r/'ArtSource/Golems/NativeWardrobe/manifest.json').read_text());assert built['success']
 exec(compile((r/'Scripts/native_wardrobe_materials.py').read_text(),'native_wardrobe_materials.py','exec'),globals())
 CLOTH_ROOTS={manifest['materials'][s['material']]['root'] for asset in manifest['assets'].values() for s in asset['materials'] if s['cape'] or s.get('coat',False)}
 world=u.EditorLoadingAndSavingUtils.load_map(base+'/Maps/Map_GolemPlayerBody');u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 source_data={};animations={};meshes={};role_materials={};roles=list(PALETTES);types={'Necromancer':'Mage','Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Mage'}
 for body in ['BodyA','BodyB']:
  source=u.load_asset('/Game/StylizedCharacters/'+body+'/Body/SKM_'+body);skeleton=source.get_editor_property('skeleton');physics=u.load_asset(folder+'/Physics/PA_Golem_'+body) or source.get_editor_property('physics_asset');source_data[body]=(skeleton,physics)
  basebp=u.load_asset(folder+'/Blueprints/'+('BP_Golem_PlayerBodyBase' if body=='BodyA' else 'BP_Golem_PlayerBodyFemale'));animations[body]=u.get_default_object(basebp.generated_class()).get_editor_property('skeletal_mesh_component').get_editor_property('animation_data').get_editor_property('anim_to_play')
  assert animations[body].get_editor_property('skeleton')==skeleton
 for key,info in built['outfits'].items():
  body=info['body'];archetype=info['role'];skeleton,physics=source_data[body];name='SK_Native_'+key
  task=u.AssetImportTask();task.filename=info['file'];task.destination_path=folder+'/Outfits';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory()
  opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=True;opt.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;opt.import_mesh=True;opt.import_animations=False;opt.import_materials=False;opt.import_textures=False;opt.create_physics_asset=False;opt.set_editor_property('skeleton',skeleton);opt.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;opt.skeletal_mesh_import_data.set_editor_property('bImportMorphTargets',True);task.options=opt;T.import_asset_tasks([task]);mesh=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh));mesh.set_editor_property('physics_asset',physics)
  slots=list(mesh.get_editor_property('materials'));names=[str(s.material_slot_name) for s in slots];center=info['glow_center_unreal'];gem=None;specs=info['materials']
  def material_for(name,role):
   if name in specs:
    spec=specs[name];native_paths=manifest['sets'][body][archetype];glow=spec['cape'] or any(('Top' in p or 'Coat' in p) and any(m['material']==spec['material'] and not m['cape'] for m in manifest['assets'][p]['materials']) for p in native_paths)
    return wardrobe_material(spec['material'],body,role,center,glow)
   if 'SoulGem' in name:return u.load_asset(base+'/Materials/MI_SoulGem_'+role)
   if 'Shadow' in name:return u.load_asset(base+'/Materials/MI_GripLeather')
   if 'glossy' in name.lower() or 'Dark' in name:return u.load_asset(base+'/Materials/MI_DarkEyes')
   return wardrobe_material(base+'/Materials/M_ClayBody',body,role,center,True)
  for i,slot in enumerate(slots):
   n=names[i];slot.set_editor_property('material_interface',material_for(n,archetype));slots[i]=slot
   if 'SoulGem' in n:gem=i
  assert gem is not None;mesh.set_editor_property('materials',slots);u.GolemClothTools.reset_cape_cloth(mesh)
  state=json.loads(u.GolemClothTools.inspect_clothing(mesh));capes=[]
  for section in state['sections']:
   n=names[section['material']]
   if n in specs and (specs[n]['cape'] or specs[n].get('coat',False)):
    assert u.GolemClothTools.create_cape_cloth(mesh,section['section'],physics,100 if specs[n].get('coat',False) else (145 if body=='BodyA' else 141),1 if specs[n].get('coat',False) else 8);capes.append(section['section'])
  if capes and not any(sp.get('coat',False) for sp in specs.values()):assert u.GolemClothTools.finalize_cape_anchors(mesh,1.5,8)
  A.save_loaded_asset(mesh,only_if_is_dirty=False);meshes[key]=mesh
  for role in roles:
   if types.get(role,role)!=archetype:continue
   role_materials[body+'_'+role]=[material_for(n,role) for n in names]
  report['meshes'][key]={'path':mesh.get_path_name(),'slots':names,'gem_slot':gem,'cape_sections':capes,'hands_unchanged':info['hands_unchanged'],'hidden_skin_triangles':info['hidden_body_triangles'],'physics':physics.get_path_name(),'glow_reference_position':center}
 weapon_scope=None
 if (r/'Saved/native_weapon_setup.json').exists() and json.loads((r/'Saved/native_weapon_setup.json').read_text()).get('success'):
  weapon_scope={'__name__':'wardrobe_weapon_configuration'};weapon_script=r/'Scripts/native_weapon_config.py';exec(compile(weapon_script.read_text(),str(weapon_script),'exec'),weapon_scope)
 def configure(actor,body,role,live=False):
  archetype=types.get(role,role);key=body+'_'+archetype;comp=actor.get_editor_property('skeletal_mesh_component');mesh=meshes[key];comp.set_skeletal_mesh_asset(mesh);comp.set_physics_asset(source_data[body][1],True);comp.set_editor_property('override_materials',role_materials[body+'_'+role]);comp.set_collision_profile_name('Pawn');comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',animations[body]);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data)
  if live:comp.play_animation(animations[body],True);comp.set_position(0,False);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);comp.recreate_clothing_actors()
  if weapon_scope:weapon_scope['configure_weapon_actor'](actor,body,role,live)
  return comp
 for body in ['BodyA','BodyB']:
  parent=u.load_asset(folder+'/Blueprints/'+('BP_Golem_PlayerBodyBase' if body=='BodyA' else 'BP_Golem_PlayerBodyFemale'))
  for role in roles:
   name='BP_Native_'+body+'_'+role;path=folder+'/Blueprints/Wardrobe/'+name;bp=u.load_asset(path)
   if not bp:
    f=u.BlueprintFactory();f.set_editor_property('parent_class',parent.generated_class());bp=T.create_asset(name,folder+'/Blueprints/Wardrobe',u.Blueprint,f)
   u.BlueprintEditorLibrary.compile_blueprint(bp);cdo=u.get_default_object(bp.generated_class());configure(cdo,body,role);A.save_loaded_asset(bp,only_if_is_dirty=False);report['blueprints'][body+'_'+role]=bp.get_path_name()
  configure(u.get_default_object(parent.generated_class()),body,'Mage');A.save_loaded_asset(parent,only_if_is_dirty=False)
 if weapon_scope:weapon_scope['apply_weapon_defaults']()
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem);placed=[];pair=[]
 for actor in actor_sys.get_all_level_actors():
  label=actor.get_actor_label()
  if label not in ['Golem - Original Player Body','Golem - Original Female Player Body']:continue
  body='BodyB' if 'Female' in label else 'BodyA';configure(actor,body,'Mage',True);actor.set_actor_rotation(u.Rotator(),False);pair.append(actor);placed.append(body)
 assert sorted(placed)==['BodyA','BodyB'];center=(pair[0].get_actor_location()+pair[1].get_actor_location())*.5;eye=center+u.Vector(100,500,140);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,center+u.Vector(0,0,95)));u.EditorLoadingAndSavingUtils.save_map(world,base+'/Maps/Map_GolemPlayerBody')
 exec(compile((r/'Scripts/native_wardrobe_review_lighting.py').read_text(),'native_wardrobe_review_lighting.py','exec'),globals())
 # Save a small diagnostic capture directly from the renderer; no foreground window is needed.
 try:
  capture=actor_sys.spawn_actor_from_class(u.SceneCapture2D,eye,u.MathLibrary.find_look_at_rotation(eye,center+u.Vector(0,0,95)));cap=capture.get_component_by_class(u.SceneCaptureComponent2D);rt=u.RenderingLibrary.create_render_target2d(world,1800,1200,u.TextureRenderTargetFormat.RTF_RGBA8);cap.set_editor_property('texture_target',rt);cap.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('fov_angle',38.);cap.capture_scene();u.RenderingLibrary.export_render_target(world,rt,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs','Elrhun_Native_Clothing_Unreal.png');actor_sys.destroy_actor(capture)
 except Exception:report['capture_error']=traceback.format_exc()
 for body,role in [(b,r) for b in ['BodyA','BodyB'] for r in roles]:
  path=report['blueprints'][body+'_'+role];cdo=u.get_default_object(u.load_asset(path).generated_class());c=cdo.get_editor_property('skeletal_mesh_component');assert c.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton')==source_data[body][0];assert c.get_editor_property('animation_data').get_editor_property('anim_to_play').get_editor_property('skeleton')==source_data[body][0]
 report['success']=True;report['review_map']=base+'/Maps/Map_GolemPlayerBody';report['gem_hidden_in_clothed_meshes']=True;report['glow']='Small emissive falloff painted in pre-skinned local space, following the fabric without runtime lights';report['materials']={'new_glow_parents':{k:v.get_path_name() for k,v in material_cache.items()},'new_clothing_sources':len(instance_cache)}
except Exception:report['error']=traceback.format_exc()
finally:
 u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1');(r/'Saved/native_wardrobe_import.json').write_text(json.dumps(report,indent=2))
if not report['success']:raise RuntimeError(report['error'])
