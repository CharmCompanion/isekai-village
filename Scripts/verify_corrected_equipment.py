import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
report={'success':False,'blueprints':{},'levels':{},'errors':[]}
try:
 imports=json.loads((root/'Saved/golem_corrected_import.json').read_text());setup=json.loads((root/'Saved/golem_corrected_setup.json').read_text());assert setup['success'],setup.get('error')
 paths=json.loads((root/'Saved/golem_setup_report.json').read_text())['blueprints']
 types={'Evil_Crimson':'Tank','Evil_Blight':'Ranger','Evil_Void':'Necromancer'}
 for role,path in paths.items():
  bp=u.load_asset(path);cdo=u.get_default_object(bp.generated_class());assert isinstance(cdo,u.GolemEquipmentActor),role
  info=imports['roles'][types.get(role,role)];comp=cdo.get_editor_property('skeletal_mesh_component');mesh=comp.get_editor_property('skeletal_mesh_asset');assert mesh.get_path_name()==info['mesh'],role
  assert comp.get_editor_property('animation_data').get_editor_property('anim_to_play').get_path_name()==info['animation'],(role,'Grip animation mismatch')
  state=json.loads(u.GolemClothTools.inspect_clothing(mesh));assert len(state['collision_bodies'])>=10,(role,state)
  if types.get(role,role) in ['Tank','Mage','Necromancer']:
   assert state['cloth_assets'],(role,'No cloth')
   assert all(x['pinned']>0 and x['moving']>0 for x in state['cloth_assets']),(role,state)
   assert any(x['cloth'] for x in state['sections']),(role,state)
  overrides=comp.get_editor_property('override_materials');assert role in overrides[info['gem_slot']].get_path_name(),role
  assert len(cdo.get_editor_property('equipped_items'))==len(info['weapons'])+(1 if role.startswith('Evil_') and 'accessories' in imports else 0)+(len(imports.get('accessories',{}).get('HealerUnderlay',[])) if role=='Healer' else 0),role
  assert all(w['bone'] in ['LeftHand','RightHand'] for w in info['weapons']),(role,info['weapons'])
  report['blueprints'][role]={'mesh':mesh.get_path_name(),'cloth':state,'weapons':[str(x.get_editor_property('bone')) for x in cdo.get_editor_property('equipped_items')]}
 actor_sys=u.get_editor_subsystem(u.EditorActorSubsystem)
 for level in [base+'/Maps/Map_GolemSoulGems','/Game/IsekaiVillage/Maps/Map_Village']:
  u.EditorLoadingAndSavingUtils.load_map(level);found=[]
  for a in actor_sys.get_all_level_actors():
   if not isinstance(a,u.GolemEquipmentActor):continue
   body=a.get_editor_property('skeletal_mesh_component')
   parts=a.get_components_by_class(u.StaticMeshComponent)
   before=len(parts);a.rebuild_equipment();parts=a.get_components_by_class(u.StaticMeshComponent)
   assert len(parts)==len(a.get_editor_property('equipped_items')),(a.get_actor_label(),len(parts))
   for part in parts:
    assert part.get_attach_parent()==body,part
    assert str(part.get_attach_socket_name()) in [str(x.get_editor_property('bone')) for x in a.get_editor_property('equipped_items')],part
    assert part.get_collision_enabled()==u.CollisionEnabled.QUERY_ONLY,part
    assert not part.is_simulating_physics(),part
   found.append({'label':a.get_actor_label(),'attachments_after_load':before,'attachments':len(parts),'bones':[str(p.get_attach_socket_name()) for p in parts]})
  assert len(found)==(8 if level.endswith('Map_GolemSoulGems') else 1),(level,found)
  report['levels'][level]=found
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_corrected_verify.json').write_text(json.dumps(report,indent=2))
