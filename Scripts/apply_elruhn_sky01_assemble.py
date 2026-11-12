"""Native scene assembly: private materials and actors in the copied map only."""
import unreal,json,math,random,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/ElRuhnSky01';MAP=R+'/Maps/Map_ElRuhnSky'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(MAP+'.');assert (O/'copy_applied.json').exists();assert not (O/'assembled.json').exists()
q=json.loads((O/'source.json').read_text());created=[]
for a in list(E.get_all_level_actors()):
 if 'ElRuhnSky01' in [str(t) for t in a.tags]:E.destroy_actor(a)
def status(s):(O/'assembly_progress.json').write_text(json.dumps({'stage':s}))
def asset(name,cls,factory,folder='Materials'):
 path=D+'/'+folder+'/'+name;return unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,D+'/'+folder,cls,factory)
def vec(mat,value):
 n=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);n.constant=unreal.LinearColor(*value,1);return n
def scalar(mat,value):
 n=M.create_material_expression(mat,unreal.MaterialExpressionConstant);n.r=value;return n
def link(a,output,b,pin):M.connect_material_expressions(a,output,b,pin)
def matcolor(name,color,emission=0,metal=0,rough=.52):
 mat=asset('M_ES01_'+name,unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 c=vec(mat,color);M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(scalar(mat,rough),'',unreal.MaterialProperty.MP_ROUGHNESS)
 if metal:M.connect_material_property(scalar(mat,metal),'',unreal.MaterialProperty.MP_METALLIC)
 if emission:M.connect_material_property(vec(mat,[v*emission for v in color]),'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 M.recompile_material(mat);A.save_loaded_asset(mat);return mat
status('private material palette')
mats={}
for name,color,em,metal,rough in [('ivory',(.62,.56,.43),0,0,.68),('trim',(.82,.72,.49),0,0,.44),('foundation',(.28,.31,.32),0,0,.77),('roof',(.025,.095,.13),0,.25,.4),('gold',(.65,.36,.075),0,.72,.3),('recess',(.009,.02,.034),0,0,.65),('door',(.025,.075,.10),0,.3,.38),('glass',(.025,.34,.5),1.1,.2,.3),('crystal',(.06,.5,.68),1.7,.3,.18),('magic',(.055,.6,.82),3,0,.4)]:mats[name]=matcolor(name,color,em,metal,rough)
# Private stone shader: reuse the pack's actual rock texture with world-aligned coordinates.
rock=asset('M_ES01_AnchorRock',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(rock);pos=M.create_material_expression(rock,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(rock,unreal.MaterialExpressionVertexNormalWS)
tex=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC');assert tex
samples=[]
for axis in ['xy','xz','yz']:
 uv=M.create_material_expression(rock,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');uv.set_editor_property('inputs',[pin]);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);uv.set_editor_property('code','return P.'+axis+'/1800.;');link(pos,'',uv,'P')
 n=M.create_material_expression(rock,unreal.MaterialExpressionTextureSample);n.texture=tex;link(uv,'',n,'UVs');samples.append(n)
blend=M.create_material_expression(rock,unreal.MaterialExpressionCustom);pins=[]
for key in ['A','B','C','N']:p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
blend.set_editor_property('inputs',pins);blend.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);blend.set_editor_property('code','float3 w=pow(abs(N),4);w/=max(dot(w,1),.001);return (A*w.z+B*w.y+C*w.x)*float3(.34,.42,.51);')
for n,key in zip(samples,['A','B','C']):link(n,'RGB',blend,key)
link(normal,'',blend,'N');M.connect_material_property(blend,'',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(scalar(rock,.72),'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(rock);A.save_loaded_asset(rock);mats['rock']=rock
# Preserve masonry detail from the existing private ivory/foundation materials where available.
for key,source in [('ivory','ivory'),('trim','trim'),('foundation','foundation')]:
 old=unreal.load_asset(R+'/Gosain42/Materials/M_Gosain42_'+source)
 if old:
  path=D+'/Materials/M_ES01_Textured_'+key;mats[key]=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(old.get_path_name(),path);A.save_loaded_asset(mats[key])
status('importing original tower and levitation meshes')
meshes={}
for row in q['assets']:
 name=row['name'];path=D+'/Meshes/'+name
 if not A.does_asset_exist(path):
  task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
  op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
 mesh=unreal.load_asset(path);assert mesh;slots=list(mesh.static_materials)
 for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name)])
 mesh.set_editor_property('static_materials',slots)
 if 'GrandTower' in name:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 A.save_loaded_asset(mesh);meshes[name]=mesh
def spawn(name,mesh,p,scale=(1,1,1),mat=None,folder='Levitation',rot=None,collision=False):
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in p]),rot or unreal.Rotator());a.static_mesh_component.set_static_mesh(mesh);a.set_actor_label(name);a.set_actor_scale3d(unreal.Vector(*scale));a.set_folder_path('El Ruhn Sky/'+folder);a.tags=['ElRuhnSky01'];a.set_actor_enable_collision(collision)
 if mat:a.static_mesh_component.set_material(0,mat)
 created.append(a.get_name());return a
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
status('placing five stones and below-village circles')
for name in ['T_ElRuhnSky_Levitation','T_ElRuhnSky_IslandScript']:
 if not A.does_asset_exist(D+'/Textures/'+name):
  task=unreal.AssetImportTask();task.filename=str(O/(name+'.png'));task.destination_path=D+'/Textures';task.automated=True;task.save=True;T.import_asset_tasks([task])
 tex=unreal.load_asset(D+'/Textures/'+name);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(tex)
