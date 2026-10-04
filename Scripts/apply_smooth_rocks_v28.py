import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
sources=json.loads((B/'Saved/rock_sources_v28.json').read_text());mapping={};report={}
for oldname,q in sources.items():
 old=unreal.load_asset(q['path']);name=oldname+'_Smooth28';path=R+'/Meshes/Refinement/'+name
 if not A.does_asset_exist(path):assert A.duplicate_asset(q['path'],path)
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);m=unreal.load_asset(path)
 m.set_editor_property('static_materials',list(old.static_materials));bs=SS.get_lod_build_settings(m,0);bs.recompute_normals=False;bs.use_high_precision_tangent_basis=True;SS.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m)
 bb=m.get_bounding_box();actual=[bb.min.x,bb.min.y,bb.min.z,bb.max.x,bb.max.y,bb.max.z];expected=q['min']+q['max'];err=max(abs(a-b) for a,b in zip(actual,expected));assert err<1.,(name,actual,expected)
 mapping[old.get_path_name()]=m;report[name]={'bounds_error_cm':err,'actors':0,'instances':0}
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  old=c.static_mesh
  if not old or old.get_path_name() not in mapping:continue
  new=mapping[old.get_path_name()];c.set_static_mesh(new)
  key='instances' if isinstance(c,unreal.InstancedStaticMeshComponent) else 'actors';report[new.get_name()][key]+=c.get_instance_count() if key=='instances' else 1
for path in A.list_assets(R+'/Foliage',recursive=True):
 ft=unreal.load_asset(path)
 if isinstance(ft,unreal.FoliageType_InstancedStaticMesh):
  old=ft.get_editor_property('mesh')
  if old and old.get_path_name() in mapping:ft.set_editor_property('mesh',mapping[old.get_path_name()]);A.save_loaded_asset(ft)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/smooth_rock_assets_applied_v28.json').write_text(json.dumps(report,indent=2))
