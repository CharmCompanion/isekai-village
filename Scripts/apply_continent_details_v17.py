import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def material(name,texture=None,water=False):
 path=R+'/Materials/'+name;mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS)
 if water:
  source=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);out='';pin='P';code='float2 p=P.xy/100.;float rip=pow(saturate(.5+.5*sin(p.x*.9+sin(p.y*.55))),18.);return float3(.022,.29,.35)+rip*float3(.025,.045,.045);'
 else:
  source=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);source.set_editor_property('texture',unreal.load_asset(texture));out='RGB';pin='C';code='return C*(.5+.5*saturate(dot(normalize(N),normalize(float3(-.6,-.4,1.)))))*1.3;'
 node=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in [pin,'N']:
  p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 node.set_editor_property('inputs',pins);node.set_editor_property('code',code);node.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 assert M.connect_material_expressions(source,out,node,pin);assert M.connect_material_expressions(normal,'',node,'N');M.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
for kind,num in [('House','04'),('HouseVar','09')]:
 mat=material('M_IV_Continental'+kind,'/Game/AdvancedVillagePack/Textures/T_Pack_'+num+'_D')
 ft=unreal.load_asset(R+'/Foliage/FT_Continent17_'+kind);ft.set_editor_property('override_materials',[mat]);A.save_loaded_asset(ft)
 for a in E.get_all_level_actors():
  if isinstance(a,unreal.InstancedFoliageActor):
   for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
    if c.static_mesh==ft.get_editor_property('mesh'):c.set_material(0,mat)
name='SM_IV_ContinentWater_v17';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
a=next((a for a in E.get_all_level_actors() if 'IVContinentWater17' in [str(v) for v in a.tags]),None)
if not a:a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.tags=[unreal.Name('IVContinentWater17')]
a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,material('M_IV_ContinentWater17',water=True));a.set_actor_enable_collision(False);a.set_actor_label('Continental lake and flowing river');a.set_folder_path('ContinentalWorld/Water')
name='FT_Continent17_Cliff';path=R+'/Foliage/'+name
ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
mesh=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Rock03');assert mesh
ft.set_editor_property('mesh',mesh);ft.set_editor_property('cast_shadow',False);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));A.save_loaded_asset(ft)
unreal.InstancedFoliageActor.remove_all_instances(w,ft);bb=mesh.get_bounding_box();transforms=[]
for x,y,z,height,yaw in json.loads((S/'continent_cliffs_v17.json').read_text()):
 s=height*100/(bb.max.z-bb.min.z);transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100-bb.min.z*s-height*18),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)))
unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/continent_details_result.json').write_text(json.dumps({'saved':True,'rock_outcrops':len(transforms),'water_surface':True,'house_materials':2}))
exec(compile((B/'Scripts/render_living_continent_v17.py').read_text(),'review details','exec'),{'__name__':'__main__'})