def rune(name,texture,glow=2.0):
 mat=asset(name,unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat);mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_ADDITIVE);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True)
 sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);sample.texture=unreal.load_asset(D+'/Textures/'+texture)
 # Slow shader rotation works in play; no editor tick-dependent animation.
 coord=M.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);tm=M.create_material_expression(mat,unreal.MaterialExpressionTime);rot=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in ['UV','T']:p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 rot.set_editor_property('inputs',pins);rot.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);rot.set_editor_property('code','float a=T*.018;float2 p=UV-.5;return .5+float2(p.x*cos(a)-p.y*sin(a),p.x*sin(a)+p.y*cos(a));');link(coord,'',rot,'UV');link(tm,'',rot,'T');link(rot,'',sample,'UVs')
 M.connect_material_property(sample,'A',unreal.MaterialProperty.MP_OPACITY);M.connect_material_property(vec(mat,[.08*glow,.65*glow,.9*glow]),'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
rm=rune('M_ES01_WindSeal','T_ElRuhnSky_Levitation',2.2);im=rune('M_ES01_IslandCovenant','T_ElRuhnSky_IslandScript',2)
for i,p in enumerate(q['anchor_centers_m']):
 spawn('Levitation Stone %d — Fivefold Covenant'%(i+1),meshes['SM_ElRuhnSky_AnchorStone_%02d'%(i+1)],p,rot=unreal.Rotator(yaw=i*31))
 spawn('Stone %d | horizontal wind seal'%(i+1),plane,p,(140,140,1),rm)
spawn('Island levitation ring | below village',meshes['SM_ElRuhnSky_IslandHalo'],(0,0,-120))
spawn('Island covenant | rune band',plane,(0,0,-119.5),(1835,1835,1),im)
status('tower courtyard and local foliage clearance')
spawn('El Ruhn | Tower of the Five Winds',meshes['SM_ElRuhnSky_GrandTower'],q['tower_origin_m'],folder='Tower',collision=True)
cx,cy,cz=q['tower_origin_m'];cleared=0
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  indices=[]
  for i in range(c.get_instance_count()):
   p=c.get_instance_transform(i,True).translation;x=p.x/100-cx;y=p.y/100-cy
   if math.hypot(x,y)<47 or (abs(x)<17 and -130<y<0):indices.append(i)
  if indices:c.remove_instances(indices);cleared+=len(indices)
status('layered stylized cloud sea')
# Painted pack clouds, reused as private material instances with two-sided visibility.
cloudmats=[]
for i in range(1,4):
 old=unreal.load_asset(R+'/Materials/MI_IV_CloudBank'+str(i));assert old
 path=D+'/Materials/MI_ES01_Cloud'+str(i);mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(old.get_path_name(),path)
 M.set_material_instance_scalar_parameter_value(mat,'Opacity',.93);M.set_material_instance_scalar_parameter_value(mat,'AlphaPower',1.1);M.set_material_instance_vector_parameter_value(mat,'Tint',unreal.LinearColor(.65,.75,.88,1));A.save_loaded_asset(mat);cloudmats.append(mat)
rng=random.Random(1031)
for j in range(180):
 # Disk covering 32 km; multiple overlapping strata prevent a single flat card read.
 angle=rng.random()*math.tau;radius=math.sqrt(rng.random())*16000;size=rng.uniform(1800,4100);z=-1000-rng.uniform(0,550)
 spawn('Cloud Sea | painted bank %03d'%j,plane,(radius*math.cos(angle),radius*math.sin(angle),z),(size,size*rng.uniform(.6,1.0),1),cloudmats[j%3],folder='Cloud Sea',rot=unreal.Rotator(pitch=rng.uniform(-4,4),yaw=rng.uniform(0,360),roll=rng.uniform(-4,4)))
# Continuous pale lower haze prevents glimpses into a black/empty void between cloud banks.
bed=matcolor('CloudHorizon',(.40,.53,.68),.55,rough=1)
spawn('Cloud Sea | distant horizon haze',plane,(0,0,-1850),(120000,120000,1),bed,folder='Cloud Sea')
# Dedicated map atmosphere belongs to this scene. The original correction stays untouched.
for a in E.get_all_level_actors():
 if isinstance(a,unreal.SkyAtmosphere):a.set_actor_location(unreal.Vector(0,0,-600000),False,False)
 if isinstance(a,unreal.ExponentialHeightFog):
  a.set_actor_location(unreal.Vector(0,0,-135000),False,False);c=a.get_component_by_class(unreal.ExponentialHeightFogComponent);c.set_editor_property('fog_density',.00055);c.set_editor_property('fog_height_falloff',.08);c.set_editor_property('start_distance',40000.)
 if isinstance(a,unreal.SkyLight):a.light_component.set_editor_property('intensity',1.1)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
source=json.loads((O/'copy_applied.json').read_text());assert hashlib.sha256((B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap').read_bytes()).hexdigest()==source['source_sha256']
(O/'assembled.json').write_text(json.dumps({'status':'saved','map':MAP,'new_actors':created,'cleared_tower_foliage_instances':cleared,'five_anchor_stones':5,'circle_z_m':-120,'source_map_unchanged':True,'native_review':'pending'},indent=2));status('saved')
