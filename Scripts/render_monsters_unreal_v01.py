import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');out=B/'ArtSource/Monsters/Models_v01/Previews';out.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cam=E.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(0,900,240));cam.set_actor_label('Monster review camera');cam.get_editor_property('camera_component').set_editor_property('field_of_view',50.)
unreal.EditorLevelLibrary.pilot_level_actor(cam)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'viewmode lit');unreal.SystemLibrary.execute_console_command(world,'ShowFlag.Materials 1');unreal.SystemLibrary.execute_console_command(world,'r.EyeAdaptationQuality 0');unreal.SystemLibrary.execute_console_command(world,'r.Streaming.PoolSize 2048')
views=[('Slime_Unreal_v01',(0,900,240),(0,0,40)),('Skeleton_Unreal_v01',(0,1450,260),(0,400,100)),('Goblin_Unreal_v01',(0,1500,200),(0,850,70)),('Ogre_Unreal_v01',(0,2500,430),(0,1350,150))]
state={'index':0,'stage':'camera','next':time.monotonic()+15,'completed':[]};holder={}
def write():(B/'Saved/monster_render_v01.json').write_text(json.dumps(state,indent=2))
def tick(delta):
    if time.monotonic()<state['next']:return
    if state['index']>=len(views):
        
        for actor in E.get_all_level_actors():
            if isinstance(actor,unreal.SkeletalMeshActor):actor.set_is_temporarily_hidden_in_editor(False)
        state['stage']='complete';write();unreal.unregister_slate_post_tick_callback(holder['handle']);return
    name,eye,target=views[state['index']];path=out/(name+'.png')
    if state['stage']=='camera':
        family=name.split('_')[0]
        for actor in E.get_all_level_actors():
            if isinstance(actor,unreal.SkeletalMeshActor):actor.set_is_temporarily_hidden_in_editor(not actor.get_actor_label().startswith(family) and not (family=='Slime' and actor.get_actor_label().endswith('Slime')))
        a=unreal.Vector(*eye);cam.set_actor_location(a,False,False);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(a,unreal.Vector(*target)),False);state['next']=time.monotonic()+7;state['stage']='capture'
    elif state['stage']=='capture':
        state['mtime']=path.stat().st_mtime if path.exists() else 0;unreal.AutomationLibrary.take_high_res_screenshot(2000,1000,str(path),camera=cam,delay=.5);state['stage']='waiting';state['next']=time.monotonic()+2
    elif path.exists() and path.stat().st_mtime>state['mtime']:state['completed'].append(str(path));state['index']+=1;state['stage']='camera'
    else:state['next']=time.monotonic()+1
    write()
holder['handle']=unreal.register_slate_post_tick_callback(tick)

