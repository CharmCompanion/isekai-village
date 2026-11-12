"""Actual G/V/J/action input, swept character walking, party follow, resources, camp and cold reload."""
from pathlib import Path
import json,time,traceback,uuid,math,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');path=r/'Saved/tower_expedition_playtest.json';reload_pass=globals().get('reload_pass',False);previous=json.loads(path.read_text()) if reload_pass else {};baseline=previous.get('creation_pass',previous) if reload_pass else {};slot=baseline['slot'] if reload_pass else 'VerifyTower_'+uuid.uuid4().hex
report={'success':False,'reload_pass':reload_pass,'slot':slot,'checks':[]}
if reload_pass:report['creation_pass']=baseline
stage='start';stamp=time.monotonic();started=stamp;handle=None;release=None;state={}
u.EditorPythonScripting.set_keep_python_script_alive(True)
def write():path.write_text(json.dumps(report,indent=2))
def check(name,yes):
 assert yes,name
 report['checks'].append(name)
def pulse(w,key):
 global release
 u.SystemLibrary.execute_console_command(w,'Input.+key '+key);release=key
def finish(error=None):
 global stage,stamp
 report['success']=not bool(error)
 if error:report['error']=error
 write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
def walk(points,after):
 global stage,stamp
 state['path']=list(points);state['after']=after;stage='walk';stamp=time.monotonic()
