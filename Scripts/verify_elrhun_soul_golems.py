import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
r=json.loads((root/'Saved/golem_setup_report.json').read_text());report={}
try:
 mesh=u.load_asset(r['mesh']);bounds=mesh.get_bounds()
 report['bounds']={'origin':[bounds.origin.x,bounds.origin.y,bounds.origin.z],'extent':[bounds.box_extent.x,bounds.box_extent.y,bounds.box_extent.z]}
 checks={}
 for role,path in r['blueprints'].items():
  bp=u.load_asset(path);cdo=u.get_default_object(bp.generated_class());comp=cdo.get_editor_property('skeletal_mesh_component')
  material=comp.get_material(r['gem_slots'][0])
  assert material.get_name()=='MI_SoulGem_'+role,(role,material.get_name())
  assert comp.get_editor_property('skeletal_mesh_asset')==mesh,role
  color=u.MaterialEditingLibrary.get_material_instance_vector_parameter_value(material,'SoulColor')
  checks[role]={'material':material.get_path_name(),'color':[color.r,color.g,color.b],'tags':[str(t) for t in cdo.tags]}
 report['roles']=checks
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem)
 world=u.EditorLoadingAndSavingUtils.load_map(r['village_placement']['map'])
 actor=next(a for a in actor_sys.get_all_level_actors() if a.get_actor_label()==r['village_placement']['actor'])
 # Match the floor level at the village start. The model's lowest foot point
 # must sit on the same plane as the floor, rather than the PlayerStart capsule.
 loc=actor.get_actor_location();loc.z=-(bounds.origin.z-bounds.box_extent.z)
 actor.set_actor_location(loc,False,False);u.EditorLoadingAndSavingUtils.save_map(world,r['village_placement']['map'])
 report['village_actor']={'class':actor.get_class().get_path_name(),'position':[loc.x,loc.y,loc.z]}
 report['review_map_saved']=u.EditorAssetLibrary.does_asset_exist(r['review_map'])
 report['success']=True
except Exception:report['success']=False;report['error']=traceback.format_exc()
(root/'Saved/golem_verify_report.json').write_text(json.dumps(report,indent=2));u.log('GOLEM_VERIFY '+json.dumps(report))
