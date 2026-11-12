"""Small rendered review court; no normal map or player save is changed."""
from pathlib import Path
import time,json,traceback,uuid,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs');path=r/'Saved/golem_hall_ui_review.json';slot='VerifyGolemHallUI_'+uuid.uuid4().hex
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
   p.gather.add_item('Stone',30);p.gather.add_item('Wood',30)
   p.set_actor_location(u.Vector(1000,-500,100),False,True);p.set_actor_hidden_in_game(True)
   p.toggle_adventure_hall()
   hall=p.get_editor_property('HallWidget')
   assert hall and hall.is_in_viewport(),'Hall did not open'
   for role,female,name in [('Mage',True,'Lumi'),('Tank',False,'Niri')]:
    control(hall,'ClassChoice').set_selected_option(role);control(hall,'BodyChoice').set_selected_option('Female body' if female else 'Male body');control(hall,'NameEntry').set_text(u.Text(name));control(hall,'CreateButton').on_clicked.broadcast()
   assert len(p.party_reserve.reserve)==2,'Preview creation failed'
   stage='settle';stamp=now;return
  if stage=='settle':
   if now-stamp<4:return
   shot=out/'Elrhun_Adventure_Hall_UI.png';u.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(shot).replace('\\','/')+'" -nosuffix');result['screenshot']=str(shot);stage='capture';stamp=now;return
  if stage=='capture':
   if now-stamp<5:return
   result['success']=(out/'Elrhun_Adventure_Hall_UI.png').exists();write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=now
 except Exception:
  result['error']=traceback.format_exc();write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
try:
 u.EditorLoadingAndSavingUtils.new_blank_map(False);e=u.get_editor_subsystem(u.EditorActorSubsystem)
 u.SystemLibrary.execute_console_command(None,'t.IdleWhenNotForeground 0');u.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling 0')
 world=u.EditorLevelLibrary.get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',u.IsekaiVillageGameMode)
 floor=e.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,-50));floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(u.Vector(50,50,1));floor.static_mesh_component.set_collision_profile_name('BlockAll')
 sun=e.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,800),u.Rotator(-45,-35,0));sun.light_component.set_editor_property('intensity',4.)
 sky=e.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,500));sky.light_component.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sky.light_component.set_editor_property('cubemap',u.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'));sky.light_component.set_editor_property('intensity',1.)
 v=e.spawn_actor_from_class(u.VillageRuntime,u.Vector());v.set_editor_property('use_authored_plots',True);v.set_editor_property('use_golem_village',True);v.set_editor_property('use_organic_golem_needs',True);v.set_editor_property('construction_save_slot',slot);v.set_editor_property('sparring_slime_class',u.load_class(None,'/Game/IsekaiVillage/Magic/Slimes/BP_WaterSlimeMage.BP_WaterSlimeMage_C'));v.set_editor_property('window_seconds',10000.)
 plots=[]
 for name,kind,location,beds in [('Home',u.TownBuilding.HOUSE,(-1000,0,0),5),('Hall',u.TownBuilding.GUILD,(1000,0,0),0),('Yard',u.TownBuilding.TRAINING,(0,0,0),0)]:
  x=u.TownPlot();x.set_editor_property('id',name);x.set_editor_property('kind',kind);x.set_editor_property('built',True);x.set_editor_property('location',u.Vector(*location));x.set_editor_property('stake_offset',u.Vector(0,-500,0));x.set_editor_property('bed_bonus',beds);plots.append(x)
 v.set_editor_property('authored_plots',plots);v.set_editor_property('building_catalog',[plots[2]]);v.set_editor_property('street_nodes',[u.Vector(-1200,-500,0),u.Vector(-1000,-500,0),u.Vector(-1000,-650,0),u.Vector(0,-650,0),u.Vector(1000,-650,0)]);v.set_editor_property('street_edges',[u.IntPoint(0,1),u.IntPoint(1,2),u.IntPoint(2,3),u.IntPoint(3,4)])
 motion=json.loads((r/'ArtSource/Golems/NativeMotion/manifest.json').read_text())['animations']
 for body,sex in [('BodyA','male'),('BodyB','female')]:
  v.set_editor_property(sex+'_worker_mesh',u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+body+'_Mage'));v.set_editor_property(sex+'_worker_idle',u.load_asset(motion[body+'_Idle']['path']));v.set_editor_property(sex+'_worker_walk',u.load_asset(motion[body+'_Walk_InPlace']['path']))
 v.set_editor_property('adventurer_meshes',{body+'_'+role:u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+body+'_'+role) for body in ['BodyA','BodyB'] for role in ['Tank','Mage','Ranger','Healer']})
 e.spawn_actor_from_class(u.PlayerStart,u.Vector(0,-350,100))
 eye=u.Vector(-650,-500,360);focus=u.Vector(0,-790,75);e.spawn_actor_from_class(u.CameraActor,eye,u.MathLibrary.find_look_at_rotation(eye,focus))
 write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
 result['error']=traceback.format_exc();write();u.EditorPythonScripting.set_keep_python_script_alive(False)
