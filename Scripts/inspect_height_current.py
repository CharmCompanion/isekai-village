import unreal

MAP = "/Game/SpellCraft/Maps/Height"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
print(f"=== HEIGHT ({len(actors)} actors) ===")
for act in actors:
    cls = act.get_class().get_name()
    loc = act.get_actor_location()
    scale = act.get_actor_scale3d()
    if isinstance(act, unreal.Landscape):
        mat = act.get_editor_property("landscape_material")
        print(f"Landscape: loc={loc} scale={scale} mat={mat.get_name() if mat else None}")
        try:
            print(f"  layers={act.get_target_layer_names()}")
            print(f"  grass={act.get_grass_enabled()}")
        except Exception as e:
            print(f"  meta err: {e}")
    elif isinstance(act, unreal.StaticMeshActor):
        comp = act.get_component_by_class(unreal.StaticMeshComponent)
        mesh = comp.get_static_mesh() if comp else None
        print(f"StaticMesh: {mesh.get_name() if mesh else '?'} at {loc} scale {scale}")
    elif isinstance(act, unreal.DirectionalLight) or "Water" in cls or "Sky" in cls or "RVT" in cls or isinstance(act, unreal.RuntimeVirtualTextureVolume):
        print(f"{cls}: {act.get_name()} at {loc}")
