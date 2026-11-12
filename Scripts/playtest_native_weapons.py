import unreal as u
import json, time, traceback, math
from pathlib import Path

u.EditorPythonScripting.set_keep_python_script_alive(True)
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
output='C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs'
focus=globals().get('focus_roles',['Tank','Mage','Ranger','Healer']);report_stem=globals().get('report_stem','native_weapon_playtest')
setup=json.loads((r/'Saved/native_weapon_setup.json').read_text())
fitting=json.loads((r/'ArtSource/Golems/NativeWeapons/fitting.json').read_text())
reference=json.loads((r/'ArtSource/Golems/NativeWeapons/poses.json').read_text())['reference']
result={'success':False,'mode':'Live Simulate In Editor; original hands; real animation and cloth ticks','phases':[],'bow_clip_metadata':{}}
for body in ['BodyA','BodyB']:
 for clip in ['Ready','Action1','Action2']:
  anim=u.load_asset(setup['animations'][body+'_Ranger'][clip]);record={'duration':anim.get_play_length(),'rate_scale':anim.get_editor_property('rate_scale')}
  try:record['curve_keys']=[list(x) for x in u.AnimationLibrary.get_float_keys(anim,'ElrhunBowDraw')]
  except Exception:record['curve_keys_error']=traceback.format_exc()
  result['bow_clip_metadata'][body+'_'+clip]=record
started=time.monotonic(); state='waiting'; phase=-1; phase_start=0.; captured=False; handle=None
phases=[('Ready','Ready',0.),('Action1_Early','Action1',0.),('Action1_Middle','Action1',.38),('Action1_Late','Action1',.70),('Action2_Early','Action2',0.),('Action2_Middle','Action2',.30),('Action2_Late','Action2',.66),('Walk','Walk',0.),('Run','Run',.10)]

