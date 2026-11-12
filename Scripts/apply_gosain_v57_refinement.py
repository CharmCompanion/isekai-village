"""Fix native-review defects using private materials and an integrated mine landform."""
import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';D='/Game/IsekaiVillage/AdventureWorld/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
assert (O/'applied.json').exists() and not (O/'refinement_applied.json').exists()
assert json.loads((O/'refinement_source.json').read_text())['nonmanifold_edges']==0
actors=E.get_all_level_actors();bylabel={a.get_actor_label():a for a in actors};plan=json.loads((O/'site_plan.json').read_text());C=plan['center'];F=plan['forward'];S=plan['side'];Z=plan['yard_floor_z']
def meshactor(name):return next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name)
terrain=meshactor('SM_IV_Continent_GosainMine57');route=meshactor('SM_Gosain57_KingdomRoutes');shell=meshactor('SM_Gosain57_MineShell')
def custom(mat,code,keys,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
 n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in keys:p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 n.set_editor_property('inputs',pins);n.set_editor_property('code',code);n.set_editor_property('output_type',typ);return n
def newmat(name):
 path=D+'/Materials/'+name;mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 for n in M.get_material_expressions(mat):M.delete_material_expression(mat,n)
 return mat
rock=newmat('M_Gosain57_WeatheredMine');pos=M.create_material_expression(rock,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(rock,unreal.MaterialExpressionVertexNormalWS);col=[];norm=[]
for plane in ['yz','xz','xy']:
 uv=custom(rock,'return P.'+plane+'/420.;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);M.connect_material_expressions(pos,'',uv,'P')
 for arr,texture,typ in [(col,'T_RockCubic_BC',unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),(norm,'T_RockCubic_N',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)]:
  t=M.create_material_expression(rock,unreal.MaterialExpressionTextureSample);t.texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Cubic/'+texture);t.sampler_type=typ;M.connect_material_expressions(uv,'',t,'UVs');arr.append(t)
code='''float3 w=pow(abs(N),4.);w/=max(dot(w,1.),.001);float3 tex=A*w.x+B*w.y+C*w.z;
float3 q=P/100.;float2 delta=q.xy-float2(15950,41900);float d=dot(delta,float2(.7592566,-.6507914));
float altitude=q.z-(-20295.54547438858+.012*d);float tone=saturate(dot(tex,float3(.3,.5,.2))*1.8);
float grain=.5+.5*sin(q.z*1.5+sin(q.x*.8)+q.y*.3);
float3 stone=lerp(float3(.032,.041,.047),float3(.090,.094,.083),tone)*lerp(.90,1.06,grain);
float grass=smoothstep(.66,.95,N.z)*smoothstep(8.,12.,altitude);
stone=lerp(stone,float3(.026,.056,.022)*lerp(.8,1.25,tone),grass*.80);
float floorMask=smoothstep(.75,.96,N.z)*(1.-smoothstep(.5,1.6,altitude));
return lerp(stone,float3(.065,.049,.030)*lerp(.8,1.2,tone),floorMask);'''
base=custom(rock,code,['P','N','A','B','C'])
for key,node in zip(['P','N','A','B','C'],[pos,normal]+col):M.connect_material_expressions(node,'',base,key)
M.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR)
ncode='''float3 w=pow(abs(N),4.);w/=max(dot(w,1.),.001);float3 s=sign(N);
float3 x=float3(A.z*s.x,A.x,A.y);float3 y=float3(B.x,B.z*s.y,B.y);float3 z=float3(C.x,C.y,C.z*s.z);
return normalize(lerp(N,normalize(x*w.x+y*w.y+z*w.z),.35));'''
nn=custom(rock,ncode,['N','A','B','C'])
for key,node in zip(['N','A','B','C'],[normal]+norm):M.connect_material_expressions(node,'',nn,key)
rock.set_editor_property('tangent_space_normal',False);M.connect_material_property(nn,'',unreal.MaterialProperty.MP_NORMAL);rough=M.create_material_expression(rock,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.9);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(rock);A.save_loaded_asset(rock)
path=D+'/Materials/M_Gosain57_YardTerrain';ground=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(terrain.static_mesh_component.get_material(0).get_path_name().split('.')[0],path)
marker='return lerp(previous,lerp(localGrass,localRock,exposed),rightMask);';found=0
for n in M.get_material_expressions(ground):
 if not isinstance(n,unreal.MaterialExpressionCustom):continue
 c=n.get_editor_property('code')
 if marker in c:
  c=c.replace(marker,'''//Gosain57YardBlend
float3 result=lerp(previous,lerp(localGrass,localRock,exposed),rightMask);
float2 delta=q.xy-float2(15950.,41900.);float dd=dot(delta,float2(.7592566,-.6507914));float ll=dot(delta,float2(.6507914,.7592566));
float radius=length(float2((dd+6.)/40.,ll/28.));radius+=.035*sin(dd*.38)*sin(ll*.33);
float yard=1.-smoothstep(.78,1.28,radius);float track=(1.-smoothstep(3.4,5.6,abs(ll)))*smoothstep(-85.,-53.,dd)*(1.-smoothstep(24.,32.,dd));
float wear=sin(dd*.34+ll*.8)*sin(ll*.6-dd*.11)*.05;
float3 dirt=lerp(float3(.072,.052,.031),D*.21,.30)*(1.+wear);
return lerp(result,dirt,max(yard,track)*.95);''');n.set_editor_property('code',c);found+=1
  # An independent material copy guarantees all other regions keep the old expression outside this footprint.
 elif '//Gosain57YardBlend' in c:found+=1
assert found==1;M.recompile_material(ground);A.save_loaded_asset(ground)
def importmesh(name,material=None,mats=None,collision=False):
 path=D+'/Meshes/'+name
 if A.does_asset_exist(path):return unreal.load_asset(path)
 task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task]);mesh=unreal.load_asset(path);assert mesh
 slots=list(mesh.static_materials)
 for slot in slots:slot.set_editor_property('material_interface',material if material else mats[str(slot.material_slot_name)])
 mesh.set_editor_property('static_materials',slots)
 if collision:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 A.save_loaded_asset(mesh);return mesh
