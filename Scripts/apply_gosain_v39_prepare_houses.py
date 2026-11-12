import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';R='/Game/IsekaiVillage/AdventureWorld/Gosain39/VerifiedMeshes'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
results=[]
for kit in json.loads((O/'native_house_kits.json').read_text()):
    name='SM_Gosain39_House_'+kit['name'];path=R+'/'+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        m=unreal.load_asset(path)
    else:
        actors=[];merged=None
        try:
            for part in kit['parts']:
                a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*part['position']),unreal.Rotator(pitch=part['rotation'][0],yaw=part['rotation'][1],roll=part['rotation'][2]),transient=True)
                a.static_mesh_component.set_static_mesh(unreal.load_asset(part['mesh']));a.set_actor_scale3d(unreal.Vector(*part['scale']))
                for i,mat in enumerate(part['materials']):
                    if mat:a.static_mesh_component.set_material(i,unreal.load_asset(mat))
                actors.append(a)
            opts=unreal.MergeStaticMeshActorsOptions();opts.base_package_name=path;opts.destroy_source_actors=False;opts.spawn_merged_actor=True
            settings=opts.mesh_merging_settings;settings.generate_light_map_uv=False;settings.merge_materials=False;opts.mesh_merging_settings=settings
            merged=SS.merge_static_mesh_actors(actors,opts);assert merged,name
            m=merged.static_mesh_component.static_mesh;unreal.EditorAssetLibrary.save_loaded_asset(m)
        finally:
            if merged:E.destroy_actor(merged)
            for a in actors:E.destroy_actor(a)
    b=m.get_bounding_box()
    results.append({'name':kit['name'],'path':m.get_path_name(),'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]})
    (O/'merged_house_assets.json').write_text(json.dumps(results,indent=2))

