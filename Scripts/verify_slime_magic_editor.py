"""Validate saved assets, capture actual editor presentation, then exercise all six lanes in PIE."""
import unreal,json,time,traceback
from pathlib import Path
B=Path(__file__).resolve().parents[1];R='/Game/IsekaiVillage/Magic/Slimes';out=B/'ArtSource/Magic/SlimeRunes';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=json.loads((B/'ArtSource/Magic/SlimeRunes/spells.json').read_text())
actors=E.get_all_level_actors();casters=[a for a in actors if isinstance(a,unreal.SlimeRunicMage) and a.get_editor_property('spell')]
assert len(casters)==6
for a in casters:
 s=a.get_editor_property('spell');assert a.mesh.get_editor_property('skeletal_mesh_asset');assert s.get_editor_property('rune_texture') and s.get_editor_property('bolt_fx') and s.get_editor_property('impact_fx')
 assert a.get_editor_property('target');assert not a.get_editor_property('target_player');assert a.get_editor_property('auto_cast')
cam=next(a for a in actors if isinstance(a,unreal.CameraActor))
unreal.EditorLevelLibrary.pilot_level_actor(cam)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for command in ['r.EyeAdaptationQuality 0','r.Streaming.PoolSize 2048','viewmode lit']:unreal.SystemLibrary.execute_console_command(world,command)
state={'stage':'editor_capture','next':time.monotonic()+12};holder={};report={'asset_checks':True,'lanes':[]}
def finish():
 (B/'Saved/slime_magic_play_validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(holder['tick'])
def tick(delta):
 if time.monotonic()<state['next']:return
 try:
  if state['stage']=='editor_capture':
   unreal.AutomationLibrary.take_high_res_screenshot(1800,1200,str(out/'SlimeMagic_Unreal.png'),camera=cam,delay=.5)
   state.update(stage='start_play',next=time.monotonic()+4)
  elif state['stage']=='start_play':
   unreal.EditorLevelLibrary.eject_pilot_level_actor();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate();state.update(stage='verify_play',next=time.monotonic()+14,play_started=time.monotonic())
  elif state['stage']=='verify_play':
   worlds=unreal.EditorLevelLibrary.get_pie_worlds(False);assert worlds,'No PIE world';pw=worlds[0]
   if unreal.GameplayStatics.get_time_seconds(pw)<14:
    assert time.monotonic()-state['play_started']<180,'Simulation did not advance'
    state['next']=time.monotonic()+1;return
   pcs=[a for a in unreal.GameplayStatics.get_all_actors_of_class(pw,unreal.SlimeRunicMage) if a.get_editor_property('spell')]
   assert len(pcs)==6,len(pcs)
   for a in pcs:
    t=a.get_editor_property('target');r={'spell':a.get_editor_property('spell').get_editor_property('spell_name'),'casts':a.get_editor_property('casts_released'),'target_hp':t.get_editor_property('health'),'max_hp':t.get_editor_property('max_health'),'tp':a.get_editor_property('tp')};report['lanes'].append(r)
    assert r['casts']>0,r
    assert r['target_hp']<r['max_hp'],r
    assert 0<=r['tp']<=100,r
   report['passed']=True;unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();finish()
 except Exception:
  report['passed']=False;report['error']=traceback.format_exc();unreal.log_error(report['error']);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();finish()
holder['tick']=unreal.register_slate_post_tick_callback(tick)