landform=importmesh('SM_Gosain57_MineLandform',rock,collision=True);routes=importmesh('SM_Gosain57_KingdomRoutesRefined',mats={str(v.material_slot_name):v.material_interface for v in route.static_mesh_component.static_mesh.static_materials})
backup=B/'Saved/WorldBackups'/('BeforeGosain57Refinement_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
shell.static_mesh_component.set_static_mesh(landform);shell.set_actor_label('Gosain | Mine hillside and adit');route.static_mesh_component.set_static_mesh(routes);terrain.static_mesh_component.set_material(0,ground)
for label in ['Gosain | Mine loading yard','Gosain | Mine entrance track']:
 a=bylabel[label];a.set_actor_hidden_in_game(True);a.static_mesh_component.set_visibility(False,True);a.set_is_temporarily_hidden_in_editor(True)
changed=0
for q in json.loads((O/'props_refined.json').read_text()):
 a=bylabel['Gosain | '+q['label']]
 if q['label'].startswith(('Mine bedrock shoulder','Mine roof strata','Mine weathered outcrop')):
  mesh=unreal.load_asset(q['path']);a.static_mesh_component.set_static_mesh(mesh);box=mesh.get_bounding_box();lo=box.min;hi=box.max;sc=[q['size'][j]*100/v for j,v in enumerate([hi.x-lo.x,hi.y-lo.y,hi.z-lo.z])];ang=math.radians(q['yaw']);cx=(lo.x+hi.x)*.5*sc[0];cy=(lo.y+hi.y)*.5*sc[1]
  loc=unreal.Vector(q['xy'][0]*100-cx*math.cos(ang)+cy*math.sin(ang),q['xy'][1]*100-cx*math.sin(ang)-cy*math.cos(ang),q['z']*100-lo.z*sc[2]);a.set_actor_location(loc,False,False);a.set_actor_scale3d(unreal.Vector(*sc));changed+=1
 if q['override']=='rock':
  for j in range(a.static_mesh_component.get_num_materials()):a.static_mesh_component.set_material(j,rock)
light_units=[]
for a in actors:
 if isinstance(a,unreal.PointLight) and 'Gosain57Mine' in [str(t) for t in a.tags]:
  c=a.point_light_component;light_units.append(str(c.get_editor_property('intensity_units')));c.set_intensity(45);c.set_attenuation_radius(1200);c.set_light_color(unreal.LinearColor(1,.71,.44,1))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'refinement_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'landform':landform.get_path_name(),'private_ground_material':ground.get_path_name(),'rock_instances_reseated':changed,'light_units':light_units,'lights_intensity':45,'native_review':'pending','yard_overlay_hidden':True,'unrelated_terrain_geometry_unchanged':True},indent=2))
