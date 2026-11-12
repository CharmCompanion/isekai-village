"""Exercise real inputs, purchase and reload in an isolated PIE save slot."""
import json, time, traceback, uuid
from pathlib import Path
import unreal

root = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
report_path = root / 'ArtSource/World/ElRuhnSky02/play_verification.json'
images = root / 'Docs/WorldDesign/ElRuhnSky02'
images.mkdir(exist_ok=True)
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert 'Map_ElRuhnSky.' in world.get_path_name() and not level.is_in_play_in_editor()
slot = 'VerifySkyConstruction_' + uuid.uuid4().hex
state = {'status':'starting','phase':0,'started':time.monotonic(),'next':time.monotonic()+1}
report = {'status':'running','isolated_save_slot':slot}
report_path.write_text(json.dumps(report,indent=2))
handle = {}

def finish():
    unreal.unregister_slate_post_tick_callback(handle['callback'])
    if level.is_in_play_in_editor():
        level.editor_request_end_play()
    if unreal.GameplayStatics.does_save_game_exist(slot,0):
        unreal.GameplayStatics.delete_game_in_slot(slot,0)
    report_path.write_text(json.dumps(report,indent=2))

def input_key(world,key,press):
    command = 'Input.+key ' if press else 'Input.-key '
    unreal.SystemLibrary.execute_console_command(world,command+key)

def check_frame(_):
    if time.monotonic()<state['next']:
        return
    try:
        if time.monotonic()-state['started']>180:
            raise RuntimeError('PIE test timed out in phase '+str(state['phase']))
        worlds=unreal.EditorLevelLibrary.get_pie_worlds(False)
        if not worlds:
            return
        game=worlds[0]
        player=unreal.GameplayStatics.get_player_character(game,0)
        if not isinstance(player,unreal.IsekaiVillageCharacter):
            return
        runtime=unreal.GameplayStatics.get_actor_of_class(game,unreal.VillageRuntime)
        pc=unreal.GameplayStatics.get_player_controller(game,0)
        inventory=player.get_component_by_class(unreal.GatherInventoryComponent)
        phase=state['phase']
        if phase==0:
            report['game_world']=game.get_path_name()
            runtime.set_editor_property('construction_save_slot',slot)
            runtime.initialize_construction()
            vacant=[p for p in runtime.plots if p.flexible_use and not p.built]
            assert len(vacant)==28
            plot=min(vacant,key=lambda p:p.location.y)
            state['plot']=str(plot.id)
            inventory.add_item('Wood',40)
            state['wood_before']=inventory.get_count('Wood')
            player.set_actor_location(plot.location+plot.stake_offset+unreal.Vector(0,0,95),False,True)
            direction=unreal.MathLibrary.find_look_at_rotation(player.get_actor_location(),plot.location+unreal.Vector(0,0,170))
            pc.set_control_rotation(direction)
            input_key(game,'B',True)
        elif phase==1:
            if not runtime.building_catalog_open:
                return
            input_key(game,'B',False)
            assert runtime.building_catalog_open,'B did not open the catalogue'
            input_key(game,'MouseScrollDown',True)
        elif phase==2:
            if runtime.selected_building_index==0:
                return
            input_key(game,'MouseScrollDown',False)
            assert runtime.selected_building_index==1,'Scroll did not change catalogue selection'
            assert runtime.select_building('Shop')
            input_key(game,'R',True)
        elif phase==3:
            if runtime.placement_turns==0:
                return
            input_key(game,'R',False)
            assert runtime.placement_turns==1,'R did not rotate the proposal'
            previews=[a for a in unreal.GameplayStatics.get_all_actors_of_class(game,unreal.Actor) if a.get_owner()==runtime and not isinstance(a,unreal.ArchitectStake)]
            assert any(a.get_class()==runtime.building_catalog[runtime.selected_building_index].building_class for a in previews),'No shop preview'
            assert inventory.get_count('Wood')==state['wood_before']
            unreal.SystemLibrary.execute_console_command(game,'Shot filename='+str(images/'Placement_Preview.png').replace('\\','/'))
        elif phase==4:
            input_key(game,'T',True)
        elif phase==5:
            chosen=next(p for p in runtime.plots if str(p.id)==state['plot'])
            if not chosen.built:
                return
            input_key(game,'T',False)
            assert chosen.built and str(chosen.catalog_id)=='Shop','T did not place selected building'
            assert chosen.kind==unreal.TownBuilding.SHOP and chosen.placement_turns==1
            cost=max(1,int(chosen.wood_cost*(1-min(max(player.sphere_build_speed,0),50)/100)+.5))
            assert inventory.get_count('Wood')==state['wood_before']-cost
            state['actual_cost']=cost
            stake=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(game,unreal.ArchitectStake) if str(a.plot_id)==state['plot'])
            model=stake.get_editor_property('built_visual');assert model and model.get_class()==chosen.building_class
            assert (model.get_actor_scale3d()-chosen.building_scale).length()<.001
            runtime.initialize_construction()
            restored=next(p for p in runtime.plots if str(p.id)==state['plot'])
            assert restored.built and str(restored.catalog_id)=='Shop' and restored.placement_turns==1
            stake=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(game,unreal.ArchitectStake) if str(a.plot_id)==state['plot'])
            assert stake.get_editor_property('built_visual').get_class()==restored.building_class
            assert sum(p.flexible_use and p.built for p in runtime.plots)==1
            report.update(plot=state['plot'],selected_building='Shop',wood_paid=cost,rotation_degrees=90,model=restored.building_class.get_name(),reload_restored_use_and_model=True,preview_did_not_charge=True,unassigned_land_after_purchase=sum(p.flexible_use and not p.built for p in runtime.plots),controls=['B','MouseScrollDown','R','T'])
            player.set_actor_location(restored.location+restored.stake_offset+unreal.Vector(0,0,95),False,True)
            state['stock_before']=runtime.shop_wood
        elif phase==6:
            input_key(game,'T',True)
        elif phase==7:
            if runtime.shop_wood==state['stock_before']:
                return
            input_key(game,'T',False)
            assert runtime.shop_wood==state['stock_before']+1
            report.update(status='passed',traded_at_player_placed_shop=True)
            finish();return
        state['phase']+=1
        state['next']=time.monotonic()+(1.5 if phase==3 else 0.0)
    except Exception:
        report.update(status='failed',phase=state['phase'],error=traceback.format_exc())
        finish()

handle['callback']=unreal.register_slate_post_tick_callback(check_frame)
level.editor_request_begin_play()
