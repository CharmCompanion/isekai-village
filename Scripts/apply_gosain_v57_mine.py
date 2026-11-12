"""Apply the Gosain mine site with native asset reuse and a recoverable map backup."""
import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.');assert not (O/'applied.json').exists();assert json.loads((O/'build_report.json').read_text())['forest_instances_in_site']==0
plan=json.loads((O/'site_plan.json').read_text());C=plan['center'];F=plan['forward'];S=plan['side'];Z=plan['yard_floor_z'];yaw=math.degrees(math.atan2(F[1],F[0]));actors=E.get_all_level_actors()
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN57 '+s)
def bymesh(n):
 aa=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==n];assert len(aa)==1,(n,len(aa));return aa[0]
terrain=bymesh('SM_IV_Continent_GosainShoulders56');route=bymesh('SM_Gosain56_KingdomRoutes')
# Reusable pack assets are loaded before scene mutation.
props=json.loads((O/'props.json').read_text());sources={p:unreal.load_asset(p) for p in sorted(set(q['path'] for q in props))};assert all(sources.values()),[p for p,m in sources.items() if not m]
def custom(mat,code,keys,typ):
 n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in keys:p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 n.set_editor_property('inputs',pins);n.set_editor_property('code',code);n.set_editor_property('output_type',typ);return n
# Private world-projected rock materials, preserving the pack's shared assets.
materials={}
for name,tint in [('M_Gosain57_MineRock','float3(.32,.34,.30)'),('M_Gosain57_Ore','float3(.17,.13,.09)')]:
 path=D+'/Materials/'+name;mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 for n in M.get_material_expressions(mat):M.delete_material_expression(mat,n)
 pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);samples=[]
 for plane in ['yz','xz','xy']:
  uv=custom(mat,'return P.'+plane+'/650.;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);M.connect_material_expressions(pos,'',uv,'P');tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);tex.texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Cubic/T_RockCubic_BC');tex.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR;M.connect_material_expressions(uv,'',tex,'UVs');samples.append(tex)
 blend=custom(mat,'float3 w=pow(abs(N),4.);w/=max(dot(w,1.),.001);return (A*w.x+B*w.y+C*w.z)*'+tint+';',['N','A','B','C'],unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 for key,n in zip(['N','A','B','C'],[normal]+samples):M.connect_material_expressions(n,'',blend,key)
 M.connect_material_property(blend,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=M.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.88);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);A.save_loaded_asset(mat);materials['rock' if 'MineRock' in name else 'ore']=mat
soil=unreal.load_asset(R+'/Gosain54/Materials/M_Gosain54_ForestTrail');assert soil

def loadmesh(name,single=None,mats=None,collision=True):
 path=D+'/Meshes/'+name
 if A.does_asset_exist(path):return unreal.load_asset(path)
 status('importing '+name);task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task]);mesh=unreal.load_asset(path);assert mesh
 slots=list(mesh.static_materials)
 for slot in slots:slot.set_editor_property('material_interface',single if single else mats[str(slot.material_slot_name)])
 mesh.set_editor_property('static_materials',slots)
 if collision:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 A.save_loaded_asset(mesh);return mesh
newterrain=loadmesh('SM_IV_Continent_GosainMine57',terrain.static_mesh_component.get_material(0));newroute=loadmesh('SM_Gosain57_KingdomRoutes',mats={str(v.material_slot_name):v.material_interface for v in route.static_mesh_component.static_mesh.static_materials},collision=False)
shell=loadmesh('SM_Gosain57_MineShell',materials['rock']);yard=loadmesh('SM_Gosain57_MineYard',soil,collision=False);approach=loadmesh('SM_Gosain57_MineApproach',soil,collision=False)
backup=B/'Saved/WorldBackups'/('BeforeGosain57_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap');oldterrain=terrain.static_mesh_component.static_mesh;oldroute=route.static_mesh_component.static_mesh;created=[]
def spawn(mesh,label,location,rotation,scale=None):
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,location,rotation);created.append(a);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_label('Gosain | '+label);a.set_folder_path('World/Gosain/Mine57');a.tags=['Gosain57Mine']
 if scale:a.set_actor_scale3d(unreal.Vector(*scale))
 return a
try:
 terrain.static_mesh_component.set_static_mesh(newterrain);route.static_mesh_component.set_static_mesh(newroute)
 for mesh,label in [(shell,'Mine adit rock shell'),(yard,'Mine loading yard'),(approach,'Mine entrance track')]:spawn(mesh,label,unreal.Vector(C[0]*100,C[1]*100,Z*100),unreal.Rotator(pitch=0,yaw=yaw,roll=0))
 for q in props:
  mesh=sources[q['path']];box=mesh.get_bounding_box();lo=box.min;hi=box.max;dims=[hi.x-lo.x,hi.y-lo.y,hi.z-lo.z];sc=[q['size'][j]*100/dims[j] for j in range(3)] if q['size'] else [q['scale']]*3
  ang=math.radians(q['yaw']);cx=(lo.x+hi.x)*.5*sc[0];cy=(lo.y+hi.y)*.5*sc[1];loc=unreal.Vector(q['xy'][0]*100-cx*math.cos(ang)+cy*math.sin(ang),q['xy'][1]*100-cx*math.sin(ang)-cy*math.cos(ang),q['z']*100-lo.z*sc[2]);a=spawn(mesh,q['label'],loc,unreal.Rotator(pitch=0,yaw=q['yaw'],roll=0),sc)
  if q['override']:
   for j in range(a.static_mesh_component.get_num_materials()):a.static_mesh_component.set_material(j,materials[q['override']])
 for i,q in enumerate(json.loads((O/'lights.json').read_text())):
  d,l=q['d'],q['l'];loc=unreal.Vector((C[0]+F[0]*d+S[0]*l)*100,(C[1]+F[1]*d+S[1]*l)*100,(Z+q['z'])*100);a=E.spawn_actor_from_class(unreal.PointLight,loc,unreal.Rotator());created.append(a);a.set_actor_label('Gosain | Mine lamplight '+str(i));a.set_folder_path('World/Gosain/Mine57');a.tags=['Gosain57Mine'];c=a.point_light_component;c.set_intensity(1400);c.set_attenuation_radius(1600);c.set_light_color(unreal.LinearColor(1,.63,.30,1));c.set_editor_property('source_radius',16)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 terrain.static_mesh_component.set_static_mesh(oldterrain);route.static_mesh_component.set_static_mesh(oldroute)
 for a in reversed(created):E.destroy_actor(a)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'actors_created':len(created),'terrain':newterrain.get_path_name(),'forest_unchanged':True,'left_island_unchanged':True,'other_regions_unchanged':True,'adit_length_m':68,'native_review':'pending','mechanics':'scenic exterior and short gated adit only; no resource extraction or deeper mine transition implemented'},indent=2));status('saved')
