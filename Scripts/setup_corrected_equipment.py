import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
report={'success':False,'physics':None,'cloth':{},'blueprints':{},'levels':{}}
try:
 imports=json.loads((root/'Saved/golem_corrected_import.json').read_text());assert imports['success'],imports
 # Reuse the established class palettes, resolving the new mesh's current slots.
 source=(root/'Scripts/setup_golem_equipment.py').read_text()
 first=source.index(' def mats_for(');last=source.index(' cache={}',first)
 palettes={'Tank':(.32,.38,.50),'Mage':(.18,.36,.78),'Ranger':(.24,.38,.16),'Healer':(.88,.80,.60),'Necromancer':(.13,.035,.22),'Evil_Crimson':(.28,.035,.045),'Evil_Blight':(.20,.29,.045),'Evil_Void':(.045,.018,.09)}
 A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools()
 report['parameter_names']={}
 exec(compile('\n'.join(line[1:] for line in source[first:last].splitlines()),'palette','exec'))
 S=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
 naked=u.load_asset(base+'/Mesh/SK_ElrhunGolem')
 physics=u.load_asset(base+'/Physics/PHYS_GolemBody_Cloth')
 if not physics:
  generated=S.create_physics_asset(naked,False,0);assert generated,'Physics creation failed'
  physics=T.duplicate_asset('PHYS_GolemBody_Cloth',base+'/Physics',generated)
  assert physics,'Physics duplication failed'
 assert u.GolemClothTools.fit_body_collision(naked,physics),'Collision fitting failed'
 A.save_loaded_asset(physics,only_if_is_dirty=False);report['physics']=physics.get_path_name()
 for role,info in imports['roles'].items():
  mesh=u.load_asset(info['mesh']);mesh.set_editor_property('physics_asset',physics)
  u.GolemClothTools.reset_cape_cloth(mesh)
  state=json.loads(u.GolemClothTools.inspect_clothing(mesh))
  for section in state['sections']:
   name=info['slots'][section['material']]
   if name not in ['Wardrobe_001','Wardrobe_006']:continue
   parent=mesh.get_editor_property('materials')[section['material']].get_editor_property('material_interface')
   while isinstance(parent,u.MaterialInstance):parent=parent.get_editor_property('parent')
   M.set_material_usage(parent,u.MaterialUsage.MATUSAGE_CLOTHING);A.save_loaded_asset(parent,only_if_is_dirty=False)
   if not section['cloth']:
    ok=u.GolemClothTools.create_cape_cloth(mesh,section['section'],physics,126,12 if role in ['Mage','Necromancer'] else 8)
    assert ok,(role,'cloth bind',section)
  assert u.GolemClothTools.finalize_cape_anchors(mesh,2.2 if role=='Tank' else 1.8,8 if role=='Tank' else 12)
  A.save_loaded_asset(mesh,only_if_is_dirty=False)
  report['cloth'][role]=json.loads(u.GolemClothTools.inspect_clothing(mesh))
  for weapon in info['weapons']:
   part=u.load_asset(weapon['mesh'])
   assert u.GolemClothTools.ensure_weapon_collision(part)>0,weapon
   A.save_loaded_asset(part,only_if_is_dirty=False)
 types={'Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Necromancer'}
 paths=json.loads((root/'Saved/golem_setup_report.json').read_text())['blueprints']
 cache={role:mats_for(role,imports['roles'][types.get(role,role)]) for role in paths}
 def configure(actor,role,live=False):
  info=imports['roles'][types.get(role,role)];comp=actor.get_editor_property('skeletal_mesh_component')
  comp.set_skeletal_mesh_asset(u.load_asset(info['mesh']));comp.set_editor_property('override_materials',cache[role])
  comp.set_physics_asset(physics,True);comp.set_collision_profile_name('Pawn');comp.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
  comp.set_editor_property('enable_per_poly_collision',False)
  comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE)
  anim=u.load_asset(info['animation']);data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);data.set_editor_property('saved_position',0);comp.set_editor_property('animation_data',data)
  equipment=[]
  accessories=([imports['accessories']['EvilBrows']] if role.startswith('Evil_') and 'accessories' in imports else [])+(imports.get('accessories',{}).get('HealerUnderlay',[]) if role=='Healer' else [])
  for w in info['weapons']+accessories:
   item=u.GolemEquipmentItem();item.set_editor_property('mesh',u.load_asset(w['mesh']));item.set_editor_property('bone',w['bone']);item.set_editor_property('adjustment',u.Transform());equipment.append(item)
  actor.set_editor_property('equipped_items',equipment)
  if live:
   comp.play_animation(anim,True);comp.set_position(0,False);comp.set_update_animation_in_editor(True);actor.rebuild_equipment()
  return info
 for role,path in paths.items():
  bp=u.load_asset(path);u.BlueprintEditorLibrary.reparent_blueprint(bp,u.GolemEquipmentActor);u.BlueprintEditorLibrary.compile_blueprint(bp)
  cdo=u.get_default_object(bp.generated_class());configure(cdo,role);A.save_loaded_asset(bp,only_if_is_dirty=False)
  report['blueprints'][role]={'path':path,'weapons':len(cdo.get_editor_property('equipped_items'))}
 actors=u.get_editor_subsystem(u.EditorActorSubsystem)
 for level in [base+'/Maps/Map_GolemSoulGems','/Game/IsekaiVillage/Maps/Map_Village']:
  world=u.EditorLoadingAndSavingUtils.load_map(level);placed=[]
  for a in list(actors.get_all_level_actors()):
   label=a.get_actor_label()
   if label.startswith('Golem '):role=label[6:]
   elif label=='Elrhun Soul Golem - Tank':role='Tank'
   else:continue
   if role not in paths:continue
   if not isinstance(a,u.GolemEquipmentActor):
    transform=a.get_actor_transform();actors.destroy_actor(a)
    a=actors.spawn_actor_from_class(u.load_asset(paths[role]).generated_class(),transform.translation,transform.rotation.rotator());a.set_actor_scale3d(transform.scale3d);a.set_actor_label(label)
   configure(a,role,True);placed.append(label)
  u.EditorLoadingAndSavingUtils.save_map(world,level);report['levels'][level]=placed
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_corrected_setup.json').write_text(json.dumps(report,indent=2))
