import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);p=R+'/Materials/MI_IV_BedrockSurface';mat=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset(R+'/Materials/MI_IV_HeroFracture',p);M.set_material_instance_scalar_parameter_value(mat,'Normal Flatness',.35);M.set_material_instance_scalar_parameter_value(mat,'Moss Multiply',0.);M.set_material_instance_scalar_parameter_value(mat,'Grass Offset',-100.);A.save_loaded_asset(mat)
for a in E.get_all_level_actors():
 if a.get_actor_label()=='Fractured island bedrock - hard geological faces':a.static_mesh_component.set_material(0,mat)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();exec(compile((B/'Scripts/render_rockrim_v10.py').read_text(),'render','exec'),{'__name__':'__main__'})
