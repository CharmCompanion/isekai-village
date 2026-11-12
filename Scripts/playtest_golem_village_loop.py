"""Actual input, movement and two-process persistence review in an isolated save slot."""
from pathlib import Path
import json,time,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs');report_path=r/'Saved/golem_village_playtest.json';reload_pass=globals().get('reload_pass',False);previous=json.loads(report_path.read_text()) if reload_pass else {};slot=previous['save_slot'] if reload_pass else 'VerifyGolemVillage_'+uuid.uuid4().hex;result={'success':False,'reload_pass':reload_pass,'save_slot':slot,'checks':[]};handle=None;stage='start';stamp=0.;started=0.;input_queue=[];release=None;worker=None;first_position=None;state={}
u.EditorPythonScripting.set_keep_python_script_alive(True)
if reload_pass:result.update(expected=previous.get('expected'),creation_pass=previous.get('creation_pass',previous))
def write():report_path.write_text(json.dumps(result,indent=2))
def done(error=None):
 global stage,stamp
 if error:result['error']=error
 else:result['success']=True
 write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
def check(name,condition):
 assert condition,name
 result['checks'].append(name)
def key(world,value):
 global release
 u.SystemLibrary.execute_console_command(world,'Input.+key '+value);release=(value,time.monotonic())
def capture(world,label,eye,target):
 actor=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.SceneCapture2D) if a.get_actor_label()=='Golem village review capture');actor.set_actor_location_and_rotation(eye,u.MathLibrary.find_look_at_rotation(eye,target),False,False);comp=actor.get_component_by_class(u.SceneCaptureComponent2D);rt=u.RenderingLibrary.create_render_target2d(world,1800,1300,u.TextureRenderTargetFormat.RTF_RGBA8);comp.set_editor_property('texture_target',rt);comp.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);comp.set_editor_property('capture_every_frame',True);comp.set_editor_property('fov_angle',45.);comp.set_editor_property('always_persist_rendering_state',True);comp.capture_scene()
def current(world):return u.GameplayStatics.get_actor_of_class(world,u.VillageRuntime),u.GameplayStatics.get_player_character(world,0),u.GameplayStatics.get_player_controller(world,0)
def at_plot(v,p,pc,ident):
 plot=next(x for x in v.plots if str(x.id)==ident);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,100),False,True);pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(p.get_actor_location()+u.Vector(0,0,55),plot.location+u.Vector(0,0,100)));return plot
