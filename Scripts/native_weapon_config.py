import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());fitting=json.loads((r/'ArtSource/Golems/NativeWeapons/fitting.json').read_text());folder='/Game/Elrhun/Golems/PlayerBody';A=u.EditorAssetLibrary
def configure_weapon_actor(actor,body,role,live=False):
 kind={'Necromancer':'Healer','Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Healer'}.get(role,role);info=fitting['bodies'][body][kind];comp=actor.get_editor_property('skeletal_mesh_component');anim=u.load_asset(setup['animations'][body+'_'+kind]['Ready']);assert anim.get_editor_property('skeleton')==comp.get_editor_property('skeletal_mesh_asset').get_editor_property('skeleton');actor.set_editor_property('animate_bow_string',False);items=[]
 for name in info['items']:
  spec=fitting['assets'][name];item=u.GolemEquipmentItem();item.set_editor_property('mesh',u.load_asset(setup['meshes'][name]));item.set_editor_property('bone',spec['bone']);item.set_editor_property('adjustment',u.Transform());items.append(item)
 if kind=='Ranger':
  bow=fitting['assets'][info['items'][0]]
  for key,value in {'bow_equipment_index':0,'bow_upper_tip':u.Vector(*bow['bow_upper_tip']),'bow_lower_tip':u.Vector(*bow['bow_lower_tip']),'bow_draw_hand':info.get('bow_draw_hand','hand_r'),'bow_draw_hand_offset':u.Vector(*info['bow_draw_hand_offset']),'bow_string_segment_mesh':u.load_asset('/Engine/BasicShapes/Cylinder'),'bow_string_material':u.load_asset('/Game/Elrhun/Golems/Materials/MI_GripLeather'),'nocked_arrow_mesh':u.load_asset(setup['meshes']['SM_Native_NockedArrow']),'bow_draw_override':-1.}.items():actor.set_editor_property(key,value)
  upper=u.Vector(*bow['bow_upper_tip']);lower=u.Vector(*bow['bow_lower_tip']);grip=u.Vector(*bow['grip_reference']);axis=(upper-lower)/(upper-lower).length();back=(upper+lower)*.5-grip;normal=u.Vector(axis.y*back.z-axis.z*back.y,axis.z*back.x-axis.x*back.z,axis.x*back.y-axis.y*back.x);normal=normal/max(.000001,normal.length());actor.set_editor_property('bow_arrow_rest',grip+axis*info.get('arrow_rest_axis_cm',6.)+normal*info.get('arrow_rest_side_cm',-2.));actor.set_editor_property('use_bow_arrow_rest',True);actor.set_editor_property('hide_blocked_preview_arrow',True)
 actor.set_editor_property('use_discrete_bow_release',kind=='Ranger' and info.get('use_discrete_bow_release',False))
 actor.set_editor_property('equipped_items',items);actor.set_editor_property('animate_bow_string',kind=='Ranger');data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);comp.set_editor_property('animation_data',data);comp.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
 physics=u.load_asset(folder+'/Physics/PA_Golem_'+body)
 if physics:comp.set_physics_asset(physics,True)
 if live:comp.play_animation(anim,True);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);actor.rebuild_equipment()
def apply_weapon_defaults():
 report={'success':False,'before':{},'after':{}}
 entries=[('BodyA','Mage',folder+'/Blueprints/BP_Golem_PlayerBodyBase'),('BodyB','Mage',folder+'/Blueprints/BP_Golem_PlayerBodyFemale')]
 entries.extend((body,role,folder+'/Blueprints/Wardrobe/BP_Native_'+body+'_'+role) for body in ['BodyA','BodyB'] for role in ['Tank','Mage','Ranger','Healer','Necromancer','Evil_Crimson','Evil_Blight','Evil_Void'])
 for body,role,path in entries:
  bp=u.load_asset(path);report['before'][path]=len(u.get_default_object(bp.generated_class()).get_editor_property('equipped_items'));bp.modify();u.BlueprintEditorLibrary.compile_blueprint(bp);cdo=u.get_default_object(bp.generated_class());cdo.modify();configure_weapon_actor(cdo,body,role);assert A.save_loaded_asset(bp,only_if_is_dirty=False);report['after'][path]=len(u.get_default_object(bp.generated_class()).get_editor_property('equipped_items'));assert report['after'][path]==(2 if role in ['Tank','Evil_Crimson'] else 1)
 report['success']=True;(r/'Saved/native_weapon_defaults.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':apply_weapon_defaults()
