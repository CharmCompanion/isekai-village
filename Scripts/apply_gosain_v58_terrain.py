"""Apply locally verified terrain/shading repair; protect existing towns and unrelated regions."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain58';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.');assert not (O/'applied.json').exists();assert json.loads((O/'source_complete.json').read_text())['status']=='ready_for_native_import';assert (O/'coast_validation.json').exists();assert (B/'Docs/WorldDesign/Gosain58_Before/native_views_complete.json').exists()
v=json.loads((O/'terrain_validation.json').read_text());assert v['outside_gosain_unchanged'] and v['town_ground_unchanged'] and v['mine_ground_unchanged']
actors=E.get_all_level_actors();terrain=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainMine57')
route=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_Gosain57_KingdomRoutesRefined')
assert (O/'surface_finish_validation.json').exists()
def state():
 out=[]
 for a in E.get_all_level_actors():
  if a in [terrain,route] or not isinstance(a,unreal.StaticMeshActor):continue
  c=a.static_mesh_component;p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();out.append([a.get_name(),c.static_mesh.get_path_name() if c.static_mesh else '',[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],[c.get_material(i).get_path_name() if c.get_material(i) else '' for i in range(c.get_num_materials())]])
 return hashlib.sha256(json.dumps(sorted(out),sort_keys=True).encode()).hexdigest()
before=state();path=D+'/Materials/M_Gosain58_TerrainDetail';oldmat=terrain.static_mesh_component.get_material(0);mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(oldmat.get_path_name().split('.')[0],path)
leaf=None
for n in M.get_material_expressions(mat):
 if not isinstance(n,unreal.MaterialExpressionCustom):continue
 code=n.get_editor_property('code')
 if '//Gosain56MountainLayers' in code:
  code=code.replace('float3(.029,.069,.025)','float3(.033,.079,.025)').replace('*.4.2,.92,1.08','*.4.2,.65,1.35').replace('*4.2,.92,1.08','*4.2,.65,1.35')
  code=code.replace('smoothstep(280.,650.,q.z+20600.)*lerp(.68,.94,patches)','smoothstep(380.,720.,q.z+20600.)*lerp(.45,.78,patches)')
  code=code.replace('float3(.064,.071,.066),float3(.100,.093,.076)','float3(.052,.068,.070),float3(.125,.115,.088)')
  n.set_editor_property('code',code);leaf=n
assert leaf
def custom(code,keys,typ):
 n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in keys:p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 n.set_editor_property('inputs',pins);n.set_editor_property('code',code);n.set_editor_property('output_type',typ);return n
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);samples=[]
for plane in ['yz','xz','xy']:
 uv=custom('return P.'+plane+'/350.;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);M.connect_material_expressions(pos,'',uv,'P');tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);tex.texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Cubic/T_RockCubic_BC');tex.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR;M.connect_material_expressions(uv,'',tex,'UVs');samples.append(tex)
blend=custom('float3 w=pow(abs(N),4.);w/=max(dot(w,1.),.001);return A*w.x+B*w.y+C*w.z;',['N','A','B','C'],unreal.CustomMaterialOutputType.CMOT_FLOAT3)
for key,node in zip(['N','A','B','C'],[normal]+samples):M.connect_material_expressions(node,'',blend,key)
M.connect_material_expressions(blend,'',leaf,'R');M.recompile_material(mat);A.save_loaded_asset(mat)
name='SM_IV_Continent_GosainRefined58';path=D+'/Meshes/'+name
if not A.does_asset_exist(path):
 (O/'apply_progress.json').write_text(json.dumps({'stage':'importing terrain'}));task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(path);assert mesh;slots=list(mesh.static_materials)
for slot in slots:slot.set_editor_property('material_interface',mat)
mesh.set_editor_property('static_materials',slots);A.save_loaded_asset(mesh)
oldroute=route.static_mesh_component.static_mesh;routepath=D+'/Meshes/SM_Gosain58_ContinuousRoutes'
if not A.does_asset_exist(routepath):
 task=unreal.AssetImportTask();task.filename=str(O/'SM_Gosain58_ContinuousRoutes.obj');task.destination_path=D+'/Meshes';task.destination_name='SM_Gosain58_ContinuousRoutes';task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
newroute=unreal.load_asset(routepath);assert newroute;mats={str(s.material_slot_name):s.material_interface for s in oldroute.static_materials};slots=list(newroute.static_materials)
for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name)])
newroute.set_editor_property('static_materials',slots);newroute.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(newroute)
groups={};oldgroups={};fts={}
for side,prefix,ftprefix,oldfile in [('left',R+'/Gosain50/Foliage/','FT_Gosain50_Tree',B/'ArtSource/World/Gosain56/left_forest_instances.json'),('right',R+'/Gosain56/Foliage/','FT_RightForestTree',B/'ArtSource/World/Gosain56/forest_instances.json')]:
 fts[side]=[unreal.load_asset(prefix+ftprefix+str(i)) for i in range(5)];assert all(fts[side]);groups[side]=[[] for _ in range(5)];oldgroups[side]=[[] for _ in range(5)]
 for dest,src in [(groups[side],O/(side+'_forest_instances.json')),(oldgroups[side],oldfile)]:
  for x,y,z,yaw,scale,i in json.loads(src.read_text()):dest[int(i)].append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(scale,scale,scale)))
backup=B/'Saved/WorldBackups'/('BeforeGosain58_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap');oldmesh=terrain.static_mesh_component.static_mesh
try:
 terrain.static_mesh_component.set_static_mesh(mesh);terrain.static_mesh_component.set_material(0,mat)
 route.static_mesh_component.set_static_mesh(newroute)
 for side in ['left','right']:
  for ft,rows in zip(fts[side],groups[side]):unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 after=state();assert before==after,'unrelated static actor state changed';assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 terrain.static_mesh_component.set_static_mesh(oldmesh);terrain.static_mesh_component.set_material(0,oldmat)
 route.static_mesh_component.set_static_mesh(oldroute)
 for side in ['left','right']:
  for ft,rows in zip(fts[side],oldgroups[side]):unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'mesh':mesh.get_path_name(),'routes':newroute.get_path_name(),'material':mat.get_path_name(),'unrelated_static_actor_signature_before':before,'unrelated_static_actor_signature_after':after,'native_review':'pending','terrain_collision_unchanged':True},indent=2));(O/'apply_progress.json').write_text(json.dumps({'stage':'saved'}))
