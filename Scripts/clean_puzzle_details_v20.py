import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for kind in ['House','HouseVar']:
 ft=unreal.load_asset(R+'/Foliage/FT_Continent17_'+kind)
 if ft:unreal.InstancedFoliageActor.remove_all_instances(w,ft)
ft=unreal.load_asset(R+'/Foliage/FT_Continent17_Cliff')
if ft:
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);mesh=ft.get_editor_property('mesh');bb=mesh.get_bounding_box();transforms=[]
 for x,y,z,h,yaw in json.loads((B/'Saved/AdventureWorldSource/continent_cliffs_v17.json').read_text()):
  if x*x+y*y<1200**2:continue
  scale=h*100/(bb.max.z-bb.min.z);transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100-bb.min.z*scale-h*18),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(scale,scale,scale)))
 if transforms:unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
ft=unreal.load_asset(R+'/Foliage/FT_PuzzleTalus19')
if ft:unreal.InstancedFoliageActor.remove_all_instances(w,ft)
T=unreal.AssetToolsHelpers.get_asset_tools()
name='SM_IV_ContinentWater_v20';t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource'/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
M=unreal.MaterialEditingLibrary
path=R+'/Materials/M_IV_ContinentWater20'
mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_IV_ContinentWater20',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
M.delete_all_material_expressions(mat)
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition)
n=M.create_material_expression(mat,unreal.MaterialExpressionCustom)
pin=unreal.CustomInput();pin.set_editor_property('input_name','P');n.set_editor_property('inputs',[pin]);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
n.set_editor_property('code','float2 p=P.xy/100.;float v=.5+.5*sin(p.x*.009+sin(p.y*.013))*sin(p.y*.016);return float3(.018,.115,.145)+v*float3(.004,.009,.01);')
M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if 'IVContinentWater17' in [str(t) for t in a.tags]:
  a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_location(unreal.Vector(0,0,0),False,False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
