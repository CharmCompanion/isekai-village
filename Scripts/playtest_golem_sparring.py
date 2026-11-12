"""Real command keys, movement, learned battle effects and cold-session persistence."""
from pathlib import Path
import json,time,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');path=r/'Saved/golem_sparring_playtest.json';reload_pass=globals().get('reload_pass',False);previous=json.loads(path.read_text()) if reload_pass else {}
slot=previous['slot'] if reload_pass else 'VerifySparring_'+uuid.uuid4().hex
report={'success':False,'reload_pass':reload_pass,'slot':slot,'checks':[],'pretrained_fixture':True};stage='start';stamp=time.monotonic();started=stamp;handle=None;release=None;state={}
u.EditorPythonScripting.set_keep_python_script_alive(True)
def check(name,yes):
 assert yes,name
 report['checks'].append(name)
def write():path.write_text(json.dumps(report,indent=2))
def pulse(w,key):
 global release
 u.SystemLibrary.execute_console_command(w,'Input.+key '+key);release=key
def finish(error=None):
 global stage,stamp
 report['success']=not bool(error)
 if error:report['error']=error
 write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
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
     job=r/'Saved/sparring_live_job.json'
     if job.exists():
      data=json.loads(job.read_text());job.unlink();u.unregister_slate_post_tick_callback(ph)
      if data.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       q=Path(data['script']);exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(ph);u.EditorPythonScripting.set_keep_python_script_alive(False)
    ph=u.register_slate_post_tick_callback(poll)
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-state.get('last_report',0)>2:
   report['stage']=stage;report['elapsed']=now-started;write();state['last_report']=now
  if now-started>240:return finish('Timeout at '+stage)
  if stage=='start':
   if now-stamp<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  w=worlds[0];v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None);p=u.GameplayStatics.get_player_character(w,0)
  if not v or not p:return
  if release:u.SystemLibrary.execute_console_command(w,'Input.-key '+release);release=None;return
  if stage=='load':
   if now-stamp<8:return
   v.set_editor_property('window_seconds',10000.)
   if reload_pass:
    v.set_actor_tick_enabled(False);v.reload_village_state(p);e=previous['expected'];a=p.party_reserve.reserve[0]
    check('Fresh session preserves one roster adventurer',len(p.party_reserve.reserve)==1);check('Fresh session preserves identity',a.golem_id.to_string()==e['id']);check('Combat-earned Guard Stance survives','GuardStance' in [str(x) for x in a.drives.skills]);check('Guard practice survives',abs(a.drives.practice.get('Guard',0)-e['guard'])<.01);check('Magic practice survives',abs(a.drives.practice.get('Magic',0)-e['magic'])<.01);check('Successful evade practice survives',abs(a.drives.practice.get('Scout',0)-e['scout'])<.01);check('No encounter restarts after reload',not u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));check('No saved combat locks remain',all('ElrhunSparring' not in [str(t) for t in x.tags] for x in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen)));report['creation_pass']=previous;report['expected']=e;return finish()
   check('Training slime is configured',v.sparring_slime_class is not None)
   for item in ['Wood','Iron']:p.gather.add_item(item,100)
   free=[x for x in v.plots if x.flexible_use and not x.built];free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
   for choice,plot in zip(['Guild','Townhouse','Training'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);check('Select '+choice,v.select_building(choice));v.try_build_plot(plot.id,p);check('Build '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
    if choice=='Training':state['yard']=str(plot.id)
   v.toggle_building_catalog();check('Create isolated fixture member',p.party_reserve.hire_adventurer(u.Text('Combat test student')));state['id']=str(p.party_reserve.reserve[0].adventurer_id);v.reconcile_golem_population()
   # Seed prior practice as test data; only the battle increments are live-earned.
   for domain,effort in [('Guard',119),('Magic',300),('Aid',300),('Scout',120)]:
    left=effort
    while left>0:p.party_reserve.record_adventurer_practice(state['id'],domain,min(5,left),True);left-=min(5,left)
   state['wood']=p.gather.get_count('Wood');state['coin']=p.gather.get_count('Coin');state['magic']=p.party_reserve.reserve[0].drives.practice.get('Magic',0);state['scout']=p.party_reserve.reserve[0].drives.practice.get('Scout',0)
   plot=next(x for x in v.plots if str(x.id)==state['yard']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True)
   stage='ready';stamp=now;return
  if stage=='ready':
   actors=list(u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen));rec=next(x for x in v.golem_residents if str(x.adventurer_id)==state['id']);a=next((x for x in actors if x.golem_id.to_string()==rec.id.to_string()),None)
   report['population']={'resident_id':rec.id.to_string(),'actors':[{'id':x.golem_id.to_string(),'job':str(x.work_plot)} for x in actors]}
   if not a:return
   a.set_editor_property('walk_speed',650.);state['first']=a.get_actor_location();u.GameplayStatics.set_global_time_dilation(w,3.);pulse(w,'J');stage='assembly';stamp=now;return
  battles=list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));b=battles[0] if battles else None
  if stage=='assembly':
   if not b:
    if now-stamp<2:return
    raise AssertionError('J did not start a sparring encounter')
   if str(b.phase)=='Result':raise AssertionError('Assembly failed: '+str(b.battle_line()))
   if str(b.phase)!='AwaitCommand':return
   check('J starts the turn-based encounter',len(b.members)==1);check('Participant walked to the yard',(b.members[0].actor.get_actor_location()-state['first']).length()>1000);check('Existing approved body is used',b.members[0].actor.golem_mesh.get_editor_property('skeletal_mesh_asset') in [v.male_worker_mesh,v.female_worker_mesh]);check('Enemy turn is held while selecting a command',abs(b.members[0].health-100)<.01)
   pc=u.GameplayStatics.get_player_controller(w,0);pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(p.get_actor_location()+u.Vector(0,0,140),b.enemy.get_actor_location()))
   if 'nullrhi' in u.SystemLibrary.get_command_line().lower():pulse(w,'Three');stage='locked';return
   state['capture_requested']=False;stage='capture';stamp=now;return
  if not b:return
  if stage=='capture':
   if now-stamp<2:return
   if not state['capture_requested']:
    screenshot=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Sparring_UI.png');report['screenshot']=str(screenshot)
    u.SystemLibrary.execute_console_command(w,'HighResShot 1600x1000 filename="'+str(screenshot).replace('\\','/')+'"');state['capture_requested']=True;stamp=now;return
   if now-stamp<3:return
   pulse(w,'Three');stage='locked';return
  if stage=='locked':
   check('Locked Guard Stance is rejected',str(b.phase)=='AwaitCommand' and 'not been learned' in b.last_error);check('Rejected command spends no TP',abs(b.members[0].tp-40)<.01);pulse(w,'Two');stage='defend';return
  if stage=='defend':
   if str(b.phase)!='AwaitCommand':return
   a=p.party_reserve.reserve[0];check('Defending reduces the actual slime hit',abs(b.members[0].health-91)<.05);check('A real block unlocks Guard Stance','GuardStance' in [str(x) for x in a.drives.skills]);pulse(w,'Three');stage='guard';return
  if stage=='guard':
   if str(b.phase)!='AwaitCommand':return
   check('Learned Guard Stance reduces damage more',abs(b.members[0].health-86.8)<.05);check('Focused Mind reduces guard TP cost',abs(b.members[0].tp-36.4)<.05);pulse(w,'Four');stage='bolt';return
  if stage=='bolt':
   if str(b.phase)!='AwaitCommand':return
   check('Arcane Bolt damages the visible slime',abs(b.enemy.health-60)<.05);check('Spell consumes the reduced TP cost',abs(b.members[0].tp-29.2)<.05);state['before_heal']=b.members[0].health;pulse(w,'Five');stage='heal';return
  if stage=='heal':
   if str(b.phase)!='AwaitCommand':return
   check('First Aid heals before the next slime hit',b.members[0].health>state['before_heal'] and abs(b.members[0].health-88)<.05);state['before_evade']=b.members[0].health;pulse(w,'Six');stage='evade';return
  if stage=='evade':
   if str(b.phase)!='AwaitCommand':return
   check('Evasive Step prevents an incoming hit',abs(b.members[0].health-state['before_evade'])<.05);check('Successful evasion earns practice',p.party_reserve.reserve[0].drives.practice.get('Scout',0)>state['scout']);pulse(w,'Four');stage='finish_one';return
  if stage=='finish_one':
   if str(b.phase)!='AwaitCommand':return
   pulse(w,'Four');stage='victory';return
  if stage=='victory':
   if str(b.phase)!='Result':return
   check('Slime defeat ends sparring',b.enemy is None);check('No permanent roster deaths',len(p.party_reserve.reserve)==1);check('No training loot is generated',p.gather.get_count('Wood')==state['wood'] and p.gather.get_count('Coin')==state['coin']);check('Village actor is released','ElrhunSparring' not in [str(t) for t in b.members[0].actor.tags]);check('Battle grants actual spell practice',p.party_reserve.reserve[0].drives.practice.get('Magic',0)>state['magic']);check('HUD explains actions and result','TRAINING SPARRING' in str(b.battle_line()) and 'Sparring won' in str(b.battle_line()))
   v.set_actor_tick_enabled(False)
   for a in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen):a.set_actor_tick_enabled(False)
   report['battle_log']=[str(x) for x in b.battle_log];pulse(w,'F5');stage='saved';return
  if stage=='saved':
   check('F5 saves combat growth',v.last_village_save_succeeded);a=p.party_reserve.reserve[0];report['expected']={'id':a.golem_id.to_string(),'guard':a.drives.practice.get('Guard',0),'magic':a.drives.practice.get('Magic',0),'scout':a.drives.practice.get('Scout',0)};return finish()
 except Exception:finish(traceback.format_exc())
try:
 if not reload_pass:
  q=r/'Scripts/setup_golem_sparring.py';exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
 else:u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
 e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
 if reload_pass:v.set_actor_tick_enabled(False)
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 report['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
