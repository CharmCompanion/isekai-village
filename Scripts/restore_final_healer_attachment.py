import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
item=next(i for i in json.loads((r/'ArtSource/Golems/HandheldEquipment/manifest.json').read_text())['HealerUnderlay'] if i['name']=='Healer_Linen_Pelvis')
t=u.AssetImportTask();t.filename=item['file'];t.destination_path=base+'/Equipment/Handheld';t.destination_name='SM_'+item['name'];t.automated=True;t.save=True;t.replace_existing=True;t.factory=u.FbxFactory()
o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.import_as_skeletal=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;t.options=o
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=next(u.load_asset(p) for p in t.imported_object_paths if isinstance(u.load_asset(p),u.StaticMesh));mat=u.load_asset(base+'/Materials/MI_HealerLinen')
for i in range(len(mesh.get_editor_property('static_materials'))):mesh.set_material(i,mat)
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 1')
for name in ['setup_corrected_equipment.py','check_final_hand_setup.py']:
 p=r/'Scripts'/name;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
