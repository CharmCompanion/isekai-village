from pathlib import Path
import unreal as u,json,time,traceback
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');report={};slot='VerifyGolemVillage_Diagnostic';phase=0;start=time.monotonic();handle=None
u.EditorPythonScripting.set_keep_python_script_alive(True)
def hit(h):
 if not h:return None
 return {'raw':str(h),'values':[list(v.to_tuple()) if hasattr(v,'to_tuple') else v.get_path_name() if hasattr(v,'get_path_name') else str(v) for v in h.to_tuple()]}
def tick(dt):
 global phase,start
 try:
  now=time.monotonic()
  if phase==0:
   if now-start<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();phase=1;start=now;return
  if phase==2:
   if now-start<3:return
   u.unregister_slate_post_tick_callback(handle)
   def poll(delta):
    p=r/'Saved/golem_village_live_job.json'
    if p.exists():
     job=json.loads(p.read_text());p.unlink();u.unregister_slate_post_tick_callback(poll_handle)
     if job.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
     else:
      p=Path(job['script']);exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
   poll_handle=u.register_slate_post_tick_callback(poll);return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds or now-start<8:return
  w=worlds[0];workers=u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen)
  if not workers:
   v=u.GameplayStatics.get_actor_of_class(w,u.VillageRuntime);player=u.GameplayStatics.get_player_character(w,0);player.gather.add_item('Wood',40);v.select_building('InheritedHouse');v.try_build_plot('ES02_15',player);v.select_building('Shop');v.try_build_plot('ES02_26',player);start=now;return
  worker=workers[0];p=worker.get_actor_location();target=worker.route[worker.route_index];direction=target-p;direction.z=0;distance=direction.length();q=p+direction*(min(20,distance)/max(.001,distance));ground=u.SystemLibrary.line_trace_single(w,q+u.Vector(0,0,250),q-u.Vector(0,0,500),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[worker],u.DrawDebugTrace.NONE,True);report.update(position=list(p.to_tuple()),target=list(target.to_tuple()),goal=list(worker.goal.to_tuple()),route_index=worker.route_index,blocked=worker.route_blocked,frame_delta=w.get_delta_seconds() if hasattr(w,'get_delta_seconds') else dt,ground=hit(ground));report['sweeps']={}
  if ground:
   details=ground.to_tuple();q.z=details[4].z+99
   for lift in [0,5,10,20]:report['sweeps'][str(lift)]=hit(u.SystemLibrary.capsule_trace_single_by_profile(w,p+u.Vector(0,0,lift),q+u.Vector(0,0,lift),35,97,'Pawn',False,[worker],u.DrawDebugTrace.NONE,True))
  (r/'Saved/golem_village_movement_diagnostic.json').write_text(json.dumps(report,indent=2));u.EditorLevelLibrary.editor_end_play();phase=2;start=now
 except Exception:
  report['error']=traceback.format_exc();(r/'Saved/golem_village_movement_diagnostic.json').write_text(json.dumps(report,indent=2));u.EditorLevelLibrary.editor_end_play();phase=2;start=time.monotonic()
world=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky');v=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot);handle=u.register_slate_post_tick_callback(tick)
