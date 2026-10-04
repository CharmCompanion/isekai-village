import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
p=R+'/Materials/M_IV_FoothillRock';mat=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset(R+'/Materials/M_IV_CaveStone',p)
old=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
if not any(isinstance(n,unreal.MaterialExpressionCustom) and 'mossAmount' in n.get_editor_property('code') for n in M.get_material_expressions(mat)):
 normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in ['C','N','P']:
  pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
 n.set_editor_property('inputs',pins);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);n.set_editor_property('code','float mossAmount=smoothstep(.28,.8,N.z)*(1-smoothstep(9000.,23000.,P.z))*(.65+.35*sin(P.x/1700.)*cos(P.y/2100.));return lerp(C*float3(.68,.72,.70),C*float3(.30,.53,.22),mossAmount);');M.connect_material_expressions(old,'',n,'C');M.connect_material_expressions(normal,'',n,'N');M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
M.recompile_material(mat);A.save_loaded_asset(mat);count=0
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  m=a.static_mesh_component.static_mesh;f=str(a.get_folder_path())
  if m and '/SoStylized/Environment/Rocks/' in m.get_path_name() and f.startswith('Nature/'):
   for i in range(a.static_mesh_component.get_num_materials()):a.static_mesh_component.set_material(i,mat)
   count+=1
 if isinstance(a,unreal.SkyLight):
  c=a.get_component_by_class(unreal.SkyLightComponent);c.set_editor_property('intensity',2.6);c.recapture_sky()
for kind in ['Rocks','Talus']:
 ft=unreal.load_asset(R+'/Foliage/FT_R08_'+kind);ft.set_editor_property('override_materials',[mat]);A.save_loaded_asset(ft)
landmat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
for n in M.get_material_expressions(landmat):
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  if 'farmSoil' in code:n.set_editor_property('code',code.replace('float3(.64,.72,.80),float3(.86,.85,.81)','float3(.40,.47,.46),float3(.58,.62,.64)'))
M.recompile_material(landmat);A.save_loaded_asset(landmat);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/mountain_blend_result.json').write_text(json.dumps({'saved':True,'existing_rock_actors_blended':count,'ground_rocks_moss_layer':True}))