def center(t,index):return t.floor_origin+t.regions[index].center+u.Vector(0,0,103)
def tick(dt):
 global stage,stamp,release
 try:
  now=time.monotonic()
  if stage=='ending':
   if now-stamp<3:return
   if (reload_pass and report['success']) or (not reload_pass and report.get('error')):u.GameplayStatics.delete_game_in_slot(slot,0)
   u.unregister_slate_post_tick_callback(handle)
   if report.get('error'):
    deadline=time.monotonic()+600
    def poll(delta):
     job=r/'Saved/tower_live_job.json'
     if job.exists():
      data=json.loads(job.read_text());job.unlink();u.unregister_slate_post_tick_callback(ph)
      if data.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       q=Path(data['script']);exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(ph);u.EditorPythonScripting.set_keep_python_script_alive(False)
    ph=u.register_slate_post_tick_callback(poll)
   elif reload_pass:u.SystemLibrary.execute_console_command(None,'Automation RunTests IsekaiVillage.')
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-state.get('last_report',0)>2:report['stage']=stage;report['elapsed']=now-started;write();state['last_report']=now
  if now-started>420:return finish('Timeout at '+stage)
  if stage=='start':
   if now-stamp<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  w=worlds[0];v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None);p=u.GameplayStatics.get_player_character(w,0);t=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.TowerExpedition)),None)
  if not v or not p or not t:return
  if release:u.SystemLibrary.execute_console_command(w,'Input.-key '+release);release=None;return
  if stage=='load':
   if now-stamp<8:return
   v.set_editor_property('window_seconds',10000.)
   if reload_pass:
    v.set_actor_tick_enabled(False);v.reload_village_state(p);expected=baseline['expected'];progress=v.tower_floor
    check('Cold reload starts safely in the village',not t.get_editor_property('bInside'));check('Floor seed survives restart',progress.seed==expected['seed']);check('Camp survives restart',progress.get_editor_property('bCampBuilt'));check('Visit counter survives restart',progress.visit==expected['visit']);check('Deposit depletion survives restart',{str(k):value for k,value in progress.harvest_days.items()}==expected['harvests']);check('Guardian clear survives restart',progress.guardian_cleared_visit==expected['visit'])
    a=p.party_reserve.reserve;check('Selected adventurer identity survives restart',len(a)==1 and a[0].golem_id.to_string()==expected['id']);check('Selected class and body survive restart',str(a[0].class_id)=='Mage' and a[0].female_body);check('Earned guard practice survives restart',abs(a[0].drives.practice.get('Guard',0)-expected['guard'])<.001)
    for key,count in expected['inventory'].items():check('Inventory survives restart '+key,p.gather.get_count(key)==count)
    actors=[a for a in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen) if a.golem_id.to_string()==expected['id']];check('Companion restores in village coordinates',len(actors)==1 and abs(actors[0].get_actor_location().x-t.floor_origin.x)>100000)
    p.set_actor_location(t.get_actor_location(),False,True);state['bread']=p.gather.get_count('Bread');pulse(w,'G');stage='reload_depart';stamp=now;return
   check('First floor has four modular regions',len(t.regions)==4);check('Regions have three reusable connections',len(t.connections)==3)
   p.gather.add_item('Wood',100);p.gather.add_item('Iron',20);p.gather.add_item('Stone',18);p.gather.add_item('Bread',8)
   free=[x for x in v.plots if x.flexible_use and not x.built];free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
   for choice,plot in zip(['Guild','Townhouse','Cottage'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);check('Select '+choice,v.select_building(choice));v.try_build_plot(plot.id,p);check('Build '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
    if choice=='Guild':state['hall']=str(plot.id)
   v.toggle_building_catalog();plot=next(x for x in v.plots if str(x.id)==state['hall']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);check('Craft a real expedition adventurer',v.create_golem_adventurer(p,'Mage',True,u.Text('Lumi Expedition')))
   state['id']=p.party_reserve.reserve[0].golem_id.to_string();state['bread']=p.gather.get_count('Bread');p.set_actor_location(t.get_actor_location(),False,True);state['return']=t.get_actor_location();pulse(w,'G');stage='depart';stamp=now;return
  if stage=='reload_depart':
   check('Saved camp supports a new expedition',t.get_editor_property('bInside'));check('New expedition arrives at the persistent camp',(p.get_actor_location()-t.camp_point()).length()<100);check('Repeat departure charges provisions once',p.gather.get_count('Bread')==state['bread']-t.bread_cost);check('Same-day crystal deposit stays depleted on revisit',not t.deposit_available('F1_Deposit2'));check('The run survives restart with its trip home spent',v.tower_floor.get_editor_property('bRunActive') and v.tower_floor.trips_home_used==1);pulse(w,'V');stage='reload_trip_refused';return
  if stage=='reload_trip_refused':
   check('Rank D allows only one trip home per run',t.get_editor_property('bInside') and 'No trips home left' in t.last_message);p.set_actor_location(t.entry_point(),False,True);pulse(w,'V');stage='reload_return';return
  if stage=='reload_return':
   check('V at the arrival gate ends the run',not t.get_editor_property('bInside') and not v.tower_floor.get_editor_property('bRunActive'));check('Ending the run loses the camp',not v.tower_floor.get_editor_property('bCampBuilt'));report['expected']=baseline['expected'];return finish()
  if stage=='depart':
   check('G at the actual gate starts an expedition',t.get_editor_property('bInside'));check('Departure charges exact provisions',p.gather.get_count('Bread')==state['bread']-t.bread_cost);check('The selected adventurer physically travels',len(t.companions)==1);state['actor']=next(x for x in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen) if x.golem_id.to_string()==state['id']);check('Companion follows expedition control',not state['actor'].is_actor_tick_enabled() and 'ElrhunTowerParty' in [str(x) for x in state['actor'].tags]);state['resource']=t.deposits[0];walk([center(t,0),center(t,1),t.floor_origin+state['resource'].offset+u.Vector(0,0,50)],'stone_ready');return
  if stage=='walk':
   if now-stamp>100:raise AssertionError('Physical walking timed out toward '+str(state['path'][0])+' at '+str(p.get_actor_location()))
   if not state['path']:stage=state['after'];stamp=now;return
   goal=state['path'][0];loc=p.get_actor_location();dx,dy=goal.x-loc.x,goal.y-loc.y;distance=math.hypot(dx,dy)
   check_z=abs(loc.z-t.floor_origin.z)<250
   if not check_z:raise AssertionError('Walking left supported floor at '+str(loc))
   if distance<65:state['path'].pop(0);return
   p.add_movement_input(u.Vector(dx/distance,dy/distance,0),1.0,False);return
  if stage=='stone_ready':
   check('Character walked the entry bridge to the garden',abs(p.get_actor_location().x-center(t,1).x)<1500);state['stone']=p.gather.get_count('Stone');pulse(w,'G');stage='stone_taken';return
  if stage=='stone_taken':
   check('G gathers exact seeded stone yield',p.gather.get_count('Stone')==state['stone']+state['resource'].get_editor_property('Yield'));check('The used deposit is depleted',not t.deposit_available(state['resource'].id));pulse(w,'G');stage='stone_duplicate';return
  if stage=='stone_duplicate':
   check('Repeated G cannot duplicate the deposit',p.gather.get_count('Stone')==state['stone']+state['resource'].get_editor_property('Yield'));walk([center(t,1),t.camp_point()],'camp_ready');return
  if stage=='camp_ready':
   state['wood']=p.gather.get_count('Wood');state['stone']=p.gather.get_count('Stone');pulse(w,'G');stage='camp_built';return
  if stage=='camp_built':
   check('G establishes a persistent camp',v.tower_floor.get_editor_property('bCampBuilt'));check('Camp charges exact wood',p.gather.get_count('Wood')==state['wood']-t.camp_wood_cost);check('Camp charges exact stone',p.gather.get_count('Stone')==state['stone']-t.camp_stone_cost);state['fatigue']=p.party_reserve.reserve[0].drives.fatigue;pulse(w,'G');stage='rested';return
  if stage=='rested':
   check('Rest is recorded for the current expedition',v.tower_floor.rested_visit==v.tower_floor.visit);check('The actual party recovers fatigue',p.party_reserve.reserve[0].drives.fatigue<state['fatigue']);pulse(w,'G');stage='rest_duplicate';return
  if stage=='rest_duplicate':
   check('Repeated rest is rejected',"rested this expedition" in t.last_message);state['crystal_node']=t.deposits[2];walk([center(t,1),center(t,2),t.floor_origin+state['crystal_node'].offset+u.Vector(0,0,50)],'locked_crystal');return
  if stage=='locked_crystal':
   state['crystal']=p.gather.get_count('Crystal');pulse(w,'G');stage='guard_check';return
  if stage=='guard_check':
   check('Guarded crystals reject collection before victory',p.gather.get_count('Crystal')==state['crystal'] and 'guardian protects' in t.last_message);walk([center(t,2),t.guardian_point()],'guardian_wait');return
  if stage=='guardian_wait':
   actor=state['actor'];distance=(actor.get_actor_location()-t.guardian_point()).length()
   if distance>1000:
    if now-stamp>90:raise AssertionError('Companion did not follow the route to the guardian: '+str(actor.get_actor_location()))
    return
   check('Companion walked across the floor to the guardian',distance<1000);state['guard']=p.party_reserve.reserve[0].drives.practice.get('Guard',0);pulse(w,'G');stage='battle';stamp=now;return
  if stage=='battle':
   battles=list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));b=battles[0] if battles else None
   if not b:
    if now-stamp<4:return
    raise AssertionError('G did not start the guardian: '+t.last_message)
   if str(b.phase)=='Result':
    check('Real command actions defeat the guardian',b.get_editor_property('bVictory'));check('Guardian is saved as cleared for this visit',v.tower_floor.guardian_cleared_visit==v.tower_floor.visit);check('Combat earns personal guard practice',p.party_reserve.reserve[0].drives.practice.get('Guard',0)>state['guard']);check('First expedition does not delete the adventurer',len(p.party_reserve.reserve)==1);pulse(w,'J');stage='battle_closed';return
   if str(b.phase)=='AwaitCommand':pulse(w,'One')
   if now-stamp>90:raise AssertionError('Guardian battle timed out: '+str(b.battle_line()))
   return
  if stage=='battle_closed':
   if list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring)):return
   walk([center(t,2),t.floor_origin+state['crystal_node'].offset+u.Vector(0,0,50)],'crystal_ready');return
  if stage=='crystal_ready':pulse(w,'G');stage='crystal_taken';return
  if stage=='crystal_taken':
   check('Victory permits exact crystal collection',p.gather.get_count('Crystal')==state['crystal']+state['crystal_node'].get_editor_property('Yield'));walk([center(t,2),center(t,1),t.camp_point()],'return_ready');return
  if stage=='return_ready':pulse(w,'V');stage='returned';return
  if stage=='returned':
   check('V at camp returns to the village',not t.get_editor_property('bInside'));check('Return reaches the original gate',(p.get_actor_location()-state['return']).length()<120);check('Companion resumes village behaviour',state['actor'].is_actor_tick_enabled() and 'ElrhunTowerParty' not in [str(x) for x in state['actor'].tags]);check('Companion returns to village coordinates',abs(state['actor'].get_actor_location().x-t.floor_origin.x)>100000);pulse(w,'F5');stage='saved';return
  if stage=='saved':
   check('F5 saves the combined village and floor progress',v.last_village_save_succeeded);a=p.party_reserve.reserve[0];progress=v.tower_floor;report['expected']={'id':a.golem_id.to_string(),'seed':progress.seed,'visit':progress.visit,'camp':progress.get_editor_property('bCampBuilt'),'harvests':{str(k):value for k,value in progress.harvest_days.items()},'guard':a.drives.practice.get('Guard',0),'inventory':{x:p.gather.get_count(x) for x in ['Stone','Wood','Bread','Crystal']}};return finish()
 except Exception:finish(traceback.format_exc())
try:
 if not reload_pass:
  q=r/'Scripts/setup_tower_expedition.py';exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
 else:u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
 e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(x for x in e.get_all_level_actors() if isinstance(x,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
 if reload_pass:v.set_actor_tick_enabled(False)
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 report['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
