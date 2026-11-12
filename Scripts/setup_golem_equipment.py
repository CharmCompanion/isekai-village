import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
report={'success':False,'roles':{},'parameter_names':{}}
try:
 imports=json.loads((root/'Saved/golem_equipped_import.json').read_text());assert imports['success'],imports
 roles=json.loads((root/'Saved/golem_setup_report.json').read_text())['blueprints']
 A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools()
 types={'Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Necromancer'}
 palettes={'Tank':(.32,.38,.50),'Mage':(.18,.36,.78),'Ranger':(.24,.38,.16),'Healer':(.88,.80,.60),'Necromancer':(.13,.035,.22),'Evil_Crimson':(.28,.035,.045),'Evil_Blight':(.20,.29,.045),'Evil_Void':(.045,.018,.09)}
 def mats_for(role,info):
  mats=[u.load_asset(path) for path in info['materials']]
  for i,parent in enumerate(mats):
   path=parent.get_path_name()
   if 'Golems/' in path or '/Weapons/' in path:continue
   names=[str(n) for n in M.get_vector_parameter_names(parent)]
   report['parameter_names'][path]=names
   tint=[n for n in names if not any(x in n.lower() for x in ['skin','hair','eye','emiss','outline','rim','specular','shadow','button','buckle','chain','metal','lacing'])]
   if not tint:continue
   name='MI_'+role+'_Wardrobe_'+str(i).zfill(2)
   mi=u.load_asset(base+'/Materials/Equipment/'+name) or T.create_asset(name,base+'/Materials/Equipment',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
   M.set_material_instance_parent(mi,parent)
   for j,n in enumerate(tint):
    color=palettes[role]
    if j%2:
     color={'Tank':(.16,.10,.055),'Mage':(.12,.28,.56),'Ranger':(.20,.12,.055),'Healer':(.70,.45,.10),'Necromancer':(.20,.045,.31),'Evil_Crimson':(.12,.015,.02),'Evil_Blight':(.12,.17,.035),'Evil_Void':(.08,.035,.16)}[role]
    M.set_material_instance_vector_parameter_value(mi,n,u.LinearColor(*color,1))
   A.save_loaded_asset(mi,only_if_is_dirty=False);mats[i]=mi
  mats[info['gem_slot']]=u.load_asset(base+'/Materials/MI_SoulGem_'+role)
  return mats
 cache={}
 def configure(comp,role,live=False):
  info=imports['roles'][types.get(role,role)];mesh=u.load_asset(info['mesh']);anim=u.load_asset(info['animation'])
  comp.set_skeletal_mesh_asset(mesh);comp.set_editor_property('override_materials',cache[role])
  comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE)
  data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);data.set_editor_property('saved_position',0)
  comp.set_editor_property('animation_data',data)
  if live:
   comp.play_animation(anim,True);comp.set_position(0,False)
   comp.set_update_animation_in_editor(True)
  return info
 for role,path in roles.items():
  info=imports['roles'][types.get(role,role)];cache[role]=mats_for(role,info)
  bp=u.load_asset(path);u.BlueprintEditorLibrary.compile_blueprint(bp)
  cdo=u.get_default_object(bp.generated_class());comp=cdo.get_editor_property('skeletal_mesh_component')
  configure(comp,role)
  A.save_loaded_asset(bp,only_if_is_dirty=False)
  report['roles'][role]={'mesh':info['mesh'],'animation':info['animation'],'gem_slot':info['gem_slot'],'materials':[m.get_path_name() for m in cache[role]]}
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem)
 for level in [base+'/Maps/Map_GolemSoulGems','/Game/IsekaiVillage/Maps/Map_Village']:
  world=u.EditorLoadingAndSavingUtils.load_map(level)
  for a in actor_sys.get_all_level_actors():
   label=a.get_actor_label()
   if not isinstance(a,u.SkeletalMeshActor):continue
   if label.startswith('Golem '):role=label.replace('Golem ','')
   elif label=='Elrhun Soul Golem - Tank':role='Tank'
   else:continue
   info=configure(a.get_editor_property('skeletal_mesh_component'),role,True)
   mesh=u.load_asset(info['mesh']);bounds=mesh.get_bounds();minimum=bounds.origin.z-bounds.box_extent.z
   loc=a.get_actor_location()
   floor=(220 if loc.y>0 else -1) if level.endswith('Map_GolemSoulGems') else 0
   loc.z=floor-minimum;a.set_actor_location(loc,False,False)
   a.set_actor_rotation(u.Rotator(pitch=0,yaw=180,roll=0),False)
  u.EditorLoadingAndSavingUtils.save_map(world,level)
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_equipment_setup.json').write_text(json.dumps(report,indent=2))
