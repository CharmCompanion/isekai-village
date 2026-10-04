import unreal
R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;path=R+'/Materials/M_IV_SculptedGeology28'
mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(R+'/Materials/M_IV_JoinedGeology_v13',path)
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code').replace('normalize(nx*w.x+ny*w.y+nz*w.z),.20)','normalize(nx*w.x+ny*w.y+nz*w.z),.12)');n.set_editor_property('code',code)
for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,.74),(unreal.MaterialProperty.MP_SPECULAR,.20)]:
 n=M.create_material_expression(mat,unreal.MaterialExpressionConstant);n.set_editor_property('r',value);M.connect_material_property(n,'',prop)
M.recompile_material(mat);A.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_JoinedMountain_v28':a.static_mesh_component.set_material(0,mat)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
