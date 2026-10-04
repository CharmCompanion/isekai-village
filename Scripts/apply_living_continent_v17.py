import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def progress(stage,**kw):(B/'Saved/living_continent_result.json').write_text(json.dumps(dict(stage=stage,**kw),indent=2))
progress('importing')
name='SM_IV_LivingContinent_v17';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
ss=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);bs=ss.get_lod_build_settings(mesh,0);bs.recompute_normals=False;ss.set_lod_build_settings(mesh,0,bs);A.save_loaded_asset(mesh)
t=unreal.AssetImportTask();t.filename=str(S/'T_IV_ContinentAtlas17.png');t.destination_path=R+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;T.import_asset_tasks([t]);tex=unreal.load_asset(R+'/Textures/T_IV_ContinentAtlas17');tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(tex)
path=R+'/Materials/M_IV_LivingContinent_v17';mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_IV_LivingContinent_v17',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
def custom(code,output,pins):
 node=M.create_material_expression(mat,unreal.MaterialExpressionCustom);inputs=[]
 for key,(obj,out) in pins.items():
  pin=unreal.CustomInput();pin.set_editor_property('input_name',key);inputs.append(pin)
 node.set_editor_property('inputs',inputs);node.set_editor_property('output_type',output);node.set_editor_property('code',code)
 for key,(obj,out) in pins.items():M.connect_material_expressions(obj,out,node,key)
 return node
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS)
uv=custom('return (P.xy/100.+8000.)/16000.;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'P':(pos,'')})
sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);sample.set_editor_property('texture',tex);sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);M.connect_material_expressions(uv,'',sample,'UVs')
t=unreal.AssetImportTask();t.filename=str(S/'T_IV_ContinentFar17.png');t.destination_path=R+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;T.import_asset_tasks([t]);fartex=unreal.load_asset(R+'/Textures/T_IV_ContinentFar17')
for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('never_stream',True),('address_x',unreal.TextureAddress.TA_WRAP),('address_y',unreal.TextureAddress.TA_WRAP)]:fartex.set_editor_property(k,v)
A.save_loaded_asset(fartex)
farsample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);farsample.set_editor_property('texture',fartex);farsample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);M.connect_material_expressions(uv,'',farsample,'UVs')
color=custom('float shade=.48+.52*saturate(dot(normalize(N),normalize(float3(-.6,-.4,1.))));float far=smoothstep(5500.,7500.,length(P.xy/100.));float3 distant=lerp(F,float3(.10,.18,.085),.3);return lerp(C,distant,far)*shade;',unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'P':(pos,''),'N':(normal,''),'C':(sample,'RGB'),'F':(farsample,'RGB')})
M.connect_material_property(color,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);M.recompile_material(mat);A.save_loaded_asset(mat)
count=0
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  m=a.static_mesh_component.static_mesh
  if m and m.get_name() in ['SM_IV_OriginContinent_v16',name] and a.static_mesh_component.is_visible():
   a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_label('Living continent - woodland watershed and fractured birthplace');a.set_actor_enable_collision(False);count+=1
assert count==1,count
progress('planting native asset forests')
rows=json.loads((S/'living_continent_v17_instances.json').read_text());P='/Game/SoStylized/Environment/'
assets={'Oak':P+'Trees/Oak/SM_OakTree2','OakVar':P+'Trees/Oak/SM_OakTree4','Pine':P+'Trees/Pine/SM_Pine01','Rocks':P+'Rocks/Spire/SM_RockSpire_RockClump02','House':'/Game/AdvancedVillagePack/Meshes/SM_House_Var01','HouseVar':'/Game/AdvancedVillagePack/Meshes/SM_House_Var02'}
counts={}
for kind,positions in rows.items():
 path=R+'/Foliage/FT_Continent17_'+kind
 ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_Continent17_'+kind,R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
 m=unreal.load_asset(assets[kind]);assert m,kind
 ft.set_editor_property('mesh',m);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));ft.set_editor_property('cast_shadow',False);A.save_loaded_asset(ft)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 bounds=m.get_bounding_box();height=max(bounds.max.z-bounds.min.z,1);transforms=[]
 for x,y,z,h,yaw in positions:
  s=h*100/height
  transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100-bounds.min.z*s),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)))
 if transforms:unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
 counts[kind]=len(transforms);progress('dressing '+kind,counts=counts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();progress('saved',counts=counts)
exec(compile((B/'Scripts/final_continent_material_v17.py').read_text(),'final continental material','exec'),{'__name__':'__main__'})
