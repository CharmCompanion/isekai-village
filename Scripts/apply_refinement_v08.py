"""Targeted v08 island art pass. Re-runnable generated actors are tagged IVRefine08."""
import unreal,json,math,random,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();rng=random.Random(280908)
assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
report={}
def log(stage):
 report['stage']=stage;(B/'Saved/refinement_apply.json').write_text(json.dumps(report,indent=2));unreal.log('REFINE08 '+stage)
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Refined_v08.r16').read_bytes())
def h(x,y):
 i=max(0,min(1008,round((x+600)*.84)));j=max(0,min(1008,round((y+600)*.84)));return (raw[j*1009+i]-32768)/64
for a in E.get_all_level_actors():
 if 'IVRefine08' in [str(t) for t in a.tags]:E.destroy_actor(a)
def actor(mesh,name,folder,loc=(0,0,0),scale=(1,1,1),rot=None,mat=None):
 m=unreal.load_asset(mesh) if isinstance(mesh,str) else mesh;assert m,mesh
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*(v*100 for v in loc)),rot or unreal.Rotator());a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_label(name);a.set_folder_path('Refinement/'+folder);a.tags=[unreal.Name('IVRefine08')]
 if mat:a.static_mesh_component.set_material(0,mat)
 return a
def import_asset(name,kind):
 t=unreal.AssetImportTask();t.filename=str(S/(name+('.png' if kind=='tex' else '.obj')));t.destination_path=R+('/Textures' if kind=='tex' else '/Meshes/Refinement');t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 if kind!='tex':
  op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;t.options=op
 T.import_asset_tasks([t]);a=unreal.load_asset(t.destination_path+'/'+name)
 if kind=='tex':
  for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:a.set_editor_property(k,v)
  A.save_loaded_asset(a)
 return a
log('Native lake and foothills')
height=import_asset('T_IV_RefinedHeight_RG','tex');biome=import_asset('T_IV_Biome_Refined_v08','tex');land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.target_gamma=1.
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(height,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionTextureSample):
  tex=n.get_editor_property('texture')
  if tex and 'Biome' in tex.get_name():n.set_editor_property('texture',biome)
M.recompile_material(mat);A.save_loaded_asset(mat)
lake=import_asset('SM_IV_GrandSkyLake','mesh')
for a in E.get_all_level_actors():
 if a.get_actor_label()=='SM_IV_SkyLake':a.static_mesh_component.set_static_mesh(lake)
 if str(a.get_folder_path())=='Floating Island/Cloud Sea':a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False);a.set_folder_path('Archived/Blob Clouds')
