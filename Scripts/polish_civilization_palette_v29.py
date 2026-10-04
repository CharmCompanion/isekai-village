"""Regional native-material variants, maintaining original pack assets."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
data=json.loads((S/'civilization_instances_v29.json').read_text());sites=json.loads((S/'world_design_v29.json').read_text())['settlements'];counts={}
def place(key,mesh,rows):
 path=R+'/Foliage/Civilizations/FT_Civ29_'+key;ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_Civ29_'+key,R+'/Foliage/Civilizations',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',mesh);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));A.save_loaded_asset(ft);unreal.InstancedFoliageActor.remove_all_instances(W,ft)
 if rows:unreal.InstancedFoliageActor.add_instances(W,ft,[unreal.Transform(location=unreal.Vector(p[0]*100,p[1]*100,p[2]*100),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*p[3:6])) for p in rows])
 counts[key]=len(rows)
for key,tex in [('HouseA','04'),('HouseB','09')]:
 original=unreal.load_asset(data['assets'][key]);place(key,original,[])
 for culture,tint in [('religious',(1.04,1.02,.95)),('arcane',(.79,1.02,1.15)),('farming',(1.12,1.03,.87))]:
  rows=[p for p in data['instances'][key] if ('religious' if sites[p[7]]['culture']=='citadel' else sites[p[7]]['culture'])==culture]
  name='M_Civ29_'+key+'_'+culture;path=R+'/Materials/Civilizations/'+name;mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials/Civilizations',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
  diffuse=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);diffuse.set_editor_property('texture',unreal.load_asset('/Game/AdvancedVillagePack/Textures/T_Pack_'+tex+'_D'));diffuse.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
  node=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','C');node.set_editor_property('inputs',[pin]);node.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);node.set_editor_property('code',f'return pow(max(C,.003),.68)*float3({tint[0]},{tint[1]},{tint[2]})*1.10;');M.connect_material_expressions(diffuse,'RGB',node,'C');M.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
  em=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);M.connect_material_expressions(node,'',em,'A');em.set_editor_property('const_b',.16);M.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  rough=M.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.83);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);A.save_loaded_asset(mat)
  mp=R+'/Meshes/Civilizations/SM_Civ29_'+key+'_'+culture;mesh=unreal.load_asset(mp) if A.does_asset_exist(mp) else A.duplicate_asset(original.get_path_name(),mp);mesh.set_material(0,mat);A.save_loaded_asset(mesh);place(key+'_'+culture,mesh,rows)
# Cult enclaves use dark fabric and dark stone; caravans retain their canvas tents.
for key in ['Tent','SM_Civ29_Bastion']:
 original=unreal.load_asset(data['assets'][key]);cult=[p for p in data['instances'][key] if p[7] is not None and sites[p[7]]['culture']=='cult'];others=[p for p in data['instances'][key] if p not in cult];place(key,original,others)
 mp=R+'/Meshes/Civilizations/SM_Civ29_Cult_'+key;mesh=unreal.load_asset(mp) if A.does_asset_exist(mp) else A.duplicate_asset(original.get_path_name(),mp)
 for i,slot in enumerate(mesh.static_materials):
  if key=='Tent' and i>0:continue
  name='darkstone' if key!='Tent' else 'crimson';mesh.set_material(i,unreal.load_asset(R+'/Materials/Civilizations/M_Civ29_'+name))
 A.save_loaded_asset(mesh);place('Cult_'+key,mesh,cult)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(B/'Saved/civilization_palette_v29.json').write_text(json.dumps(counts,indent=2))
