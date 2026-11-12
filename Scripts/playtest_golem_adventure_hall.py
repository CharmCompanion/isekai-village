"""H opening, actual widget button delegates, crafting, party switching, and cold reload."""
from pathlib import Path
import json,time,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');path=r/'Saved/golem_hall_creation_playtest.json';reload_pass=globals().get('reload_pass',False);previous=json.loads(path.read_text()) if reload_pass else {};slot=previous['slot'] if reload_pass else 'VerifyGolemHall_'+uuid.uuid4().hex
report={'success':False,'reload_pass':reload_pass,'slot':slot,'checks':[]};state={};stage='start';stamp=time.monotonic();started=stamp;handle=None;release=None
u.EditorPythonScripting.set_keep_python_script_alive(True)
def check(name,yes):
 assert yes,name
 report['checks'].append(name)
def control(widget,name):
 obj=u.find_object(widget,'HallTree.'+name) or u.find_object(widget,'RosterRowTree.'+name)
 assert obj,'Missing control '+name
 return obj

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
     job=r/'Saved/golem_hall_ui_job.json'
     if job.exists():
      data=json.loads(job.read_text());job.unlink();u.unregister_slate_post_tick_callback(ph)
      if data.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       q=Path(data['script']);exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(ph);u.EditorPythonScripting.set_keep_python_script_alive(False)
    ph=u.register_slate_post_tick_callback(poll)
   elif reload_pass:
    u.SystemLibrary.execute_console_command(None,'Automation RunTests IsekaiVillage.')
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-state.get('last_report',0)>2:report['stage']=stage;report['elapsed']=now-started;write();state['last_report']=now
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
    v.set_actor_tick_enabled(False);v.reload_village_state(p);e=previous['expected'];a=p.party_reserve.reserve
    check('Fresh session keeps all three crafted adventurers',len(a)==3);check('Identities survive', [x.golem_id.to_string() for x in a]==e['ids']);check('Class choices survive',[str(x.class_id) for x in a]==e['classes']);check('Body choices survive',[x.female_body for x in a]==e['female']);check('Active selection survives',[x.get_editor_property('bInActiveParty') for x in a]==e['active']);check('Stone charges survive',p.gather.get_count('Stone')==e['stone']);check('Wood charges survive',p.gather.get_count('Wood')==e['wood']);check('Personality survives',all(abs(x.drives.diligence-y)<.001 for x,y in zip(a,e['diligence'])));check('Golem roster mode survives setup',p.party_reserve.use_golem_roster)
    actors={x.golem_id.to_string():x for x in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen)}
    for x in a:
     actor=actors[x.golem_id.to_string()];check('Saved outfit restored '+str(x.class_id),actor.golem_mesh.get_editor_property('skeletal_mesh_asset')==v.find_adventurer_mesh(x.class_id,x.female_body))
    report['expected']=e;report['creation_pass']=previous;return finish()
   check('All eight existing outfits configured',len(v.adventurer_meshes)==8)
   p.gather.add_item('Wood',100);p.gather.add_item('Iron',20);p.gather.add_item('Stone',18)
   free=[x for x in v.plots if x.flexible_use and not x.built];free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
   for choice,plot in zip(['Guild','Townhouse','Cottage','Training'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);check('Select '+choice,v.select_building(choice));v.try_build_plot(plot.id,p);check('Build '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
    if choice=='Guild':state['hall']=str(plot.id)
   v.toggle_building_catalog();plot=next(x for x in v.plots if str(x.id)==state['hall']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);state['wood']=p.gather.get_count('Wood');pulse(w,'H');stage='open';stamp=now;return
  if stage=='open':
   widgets=u.WidgetLibrary.get_all_widgets_of_class(w,u.GolemHallWidget,False)
   if not widgets:
    if now-stamp<3:return
    raise AssertionError('H did not open adventure hall')
   hall=widgets[0];state['widget']=hall;check('H opens the real creation menu',hall.is_in_viewport());check('Menu shows resource and body controls',control(hall,'ClassChoice') is not None and control(hall,'BodyChoice') is not None)
   for role,female,name in [('Mage',True,'Lumi'),('Tank',False,'Niri'),('Healer',True,'Mae')]:
    control(hall,'ClassChoice').set_selected_option(role);control(hall,'BodyChoice').set_selected_option('Female body' if female else 'Male body');control(hall,'NameEntry').set_text(u.Text(name));control(hall,'CreateButton').on_clicked.broadcast()
    check('Creation button creates '+name,len(p.party_reserve.reserve)==['Lumi','Niri','Mae'].index(name)+1);a=p.party_reserve.reserve[-1];check('Selected class applied '+name,str(a.class_id)==role);check('Selected body applied '+name,a.has_chosen_body and a.female_body==female);check('Entered name applied '+name,str(a.name)==name);check('New golem must learn skills '+name,len(a.drives.skills)==0)
   check('Exact stone charged for three golems',p.gather.get_count('Stone')==0);check('Exact wood charged for three golems',p.gather.get_count('Wood')==state['wood']-12);check('Creation disables without another free bed or recipe',not control(hall,'CreateButton').get_is_enabled())
   roster=control(hall,'RosterBox');control(roster.get_child_at(0),'ActiveButton').on_clicked.broadcast();check('Bench button removes first member',not p.party_reserve.reserve[0].get_editor_property('bInActiveParty'));control(roster.get_child_at(1),'ActiveButton').on_clicked.broadcast();check('Make active selects the preferred member',p.party_reserve.reserve[1].get_editor_property('bInActiveParty'));check('Only one companion is active at current capacity',p.party_reserve.get_active_companion_count()==1)
   control(hall,'CloseButton').on_clicked.broadcast();check('Close button dismisses menu',not hall.is_in_viewport());pulse(w,'F5');stage='saved';return
  if stage=='saved':
   check('F5 saves created roster',v.last_village_save_succeeded);a=p.party_reserve.reserve;report['expected']={'ids':[x.golem_id.to_string() for x in a],'classes':[str(x.class_id) for x in a],'female':[x.female_body for x in a],'active':[x.get_editor_property('bInActiveParty') for x in a],'stone':p.gather.get_count('Stone'),'wood':p.gather.get_count('Wood'),'diligence':[x.drives.diligence for x in a]};return finish()
 except Exception:finish(traceback.format_exc())
try:
 if not reload_pass:
  q=r/'Scripts/setup_golem_adventure_hall.py';exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
 else:u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
 e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(x for x in e.get_all_level_actors() if isinstance(x,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
 if reload_pass:v.set_actor_tick_enabled(False)
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 report['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
