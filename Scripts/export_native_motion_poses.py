import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/NativeMotion';manifest=json.loads((out/'manifest.json').read_text());poses={'success':False,'animations':{},'reference':{}}
def packed(t):return {'p':[t.translation.x,t.translation.y,t.translation.z],'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
for body in ['BodyA','BodyB']:
 mesh=u.load_asset('/Game/StylizedCharacters/'+body+'/Body/SKM_'+body);skeleton=mesh.get_editor_property('skeleton');ref=u.AnimPoseExtensions.get_reference_pose(skeleton);names=u.AnimPoseExtensions.get_bone_names(ref);poses['reference'][body]={str(n):packed(u.AnimPoseExtensions.get_bone_pose(ref,n,u.AnimPoseSpaces.WORLD)) for n in names};options=u.AnimPoseEvaluationOptions();options.set_editor_property('optional_skeletal_mesh',mesh);options.set_editor_property('incorporate_root_motion_into_pose',False)
 for key,meta in manifest['animations'].items():
  if not key.startswith(body+'_'):continue
  anim=u.load_asset(meta['path']);frames=[]
  for phase in [.02,.15,.28,.41,.54,.67,.80,.93]:
   t=meta['duration']*phase;pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,t,options);frames.append({'phase':phase,'time':t,'bones':{str(n):packed(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD)) for n in names}})
  poses['animations'][key]={'path':meta['path'],'frames':frames}
poses['success']=True;(out/'native_pose_samples.json').write_text(json.dumps(poses))
