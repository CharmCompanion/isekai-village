import unreal as u,json,time,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=Path('C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/work/cloth_diagnostics');out.mkdir(exist_ok=True)
actors=[a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.GolemEquipmentActor)]
role_data=json.loads((root/'Saved/golem_corrected_import.json').read_text())['roles'];role_types={'Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Necromancer'}
def info_for(a):
 role=a.get_actor_label().replace('Golem ','');return role_data[role_types.get(role,role)]
pose_report={'poses':{},'errors':[]}
animation=u.load_asset('/Game/Elrhun/Golems/Animations/A_Golem_EquipmentFitCheck')
if not animation:
 assets=json.loads((root/'Saved/golem_fit_pose_import.json').read_text())['assets'];animation=next(u.load_asset(p) for p in assets if isinstance(u.load_asset(p),u.AnimSequence))
times=json.loads((root/'ArtSource/Golems/CorrectedWardrobe/fit_pose_times.json').read_text())
sequence=['Idle','WalkLeft','Crouch','Raised','Idle'];current=-1;deadline=0;phase='pose'
def check_tick(delta):
 global current,deadline,phase
 now=time.monotonic()
 if now<deadline:return
 try:
  if phase=='pose':
   current+=1
   if current==len(sequence):
    for a in actors:
     comp=a.get_editor_property('skeletal_mesh_component');comp.play_animation(u.load_asset(info_for(a)['animation']),True);comp.set_play_rate(1);comp.set_position(0,False);comp.force_cloth_next_update_teleport_and_reset()
    u.unregister_slate_post_tick_callback(check_handle)
    (root/'Saved/golem_live_pose_check.json').write_text(json.dumps(pose_report,indent=2));return
   pose=sequence[current]
   for a in actors:
    comp=a.get_editor_property('skeletal_mesh_component');comp.play_animation(u.load_asset(info_for(a).get('grip_check_animation')) if info_for(a).get('grip_check_animation') else animation,True);comp.set_position(times[pose],False);comp.set_play_rate(0);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True)
    if current==0:comp.recreate_clothing_actors()
    comp.force_cloth_next_update_teleport_and_reset()
   phase='capture';deadline=now+5
  else:
   pose=sequence[current];stats=[]
   for a in actors:
    comp=a.get_editor_property('skeletal_mesh_component');interactor=comp.get_clothing_simulation_interactor()
    data={'actor':a.get_actor_label(),'weapons':len(a.get_components_by_class(u.StaticMeshComponent))}
    if interactor:
     for method in ['get_num_cloths','get_num_dynamic_particles','get_num_kinematic_particles','get_simulation_time']:
      if hasattr(interactor,method):data[method]=getattr(interactor,method)()
    stats.append(data)
   pose_report['poses'][pose]=stats
   u.AutomationLibrary.take_high_res_screenshot(1920,1200,str(out/('Elrhun_Clothing_'+pose+'.png')),delay=1,force_game_view=False)
   phase='pose';deadline=now+3
 except Exception:
  pose_report['errors'].append(traceback.format_exc());(root/'Saved/golem_live_pose_check.json').write_text(json.dumps(pose_report,indent=2));u.unregister_slate_post_tick_callback(check_handle)
check_handle=u.register_slate_post_tick_callback(check_tick)
