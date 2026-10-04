import unreal,json,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
report={}
def log(stage):report['stage']=stage;(B/'Saved/rockrim_apply_result.json').write_text(json.dumps(report,indent=2))
def texture(name):
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.png'));t.destination_path=R+'/Textures';t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True;T.import_asset_tasks([t]);a=unreal.load_asset(t.destination_path+'/'+name)
 for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:a.set_editor_property(k,v)
 A.save_loaded_asset(a);return a
log('Raising native natural boundary')
ht=texture('T_IV_RockRimHeight_RG');biome=texture('T_IV_Biome_RockRim_v10');land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.);c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(ht,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
lm=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
for n in M.get_material_expressions(lm):
 if isinstance(n,unreal.MaterialExpressionTextureSample):
  tex=n.get_editor_property('texture')
  if tex and 'Biome' in tex.get_name():n.set_editor_property('texture',biome)
M.recompile_material(lm);A.save_loaded_asset(lm)
log('Importing hard fracture normals')
for a in E.get_all_level_actors():
 if 'IVOrganic09' in [str(t) for t in a.tags]:
  a.set_folder_path('Archived/Organic Bedrock v09');a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True)
 if 'IVRockRim10' in [str(t) for t in a.tags]:E.destroy_actor(a)
name='SM_IV_FractureBedrock_v10';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
p=R+'/Materials/M_IV_CrackedBedrock_v10';mat=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset(R+'/Materials/M_IV_CaveStone',p)
def node(cls,**props):
 n=M.create_material_expression(mat,cls)
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def custom(code,inputs,typ):
 pins=[]
 for k in inputs:
  p=unreal.CustomInput();p.set_editor_property('input_name',k);pins.append(p)
 n=node(unreal.MaterialExpressionCustom,code=code,inputs=pins,output_type=typ)
 for k,(v,o) in inputs.items():M.connect_material_expressions(v,o,n,k)
 return n
nodes=M.get_material_expressions(mat);pos=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionWorldPosition));normal=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionVertexNormalWS))
if not any(isinstance(n,unreal.MaterialExpressionCustom) and 'Bedrock10' in n.get_editor_property('code') for n in nodes):
 base=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
 for n in nodes:
  if isinstance(n,unreal.MaterialExpressionCustom):n.set_editor_property('code',n.get_editor_property('code').replace('/400.','/1500.'))
 col=custom('/*Bedrock10*/ float layer=.8+.12*sin((P.z+.25*P.x-.15*P.y)/1900.+sin(P.x/4200.));return C*layer*float3(.83,.81,.75);',{'C':(base,''),'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT3);M.connect_material_property(col,'',unreal.MaterialProperty.MP_BASE_COLOR)
 emiss=node(unreal.MaterialExpressionMultiply,const_b=.10);M.connect_material_expressions(col,'',emiss,'A');M.connect_material_property(emiss,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 samples=[]
 for plane in ['xy','xz','yz']:
  uv=custom('return P.'+plane+'/1300.;',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT2);sample=node(unreal.MaterialExpressionTextureSample,texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Classic/T_RockClassicCliffs_N'),sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);M.connect_material_expressions(uv,'',sample,'UVs');samples.append(sample)
 detail=custom('float3 w=pow(abs(N),5);w/=max(dot(w,1),.001);float3 nx=float3(C.z*sign(N.x),C.x,C.y);float3 ny=float3(B.x,B.z*sign(N.y),B.y);float3 nz=float3(A.x,A.y,A.z*sign(N.z));return normalize(lerp(N,normalize(nx*w.x+ny*w.y+nz*w.z),.42));',{'N':(normal,''),'A':(samples[0],'RGB'),'B':(samples[1],'RGB'),'C':(samples[2],'RGB')},unreal.CustomMaterialOutputType.CMOT_FLOAT3);mat.set_editor_property('tangent_space_normal',False);M.connect_material_property(detail,'',unreal.MaterialProperty.MP_NORMAL)
M.recompile_material(mat);A.save_loaded_asset(mat)
a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_label('Fractured island bedrock - hard geological faces');a.set_folder_path('Floating Island/Fractured Bedrock');a.tags=[unreal.Name('IVRockRim10')]
# Native foliage updates preserve type ownership even where multiple types share one mesh.
log('Regrounding vegetation on raised rim')
new=struct.unpack('<'+'H'*1009**2,(S/'IV_RockRim_v10.r16').read_bytes());old=struct.unpack('<'+'H'*1009**2,(S/'IV_RimPrevious_v10.r16').read_bytes())
def height(raw,x,y):
 i=max(0,min(1008,round((x+600)*.84)));j=max(0,min(1008,round((y+600)*.84)));return (raw[j*1009+i]-32768)/64
moved=0;removed=0
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
 ft=unreal.load_asset(path)
 if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
 mesh=ft.get_editor_property('mesh');before=[]
 for actor in E.get_all_level_actors():
  if isinstance(actor,unreal.InstancedFoliageActor):
   for comp in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
    if comp.static_mesh==mesh:before.append((comp,[comp.get_instance_transform(i,world_space=True) for i in range(comp.get_instance_count())]))
 if not before:continue
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);own=[]
 for comp,transforms in before:
  if not unreal.SystemLibrary.is_valid(comp) or comp.get_instance_count()==0:own.extend(transforms)
 kept=[]
 for tf in own:
  p=tf.translation;x=p.x/100;y=p.y/100;delta=height(new,x,y)-height(old,x,y)
  if abs(delta)>.25:
   slope=math.hypot(height(new,x+2,y)-height(new,x-2,y),height(new,x,y+2)-height(new,x,y-2))/4
   if slope>1.15:removed+=1;continue
   tf.translation=unreal.Vector(p.x,p.y,p.z+delta*100);moved+=1
  kept.append(tf)
 if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
report.update(vegetation_regrounded=moved,vegetation_removed_from_steep_scarp=removed)
unreal.SystemLibrary.execute_console_command(w,'RecreateLandscapeCollision');unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();log('saved')
