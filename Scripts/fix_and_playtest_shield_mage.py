import unreal as u,json,math,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 p=r/'Scripts/setup_native_golem_weapons.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','only_keys':{'BodyA_Tank','BodyB_Tank','BodyA_Mage','BodyB_Mage'}})
 fitting=json.loads((r/'ArtSource/Golems/NativeWeapons/fitting.json').read_text());setup=json.loads((r/'Saved/native_weapon_setup.json').read_text())
 def placement_check(actor,anim):
  label=actor.get_actor_label();body='BodyB' if 'BodyB' in label else 'BodyA';role=label.split()[-1];comp=actor.get_editor_property('skeletal_mesh_component')
  if role=='Tank':
   name='SM_'+body+'_Tank_Shield';spec=fitting['assets'][name];mesh=u.load_asset(setup['meshes'][name]);part=next(p for p in actor.get_components_by_class(u.StaticMeshComponent) if p.get_editor_property('static_mesh')==mesh);tr=part.get_world_transform();g=u.MathLibrary.transform_location(tr,u.Vector(*spec['grip_reference']));front=u.MathLibrary.transform_location(tr,u.Vector(*spec['shield_front_point_reference']));n=(front-g)/(front-g).length();forward=actor.get_actor_right_vector();dot=n.x*forward.x+n.y*forward.y+n.z*forward.z
   if anim.get_name().endswith('_Ready'):assert dot>.8,(label,'ready shield not facing forward',dot)
   if anim.get_name().endswith('_Action2'):assert dot>.25,(label,'guard shield faces backward',dot)
   return {'shield_front_alignment':dot}
  opts=u.AnimPoseEvaluationOptions();opts.set_editor_property('optional_skeletal_mesh',comp.get_editor_property('skeletal_mesh_asset'));pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,comp.get_position(),opts);maximum=0.
  for bone,target in fitting['bodies'][body]['Mage']['free_hand_local_pose'].items():
   q=u.AnimPoseExtensions.get_bone_pose(pose,bone,u.AnimPoseSpaces.LOCAL).rotation;t=target['q'];dot=abs(q.x*t[0]+q.y*t[1]+q.z*t[2]+q.w*t[3]);angle=math.degrees(2*math.acos(min(1.,dot)));maximum=max(maximum,angle)
  assert maximum<.5,(label,'free wrist/fingers not corrected',maximum)
  return {'maximum_free_hand_pose_error_degrees':maximum}
 def detail_capture(world,actors,phase,capture):
  if phase!='Ready':return
  for body in ['BodyA','BodyB']:
   for role in ['Tank','Mage']:
    chosen=next(a for a in actors if a.get_actor_label()=='Armed - '+body+' '+role)
    for a in actors:a.set_actor_hidden_in_game(a!=chosen)
    pos=chosen.get_actor_location()
    if role=='Tank':capture(world,'Elrhun_ShieldMage_'+body+'_Shield_Back',pos+u.Vector(-160,-300,145),pos+u.Vector(-10,15,115),40.)
    else:
     hand=chosen.get_editor_property('skeletal_mesh_component').get_socket_location('hand_l');capture(world,'Elrhun_ShieldMage_'+body+'_Mage_FreeHand',hand+u.Vector(35,90,18),hand,38.)
    for a in actors:a.set_actor_hidden_in_game(False)
  pair=[a for a in actors if a.get_actor_label() in ['Armed - BodyB Tank','Armed - BodyB Mage']]
  for a in actors:a.set_actor_hidden_in_game(a not in pair)
  center=(pair[0].get_actor_location()+pair[1].get_actor_location())*.5
  capture(world,'Elrhun_ShieldMage_Corrected',center+u.Vector(80,620,190),center+u.Vector(0,0,100),44.)
  for a in actors:a.set_actor_hidden_in_game(False)
 scope={'__name__':'__main__','focus_roles':['Tank','Mage'],'report_stem':'shield_mage_fix_playtest','capture_both_bodies':True,'extra_inspect_actor':placement_check,'extra_capture':detail_capture,'setup_scripts':['native_weapon_config.py','setup_native_weapon_review.py']};p=r/'Scripts/playtest_native_weapons.py';exec(compile(p.read_text(),str(p),'exec'),scope)
except Exception:(r/'Saved/shield_mage_fix_error.txt').write_text(traceback.format_exc());raise
