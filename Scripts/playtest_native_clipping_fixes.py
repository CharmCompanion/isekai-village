import unreal as u,json,math
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');audit=json.loads((r/'ArtSource/Golems/NativeClipping/geometry_audit.json').read_text());setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());assert audit['success'];geometry=audit['weapon_geometry']
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def dot(a,b):return sum(a[i]*b[i] for i in range(3))
def add(a,b,s):return [a[i]+b[i]*s for i in range(3)]
def nearest_triangle(p,a,b,c):
 ab=sub(b,a);ac=sub(c,a);ap=sub(p,a);d1=dot(ab,ap);d2=dot(ac,ap)
 if d1<=0 and d2<=0:return a
 bp=sub(p,b);d3=dot(ab,bp);d4=dot(ac,bp)
 if d3>=0 and d4<=d3:return b
 vc=d1*d4-d3*d2
 if vc<=0 and d1>=0 and d3<=0:return add(a,ab,d1/max(.0000001,d1-d3))
 cp=sub(p,c);d5=dot(ab,cp);d6=dot(ac,cp)
 if d6>=0 and d5<=d6:return c
 vb=d5*d2-d1*d6
 if vb<=0 and d2>=0 and d6<=0:return add(a,ac,d2/max(.0000001,d2-d6))
 va=d3*d6-d5*d4
 if va<=0 and d4-d3>=0 and d5-d6>=0:return add(b,sub(c,b),(d4-d3)/max(.0000001,d4-d3+d5-d6))
 den=1/max(.0000001,va+vb+vc);return add(add(a,ab,vb*den),ac,vc*den)
def check_head_clearance(actor,anim):
 label=actor.get_actor_label();body='BodyB' if 'BodyB' in label else 'BodyA';comp=actor.get_editor_property('skeletal_mesh_component');shape=audit['head_shapes'][body];center=u.MathLibrary.transform_location(comp.get_socket_transform('head'),u.Vector(*shape['local_center_cm']));gaps={}
 for item in actor.get_editor_property('equipped_items'):
  name=item.mesh.get_name();mesh=geometry[name];part=next(p for p in actor.get_components_by_class(u.StaticMeshComponent) if p.get_editor_property('static_mesh')==item.mesh);point=u.MathLibrary.inverse_transform_location(part.get_world_transform(),center).to_tuple();positions=mesh['points'];d2=min(dot(sub(point,q),sub(point,q)) for indices in mesh['triangles'] for q in [nearest_triangle(point,*[positions[i] for i in indices])]);gap=math.sqrt(d2)-shape['radius_cm'];assert gap>.5,(label,name,'head penetration or unsafe margin',gap);gaps[name]=gap
 check={'weapon_head_clearance_cm':gaps,'golem_physics':comp.get_editor_property('physics_asset_override').get_path_name()}
 if label.endswith('Ranger'):
  assert actor.get_editor_property('use_discrete_bow_release')
  parts=actor.get_components_by_class(u.StaticMeshComponent);bow=next(p for p in parts if p.get_editor_property('static_mesh').get_name().endswith('_Bow'));strings=[p for p in parts if p.get_editor_property('static_mesh')==u.load_asset('/Engine/BasicShapes/Cylinder')];upper=u.MathLibrary.transform_location(bow.get_world_transform(),actor.get_editor_property('bow_upper_tip'));lower=u.MathLibrary.transform_location(bow.get_world_transform(),actor.get_editor_property('bow_lower_tip'));rest=(upper+lower)*.5;hand=u.MathLibrary.transform_location(comp.get_socket_transform(actor.get_editor_property('bow_draw_hand')),actor.get_editor_property('bow_draw_hand_offset'));delta=hand-rest
  if delta.length()>120:hand=rest+delta*(120/delta.length())
  draw=comp.get_anim_instance().get_curve_value('ElrhunBowDraw');expected=hand if draw>=.5 else rest;error=max(min((part.get_world_location()*2-tip-expected).length() for tip in [upper,lower]) for part in strings);assert error<.2,(label,'bow release position',draw,error);check['discrete_bow_release']=True;check['bow_string_nock_error_cm']=error
 return check
def capture_details(world,actors,phase,capture):
 if phase not in ['Ready','Run']:return
 for body in ['BodyA','BodyB']:
  for role in ['Tank','Mage','Ranger','Healer']:
   chosen=next(a for a in actors if a.get_actor_label()=='Armed - '+body+' '+role)
   for a in actors:a.set_actor_hidden_in_game(a!=chosen)
   pos=chosen.get_actor_location();capture(world,'Elrhun_Clearance_'+body+'_'+role+'_'+phase+'_Side',pos+u.Vector(380,130,155),pos+u.Vector(0,0,105),44.)
   for a in actors:a.set_actor_hidden_in_game(False)
scope={'__name__':'__main__','report_stem':'native_clipping_playtest','capture_both_bodies':True,'capture_phases':[0,2,6,7,8],'extra_inspect_actor':check_head_clearance,'extra_capture':capture_details,'setup_scripts':['native_weapon_config.py','setup_native_clipping_review.py']};p=r/'Scripts/playtest_native_weapons.py';exec(compile(p.read_text(),str(p),'exec'),scope)
