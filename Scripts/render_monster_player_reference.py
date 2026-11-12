"""Render BodyA in a transient review world without saving project maps."""
import unreal,time,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/MonsterArtReference')
root.mkdir(parents=True,exist_ok=True)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
paths=['/Game/StylizedCharacters/BodyA/Body/SKM_BodyA','/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01']
rows=[]
for path in paths:
    mesh=unreal.load_asset(path)
    if not mesh:raise RuntimeError('Missing reference '+path)
    actor=E.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0))
    comp=actor.get_editor_property('skeletal_mesh_component')
    comp.set_skeletal_mesh_asset(mesh)
    rows.append({'mesh':path,'materials':[m.get_path_name() if m else None for m in comp.get_materials()]})
light=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(-35,-40,0))
light.get_editor_property('light_component').set_editor_property('intensity',10.)
fill=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,300),unreal.Rotator(-20,-130,0))
fill.get_editor_property('light_component').set_editor_property('intensity',6.)
fill.get_editor_property('light_component').set_editor_property('cast_shadows',False)
sky=E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,300))
sky.get_editor_property('light_component').set_editor_property('intensity',1.)
floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-2))
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'))
floor.set_actor_scale3d(unreal.Vector(10,10,1))
cam=E.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(280,500,125))
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),unreal.Vector(0,0,90)),False)
cam.get_editor_property('camera_component').set_editor_property('field_of_view',45.)
unreal.EditorLevelLibrary.pilot_level_actor(cam)
world=unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.SetRes 1400x1000w')
unreal.SystemLibrary.execute_console_command(world,'r.Streaming.PoolSize 2048')
unreal.SystemLibrary.execute_console_command(world,'r.EyeAdaptationQuality 0')
(root/'reference_materials.json').write_text(json.dumps(rows,indent=2))
started=time.monotonic()
stage=0
def tick(delta):
    global stage
    elapsed=time.monotonic()-started
    if elapsed>35 and stage==0:
        unreal.AutomationLibrary.take_high_res_screenshot(1400,1000,str(root/'BodyA_Reference.png'),camera=cam)
        stage=1
    elif elapsed>48 and stage==1:
        (root/'render_complete.json').write_text(json.dumps({'requested':True,'image':str(root/'BodyA_Reference.png')}))
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.execute_console_command(world,'QUIT_EDITOR')
handle=unreal.register_slate_post_tick_callback(tick)
