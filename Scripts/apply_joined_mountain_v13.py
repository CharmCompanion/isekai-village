import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);T=unreal.AssetToolsHelpers.get_asset_tools()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
name='SM_IV_JoinedMountain_v13';task=unreal.AssetImportTask();task.filename=str(S/(name+'.obj'));task.destination_path=R+'/Meshes/Refinement';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(task.destination_path+'/'+name);sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);bs=sub.get_lod_build_settings(mesh,0);bs.recompute_normals=False;bs.recompute_tangents=True;sub.set_lod_build_settings(mesh,0,bs);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
path=R+'/Materials/M_IV_JoinedGeology_v13';mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(R+'/Materials/M_IV_MountainGeology_v12',path)
nodes=M.get_material_expressions(mat)
for n in nodes:
 if isinstance(n,unreal.MaterialExpressionCustom):n.set_editor_property('code',n.get_editor_property('code').replace('/400.','/9500.'))
base=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);pos=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionWorldPosition));normal=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionVertexNormalWS))
def node(cls,**props):
 n=M.create_material_expression(mat,cls)
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def custom(code,inputs,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
 pins=[]
 for k in inputs:
  pin=unreal.CustomInput();pin.set_editor_property('input_name',k);pins.append(pin)
 n=node(unreal.MaterialExpressionCustom,code=code,inputs=pins,output_type=typ)
 for k,(src,out) in inputs.items():M.connect_material_expressions(src,out,n,k)
 return n
if not any(isinstance(n,unreal.MaterialExpressionCustom) and 'Mountain12' in n.get_editor_property('code') for n in nodes):
 uv=node(unreal.MaterialExpressionTextureCoordinate)
 mapuv=custom('return (P.xy+60000.)/120000.;',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
 ht=node(unreal.MaterialExpressionTextureSample,texture=unreal.load_asset(R+'/Textures/T_IV_DishHeight_RG'),sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
 M.connect_material_expressions(mapuv,'',ht,'UVs')
 code='''/*Mountain12*/
 float3 q=P/13000.;float3 i=floor(q);float3 f=frac(q);f=f*f*(3-2*f);float n=0;
 for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
 float3 c=float3(x,y,z);float h=frac(sin(dot(i+c,float3(127.1,311.7,74.7)))*43758.5453);
 float3 w=lerp(1-f,f,c);n+=h*w.x*w.y*w.z;}
 float valley=saturate(U.x);float3 rock=C*float3(.83,.84,.80)*lerp(.78,1.05,n)*(1-.20*valley);
 float height=(H.r*65280.+H.g*255.-32768.)/64.*100.;
 float below=max(0,height-P.z);
 float soil=(1-smoothstep(70.,460.,below))*(.5+.5*n);
 return lerp(rock,rock*float3(.72,.62,.40),soil);
 '''
 c=custom(code,{'C':(base,''),'P':(pos,''),'N':(normal,''),'U':(uv,''),'H':(ht,'RGB')});M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 glow=custom('return C*.055;',{'C':(c,'')});M.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
# Existing pack's painted spire palette, projected at human-readable scales.
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionTextureSample):
  tex=n.get_editor_property('texture')
  if tex and 'T_RockClassic_Rocks_BC' in tex.get_name():n.set_editor_property('texture',unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC'))
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code').replace('/9500.','/4500.').replace('float3(.83,.84,.80)','float3(.94,.90,.83)')
  n.set_editor_property('code',code)
if not any(isinstance(n,unreal.MaterialExpressionCustom) and 'JoinedRockDetail' in n.get_editor_property('code') for n in M.get_material_expressions(mat)):
 ns=[]
 for axes in ['xy','xz','yz']:
  coord=custom('return P.'+axes+'/1800.;',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
  tex=node(unreal.MaterialExpressionTextureSample,texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_N'),sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
  M.connect_material_expressions(coord,'',tex,'UVs');ns.append(tex)
 detail=custom('/*JoinedRockDetail*/ float3 w=pow(abs(N),5);w/=max(dot(w,1),.001);float3 nx=float3(C.z*sign(N.x),C.x,C.y);float3 ny=float3(B.x,B.z*sign(N.y),B.y);float3 nz=float3(A.x,A.y,A.z*sign(N.z));return normalize(lerp(N,normalize(nx*w.x+ny*w.y+nz*w.z),.20));',{'N':(normal,''),'A':(ns[0],'RGB'),'B':(ns[1],'RGB'),'C':(ns[2],'RGB')})
 mat.set_editor_property('tangent_space_normal',False);M.connect_material_property(detail,'',unreal.MaterialProperty.MP_NORMAL)
mat.set_editor_property('two_sided',False);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in E.get_all_level_actors():
 if 'IVOrbit12' in [str(t) for t in a.tags]:
  a.set_folder_path('Archived/Orbit Mountain v12');a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True)
 if 'IVDishPeak11' in [str(t) for t in a.tags]:
  a.set_folder_path('Archived/Inverted Peak v11');a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True)
 if 'IVJoined13' in [str(t) for t in a.tags]:E.destroy_actor(a)
a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_label('Inverted mountain - overlapping terrain join and relieved rock faces');a.set_folder_path('Floating Island/Inverted Mountain');a.tags=[unreal.Name('IVJoined13')]
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/join_apply_result.json').write_text(json.dumps({'saved':True,'terrain_unchanged':True,'mountain_mesh':mesh.get_path_name(),'material':mat.get_path_name()},indent=2))
exec(compile((B/'Scripts/render_join_review_v13.py').read_text(),'orbit render','exec'),{'__name__':'__main__'})
