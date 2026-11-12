import unreal as u,json,time,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs')
u.EditorPythonScripting.set_keep_python_script_alive(True)
level='/Game/Elrhun/Golems/Maps/Map_GolemSoulGems'
u.EditorLoadingAndSavingUtils.load_map(level)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
report={'actors':[]}
for a in actors.get_all_level_actors():
 if not isinstance(a,u.GolemEquipmentActor):continue
 comp=a.get_editor_property('skeletal_mesh_component');anim=comp.get_editor_property('animation_data').get_editor_property('anim_to_play')
 count_before=len(a.get_components_by_class(u.StaticMeshComponent));a.rebuild_equipment()
 comp.play_animation(anim,True);comp.set_position(0,False);comp.set_update_animation_in_editor(True)
 if hasattr(comp,'set_update_cloth_in_editor'):comp.set_update_cloth_in_editor(True);comp.recreate_clothing_actors()
 report['actors'].append({'name':a.get_actor_label(),'weapons_after_fresh_load':count_before,'components':len(a.get_components_by_class(u.StaticMeshComponent)),'head_transform':str(comp.get_socket_transform('Head'))})
 report['cloth_api']=[v for v in dir(comp) if 'cloth' in v or 'collision' in v]
actors.set_selected_level_actors([])
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for command in ['r.ScreenPercentage 100','showflag.BillboardSprites 0','showflag.CompositeEditorPrimitives 0','showflag.Grid 0']:
 u.SystemLibrary.execute_console_command(world,command)
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
(root/'Saved/golem_corrected_preview.json').write_text(json.dumps(report,indent=2))
started=time.monotonic();last_job=None
def poll(delta):
 global last_job
 request=root/'Saved/golem_equipment_review_job.json'
 if not request.exists():return
 job=json.loads(request.read_text())
 if last_job==job['id']:return
 last_job=job['id']
 try:
  p=root/'Scripts'/job['script'];exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 except Exception:(root/'Saved/golem_equipment_review_error.txt').write_text(traceback.format_exc())
poll_handle=u.register_slate_post_tick_callback(poll)
