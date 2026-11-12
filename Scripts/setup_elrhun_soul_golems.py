import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary
report={}
def asset(name,path,cls,factory):
 return u.load_asset(path+'/'+name) or T.create_asset(name,path,cls,factory)
def scalar(material,name,value,x,y):
 e=M.create_material_expression(material,u.MaterialExpressionScalarParameter,x,y);e.set_editor_property('parameter_name',name);e.set_editor_property('default_value',value);return e
def vector(material,name,color,x,y):
 e=M.create_material_expression(material,u.MaterialExpressionVectorParameter,x,y);e.set_editor_property('parameter_name',name);e.set_editor_property('default_value',u.LinearColor(*color,1));return e
def parent_material(name,color,emissive=False):
 m=asset(name,base+'/Materials',u.Material,u.MaterialFactoryNew())
 M.delete_all_material_expressions(m)
 c=vector(m,'SoulColor' if emissive else 'BodyColor',color,-400,-100)
 M.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 rough=scalar(m,'Roughness',.22 if emissive else .63,-400,150)
 M.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 if emissive:
  strength=scalar(m,'GlowStrength',3,-400,50)
  mul=M.create_material_expression(m,u.MaterialExpressionMultiply,-150,0)
  M.connect_material_expressions(c,'',mul,'A');M.connect_material_expressions(strength,'',mul,'B')
  M.connect_material_property(mul,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 M.recompile_material(m);A.save_loaded_asset(m)
 return m
def instance(name,parent,color,glow=None):
 m=asset(name,base+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
 M.set_material_instance_parent(m,parent)
 M.set_material_instance_vector_parameter_value(m,'SoulColor' if glow is not None else 'BodyColor',u.LinearColor(*color,1))
 if glow is not None:M.set_material_instance_scalar_parameter_value(m,'GlowStrength',glow)
 A.save_loaded_asset(m);return m
try:
 incoming=json.loads((root/'Saved/golem_import_report.json').read_text());assert incoming['success'],incoming
 mesh=u.load_asset(incoming['mesh'])
 body=parent_material('M_ClayBody',(.62,.245,.105))
 joint=instance('MI_PolishedClay',body,(.46,.155,.060))
 M.set_material_instance_scalar_parameter_value(joint,'Roughness',.38);A.save_loaded_asset(joint)
 ink=instance('MI_DarkEyes',body,(.009,.006,.004))
 gem_parent=parent_material('M_SoulGem',(.01,.25,1),True)
 colors={
 'Tank':(1,.012,.008),'Mage':(.015,.15,1),'Ranger':(.015,.8,.075),
 'Healer':(1,.72,.015),'Necromancer':(.40,.015,.85),
 'Evil_Crimson':(.65,.002,.045),'Evil_Blight':(.37,.72,.008),'Evil_Void':(.075,.008,.25)}
 mats={name:instance('MI_SoulGem_'+name,gem_parent,c,3) for name,c in colors.items()}
 gem_slots=[]
 slots=list(mesh.get_editor_property('materials'))
 for i,slot in enumerate(slots):
  name=str(slot.material_slot_name).lower()
  if 'soul' in name or 'gem' in name:
   slot.set_editor_property('material_interface',mats['Tank']);gem_slots.append(i)
  elif 'obsidian' in name or 'bead' in name or 'dark glossy' in name:
   slot.set_editor_property('material_interface',ink)
  elif 'joint' in name or 'burnished' in name or 'polished' in name:
   slot.set_editor_property('material_interface',joint)
  else:slot.set_editor_property('material_interface',body)
  slots[i]=slot
 assert gem_slots,'Gem material slot missing'
 mesh.set_editor_property('materials',slots)
 A.save_loaded_asset(mesh)
 blueprints={}
 for role,mat in mats.items():
  factory=u.BlueprintFactory();factory.set_editor_property('parent_class',u.SkeletalMeshActor)
  bp=asset('BP_Golem_'+role,base+'/Blueprints',u.Blueprint,factory)
  u.BlueprintEditorLibrary.compile_blueprint(bp)
  cls=bp.generated_class();cdo=u.get_default_object(cls)
  component=cdo.get_editor_property('skeletal_mesh_component')
  component.set_skeletal_mesh_asset(mesh)
  faction='Corrupted' if role.startswith('Evil_') or role=='Necromancer' else 'Elrhun'
  cdo.set_editor_property('tags',[u.Name('ElrhunGolem'),u.Name('Role.'+role),u.Name('Faction.'+faction)])
  for slot in gem_slots:component.set_material(slot,mat)
  u.BlueprintEditorLibrary.compile_blueprint(bp);A.save_loaded_asset(bp)
  blueprints[role]=bp.get_path_name()
 # A self-contained review map, including friendly and corrupted variants.
 level=base+'/Maps/Map_GolemSoulGems'
 world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem)
 def spawn(cls,loc,label,rot=u.Rotator()):
  a=actor_sys.spawn_actor_from_class(cls,u.Vector(*loc),rot);a.set_actor_label(label);return a
 ground=spawn(u.StaticMeshActor,(0,0,-6),'Review floor')
 comp=ground.get_editor_property('static_mesh_component');comp.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
 ground.set_actor_scale3d(u.Vector(14,8,.1))
 for i,(role,path) in enumerate(blueprints.items()):
  row=i//4;column=i%4
  a=spawn(u.load_asset(path).generated_class(),(column*260-390,row*300-150,0),'Golem '+role)
  label=spawn(u.TextRenderActor,(column*260-390,row*300-230,200),role+' label',u.Rotator(0,0,0))
  text=label.get_editor_property('text_render');text.set_text(role.replace('_',' '));text.set_world_size(22);text.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
 light=spawn(u.DirectionalLight,(0,0,500),'Key light',u.Rotator(pitch=-50,yaw=-35,roll=0))
 sky=spawn(u.SkyLight,(0,0,350),'Sky light')
 spawn(u.PlayerStart,(-600,-700,100),'Review start')
 u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(-850,-1000,450),u.Rotator(pitch=-12,yaw=48,roll=0))
 u.EditorLoadingAndSavingUtils.save_map(world,level)
 village_placement=None
 village='/Game/IsekaiVillage/Maps/Map_Village'
 if A.does_asset_exist(village):
  village_world=u.EditorLoadingAndSavingUtils.load_map(village)
  starts=[a for a in actor_sys.get_all_level_actors() if isinstance(a,u.PlayerStart)]
  already=[a for a in actor_sys.get_all_level_actors() if a.get_actor_label()=='Elrhun Soul Golem - Tank']
  if starts and not already:
   location=starts[0].get_actor_location()+u.Vector(180,180,-90)
   a=actor_sys.spawn_actor_from_class(u.load_asset(blueprints['Tank']).generated_class(),location)
   a.set_actor_label('Elrhun Soul Golem - Tank')
   u.EditorLoadingAndSavingUtils.save_map(village_world,village)
   village_placement={'map':village,'actor':a.get_actor_label(),'location':[location.x,location.y,location.z]}
  elif already:village_placement={'map':village,'actor':already[0].get_actor_label()}
 report={'success':True,'village_placement':village_placement,'mesh':mesh.get_path_name(),'gem_slots':gem_slots,'blueprints':blueprints,'review_map':level,'colors':colors}
except Exception:
 report={'success':False,'error':traceback.format_exc()}
finally:
 (root/'Saved/golem_setup_report.json').write_text(json.dumps(report,indent=2));u.log('GOLEM_SETUP_REPORT '+json.dumps(report))



