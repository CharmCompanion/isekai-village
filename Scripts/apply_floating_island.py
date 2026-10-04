import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert not any('IVFloatingV07' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Already applied'
def texture(name):
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.png'));t.destination_path=R+'/Textures';t.destination_name=name;t.automated=True;t.save=True;T.import_asset_tasks([t]);a=unreal.load_asset(R+'/Textures/'+name)
 for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST)]:a.set_editor_property(k,v)
 A.save_loaded_asset(a);return a
def target(tex):
 rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
 c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(tex,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);return rt
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
assert land.landscape_import_heightmap_from_render_target(target(texture('T_IV_FloatingHeight_RG')),True,0)
biome=texture('T_IV_Biome_Floating_v07');vis=texture('T_IV_FloatingVisibility')
mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape') or A.duplicate_asset(R+'/Materials/M_IV_Landscape_Layered',R+'/Materials/M_IV_FloatingLandscape')
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionTextureSample) and n.get_editor_property('texture')==unreal.load_asset(R+'/Textures/T_IV_Biome_Coastal_v06'):n.set_editor_property('texture',biome)
mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
mask=M.create_material_expression(mat,unreal.MaterialExpressionLandscapeVisibilityMask);M.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK);M.recompile_material(mat);A.save_loaded_asset(mat)
land.set_editor_property('landscape_material',mat);land.set_editor_property('landscape_hole_material',mat);land.force_layers_full_update()
visibility_ok=False
if not visibility_ok:
 # Explicit visual fallback retained only if engine cannot initialize its visibility target.
 pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');n.set_editor_property('inputs',[pin]);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1);n.set_editor_property('code','float2 p=float2(P.x/58000.,(P.y-2000.)/57000.); float t=atan2(p.y,p.x);return 1+.012*sin(t*7)+.008*sin(t*13)-pow(pow(abs(p.x),4)+pow(abs(p.y),4),.25)>0?1:0;');M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_OPACITY_MASK);M.recompile_material(mat);A.save_loaded_asset(mat)
def actor(mesh,name,p=(0,0,0),scale=(1,1,1),material=None,folder='Floating Island'):
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*(v*100 for v in p)));a.static_mesh_component.set_static_mesh(unreal.load_asset(mesh) if isinstance(mesh,str) else mesh);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_label(name);a.set_folder_path(folder);a.set_editor_property('tags',[unreal.Name('IVFloatingV07')])
 if material:a.static_mesh_component.set_material(0,material)
 return a
def imported(name,material,collision=True):
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/FloatingIsland';t.destination_name=name;t.automated=True;t.save=True
 op=unreal.FbxImportUI();op.set_editor_property('import_materials',False);op.set_editor_property('import_textures',False);op.static_mesh_import_data.set_editor_property('combine_meshes',True);op.static_mesh_import_data.set_editor_property('auto_generate_collision',False);t.options=op;T.import_asset_tasks([t]);m=unreal.load_asset(R+'/Meshes/FloatingIsland/'+name)
 if collision:m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 A.save_loaded_asset(m);a=actor(m,name,material=material)
 if not collision:a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 return a
stone=unreal.load_asset(R+'/Materials/M_IV_CaveStone');water=unreal.load_asset('/Game/SoStylized/Environment/Water/Materials/MI_Water')
underside=imported('SM_IV_FloatingUnderside',stone)
imported('SM_IV_SkyLake',water,False);imported('SM_IV_SkyRiver',water,False)
# Archive the old ocean and sea-level harbor without deleting their actors.
hidden=[]
for a in E.get_all_level_actors():
 label=a.get_actor_label();folder=str(a.get_folder_path());p=a.get_actor_location()
 if 'Coastal Ocean' in label or folder.startswith('Harbor') or folder.startswith('Coast/') or ('harbor' in label.lower() and p.y<-25000):
  a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False)
  for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False)
  a.set_folder_path('Archived/Continental Coast');hidden.append(label)
 if 'continuous walkable tunnel' in label:a.set_actor_location(unreal.Vector(0,0,12),False,False)
 if isinstance(a,unreal.PointLight) and folder.startswith('Adventure/Routes/'):
  c=a.get_component_by_class(unreal.PointLightComponent);c.set_editor_property('light_color',unreal.Color(r=100,g=162,b=255,a=255) if 'Dungeon' in folder else unreal.Color(r=255,g=191,b=104,a=255))
 if isinstance(a,unreal.SkyLight):
  c=a.get_component_by_class(unreal.SkyLightComponent);c.set_intensity(1.4);c.set_editor_property('lower_hemisphere_is_black',False);c.set_lower_hemisphere_color(unreal.LinearColor(.12,.17,.23,1));c.recapture_sky()
# A broad cascade falls into open sky from the river mouth.
fall=actor('/Game/SoStylized/Environment/Water/Waterfalls/SM_Waterfall1','Skyfall - river spilling into clouds',(-280,-544,-292),(1.8,1.6,81.15));fall.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
# Landing stage: wood decking, massive angled stone supports and safety rails.
wood=unreal.load_asset(R+'/Materials/M_IV_MineTimber');cube='/Engine/BasicShapes/Cube'
for i in range(44):actor(cube,'Airship quay deck plank',(275,-493-i*1.9,23.6),(22,1.8,.65),wood,'Floating Island/Airship Landing')
for x in [264.4,285.6]:
 for y in range(-497,-575,-9):actor(cube,'Quay railing post',(x,y,25.1),(.45,.45,2.8),wood,'Floating Island/Airship Landing')
 for z in [25,26.2]:actor(cube,'Quay horizontal rail',(x,-535,z),(.28,79,.26),wood,'Floating Island/Airship Landing')
for x in [268,282]:
 a=actor(cube,'Landing dock stone buttress',(x,-541,7),(3,38,4),stone,'Floating Island/Airship Landing');a.set_actor_rotation(unreal.Rotator(pitch=-25),False)
for x in [268,282]:actor('/Engine/BasicShapes/Cylinder','Airship mooring bollard',(x,-572,25),(1.1,1.1,2.6),wood,'Floating Island/Airship Landing')
# Reground vegetation only where terrain changed; omit lake, river and removed perimeter.
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Floating_v07.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
 ft=unreal.load_asset(path)
 if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
 kept=[]
 for a in E.get_all_level_actors():
  if not isinstance(a,unreal.InstancedFoliageActor):continue
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh!=ft.get_editor_property('mesh'):continue
   for i in range(c.get_instance_count()):
    tf=c.get_instance_transform(i,world_space=True);p=tf.translation;x=p.x/100;y=p.y/100
    if abs(x)>600 or abs(y)>600:continue
    if ((x+285)/78)**2+((y+320)/64)**2<1 or (y<-365 and abs(x-(-285+18*math.sin((y+355)/55)))<12):continue
    t=math.atan2((y-20)/570,x/580)
    if (abs(x/580)**4+abs((y-20)/570)**4)**.25>1+.012*math.sin(t*7)+.008*math.sin(t*13)-.008:continue
    if y<-240 or x>330:tf.translation=unreal.Vector(p.x,p.y,h(x,y)*100-12)
    kept.append(tf)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/floating_island_result.json').write_text(json.dumps({'saved':True,'native_visibility_collision_holes':visibility_ok,'archived_coastal_actors':hidden},indent=2))
