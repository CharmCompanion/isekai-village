import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());assert setup['success']
template=(r/'Scripts/setup_native_motion_review.py').read_text().replace('Map_GolemMotionReview','Map_GolemWeaponReview').replace('Motion - ','Armed - ').replace('Saved/native_motion_review.json','Saved/native_weapon_review.json')
exec(compile(template,'native_weapon_review_scene.py','exec'),{'__name__':'__main__'})
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Map_GolemWeaponReview';E=u.get_editor_subsystem(u.EditorActorSubsystem);actors={}
scope={'__name__':'weapon_configuration'};p=r/'Scripts/native_weapon_config.py';exec(compile(p.read_text(),str(p),'exec'),scope)
for actor in E.get_all_level_actors():
 label=actor.get_actor_label()
 if not label.startswith('Armed - '):continue
 body='BodyB' if 'BodyB' in label else 'BodyA';role=label.split()[-1];scope['configure_weapon_actor'](actor,body,role,True);anim=u.load_asset(setup['animations'][body+'_'+role]['Action1']);comp=actor.get_editor_property('skeletal_mesh_component');data=u.SingleAnimationPlayData();data.set_editor_property('anim_to_play',anim);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);comp.set_editor_property('animation_data',data);comp.play_animation(anim,True);comp.set_update_animation_in_editor(True);comp.set_update_cloth_in_editor(True);actor.rebuild_equipment();assert len(actor.get_editor_property('equipped_items'))==(2 if role=='Tank' else 1);actors[label]={'animation':anim.get_path_name(),'weapons':[x.mesh.get_path_name() for x in actor.get_editor_property('equipped_items')]}
assert len(actors)==8;dest='/Game/Elrhun/Golems/Maps/Map_GolemWeaponReview';assert u.EditorLoadingAndSavingUtils.save_map(world,dest);(r/'Saved/native_weapon_review.json').write_text(json.dumps({'success':True,'map':dest,'actors':actors},indent=2))
