import unreal,json
from pathlib import Path
R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
mask=next(n for n in M.get_material_expressions(mat) if isinstance(n,unreal.MaterialExpressionCustom) and 'atan2' in n.get_editor_property('code'))
M.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK);M.recompile_material(mat);A.save_loaded_asset(mat);land.set_editor_property('landscape_material',mat);land.set_editor_property('landscape_hole_material',mat)
stone=A.duplicate_asset(R+'/Materials/M_IV_CaveStone',R+'/Materials/M_IV_IslandRock') if not A.does_asset_exist(R+'/Materials/M_IV_IslandRock') else unreal.load_asset(R+'/Materials/M_IV_IslandRock')
for n in M.get_material_expressions(stone):
 if isinstance(n,unreal.MaterialExpressionCustom) and '0.72,0.78,0.83' in n.get_editor_property('code'):n.set_editor_property('code',n.get_editor_property('code').replace('0.72,0.78,0.83','0.28,0.36,0.43'))
stone.set_editor_property('used_with_nanite',True);M.recompile_material(stone);A.save_loaded_asset(stone)
for a in E.get_all_level_actors():
 if a.get_actor_label()=='SM_IV_FloatingUnderside':a.static_mesh_component.set_material(0,stone)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/landscape_api.json').write_text(json.dumps({'methods':[m for m in dir(land) if any(k in m for k in ['collision','layer','weight','render'])],'classes':[m for m in dir(unreal) if 'Landscape' in m and 'Subsystem' in m]},indent=2))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
