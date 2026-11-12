import unreal as u,json,math,bisect,shutil
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');source=r/'ArtSource/Golems/NativeClipping/safe_animation_tracks.json';data=json.loads(source.read_text());assert data['success'];report={'success':False,'clips':{}};A=u.EditorAssetLibrary
def transform(t):
 v=u.Transform();v.translation=u.Vector(*t['p']);v.rotation=u.Quat(*t['q']);v.scale3d=u.Vector(*t['s']);return v
def blend(a,b,t):
 qa=a['q'];qb=b['q'];dot=sum(x*y for x,y in zip(qa,qb))
 if dot<0:qb=[-x for x in qb];dot=-dot
 if dot>.9995:q=[x+(y-x)*t for x,y in zip(qa,qb)]
 else:
  theta=math.acos(min(1,dot));q=[(x*math.sin((1-t)*theta)+y*math.sin(t*theta))/math.sin(theta) for x,y in zip(qa,qb)]
 length=math.sqrt(sum(x*x for x in q));return {'p':[x+(y-x)*t for x,y in zip(a['p'],b['p'])],'q':[x/length for x in q],'s':[x+(y-x)*t for x,y in zip(a['s'],b['s'])]}
for key,spec in data['clips'].items():
 anim=u.load_asset(spec['path']);assert anim;backup=r/'Saved/NativeClippingBackup/AnimationAssets'/Path(spec['path'].split('.')[0].replace('/Game/','')+'.uasset');original=r/'Content'/Path(spec['path'].split('.')[0].replace('/Game/','')+'.uasset');backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():shutil.copy2(original,backup)
 if spec['constant_bones']:assert u.GolemClothTools.apply_held_bone_pose(anim,{n:transform(t) for n,t in spec['constant_bones'].items()}),key
 try:model=anim.get_editor_property('data_model_interface');count=model.get_number_of_keys()
 except Exception:count=u.AnimationLibrary.get_num_keys(anim)
 for bone,records in spec['tracks'].items():
  times=[x['time'] for x in records];keys=[]
  for i in range(count):
   t=anim.get_play_length()*i/max(1,count-1);j=max(0,min(len(times)-2,bisect.bisect_right(times,t)-1));alpha=max(0,min(1,(t-times[j])/max(.000001,times[j+1]-times[j])));keys.append(transform(blend(records[j]['transform'],records[j+1]['transform'],alpha)))
  assert u.GolemClothTools.set_equipment_bone_track(anim,bone,keys),(key,bone,count)
 if spec.get('use_walk_lower_body'):
  body,role,label=key.split('_');walk=u.load_asset(spec['path'].replace('_Run.','_Walk.').replace('_Run','_Walk'));mesh=u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+body+'_'+role);options=u.AnimPoseEvaluationOptions();options.set_editor_property('optional_skeletal_mesh',mesh);frames=[u.AnimPoseExtensions.get_anim_pose_at_time(walk,walk.get_play_length()*i/max(1,count-1),options) for i in range(count)];names=[str(n) for n in u.AnimPoseExtensions.get_bone_names(frames[0])];parents=json.loads((r/'ArtSource/Golems/NativeWeapons/fitting.json').read_text())['bodies'][body][role]['parents']
  def leg(name):
   while name:
    if name in ['thigh_l','thigh_r','ik_foot_root']:return True
    name=parents.get(name)
   return False
  for bone in names:
   if bone in ['root','pelvis'] or leg(bone):assert u.GolemClothTools.set_equipment_bone_track(anim,bone,[u.AnimPoseExtensions.get_bone_pose(p,bone,u.AnimPoseSpaces.LOCAL) for p in frames]),(key,bone)
 assert A.save_loaded_asset(anim,only_if_is_dirty=False);report['clips'][key]={'keys':count,'constant_bones':len(spec['constant_bones']),'animated_corrections':list(spec['tracks']),'minimum_predicted_head_clearance_cm':spec['minimum_head_gap_cm'],'short_equipped_stride':bool(spec.get('use_walk_lower_body'))}
report['success']=True;(r/'Saved/native_clearance_poses.json').write_text(json.dumps(report,indent=2))
