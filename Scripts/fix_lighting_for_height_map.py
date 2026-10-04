import unreal

def fix_level_lighting():
    maps = [
        "/Game/SpellCraft/Maps/Height",
        "/Game/SpellCraft/Maps/Map_IslandSanctum"
    ]

    for m in maps:
        if not unreal.EditorAssetLibrary.does_asset_exist(m):
            continue

        print(f"Fixing lighting in {m}...")
        unreal.EditorLevelLibrary.load_level(m)
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

        has_sun = False
        has_skylight = False
        has_atmos = False

        for act in all_actors:
            if isinstance(act, unreal.DirectionalLight):
                has_sun = True
                sun_comp = act.get_component_by_class(unreal.DirectionalLightComponent)
                if sun_comp:
                    sun_comp.set_editor_property("intensity", 8.0)
                    sun_comp.set_editor_property("atmosphere_sun_light", True)
            elif isinstance(act, unreal.SkyLight):
                has_skylight = True
                sl_comp = act.get_component_by_class(unreal.SkyLightComponent)
                if sl_comp:
                    sl_comp.set_editor_property("real_time_capture", True)
            elif isinstance(act, unreal.SkyAtmosphere):
                has_atmos = True

        if not has_sun:
            sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 10000), unreal.Rotator(-45, -35, 0))
            if sun:
                sun_comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
                if sun_comp:
                    sun_comp.set_editor_property("intensity", 8.0)
                    sun_comp.set_editor_property("light_color", unreal.Color(255, 248, 235, 255))
                    sun_comp.set_editor_property("atmosphere_sun_light", True)
            print("Spawned Sun Directional Light!")

        if not has_skylight:
            sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, 0, 0))
            if sl:
                sl_comp = sl.get_component_by_class(unreal.SkyLightComponent)
                if sl_comp:
                    sl_comp.set_editor_property("real_time_capture", True)
            print("Spawned SkyLight!")

        if not has_atmos:
            unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))

        unreal.EditorLevelLibrary.save_current_level()
        print(f"Saved lighting for {m} successfully!")

if __name__ == "__main__":
    fix_level_lighting()
