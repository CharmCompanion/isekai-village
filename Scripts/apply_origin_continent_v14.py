import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);T=unreal.AssetToolsHelpers.get_asset_tools()
name='SM_IV_OriginContinent_v14';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
ss=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);settings=ss.get_lod_build_settings(mesh,0);settings.recompute_normals=False;settings.recompute_tangents=True;ss.set_lod_build_settings(mesh,0,settings);A.save_loaded_asset(mesh)
path=R+'/Materials/M_IV_OriginContinent_v14';mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_IV_OriginContinent_v14',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
for key in ['P','N']:
 pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
n.set_editor_property('inputs',pins);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
n.set_editor_property('code','''float3 p=P/100.;
float2 q=float2(p.x/580.,(p.y-20.)/570.);float a=atan2(q.y,q.x);
float r=pow(pow(abs(q.x),4)+pow(abs(q.y),4),.25)/(1+.012*sin(7*a)+.008*sin(13*a));
float patch=saturate(.5+.22*sin(p.x/3700.+sin(p.y/4900.))*cos(p.y/2700.)+.12*sin((p.x+p.y)/1700.));
float altitude=saturate((p.z+7200.)/2750.);
float3 c=lerp(float3(.018,.065,.032),float3(.15,.23,.065),smoothstep(.30,.70,patch));
float slope=1-normalize(N).z;
c=lerp(c,float3(.22,.19,.145),max(smoothstep(.18,.48,slope),smoothstep(.4,.87,altitude))*.88);
c=lerp(c,float3(.43,.48,.48),smoothstep(.80,1.,altitude)*.65);
float riverx=5200.+2900.*sin(p.y/10500.)+900.*sin(p.y/4500.);
float river=1-smoothstep(85.,155.,abs(p.x-riverx));c=lerp(c,float3(.065,.25,.30),river);
float scar=1-smoothstep(1.32,1.87,r);
float depth=saturate((-p.z-6870.)/1050.);
float bedding=.90+.10*sin((p.z+.13*p.x-.08*p.y)/85.);
float3 stone=lerp(float3(.30,.24,.17),float3(.17,.20,.23),depth)*bedding;
c=lerp(c,stone,scar);
float shade=.22+.78*saturate(dot(normalize(float3(N.xy*2.5,N.z)),normalize(float3(-.85,-.45,.65))));
float farfade=smoothstep(18000.,45000.,length(p.xy));
return lerp(c*shade,float3(.075,.115,.10),farfade);
''')
M.connect_material_expressions(pos,'',n,'P');M.connect_material_expressions(normal,'',n,'N');M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',False);M.recompile_material(mat);A.save_loaded_asset(mat)
count=0
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  old=a.static_mesh_component.static_mesh
  if old and old.get_name() in ['SM_IV_DistantContinent','SM_IV_OriginContinent_v14'] and a.static_mesh_component.is_visible():
   a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_label('Continental birthplace - aligned mountain crescent and extraction hollow');a.set_actor_enable_collision(False);a.tags=list(a.tags)+[unreal.Name('IVOrigin14')];count+=1
assert count==1,count
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/origin_continent_result.json').write_text(json.dumps({'saved':True,'replaced_continents':count,'new_mesh':mesh.get_path_name()},indent=2))
exec(compile((B/'Scripts/render_valley_origin_v14.py').read_text(),'valley and origin views','exec'),{'__name__':'__main__'})
