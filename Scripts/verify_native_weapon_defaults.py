import unreal as u,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');folder='/Game/Elrhun/Golems/PlayerBody';A=u.EditorAssetLibrary;setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());report={'success':False,'mode':'Fresh process; read saved defaults and spawn new actors without reconfiguration','classes':{}}
try:
 world=u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemWeaponReview');assert world
 E=u.get_editor_subsystem(u.EditorActorSubsystem)
 entries=[('BodyA','Mage',folder+'/Blueprints/BP_Golem_PlayerBodyBase'),('BodyB','Mage',folder+'/Blueprints/BP_Golem_PlayerBodyFemale')]
 entries.extend((body,role,folder+'/Blueprints/Wardrobe/BP_Native_'+body+'_'+role) for body in ['BodyA','BodyB'] for role in ['Tank','Mage','Ranger','Healer','Necromancer','Evil_Crimson','Evil_Blight','Evil_Void'])
 for body,role,path in entries:
  kind={'Necromancer':'Healer','Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Healer'}.get(role,role);cls=A.load_blueprint_class(path);cdo=u.get_default_object(cls);items=list(cdo.get_editor_property('equipped_items'));expected=2 if kind=='Tank' else 1;assert len(items)==expected,(path,'saved equipment count',len(items));actor=E.spawn_actor_from_class(cls,u.Vector(0,0,-1000),u.Rotator());spawned=list(actor.get_editor_property('equipped_items'));assert len(spawned)==expected,(path,'spawned equipment count',len(spawned))
  comp=actor.get_editor_property('skeletal_mesh_component');anim=comp.get_editor_property('animation_data').get_editor_property('anim_to_play');assert anim and anim.get_path_name()==setup['animations'][body+'_'+kind]['Ready'],(path,'ready animation',str(anim));assert anim.get_editor_property('skeleton')==comp.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton')
  components=actor.get_components_by_class(u.StaticMeshComponent)
  for item in spawned:assert sum(p.get_editor_property('static_mesh')==item.mesh for p in components)==1,(path,str(item.mesh),'missing component')
  if kind=='Ranger':assert actor.get_editor_property('animate_bow_string') and abs(actor.get_editor_property('bow_upper_tip').z)>20
  report['classes'][path]={'saved_equipment':len(items),'spawned_equipment':len(spawned),'animation':anim.get_path_name(),'meshes':[x.mesh.get_path_name() for x in spawned]};E.destroy_actor(actor)
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(r/'Saved/native_weapon_cold_verify.json').write_text(json.dumps(report,indent=2))
if not report['success']:raise RuntimeError(report['error'])
