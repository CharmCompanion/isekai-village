"""Playtest for consecutive floor-by-floor ascension, Town-to-Tower forge loop, and Floor 5 Boss Minion encounter."""
from pathlib import Path
import json,time,traceback,uuid,math,unreal as u

r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
path=r/'Saved/tower_ascent_playtest.json'
slot='VerifyAscent_'+uuid.uuid4().hex
report={'success':False,'slot':slot,'checks':[]}
stage='start';stamp=time.monotonic();started=stamp;handle=None;release=None;state={}
u.EditorPythonScripting.set_keep_python_script_alive(True)

def write():path.write_text(json.dumps(report,indent=2))
def check(name,yes):
    assert yes,name
    report['checks'].append(name)
def pulse(w,key):
    global release
    u.SystemLibrary.execute_console_command(w,'Input.+key '+key);release=key
def finish(error=None):
    global stage,stamp
    report['success']=not bool(error)
    if error:report['error']=error
    write();u.EditorLevelLibrary.editor_end_play();stage='ending';stamp=time.monotonic()
def walk(points,after):
    global stage,stamp
    state['path']=list(points);state['after']=after;stage='walk';stamp=time.monotonic()
def center(t,index):return t.floor_origin+t.regions[index].center+u.Vector(0,0,103)

def tick(dt):
    global stage,stamp,release
    try:
        now=time.monotonic()
        if stage=='ending':
            if now-stamp<3:return
            u.GameplayStatics.delete_game_in_slot(slot,0)
            u.unregister_slate_post_tick_callback(handle)
            u.EditorPythonScripting.set_keep_python_script_alive(False)
            return
        if now-state.get('last_report',0)>2:
            report['stage']=stage;report['elapsed']=now-started;write();state['last_report']=now
        if now-started>360:return finish('Timeout at '+stage)

        if stage=='start':
            if now-stamp<3:return
            u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play()
            stage='load';stamp=now;return

        worlds=u.EditorLevelLibrary.get_pie_worlds(False)
        if not worlds:return
        w=worlds[0]
        v=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.VillageRuntime)),None)
        p=u.GameplayStatics.get_player_character(w,0)
        t=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.TowerExpedition)),None)
        if not v or not p or not t:return

        if release:
            u.SystemLibrary.execute_console_command(w,'Input.-key '+release);release=None;return

        if stage=='load':
            if now-stamp<8:return
            v.set_editor_property('window_seconds',10000.)
            p.gather.add_item('Wood',100);p.gather.add_item('Iron',20);p.gather.add_item('Stone',18);p.gather.add_item('Bread',12)
            free=[x for x in v.plots if x.flexible_use and not x.built]
            free.sort(key=lambda x:(x.location.x-10000)**2+(x.location.y-2000)**2)
            for choice,plot in zip(['Guild','Townhouse','Cottage'],free):
                p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True)
                check('Select '+choice,v.select_building(choice))
                v.try_build_plot(plot.id,p)
                check('Build '+choice,any(x.id==plot.id and x.built and str(x.catalog_id)==choice for x in v.plots))
                if choice=='Guild':state['hall']=str(plot.id)
            v.toggle_building_catalog()
            plot=next(x for x in v.plots if str(x.id)==state['hall'])
            p.set_actor_location(plot.location+plot.stake_offset+u.Vector(0,0,110),False,True)
            ok=v.create_golem_adventurer(p,'Mage',True,u.Text('Lumi Ascent'))
            if not ok:raise AssertionError('Craft adventurer failed: '+str(v.last_hall_message))
            check('Craft adventurer for floor ascent',ok)
            state['id']=p.party_reserve.reserve[0].golem_id.to_string()
            forge=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.BlacksmithForge)),None)
            if not forge:
                trans=u.Transform(p.get_actor_location(),u.Rotator(),u.Vector(1,1,1))
                forge=u.GameplayStatics.begin_deferred_actor_spawn_from_class(w,u.BlacksmithForge,trans)
                if forge:u.GameplayStatics.finish_spawning_actor(forge,trans)
            check('Forge status line has options',len(forge.forge_status_line(p))>0)
            check('Forge adventurer weapon',forge.try_forge_adventurer_gear(p))
            check('Adventurer weapon tier is 1',p.party_reserve.reserve[0].weapon_tier==1)
            check('Forge adventurer armor',forge.try_forge_adventurer_gear(p))
            check('Adventurer armor tier is 1',p.party_reserve.reserve[0].armor_tier==1)
            p.set_actor_location(t.get_actor_location(),False,True)
            pulse(w,'G');stage='depart';stamp=now;return

        if stage=='depart':
            check('Depart begins on Floor 1',t.get_editor_property('bInside') and v.tower_floor.floor==1)
            check('Chamber floor has unified layout',len(t.regions)==4)
            state['actor']=next(x for x in u.GameplayStatics.get_all_actors_of_class(w,u.VillageGolemCitizen) if x.golem_id.to_string()==state['id'])
            check('Floor 1 Relic Altar available',t.floor_altar_available())
            walk([center(t,1),t.altar_point()-u.Vector(0,140,0)],'f1_altar')
            return

        if stage=='f1_altar':
            pulse(w,'G');stage='f1_altar_claimed';stamp=now;return

        if stage=='f1_altar_claimed':
            if t.floor_altar_available():
                if now-stamp<4:return
                raise AssertionError('Failed to claim Floor 1 Relic Altar: '+t.last_message)
            check('Claimed Floor 1 Relic Altar boon',len(v.tower_floor.run_relics)==1 and not t.floor_altar_available())
            walk([center(t,1),center(t,2),t.guardian_point()],'f1_guardian_wait')
            return

        if stage=='walk':
            if now-stamp>60:raise AssertionError('Walking timed out toward '+str(state['path'][0])+' at '+str(p.get_actor_location()))
            if not state['path']:stage=state['after'];stamp=now;return
            goal=state['path'][0];loc=p.get_actor_location();dx,dy=goal.x-loc.x,goal.y-loc.y;dist=math.hypot(dx,dy)
            if dist<65:state['path'].pop(0);return
            p.add_movement_input(u.Vector(dx/dist,dy/dist,0),1.0,False);return

        if stage=='f1_guardian_wait':
            actor=state['actor'];distance=(actor.get_actor_location()-t.guardian_point()).length()
            if distance>1000:
                if now-stamp>45:raise AssertionError('Companion lagged behind: '+str(actor.get_actor_location()))
                return
            check('Party reached Floor 1 Guardian',distance<1000)
            pulse(w,'G');stage='f1_battle';stamp=now;return

        if stage=='f1_battle':
            battles=list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));b=battles[0] if battles else None
            if not b:
                if now-stamp<4:return
                raise AssertionError('G did not start battle: '+t.last_message)
            if 'verified_gear' not in state and len(b.members)>0:
                check('Sparring member has Weapon Tier 1',b.members[0].weapon_tier==1)
                check('Sparring member has Armor Tier 1',b.members[0].armor_tier==1)
                check('Sparring member max health boosted (>= 125)',b.members[0].max_health>=125.0)
                state['verified_gear']=True
            if str(b.phase)=='Result':
                check('Defeated Floor 1 Guardian',b.get_editor_property('bVictory'))
                pulse(w,'J');stage='f1_closed';return
            if str(b.phase)=='AwaitCommand':pulse(w,'One')
            if now-stamp>60:raise AssertionError('Floor 1 battle timed out')
            return

        if stage=='f1_closed':
            if list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring)):return
            portals=t.available_portals()
            check('Floor 1 clear opens Forward portal',any('FORWARD' in str(x).upper() for x in portals))
            target_portal=next(x for x in portals if 'FORWARD' in str(x).upper())
            walk([t.portal_point(target_portal)],'forward_ready')
            return

        if stage=='forward_ready':
            pulse(w,'G');stage='f2_arrived';stamp=now;return

        if stage=='f2_arrived':
            if v.tower_floor.floor!=2:
                if now-stamp<5:return
                raise AssertionError('Failed to advance to Floor 2: '+t.last_message)
            check('Ascended to Floor 2',v.tower_floor.floor==2)
            check('Floor 2 adapts against player habits',len(v.tower_floor.current_plan.rules)>0 or v.tower_floor.current_plan.announcement!='')
            check('Share bread on Floor 2',t.share_rations(p))
            walk([center(t,1),center(t,2),t.guardian_point()],'f2_guardian_wait')
            return

        if stage=='f2_guardian_wait':
            actor=state['actor'];distance=(actor.get_actor_location()-t.guardian_point()).length()
            if distance>1000:
                if now-stamp>45:raise AssertionError('Companion lagged behind on F2: '+str(actor.get_actor_location()))
                return
            check('Party reached Floor 2 Guardian',distance<1000)
            pulse(w,'G');stage='f2_battle';stamp=now;return

        if stage=='f2_battle':
            battles=list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));b=battles[0] if battles else None
            if not b:
                if now-stamp<4:return
                raise AssertionError('G did not start F2 battle: '+t.last_message)
            if str(b.phase)=='Result':
                check('Defeated Floor 2 Guardian',b.get_editor_property('bVictory'))
                pulse(w,'J');stage='f2_closed';return
            if str(b.phase)=='AwaitCommand':pulse(w,'One')
            if now-stamp>60:raise AssertionError('Floor 2 battle timed out')
            return

        if stage=='f2_closed':
            if list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring)):return
            portals=t.available_portals()
            check('Floor 2 clear offers portals',len(portals)>=2)
            has_leap=any('LEAP' in str(x).upper() for x in portals)
            if has_leap:
                check('Floor 2 offers Leap portal',v.tower_floor.leap_offer>=2)
                target_portal=next(x for x in portals if 'LEAP' in str(x).upper())
            else:
                target_portal=next(x for x in portals if 'FORWARD' in str(x).upper())
            walk([t.portal_point(target_portal)],'leap_ready')
            return

        if stage=='leap_ready':
            pulse(w,'G');stage='higher_floor_arrived';stamp=now;return

        if stage=='higher_floor_arrived':
            if v.tower_floor.floor<=2:
                if now-stamp<5:return
                raise AssertionError('Failed to leap/ascend past Floor 2: '+t.last_message)
            check('Advanced to higher floor: Floor '+str(v.tower_floor.floor),v.tower_floor.floor>=3)
            dist_to_entry=(p.get_actor_location()-t.entry_point()).length()
            check('Party placed at new floor entry gate',dist_to_entry<250)
            pulse(w,'V');stage='returned_home';stamp=now;return

        if stage=='returned_home':
            if t.get_editor_property('bInside'):
                if now-stamp<5:return
                raise AssertionError('Arrival gate V did not return to village: '+t.last_message)
            check('Arrival gate safely ends ascension run',not t.get_editor_property('bInside'))
            check('Companion restored to village',state['actor'].is_actor_tick_enabled())
            check('Returning home resets temporary RunRelics',len(v.tower_floor.run_relics)==0)
            p.gather.add_item('Crystal',12);p.gather.add_item('Iron',16);p.gather.add_item('Bread',6)
            forge=next(iter(u.GameplayStatics.get_all_actors_of_class(w,u.BlacksmithForge)),None)
            check('Forge Runic Weapon (Tier 2)',bool(forge and forge.try_forge_adventurer_gear(p) and p.party_reserve.reserve[0].weapon_tier==2))
            check('Forge Runic Armor (Tier 2)',bool(forge and forge.try_forge_adventurer_gear(p) and p.party_reserve.reserve[0].armor_tier==2))
            p.set_actor_location(t.get_actor_location(),False,True)
            pulse(w,'G');stage='run2_depart';stamp=now;return

        if stage=='run2_depart':
            if not t.get_editor_property('bInside'):
                if now-stamp<4:return
                raise AssertionError('Failed Run 2 departure: '+t.last_message)
            check('Run 2 starts cleanly on Floor '+str(v.tower_floor.floor),v.tower_floor.floor>=3)
            walk([center(t,1),center(t,2),t.guardian_point()],'run2_guardian_wait')
            return

        if stage=='run2_guardian_wait':
            actor=state['actor'];distance=(actor.get_actor_location()-t.guardian_point()).length()
            if distance>1000:
                if now-stamp>45:raise AssertionError('Companion lagged behind on Floor '+str(v.tower_floor.floor))
                return
            if v.tower_floor.floor==5:
                t.share_rations(p)
            pulse(w,'G');stage='run2_battle';stamp=now;return

        if stage=='run2_battle':
            battles=list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring));b=battles[0] if battles else None
            if not b:
                if now-stamp<4:return
                raise AssertionError('G did not start battle on Floor '+str(v.tower_floor.floor)+': '+t.last_message)
            if v.tower_floor.floor==5:
                if 'f5_checked' not in state and len(b.minions)>0:
                    check('Floor 5 Boss spawns minion acolyte',len(b.minions)==1)
                    check('Floor 5 Boss Ward active',b.boss_ward_reduction()>0.1)
                    check('Floor 5 Runic Armor HP=150',len(b.members)>0 and b.members[0].max_health==150.0)
                    pulse(w,'Tab');state['f5_checked']=True;return
                if state.get('f5_checked') and not state.get('tab_verified'):
                    check('Tab switches target to minion acolyte',b.selected_enemy_index==1)
                    state['tab_verified']=True
            if str(b.phase)=='Result':
                check('Defeated Floor '+str(v.tower_floor.floor)+' Guardian',b.get_editor_property('bVictory'))
                pulse(w,'J');stage='run2_closed';stamp=now;return
            if str(b.phase)=='AwaitCommand':pulse(w,'One')
            if now-stamp>90:raise AssertionError('Floor '+str(v.tower_floor.floor)+' battle timed out')
            return

        if stage=='run2_closed':
            if list(u.GameplayStatics.get_all_actors_of_class(w,u.GolemSparring)):return
            if v.tower_floor.floor==5:
                check('Floor 5 Boss exam cleared in save state',t.floor_cleared())
                return finish()
            portals=t.available_portals()
            check('Floor '+str(v.tower_floor.floor)+' offers Forward portal',any('FORWARD' in str(x).upper() for x in portals))
            target_portal=next(x for x in portals if 'FORWARD' in str(x).upper())
            state['prev_floor']=v.tower_floor.floor
            walk([t.portal_point(target_portal)],'run2_portal_interact')
            return

        if stage=='run2_portal_interact':
            pulse(w,'G');stage='run2_portal_arrived';stamp=now;return

        if stage=='run2_portal_arrived':
            if v.tower_floor.floor<=state['prev_floor']:
                if now-stamp<5:return
                raise AssertionError('Failed to advance via portal: '+t.last_message)
            walk([center(t,1),center(t,2),t.guardian_point()],'run2_guardian_wait')
            return

    except Exception:
        finish(traceback.format_exc())

try:
    q=r/'Scripts/setup_tower_expedition.py';exec(compile(q.read_text(),str(q),'exec'),{'__name__':'__main__'})
    e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(x for x in e.get_all_level_actors() if isinstance(x,u.VillageRuntime));v.set_editor_property('construction_save_slot',slot)
    write();handle=u.register_slate_post_tick_callback(tick)
except Exception:
    finish(traceback.format_exc())
