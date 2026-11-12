import unreal as u,json,time,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs');base='/Game/Elrhun/Golems';u.EditorPythonScripting.set_keep_python_script_alive(True)
A=u.EditorAssetLibrary;actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.LevelEditorSubsystem);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
report={'success':False}
try:
 mesh=u.load_asset(base+'/PlayerBody/Mesh/SK_Golem_PlayerBody');bp=u.load_asset(base+'/PlayerBody/Blueprints/BP_Golem_PlayerBodyBase');assert mesh and bp;native=u.load_asset('/Game/StylizedCharacters/BodyA/Body/SK_BodyA');assert mesh.get_editor_property('skeleton')==native
 cdo=u.get_default_object(bp.generated_class());c=cdo.get_editor_property('skeletal_mesh_component');anim=c.get_editor_property('animation_data').get_editor_property('anim_to_play');assert anim and anim.get_editor_property('skeleton')==native
 loc=u.Vector(480,-180,5);rot=u.Rotator()
 for a in list(actors.get_all_level_actors()):
  if a.get_actor_label()=='Golem Tank':loc=a.get_actor_location();rot=a.get_actor_rotation()
  if isinstance(a,u.GolemEquipmentActor) or isinstance(a,u.TextRenderActor):actors.destroy_actor(a)
 actor=actors.spawn_actor_from_class(bp.generated_class(),loc,rot);actor.set_actor_label('Golem - Original Player Body');actor.set_actor_scale3d(u.Vector(1,1,1));c=actor.get_editor_property('skeletal_mesh_component');c.play_animation(anim,True);c.set_position(0,False);c.set_update_animation_in_editor(True);actors.set_selected_level_actors([])
 for cmd in ['r.ScreenPercentage 100','showflag.BillboardSprites 0','showflag.CompositeEditorPrimitives 0','showflag.Grid 0']:u.SystemLibrary.execute_console_command(world,cmd)
 eye=loc+u.Vector(150,400,140);u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,loc+u.Vector(0,0,100)));u.EditorLoadingAndSavingUtils.save_map(world,base+'/Maps/Map_GolemPlayerBody')
 report.update({'success':True,'mesh':mesh.get_path_name(),'blueprint':bp.get_path_name(),'map':base+'/Maps/Map_GolemPlayerBody','animation':anim.get_path_name(),'skeleton':native.get_path_name(),'integrity':json.loads((r/'ArtSource/Golems/PlayerBody/body_integrity.json').read_text())});(r/'Saved/golem_player_body_import.json').write_text(json.dumps(report,indent=2))
except Exception:
 report['error']=traceback.format_exc();(r/'Saved/golem_player_body_import.json').write_text(json.dumps(report,indent=2));raise
# Keep a small task queue for the review shots; no map switching or duplicate-world loads.
last_job=None
def poll(delta):
 global last_job
 p=r/'Saved/golem_player_body_job.json'
 if not p.exists():return
 job=json.loads(p.read_text())
 if last_job==job['id']:return
 last_job=job['id']
 try:
  script=r/'Scripts'/job['script'];exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
 except Exception:(r/'Saved/golem_player_body_review_error.txt').write_text(traceback.format_exc())
handle=u.register_slate_post_tick_callback(poll)
