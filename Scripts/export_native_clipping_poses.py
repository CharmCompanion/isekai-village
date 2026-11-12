import unreal as u,json,math,time
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/NativeClipping';out.mkdir(exist_ok=True);setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());result={'success':False,'rate':30,'reference':{},'clips':{}}
essential=['root','pelvis','spine_01','spine_03','spine_05','neck_01','head']+[n+'_'+s for s in ['l','r'] for n in ['clavicle','upperarm','lowerarm','hand','thigh','calf','foot','ball']]
def pack(t):return {'p':list(t.translation.to_tuple()),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':list(t.scale3d.to_tuple())}
for body in ['BodyA','BodyB']:
 mesh=u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+body+'_Mage');sk=mesh.get_editor_property('skeleton');ref=u.AnimPoseExtensions.get_reference_pose(sk);names=u.AnimPoseExtensions.get_bone_names(ref);valid={str(n) for n in names};result['reference'][body]={str(n):pack(u.AnimPoseExtensions.get_bone_pose(ref,n,u.AnimPoseSpaces.WORLD)) for n in names};options=u.AnimPoseEvaluationOptions();options.set_editor_property('optional_skeletal_mesh',mesh);options.set_editor_property('incorporate_root_motion_into_pose',False)
 for key,clips in setup['animations'].items():
  if not key.startswith(body+'_'):continue
  for label,path in clips.items():
   anim=u.load_asset(path);duration=anim.get_play_length();dense=[];frames=[]
   for i in range(1 if label=='Ready' else int(math.ceil(duration*30))+1):
    t=min(duration,float(i)/30);pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,t,options);dense.append({'time':t,'phase':t/duration,'bones':{n:pack(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD)) for n in essential if n in valid}})
   for phase in ([0.] if label=='Ready' else [i/20 for i in range(21)]):
    t=duration*phase;pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,t,options);frames.append({'time':t,'phase':phase,'bones':{str(n):pack(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD)) for n in names}})
   result['clips'][key+'_'+label]={'body':body,'role':key.split('_',1)[1],'label':label,'path':path,'duration':duration,'dense':dense,'frames':frames};u.log('CLIPPING_POSES '+key+' '+label+' '+str(len(dense)))
result['success']=True;(out/'equipped_poses.json').write_text(json.dumps(result,separators=(',',':')));(r/'Saved/native_clipping_export.json').write_text(json.dumps({'success':True,'clips':len(result['clips']),'dense_frames':sum(len(v['dense']) for v in result['clips'].values()),'full_pose_samples':sum(len(v['frames']) for v in result['clips'].values())},indent=2))
