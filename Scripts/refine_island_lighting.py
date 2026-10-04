import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
mat=A.duplicate_asset(R+'/Materials/M_IV_IslandRock',R+'/Materials/M_IV_FracturedIsland') if not A.does_asset_exist(R+'/Materials/M_IV_FracturedIsland') else unreal.load_asset(R+'/Materials/M_IV_FracturedIsland')
old=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
em=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);em.set_editor_property('const_b',.38);M.connect_material_expressions(old,'',em,'A');M.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat)
d=[]
for a in E.get_all_level_actors():
 f=str(a.get_folder_path());l=a.get_actor_label()
 if f=='Archived/Blob Clouds':a.static_mesh_component.set_visibility(False,True)
 if l=='SoStylized illustrated cloud horizon':
  a.static_mesh_component.set_visibility(False,True);a.set_actor_hidden_in_game(True)
  d.append({'cloud_dome_blend':str(a.static_mesh_component.get_material(0).get_base_material().get_editor_property('blend_mode'))})
 if f=='Refinement/Underside' or l=='SM_IV_FloatingUnderside':
  for slot in range(a.static_mesh_component.get_num_materials()):a.static_mesh_component.set_material(slot,mat)
 if isinstance(a,unreal.SkyLight):
  c=a.get_component_by_class(unreal.SkyLightComponent);c.set_editor_property('intensity',1.7);c.recapture_sky()
 if isinstance(a,unreal.ExponentialHeightFog):a.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_density',.000025)
(B/'Saved/refinement_lighting_audit.json').write_text(json.dumps(d,indent=2))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/refine_forest_floor.py').read_text(),str(B/'Scripts/refine_forest_floor.py'),'exec'),{'__name__':'__main__'})
