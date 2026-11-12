"""Small rendered review court; no normal map or player save is changed."""
from pathlib import Path
import time,json,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs');path=r/'Saved/tower_expedition_ui_review.json';slot='VerifyTowerUI_'+uuid.uuid4().hex
result={'success':False,'slot':slot};stage='start';stamp=time.monotonic();started=stamp;handle=None
u.EditorPythonScripting.set_keep_python_script_alive(True)
def control(widget,name):
 obj=u.find_object(widget,'HallTree.'+name) or u.find_object(widget,'RosterRowTree.'+name)
 assert obj,'Missing control '+name
 return obj

def write():path.write_text(json.dumps(result,indent=2))
def tick(dt):
 global stage,stamp
 try:
  now=time.monotonic()
  if now-result.get('reported_at',0)>1:
   result['stage']=stage;result['elapsed']=now-started;result['reported_at']=now;write()
  if stage!='ending' and now-started>120:raise RuntimeError('UI preview timeout at '+stage)
  if stage=='ending':
   if now-stamp<3:return
   u.GameplayStatics.delete_game_in_slot(slot,0);u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False);return
  if stage=='start':
   if now-stamp<2:return
   u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play();stage='load';stamp=now;return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  w=worlds[0];v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None);p=u.GameplayStatics.get_player_character(w,0)
  if not v or not p:return
  if stage=='load':
   if now-stamp<5:return
   p.gather.add_item('Stone',30);p.gather.add_item('Wood',100);p.gather.add_item('Iron',20);p.gather.add_item('Bread',8)
   free=[x for x in v.plots if x.flexible_use and not x.built];free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
   hall=None
   for choice,plot in zip(['Guild','Townhouse','Cottage'],free):
    p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True);assert v.select_building(choice);v.try_build_plot(plot.id,p)
    if choice=='Guild':hall=plot
   v.toggle_building_catalog();p.set_actor_location(hall.location+hall.stake_offset+u.Vector(0,0,110),False,True);assert v.create_golem_adventurer(p,'Mage',True,u.Text('Lumi'))
   t=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.TowerExpedition)));p.set_actor_location(t.get_actor_location(),False,True);assert t.depart(p),t.last_message
   p.set_actor_location(t.camp_point(),False,True);assert t.use_camp(p),t.last_message
   p.set_actor_location(t.guardian_point(),False,True)
   ids=[a.golem_id.to_string() for a in p.party_reserve.reserve]
   allies=[a for a in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen) if a.golem_id.to_string() in ids]
   for i,actor in enumerate(allies):actor.set_actor_location(t.guardian_point()+u.Vector(150*(i+1),0,0),False,True)
   camera=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.CameraActor)));camera.set_actor_location(t.floor_origin+u.Vector(3600,-11500,10000),False,True);camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(camera.get_actor_location(),t.floor_origin+u.Vector(3600,-1000,0)),True);u.GameplayStatics.get_player_controller(w,0).set_view_target_with_blend(camera,0)
   stage='overview';stamp=now;return
  t=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.TowerExpedition)))
  if stage=='overview':
   if now-stamp<4:return
   shot=out/'Elrhun_Tower_Floor01_Overview.png';u.SystemLibrary.execute_console_command(w,'HighResShot 1600x1000 filename="'+str(shot).replace('\\','/')+'"');result['overview']=str(shot);stage='closeup';stamp=now;return
  if stage=='closeup':
   if now-stamp<4:return
   camera=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.CameraActor)));camera.set_actor_location(t.guardian_point()+u.Vector(-350,-1100,650),False,True);camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(camera.get_actor_location(),t.guardian_point()+u.Vector(0,320,60)),True);assert t.challenge_guardian(p),t.last_message;stage='battle';stamp=now;return
  if stage=='battle':
   if not t.guardian_battle or str(t.guardian_battle.phase)!='AwaitCommand':return
   if now-stamp<3:return
   shot=out/'Elrhun_Tower_Guardian_UI.png';u.SystemLibrary.execute_console_command(w,'HighResShot 1600x1000 filename="'+str(shot).replace('\\','/')+'"');result['battle']=str(shot);stage='capture';stamp=now;return
  if stage=='capture':
   if now-stamp<5:return
   result['success']=(out/'Elrhun_Tower_Floor01_Overview.png').exists() and (out/'Elrhun_Tower_Guardian_UI.png').exists();write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=now
 except Exception:
  result['error']=traceback.format_exc();write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
try:
 u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky');e=u.get_editor_subsystem(u.EditorActorSubsystem)
 u.SystemLibrary.execute_console_command(None,'t.IdleWhenNotForeground 0');u.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling 0')
 v=next(x for x in e.get_all_level_actors() if isinstance(x,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot);v.set_editor_property('window_seconds',10000.)
 e.spawn_actor_from_class(u.CameraActor,u.Vector(0,0,100))
 result['scene']='Actual sky village and runtime tower floor';write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 result['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
