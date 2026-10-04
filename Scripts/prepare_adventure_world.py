import unreal
PATH='/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure'
lev=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(PATH):
    lev.load_level(PATH)
else:
    assert lev.new_level(PATH)
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun=sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,5000),unreal.Rotator(-38,-35,0))
    sun.set_actor_label('Sun - Warm Coastal Morning')
    c=sun.get_component_by_class(unreal.DirectionalLightComponent)
    c.set_editor_property('intensity',5.0)
    c.set_editor_property('atmosphere_sun_light',True)
    sub.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector())
    sky=sub.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500))
    sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property('real_time_capture',True)
    fog=sub.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(0,0,0))
    fog.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_density',.0015)
    lev.save_current_level()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(0,-90000,65000),unreal.Rotator(-40,90,0))
