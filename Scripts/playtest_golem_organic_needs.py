"""Autonomous practice, personal unlocks, recharge, and fresh-session persistence."""
from pathlib import Path
import json,time,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');path=r/'Saved/golem_organic_playtest.json'
reload_pass=globals().get('reload_pass',False);previous=json.loads(path.read_text()) if reload_pass else {}
slot=previous['slot'] if reload_pass else 'VerifyOrganic_'+uuid.uuid4().hex
report={'success':False,'reload_pass':reload_pass,'slot':slot,'checks':[]};stage='start';stamp=time.monotonic();started=stamp;handle=None;state={}
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
def mutate(v,p,mode):
 for row in v.golem_residents:
  if str(row.adventurer_id)=='None':continue
  if mode=='initial':
   student=str(row.adventurer_id)==state['student']
   check('Set initial needs '+str(row.adventurer_id),v.set_golem_needs(row.id,0. if student else 95.,100. if student else 0.,0.,'Guard' if student else 'Magic'))
  elif str(row.adventurer_id)==state['student']:
   check('Set exhaustion stimulus',v.set_golem_needs(row.id,95.,row.drives.curiosity,row.drives.loneliness,row.drives.interest))
def tick(dt):
 global stage,stamp
 try:
  now=time.monotonic()
  if stage=='ending':
   if now-stamp<3:return
   if reload_pass or report.get('error'):u.GameplayStatics.delete_game_in_slot(slot,0)
   u.unregister_slate_post_tick_callback(handle)
   if report.get('error'):
    deadline=time.monotonic()+600
    def poll(delta):
     job=r/'Saved/organic_live_job.json'
     if job.exists():
      data=json.loads(job.read_text());job.unlink();u.unregister_slate_post_tick_callback(ph)
      if data.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       q=Path(data['script']);exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(ph);u.EditorPythonScripting.set_keep_python_script_alive(False)
    ph=u.register_slate_post_tick_callback(poll)
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-started>420:return finish('Timeout at '+stage)
  if stage=='start':
   if now-stamp<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  w=worlds[0];v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None);p=u.GameplayStatics.get_player_character(w,0)
  if not v or not p:return
  if stage=='load':
   if now-stamp<8:return
   v.set_editor_property('window_seconds',10000.)
   if reload_pass:
    v.set_actor_tick_enabled(False);v.reload_village_state(p);e=previous['expected'];rec=next(x for x in v.golem_residents if str(x.adventurer_id)==e['student'])
    check('Fresh session keeps four housed individuals',len(v.golem_residents)==4)
    check('Fresh session preserves adventurer identity',rec.id.to_string()==e['id'])
    check('Fresh session preserves practice',abs(rec.drives.practice.get('Guard',0)-e['practice'])<.01)
    check('Fresh session preserves learned skill','GuardStance' in [str(x) for x in rec.drives.skills])
    check('Fresh session preserves learned passive','EnduringCore' in [str(x) for x in rec.drives.passives])
    check('Fresh session preserves personality',abs(rec.drives.diligence-e['diligence'])<.001)
    a=next(x for x in p.party_reserve.reserve if str(x.adventurer_id)==e['student']);check('Roster and village agree on personal learning',abs(a.drives.practice.get('Guard',0)-e['practice'])<.01)
    report['creation_pass']=previous;report['expected']=e;return finish()
   check('Organic choices enabled in saved map',v.use_organic_golem_needs)
   for item in ['Wood','Iron']:p.gather.add_item(item,100)
   free=[x for x in v.plots if x.flexible_use and not x.built]
   # Nearby central frontages keep the test focused on decisions and arrival.
   free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
   for choice,plot in zip(['Guild','Townhouse','Cottage','Training'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);check('Selected '+choice,v.select_building(choice));v.try_build_plot(plot.id,p);check('Built '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
   v.toggle_building_catalog();p.set_actor_location(u.Vector(0,0,3000),False,True)
   check('Add isolated test adventurer',p.party_reserve.hire_adventurer(u.Text('Practice student')));check('Add isolated test peer',p.party_reserve.hire_adventurer(u.Text('Recharge peer')))
   state['student']=str(p.party_reserve.reserve[0].adventurer_id);state['peer']=str(p.party_reserve.reserve[1].adventurer_id);v.reconcile_golem_population();mutate(v,p,'initial')
   state['moved']=False;state['peer_recharged']=False;state['travel_checked']=False;state['worker_worked']=False;stage='learning';stamp=now
   u.GameplayStatics.set_global_time_dilation(w,5.)
   return
  records={str(x.adventurer_id):x for x in v.golem_residents if str(x.adventurer_id)!='None'}
  student=records[state['student']];peer=records[state['peer']];actors={a.golem_id.to_string():a for a in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen)};actor=actors.get(student.id.to_string())
  for a in actors.values():a.set_editor_property('walk_speed',650.)
  if stage=='learning':
   progress=student.drives.practice.get('Guard',0)
   if not state['travel_checked'] and actor and (actor.get_actor_location()-actor.goal).length()>500:
    check('Travelling gives no practice credit',progress==0);state['travel_checked']=True;state['first']=actor.get_actor_location()
   if actor and 'first' in state and (actor.get_actor_location()-state['first']).length()>1000:state['moved']=True
   if peer.drives.fatigue<35:state['peer_recharged']=True
   for x in v.golem_residents:
    if str(x.adventurer_id)=='None' and x.cargo_count>0:state['worker_worked']=True
   if now-stamp>1:
    report['progress']={'seconds':now-started,'practice':progress,'activity':str(student.drives.activity),'skills':[str(x) for x in student.drives.skills],'passives':[str(x) for x in student.drives.passives],'peer_fatigue':peer.drives.fatigue,'blocked':actor.route_blocked if actor else None,'position':list(actor.get_actor_location().to_tuple()) if actor else None};write();stamp=now
   if 'EnduringCore' not in [str(x) for x in student.drives.passives]:return
   check('Adventurer walked to chosen practice',state['moved']);check('Another adventurer independently recharged',state['peer_recharged']);check('Civilian work continues alongside personal activities',state['worker_worked']);check('Practice earned Guard Stance','GuardStance' in [str(x) for x in student.drives.skills]);check('Sustained practice earned Enduring Core',progress>=300);check('Peer has separate learning','GuardStance' not in [str(x) for x in peer.drives.skills]);report['want_line']=str(v.golem_want_line(student.id));state['practice']=progress;mutate(v,p,'exhaustion');stage='recharge';stamp=now;return
  if stage=='recharge':
   if student.drives.fatigue>=35:return
   check('Exhaustion led to recharge at home',str(student.drives.activity)=='Rest');check('Recharge did not generate practice',abs(student.drives.practice.get('Guard',0)-state['practice'])<.01)
   v.set_actor_tick_enabled(False)
   for a in actors.values():a.set_actor_tick_enabled(False)
   check('Save completed organic scenario',v.save_village_state(p));report['expected']={'student':state['student'],'id':student.id.to_string(),'practice':student.drives.practice.get('Guard',0),'diligence':student.drives.diligence};return finish()
 except Exception:finish(traceback.format_exc())
try:
 if not reload_pass:
  q=r/'Scripts/setup_golem_organic_needs.py';exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
 else:u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
 e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
 if reload_pass:v.set_actor_tick_enabled(False)
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 report['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