def tick(dt):
 global stage,stamp,release,worker,first_position
 try:
  now=time.monotonic()
  if stage=='ending':
   if now-stamp<3:return
   if reload_pass and u.GameplayStatics.does_save_game_exist(slot,0):u.GameplayStatics.delete_game_in_slot(slot,0)
   u.unregister_slate_post_tick_callback(handle)
   if result.get('error'):
    if u.GameplayStatics.does_save_game_exist(slot,0):u.GameplayStatics.delete_game_in_slot(slot,0)
    deadline=time.monotonic()+600
    def poll(delta):
     job_path=r/'Saved/golem_village_live_job.json'
     if job_path.exists():
      job=json.loads(job_path.read_text());job_path.unlink();u.unregister_slate_post_tick_callback(poll_handle)
      if job.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
      else:
       script=Path(job['script']);exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
     elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(poll_handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
    poll_handle=u.register_slate_post_tick_callback(poll)
   else:u.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if now-started>240:return done('Timed out at '+stage)
  if stage=='start':
   if now-stamp<3:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  world=worlds[0];v,p,pc=current(world)
  if not v or not p:return
  if release:
   if now<release[1]:return
   result.setdefault('input_trace',[]).append({'key':release[0],'catalogue_open':v.building_catalog_open,'selected':v.selected_building_index});write()
   u.SystemLibrary.execute_console_command(world,'Input.-key '+release[0]);release=None;stamp=now;return
  if now-stamp<.4:return
  if stage=='load':
   if now-stamp<7:return
   check('current village uses golem population',v.use_golem_village)
   if reload_pass:
    expected=previous['expected'];records=v.golem_residents;check('fresh process restored one worker',len(records)==1);record=records[0];check('fresh process preserved identity',record.id.to_string()==expected['id']);check('fresh process preserved home',str(record.home_plot)==expected['home']);check('fresh process preserved job',str(record.work_plot)==expected['shop']);check('fresh process restored wood',p.gather.get_count('Wood')==expected['wood']);check('fresh process restored coins',p.gather.get_count('Coin')==expected['coins']);check('fresh process restored shop wood',v.golem_shops[0].wood==expected['shop_wood']);check('fresh process restored till',v.golem_shops[0].coins==expected['shop_coins']);check('fresh process restored grid points',p.sphere_points==expected['sphere_points']);workers=u.GameplayStatics.get_all_actors_of_class(world,u.VillageGolemCitizen);check('fresh process has no duplicate actors',len(workers)==1);result['creation_pass']=previous;result['expected']=expected;result['worker_mesh']=workers[0].golem_mesh.get_editor_property('skeletal_mesh_asset').get_path_name();return done()
   v.set_editor_property('window_seconds',10000.);p.gather.add_item('Wood',40);state['wood_before']=p.gather.get_count('Wood');plots=[x for x in v.plots if x.flexible_use and not x.built];check('all 28 parcels begin available',len(plots)==28);pair=min(((a,b) for a in plots for b in plots if a.id!=b.id),key=lambda ab:(ab[0].location-ab[1].location).length());state['home']=str(pair[0].id);state['shop']=str(pair[1].id);at_plot(v,p,pc,state['home']);key(world,'B');stage='catalogue';return
  if stage=='catalogue':
   check('B opens catalogue',v.building_catalog_open);check('inherited home is selected',str(v.building_catalog[v.selected_building_index].id)=='InheritedHouse');key(world,'T');stage='home';return
  if stage=='home':
   check('T placed inherited home',next(x for x in v.plots if str(x.id)==state['home']).built);check('deed is free',p.gather.get_count('Wood')==state['wood_before']);check('house alone creates no shopkeeper',len(v.golem_residents)==0);state['shop_index']=next(i for i,x in enumerate(v.building_catalog) if str(x.id)=='Shop');key(world,'PageDown');state['previous_index']=0;stage='select';return
  if stage=='select':
   check('keyboard advances catalogue '+str(state['previous_index']),v.selected_building_index==state['previous_index']+1);state['previous_index']=v.selected_building_index
   if v.selected_building_index!=state['shop_index']:key(world,'PageDown');return
   at_plot(v,p,pc,state['shop']);key(world,'R');stage='rotate';return
  if stage=='rotate':
   check('R rotates selected building',v.placement_turns==1);state['shop_cost']=v.building_catalog[v.selected_building_index].wood_cost;key(world,'T');stage='shop';return
  if stage=='shop':
   plot=next(x for x in v.plots if str(x.id)==state['shop']);check('T placed shop',plot.built and str(plot.catalog_id)=='Shop');check('purchase paid exact materials',p.gather.get_count('Wood')==state['wood_before']-state['shop_cost']);check('housing creates one worker',len(v.golem_residents)==1);record=v.golem_residents[0];workers=u.GameplayStatics.get_all_actors_of_class(world,u.VillageGolemCitizen);check('one worker actor exists',len(workers)==1);worker=workers[0];check('worker uses approved body',worker.golem_mesh.get_editor_property('skeletal_mesh_asset')==v.male_worker_mesh);check('worker has assigned home and shop',str(record.home_plot)==state['home'] and str(record.work_plot)==state['shop']);first_position=worker.get_actor_location();key(world,'B');p.set_actor_location(plot.location+plot.stake_offset+u.Vector(350,0,100),False,True);stage='commute';stamp=now;state['commute_started']=now;return
  if stage=='commute':
   if not v.is_shop_staffed(state['shop']) or ((worker.get_actor_location()-worker.goal).x**2+(worker.get_actor_location()-worker.goal).y**2)**.5>35:
    result['movement_progress']={'seconds':now-state['commute_started'],'position':list(worker.get_actor_location().to_tuple()),'blocked':worker.route_blocked,'route_index':worker.route_index,'route_points':len(worker.route)};write();return
   check('worker walked to shop without teleport',(worker.get_actor_location()-first_position).length()>1000);check('worker followed street route',len(worker.route)>5);check('worker reached work',not worker.route_blocked);state['wood_pre_trade']=p.gather.get_count('Wood');pos=worker.get_actor_location();capture(world,'Elrhun_Village_Working_Shopkeeper',pos+worker.get_actor_forward_vector()*440+worker.get_actor_right_vector()*220+u.Vector(0,0,110),pos);stage='portrait';stamp=now;return
  if stage=='portrait':
   if now-stamp<3:return
   actor=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.SceneCapture2D) if a.get_actor_label()=='Golem village review capture');component=actor.get_component_by_class(u.SceneCaptureComponent2D);u.RenderingLibrary.export_render_target(world,component.get_editor_property('texture_target'),str(out),'Elrhun_Village_Working_Shopkeeper.png');plot=next(x for x in v.plots if str(x.id)==state['shop']);p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,100),False,True);key(world,'T');stage='sold';return
  if stage=='sold':
   check('T sale consumes wood',p.gather.get_count('Wood')==state['wood_pre_trade']-1);check('T sale pays coins',p.gather.get_count('Coin')==2);key(world,'Y');stage='bought';return
  if stage=='bought':
   check('Y purchase restores wood',p.gather.get_count('Wood')==state['wood_pre_trade']);check('Y purchase spends coins',p.gather.get_count('Coin')==0);key(world,'T');stage='save';return
  if stage=='save':
   p.set_editor_property('sphere_points',9);key(world,'F5');stage='saved';return
  if stage=='saved':
   check('F5 saved successfully',v.last_village_save_succeeded);record=v.golem_residents[0];result['expected']={'id':record.id.to_string(),'home':str(record.home_plot),'shop':str(record.work_plot),'wood':p.gather.get_count('Wood'),'coins':p.gather.get_count('Coin'),'shop_wood':v.golem_shops[0].wood,'shop_coins':v.golem_shops[0].coins,'sphere_points':p.sphere_points};check('real trade state saved',result['expected']['coins']==2 and result['expected']['shop_coins']==38);result['commute_seconds']=now-state['commute_started'];return done()
 except Exception:done(traceback.format_exc())
try:
 world=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky');E=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in E.get_all_level_actors() if isinstance(a,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot);a=E.spawn_actor_from_class(u.SceneCapture2D,u.Vector());a.set_actor_label('Golem village review capture');started=time.monotonic();stamp=started;write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 result['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
