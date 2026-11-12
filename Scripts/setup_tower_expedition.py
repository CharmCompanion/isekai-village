"""Configure the first floor and its gate on the existing sky map. No player save is edited."""
from pathlib import Path
import json,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');map_path='/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky'
w=u.EditorLoadingAndSavingUtils.load_map(map_path);e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime));normal_slot=str(v.construction_save_slot)
a=u.EditorAssetLibrary;m=u.MaterialEditingLibrary;factory=u.AssetToolsHelpers.get_asset_tools();folder='/Game/Elrhun/Tower/Floor01/Materials'
def material(name,color,glow=False):
 path=folder+'/'+name
 if a.does_asset_exist(path):return u.load_asset(path)
 x=factory.create_asset(name,folder,u.Material,u.MaterialFactoryNew())
 n=m.create_material_expression(x,u.MaterialExpressionConstant3Vector,-400,0);n.set_editor_property('constant',u.LinearColor(*color,1));m.connect_material_property(n,'',u.MaterialProperty.MP_BASE_COLOR)
 if glow:m.connect_material_property(n,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 rough=m.create_material_expression(x,u.MaterialExpressionConstant,-400,200);rough.set_editor_property('r',.85);m.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 m.set_material_usage(x,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);m.recompile_material(x);a.save_loaded_asset(x);return x
stone=material('M_Rootbound_Stone',(.21,.27,.32));moss=material('M_Rootbound_Moss',(.13,.3,.2));gem=material('M_Rootbound_Soulglass',(.12,.55,1.3),True)
towers=[x for x in e.get_all_level_actors() if isinstance(x,u.TowerExpedition)];assert len(towers)<=1,'Duplicate expedition managers'
old=next(x for x in e.get_all_level_actors() if x.get_actor_label()=='El Ruhn | Tower of the Five Winds');p=old.get_actor_location();x,y=p.x,p.y-6500
ignore=[z for z in e.get_all_level_actors() if 'TowerExpeditionGate' in [str(t) for t in z.tags]]
hit=u.SystemLibrary.line_trace_single(w,u.Vector(x,y,p.z+3000),u.Vector(x,y,p.z-6000),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,u.DrawDebugTrace.NONE,True);assert hit and hit.to_tuple()[0],'Tower approach must have supported ground'
ground=hit.to_tuple()[5];assert hit.to_tuple()[7].z>.8,'Tower gate ground is too steep'
t=towers[0] if towers else e.spawn_actor_from_class(u.TowerExpedition,ground+u.Vector(0,0,103));t.modify();t.set_actor_location(ground+u.Vector(0,0,103),False,True);t.set_actor_label('Tower | Floor 1 expedition gate');t.set_folder_path('Elrhun/Tower Expedition');t.set_editor_property('stone_material',stone);t.set_editor_property('moss_material',moss);t.set_editor_property('crystal_material',gem)
for z in ignore:e.destroy_actor(z)
disc=e.spawn_actor_from_class(u.StaticMeshActor,ground+u.Vector(0,0,5));disc.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cylinder'));disc.static_mesh_component.set_material(0,gem);disc.set_actor_scale3d(u.Vector(3.2,3.2,.1));disc.set_actor_enable_collision(False);disc.set_actor_label('Tower | Expedition arrival rune');disc.set_folder_path('Elrhun/Tower Expedition');disc.tags=['TowerExpeditionGate']
circle=e.spawn_actor_from_class(u.ProceduralMagicCircle,ground+u.Vector(0,0,15));circle.set_actor_scale3d(u.Vector(2));circle.set_actor_label('Tower | Gate magic');circle.set_folder_path('Elrhun/Tower Expedition');circle.tags=['TowerExpeditionGate']
assert str(v.construction_save_slot)==normal_slot
assert u.EditorLoadingAndSavingUtils.save_map(w,map_path)
report={'success':True,'normal_slot':normal_slot,'gate':[t.get_actor_location().x,t.get_actor_location().y,t.get_actor_location().z],'floor_origin':[t.floor_origin.x,t.floor_origin.y,t.floor_origin.z],'modules':len(t.regions),'connections':len(t.connections),'recipe_bread':t.bread_cost,'camp_wood':t.camp_wood_cost,'camp_stone':t.camp_stone_cost,'map':map_path}
(r/'Saved/tower_expedition_setup.json').write_text(json.dumps(report,indent=2))
