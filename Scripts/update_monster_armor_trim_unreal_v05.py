import unreal,json,builtins
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'ArtSource/Monsters/Models_v05'
holder=getattr(builtins,'iv_monster_capture_holder',None)
if holder:
    try:unreal.unregister_slate_post_tick_callback(holder['handle'])
    except:pass
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorLevelLibrary.eject_pilot_level_actor()
for actor in E.get_all_level_actors():
    if actor.get_actor_label()=='Monster review camera':E.destroy_actor(actor)
    elif isinstance(actor,unreal.SkeletalMeshActor):actor.set_is_temporarily_hidden_in_editor(False)
T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;SS=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
manifest=json.loads((S/'model_manifest.json').read_text());report=json.loads((B/'Saved/monster_import_v05.json').read_text())
assert report['stage']=='complete'
for name in ['SkeletonKnight','OgreChampion']:
    spec=next(m for m in manifest['models'] if m['id']==name);row=next(m for m in report['models'] if m['id']==name)
    mesh=unreal.load_asset(row['asset']);materials=list(mesh.get_editor_property('materials'));skeleton=mesh.get_editor_property('skeleton')
    op=unreal.FbxImportUI();op.automated_import_should_detect_type=False;op.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;op.import_as_skeletal=True;op.import_mesh=True;op.import_animations=False;op.import_materials=False;op.import_textures=False;op.create_physics_asset=False;op.skeleton=skeleton
    op.skeletal_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    task=unreal.AssetImportTask();task.filename=spec['fbx'];task.destination_path=row['asset'].split('.')[0].rsplit('/',1)[0];task.destination_name='SK_'+name;task.options=op;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
    mesh=unreal.load_asset(row['asset']);assert len(materials)==len(mesh.get_editor_property('materials'));mesh.set_editor_property('materials',materials)
    SS.regenerate_lod(mesh,3,False,False);A.save_loaded_asset(mesh)
    row['lod_vertices']=[SS.get_num_verts(mesh,i) for i in range(3)]
report['trim_alignment']='corrected and reimported SkeletonKnight/OgreChampion';(B/'Saved/monster_import_v05.json').write_text(json.dumps(report,indent=2))
exec(compile((B/'Scripts/render_monsters_unreal_v05.py').read_text(),'final v05 native views','exec'),{'__name__':'__main__'})