log('Fractured SoStylized rock shell')
cliffs=[unreal.load_asset('/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic'+str(i)) for i in range(1,7)]
spires=[unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Spire'+str(i).zfill(2)) for i in range(1,9)]
def fitted(m,name,folder,loc,dims,rot):
 b=m.get_bounding_box();s=tuple(d*100/max(1,v) for d,v in zip(dims,[b.max.x-b.min.x,b.max.y-b.min.y,b.max.z-b.min.z]));a=actor(m,name,folder,loc,s,rot)
 o,_=a.get_actor_bounds(False);p=a.get_actor_location();a.set_actor_location(p+unreal.Vector(*(v*100 for v in loc))-o,False,False);return a
count=0
for ring,(num,rad,z,width,heightm) in enumerate([(72,570,-70,115,190),(60,493,-190,150,220),(42,375,-315,165,240),(27,238,-465,150,235),(12,95,-615,125,240)]):
 for i in range(num):
  t=2*math.pi*(i+rng.random()*.4)/num;den=(abs(math.cos(t))**4+abs(math.sin(t))**4)**.25;rr=rad/den
  x=rr*math.cos(t)-ring*8;y=20+rr*.97*math.sin(t)+ring*5;zz=z+rng.uniform(-22,22)
  if ring==0:zz=min(zz,h(max(-599,min(599,x)),max(-599,min(599,y)))-heightm*.52)
  fitted(rng.choice(cliffs),'Upheaved cliff strata','Underside',(x,y,zz),(width*rng.uniform(.8,1.3),width*.9,heightm*rng.uniform(.8,1.2)),unreal.Rotator(pitch=rng.uniform(-20,20),yaw=math.degrees(t)+rng.uniform(-30,30),roll=rng.uniform(-16,16)));count+=1
for i in range(74):
 t=rng.uniform(0,2*math.pi);rad=rng.uniform(160,520);depth=-150-(560-rad)*1.1
 fitted(rng.choice(spires),'Torn downward rock fang','Underside',(rad*math.cos(t)-25,rad*math.sin(t)+30,depth),(rng.uniform(45,95),rng.uniform(50,100),rng.uniform(170,370)),unreal.Rotator(pitch=rng.uniform(-18,18),yaw=rng.uniform(0,360),roll=180+rng.uniform(-18,18)));count+=1
report['underside_rock_pieces']=count
log('Distant continental relief and painted cloud layers')
continent=import_asset('SM_IV_DistantContinent','mesh')
mp=R+'/Materials/M_IV_DistantMainland';mainmat=unreal.load_asset(mp) if A.does_asset_exist(mp) else T.create_asset('M_IV_DistantMainland',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mainmat)
pos=M.create_material_expression(mainmat,unreal.MaterialExpressionWorldPosition);n=M.create_material_expression(mainmat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');n.set_editor_property('inputs',[pin]);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
n.set_editor_property('code','''float3 p=P/100.;float riverx=3500.+4200.*sin(p.y/8000.)+1600.*sin(p.y/3100.);float river=1.-smoothstep(170.,330.,abs(p.x-riverx));float altitude=saturate((p.z+7400.)/2400.);float patch=.5+.5*sin(p.x/900.+sin(p.y/1700.))*cos(p.y/1300.);float3 c=lerp(float3(.055,.17,.14),float3(.20,.28,.15),patch);c=lerp(c,float3(.25,.31,.34),smoothstep(.25,.75,altitude));c=lerp(c,float3(.58,.64,.65),smoothstep(.8,1.,altitude));return lerp(c,float3(.035,.21,.29),river);''')
M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=M.create_material_expression(mainmat,unreal.MaterialExpressionConstant);rough.r=.95;M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mainmat);A.save_loaded_asset(mainmat)
a=actor(continent,'Continental mountains and river - 7km below','Distant World',mat=mainmat);a.set_actor_enable_collision(False)
# Pack-authored layered cloud dome for illustrated silhouettes on the horizon.
skymat=A.duplicate_asset('/Game/SoStylized/Environment/Sky/Materials/MI_StylizedClouds_Lite',R+'/Materials/MI_IV_PaintedSky') if not A.does_asset_exist(R+'/Materials/MI_IV_PaintedSky') else unreal.load_asset(R+'/Materials/MI_IV_PaintedSky')
M.set_material_instance_scalar_parameter_value(skymat,'Strength',1.15);M.set_material_instance_scalar_parameter_value(skymat,'Vertical Stretch',.5);M.set_material_instance_scalar_parameter_value(skymat,'Vertical Offset',-.04);A.save_loaded_asset(skymat)
a=actor('/Game/SoStylized/Environment/Sky/Meshes/SM_StylizedSkyDome_Clouds','SoStylized illustrated cloud horizon','Clouds',(0,0,-600),mat=skymat);a.set_actor_enable_collision(False);a.static_mesh_component.set_cast_shadow(False)
cloudmats=[]
for i in [1,2,3]:
 name='MI_IV_CloudBank'+str(i);p=R+'/Materials/'+name;cm=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset('/Game/StylizedIsland/StylizedVFX/Fog/Materials/FogCard/MI_FogCard_0'+str(i),p)
 for key,val in [('Opacity',.88),('AlphaPower',1.2),('AnimSpeed',.12),('DF',500.)]:M.set_material_instance_scalar_parameter_value(cm,key,val)
 M.set_material_instance_vector_parameter_value(cm,'Tint',unreal.LinearColor(.85,.93,1.,1));A.save_loaded_asset(cm);cloudmats.append(cm)
for i in range(32):
 t=rng.uniform(0,2*math.pi);rad=rng.uniform(1700,6500);size=rng.uniform(900,1900)
 a=actor('/Engine/BasicShapes/Plane','Painted drifting cloudbank','Clouds',(rad*math.cos(t),rad*math.sin(t),rng.uniform(-2100,-1100)),(size,size*.7,1),unreal.Rotator(pitch=rng.uniform(-25,25),yaw=rng.uniform(0,360),roll=rng.uniform(-18,18)),rng.choice(cloudmats));a.set_actor_enable_collision(False);a.static_mesh_component.set_cast_shadow(False)
for a in E.get_all_level_actors():
 if isinstance(a,unreal.SkyAtmosphere):a.set_actor_location(unreal.Vector(0,0,-1300000),False,False)
 if isinstance(a,unreal.ExponentialHeightFog):
  a.set_actor_location(unreal.Vector(0,0,-560000),False,False);a.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_density',.00012)
unreal.SystemLibrary.execute_console_command(w,'RecreateLandscapeCollision');unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();log('Terrain, rock shell, mainland and clouds saved')