def finish(error=None):
 global handle,state
 state='finished'
 if handle:u.unregister_slate_post_tick_callback(handle);handle=None
 if error:result['error']=error
 try:u.EditorLevelLibrary.editor_end_play()
 except Exception:pass
 (r/('Saved/'+report_stem+'.json')).write_text(json.dumps(result,indent=2))
 if not error:u.EditorPythonScripting.set_keep_python_script_alive(False)
 else:
  deadline=time.monotonic()+600
  def poll(delta):
   p=r/'Saved/native_weapon_live_job.json'
   if p.exists():
    job=json.loads(p.read_text());p.unlink();u.unregister_slate_post_tick_callback(poll_handle)
    if job.get('stop'):u.EditorPythonScripting.set_keep_python_script_alive(False)
    else:
     script=Path(job['script']);exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
   elif time.monotonic()>deadline:u.unregister_slate_post_tick_callback(poll_handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
  poll_handle=u.register_slate_post_tick_callback(poll)

def capture(world,label,eye,target,fov=48.):
 actor=u.GameplayStatics.get_all_actors_of_class(world,u.SceneCapture2D)[0]
 actor.set_actor_location_and_rotation(eye,u.MathLibrary.find_look_at_rotation(eye,target),False,False)
 cap=actor.get_component_by_class(u.SceneCaptureComponent2D)
 rt=u.RenderingLibrary.create_render_target2d(world,2000,1350,u.TextureRenderTargetFormat.RTF_RGBA8)
 cap.set_editor_property('texture_target',rt);cap.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('fov_angle',fov);cap.capture_scene()
 u.RenderingLibrary.export_render_target(world,rt,output,label+'.png')

def transform(t):
 v=u.Transform();v.translation=u.Vector(*t['p']);v.rotation=u.Quat(*t['q']);v.scale3d=u.Vector(*t['s']);return v

def distance(a,b):return (a-b).length()

def inspect_actor(actor):
 label=actor.get_actor_label();body='BodyB' if 'BodyB' in label else 'BodyA';role=label.split()[-1]
 comp=actor.get_editor_property('skeletal_mesh_component');origin,extent=actor.get_actor_bounds(False)
 assert all(math.isfinite(v) for v in [*origin.to_tuple(),*extent.to_tuple()])
 assert max(extent.to_tuple())<800,(label,extent)
 parts=actor.get_components_by_class(u.StaticMeshComponent);specs=fitting['bodies'][body][role]
 anim=u.load_asset(setup['animations'][body+'_'+role][phases[phase][1]])
 feet=[comp.get_socket_location(n).z-actor.get_actor_location().z for n in ['foot_l','foot_r']];head=comp.get_socket_location('head').z-actor.get_actor_location().z;assert min(feet)>-2 and min(feet)<35 and head>110,(label,'body below floor or floating',feet,head)
 sample={'animation_time':comp.get_position(),'animation_fraction':comp.get_position()/anim.get_play_length(),'bounds_extent':extent.to_tuple(),'feet_z':feet,'head_z':head,'weapons':[]}
 for name in specs['items']:
  expected=u.load_asset(setup['meshes'][name]);matches=[p for p in parts if p.get_editor_property('static_mesh')==expected];assert len(matches)==1,(label,name,len(matches))
  part=matches[0];spec=fitting['assets'][name];bone=spec['bone'];assert str(part.get_attach_socket_name())==bone
  point=u.Vector(*spec['grip_reference']);local=u.MathLibrary.inverse_transform_location(transform(reference[body][bone]),point)
  actual=u.MathLibrary.transform_location(part.get_world_transform(),point);hand=u.MathLibrary.transform_location(comp.get_socket_transform(bone),local);drift=distance(actual,hand)
  assert drift<.1,(label,name,'attachment drift cm',drift)
  sample['weapons'].append({'mesh':name,'bone':bone,'grip_drift_cm':drift})
 if role=='Ranger':
  strings=[p for p in parts if p.get_editor_property('static_mesh')==u.load_asset('/Engine/BasicShapes/Cylinder')];arrows=[p for p in parts if p.get_editor_property('static_mesh')==u.load_asset(setup['meshes']['SM_Native_NockedArrow'])];assert len(strings)==2 and len(arrows)==1
  draw=comp.get_anim_instance().get_curve_value('ElrhunBowDraw');assert -.01<=draw<=1.01
  times,values=u.AnimationLibrary.get_float_keys(anim,'ElrhunBowDraw');t=comp.get_position();expected=float(values[-1])
  for i in range(len(times)-1):
   if times[i]<=t<=times[i+1]:expected=float(values[i]+(values[i+1]-values[i])*(t-times[i])/(times[i+1]-times[i]));break
  sample['bow_curve_expected']=expected;assert abs(draw-expected)<.06,(label,'stale bow curve',draw,expected)
  if draw<=.1:assert not arrows[0].is_visible(),(label,draw,'arrow should be released')
  elif not actor.get_editor_property('hide_blocked_preview_arrow'):assert arrows[0].is_visible(),(label,draw,'missing nocked arrow')
  if draw>.99:
   hand=u.MathLibrary.transform_location(comp.get_socket_transform(actor.get_editor_property('bow_draw_hand')),actor.get_editor_property('bow_draw_hand_offset'));drift=distance(arrows[0].get_world_location(),hand)
   sample['nock_hand_drift_cm']=drift;sample['draw_hand']=hand.to_tuple();sample['arrow_tail']=arrows[0].get_world_location().to_tuple();assert drift<2.,(label,'nock drift cm',drift)
  sample['actor_tick_enabled']=actor.is_actor_tick_enabled()
  sample['bow_draw']=draw;sample['arrow_visible']=arrows[0].is_visible();sample['string_segments']=len(strings)
 if globals().get('extra_inspect_actor'):sample['placement_check']=extra_inspect_actor(actor,anim)
 return sample

def tick(delta):
 global state,phase,phase_start,captured,started
 try:
  now=time.monotonic()
  if now-started>180:return finish('Playtest timed out')
  if state=='waiting':
   if now-started<4:return
   u.EditorLevelLibrary.editor_play_simulate();state='starting';return
  worlds=u.EditorLevelLibrary.get_pie_worlds(False)
  if not worlds:return
  world=worlds[0];all_actors=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.SkeletalMeshActor) if a.get_actor_label().startswith('Armed - ')];actors=[a for a in all_actors if a.get_actor_label().split()[-1] in focus]
  if len(actors)!=len(focus)*2:return
  if state=='starting' or now-phase_start>2.6:
   phase+=1
   if phase==len(phases):result['success']=True;return finish()
   state='playing';phase_start=now;captured=False
   for actor in actors:
    label=actor.get_actor_label();body='BodyB' if 'BodyB' in label else 'BodyA';role=label.split()[-1];comp=actor.get_editor_property('skeletal_mesh_component');anim=u.load_asset(setup['animations'][body+'_'+role][phases[phase][1]]);assert anim.get_editor_property('skeleton')==comp.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton');comp.play_animation(anim,True);comp.set_position(anim.get_play_length()*phases[phase][2],False)
   return
  if captured or now-phase_start<.8:return
  captured=True;sample={'phase':phases[phase][0],'actors':{a.get_actor_label():inspect_actor(a) for a in actors}}
  capture(world,'Elrhun_Live_Weapons_'+phases[phase][0],u.Vector(180,1240,760),u.Vector(0,-80,95))
  if phase in globals().get('capture_phases',[0,2,3,6]):
   for body in (['BodyA','BodyB'] if globals().get('capture_both_bodies') else ['BodyB']):
    for role in ([x for x in ['Tank','Mage','Ranger','Healer'] if x in focus] if globals().get('capture_both_bodies') else ['Tank','Ranger','Healer']):
     chosen=next(a for a in actors if a.get_actor_label()=='Armed - '+body+' '+role)
     for a in all_actors:a.set_actor_hidden_in_game(a!=chosen)
     prefix='Elrhun_ShieldMage_'+body+'_'+role if globals().get('capture_both_bodies') else 'Elrhun_Live_Weapon_'+role
     pos=chosen.get_actor_location();capture(world,prefix+'_'+phases[phase][0],pos+u.Vector(110,390,145),pos+u.Vector(0,0,105))
     if phase==0:
      hand=chosen.get_editor_property('skeletal_mesh_component').get_socket_location('hand_l' if role=='Ranger' else 'hand_r');capture(world,prefix+'_Grip',hand+u.Vector(34,80,25),hand,38.)
     for a in all_actors:a.set_actor_hidden_in_game(False)
  if globals().get('extra_capture'):extra_capture(world,all_actors,phases[phase][0],capture)
  result['phases'].append(sample);(r/('Saved/'+report_stem+'_progress.json')).write_text(json.dumps(result,indent=2))
 except Exception:finish(traceback.format_exc())

try:
 for script in globals().get('setup_scripts',['correct_native_weapon_roots.py','native_weapon_config.py','setup_native_weapon_review.py']):
  p=r/'Scripts'/script;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 started=time.monotonic();handle=u.register_slate_post_tick_callback(tick)
except Exception:finish(traceback.format_exc())
