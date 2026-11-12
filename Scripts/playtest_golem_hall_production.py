"""Real sky-map worker routes, production, T collection and fresh-session save review."""
from pathlib import Path
import json,time,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');path=r/'Saved/golem_hall_playtest.json'
reload_pass=globals().get('reload_pass',False);previous=json.loads(path.read_text()) if reload_pass else {}
slot=previous['slot'] if reload_pass else 'VerifyHallWorkers_'+uuid.uuid4().hex
report={'success':False,'reload_pass':reload_pass,'slot':slot,'checks':[]};stage='start';started=time.monotonic();stamp=started;handle=None;release=None;state={};items=['Stone','Fish','Wood','Wheat','Bread','ToolParts']
u.EditorPythonScripting.set_keep_python_script_alive(True)
def check(name,yes):
 assert yes,name
 report['checks'].append(name)
def write():path.write_text(json.dumps(report,indent=2))
def finish(error=None):
 global stage,stamp
 report['success']=not bool(error)
 if error:report['error']=error
 write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
def pulse(w,key):
 global release
 u.SystemLibrary.execute_console_command(w,'Input.+key '+key);release=key
def counts(v):return {str(k):n for k,n in v.hall_supplies.items()}
def tick(dt):
 global stage,stamp,release
 try:
  now=time.monotonic()
  if stage=='ending':
   if now-stamp<3:return
   if reload_pass or report.get('error'):u.GameplayStatics.delete_game_in_slot(slot,0)
   u.unregister_slate_post_tick_callback(handle)
   if report.get('error'):
    deadline=time.monotonic()+600
    def poll(delta):
     job=r/'Saved/hall_live_job.json'
     if job.exists():
      data=json.loads(job.read_text());job.unlink();u.unregister_slate_post_tick_callback(poll_handle)
      if data.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       q=Path(data['script']);exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(poll_handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
    poll_handle=u.register_slate_post_tick_callback(poll)
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-started>540:return finish('Timeout at '+stage)
  if stage=='start':
   if now-stamp<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  w=worlds[0];v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None);p=u.GameplayStatics.get_player_character(w,0)
  if not v or not p:return
  if release:u.SystemLibrary.execute_console_command(w,'Input.-key '+release);release=None;return
  workers=list(u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen))
  if stage=='load':
   if now-stamp<8:return
   v.set_editor_property('window_seconds',10000.)
   if reload_pass:
    v.set_actor_tick_enabled(False);v.reload_village_state(p)
    workers=list(u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen))
    e=previous['expected'];check('Fresh session restores all five jobs',len(v.golem_residents)==5 and len(workers)==5)
    check('Stable worker identities survive fresh session',sorted(x.id.to_string() for x in v.golem_residents)==e['ids'])
    check('Collected inventory survives fresh session',all(p.gather.get_count(k)==n for k,n in e['inventory'].items()))
    check('Withdrawn store stays empty',all(n==0 for n in counts(v).values()))
    check('Supply site depletion survives fresh session',[x.stock for x in v.supply_sites]==e['stocks'])
    report['creation_pass']=previous;report['expected']=e;return finish()
   check('Three basic depots configured',len(v.supply_sites)==3)
   for item in ['Wood','Iron','Crystal']:p.gather.add_item(item,200)
   free=[x for x in v.plots if x.flexible_use and not x.built]
   farm=next(x for x in v.plots if str(x.id)=='ExistingFarm');free.sort(key=lambda x:(x.location-farm.location).length())
   for choice,plot in zip(['Guild','Townhouse','Cottage','Bakery','Smith','Warehouse'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True)
    check('Catalogue selects '+choice,v.select_building(choice));v.try_build_plot(plot.id,p)
    check('Placed '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
    if choice=='Guild':state['hall']=str(plot.id)
   v.toggle_building_catalog();workers=list(u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen))
   plot=next(x for x in v.plots if str(x.id)==state['hall']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(350,0,110),False,True)
   stage='staffing';stamp=now;return
  if stage=='staffing':
   report['population']={'records':[{'job':str(x.work_plot),'home':str(x.home_plot)} for x in v.golem_residents],'actor_jobs':[str(a.work_plot) for a in workers],'farm':[{'id':str(x.id),'built':x.built,'scenery':x.scenery,'kind':str(x.kind)} for x in v.plots if str(x.id)=='ExistingFarm']};write()
   if len(workers)!=5 and now-stamp<60:return
   check('Five beds staff five workplaces',len(v.golem_residents)==5 and len(workers)==5)
   state['initial']={a.golem_id.to_string():a.get_actor_location() for a in workers};state['cargo']=set();state['moved']=set()
   for a in workers:a.set_editor_property('walk_speed',650.)
   u.GameplayStatics.set_global_time_dilation(w,3.)
   stage='production';stamp=now;return
  if stage=='production':
   for a in workers:
    if (a.get_actor_location()-state['initial'][a.golem_id.to_string()]).length()>1000:state['moved'].add(a.golem_id.to_string())
   for rec in v.golem_residents:
    if rec.cargo_count>0:state['cargo'].add(str(rec.cargo))
   store=counts(v)
   if now-stamp>1:
    report['progress']={'seconds':now-started,'store':store,'cargo_seen':sorted(state['cargo']),'workers':[{'job':str(a.work_plot),'position':list(a.get_actor_location().to_tuple()),'goal':list(a.goal.to_tuple()),'blocked':a.route_blocked,'route_index':a.route_index,'route_size':len(a.route)} for a in workers]};write();stamp=now
   if not all(store.get(k,0)>0 for k in ['Stone','Fish','Wood','Bread','ToolParts']):return
   check('All workers physically traversed streets',len(state['moved'])==5)
   check('Stone fish and wood reached hall',all(store.get(k,0)>0 for k in ['Stone','Fish','Wood']))
   check('Bread and tool parts physically delivered',store.get('Bread',0)>=2 and store.get('ToolParts',0)>=1)
   check('Observed carried resource and production cargo',all(k in state['cargo'] for k in ['Stone','Fish','Wood','Wheat','Bread','ToolParts']))
   v.set_actor_tick_enabled(False)
   for a in workers:a.set_actor_tick_enabled(False)
   state['before']={k:p.gather.get_count(k) for k in items};state['store']=store
   plot=next(x for x in v.plots if str(x.id)==state['hall']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True)
   pulse(w,'T');stage='collect';return
  if stage=='collect':
   check('T transfers every delivered resource',all(p.gather.get_count(k)==state['before'][k]+state['store'].get(k,0) for k in items))
   check('T empties the hall store',all(n==0 for n in counts(v).values()))
   pulse(w,'F5');stage='save';return
  if stage=='save':
   check('F5 saves worker economy',v.last_village_save_succeeded)
   report['expected']={'ids':sorted(x.id.to_string() for x in v.golem_residents),'inventory':{k:p.gather.get_count(k) for k in items},'stocks':[x.stock for x in v.supply_sites]};return finish()
 except Exception:finish(traceback.format_exc())
try:
 if not reload_pass:
  script=r/'Scripts/setup_golem_hall_deliveries.py';exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
 else:u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
 e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
 # Freeze fresh-session jobs until inventory has been inspected.
 if reload_pass:v.set_actor_tick_enabled(False)
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 report['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
