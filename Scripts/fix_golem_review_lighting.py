import unreal as u,json,traceback,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
report={}
try:
 world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem)
 actors=actor_sys.get_all_level_actors()
 pos,rot=u.EditorLevelLibrary.get_level_viewport_camera_info()
 report['before_camera']={'position':[pos.x,pos.y,pos.z],'rotation':[rot.pitch,rot.yaw,rot.roll]}
 report['world']=world.get_path_name()
 report['actors']=[]
 for a in actors:
  item={'label':a.get_actor_label(),'class':a.get_class().get_name(),'hidden':a.is_hidden_ed(),'location':str(a.get_actor_location())}
  if isinstance(a,u.SkeletalMeshActor):
   c=a.get_editor_property('skeletal_mesh_component')
   item['mesh']=str(c.get_editor_property('skeletal_mesh_asset'))
   item['visible']=c.is_visible()
  report['actors'].append(item)
 # Repair only the golem review scene.
 assert world.get_name()=='Map_GolemSoulGems',world.get_name()
 def spawn_or_find(cls,label,loc,rot=u.Rotator()):
  a=next((a for a in actor_sys.get_all_level_actors() if a.get_actor_label()==label),None)
  if not a:a=actor_sys.spawn_actor_from_class(cls,u.Vector(*loc),rot)
  a.set_actor_label(label);a.set_actor_location(u.Vector(*loc),False,False);a.set_actor_rotation(rot,False)
  return a
 for a in actors:
  if isinstance(a,u.Light):
   comp=a.get_component_by_class(u.LightComponent)
   if comp:
    comp.set_mobility(u.ComponentMobility.MOVABLE)
    if isinstance(a,u.DirectionalLight):comp.set_intensity(3.5)
 sun=spawn_or_find(u.DirectionalLight,'Review soft sun',(0,0,600),u.Rotator(pitch=-45,yaw=-65,roll=0))
 sun.get_component_by_class(u.DirectionalLightComponent).set_intensity(3.5)
 sun.get_component_by_class(u.DirectionalLightComponent).set_mobility(u.ComponentMobility.MOVABLE)
 for name,loc,rotation,power in [
 ('Review key',(-400,-500,550),u.Rotator(pitch=-25,yaw=65,roll=0),18000),
 ('Review fill',(500,-300,420),u.Rotator(pitch=-20,yaw=125,roll=0),12000)]:
  a=spawn_or_find(u.RectLight,name,loc,rotation)
  c=a.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE);c.set_intensity(power)
  c.set_editor_property('attenuation_radius',2500)
  c.set_editor_property('source_width',500);c.set_editor_property('source_height',400)
 pp=spawn_or_find(u.PostProcessVolume,'Review fixed exposure',(0,0,0))
 pp.set_editor_property('unbound',True)
 settings=pp.get_editor_property('settings')
 settings.set_editor_property('override_auto_exposure_method',True)
 settings.set_editor_property('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL)
 settings.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True)
 settings.set_editor_property('auto_exposure_apply_physical_camera_exposure',False)
 settings.set_editor_property('override_auto_exposure_bias',True)
 settings.set_editor_property('auto_exposure_bias',0)
 pp.set_editor_property('settings',settings)
 # Bright, neutral studio background with a material unaffected by lighting.
 T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;A=u.EditorAssetLibrary
 path='/Game/Elrhun/Golems/Materials/M_ReviewBackdrop'
 mat=u.load_asset(path)
 if not mat:
  mat=T.create_asset('M_ReviewBackdrop','/Game/Elrhun/Golems/Materials',u.Material,u.MaterialFactoryNew())
  mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
  mat.set_editor_property('two_sided',True)
  color=M.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-200,0)
  color.set_editor_property('constant',u.LinearColor(.16,.20,.25,1))
  M.connect_material_property(color,'',u.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat)
 dome=spawn_or_find(u.StaticMeshActor,'Review backdrop sphere',(0,0,0))
 c=dome.get_editor_property('static_mesh_component');c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'));c.set_material(0,mat);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 c.set_editor_property('cast_shadow',False);dome.set_actor_scale3d(u.Vector(80,80,80))
 for command in ('viewmode lit','showflag.Lighting 1','showflag.Materials 1','showflag.StaticMeshes 1','showflag.SkeletalMeshes 1','r.EyeAdaptationQuality 0'):
  u.SystemLibrary.execute_console_command(world,command)
 u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
 u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
 report['success']=True
except Exception:report['success']=False;report['error']=traceback.format_exc()
(root/'Saved/golem_lighting_report.json').write_text(json.dumps(report,indent=2))
# Keep a small editor task queue available for inspection without restarting Unreal.
def poll(delta):
 global last_job
 p=root/'Saved/golem_lighting_job.json'
 if not p.exists():return
 job=json.loads(p.read_text())
 if job['id']==last_job:return
 last_job=job['id']
 try:
  script=root/'Scripts'/job['script']
  exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
 except Exception:(root/'Saved/golem_lighting_job_error.txt').write_text(traceback.format_exc())
last_job=None
lighting_handle=u.register_slate_post_tick_callback(poll)
