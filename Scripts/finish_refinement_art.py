import unreal,json,random,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';S=B/'Saved/AdventureWorldSource';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();rng=random.Random(928)
t=unreal.AssetImportTask();t.filename=str(S/'SM_IV_DistantContinent.obj');t.destination_path=R+'/Meshes/Refinement';t.destination_name='SM_IV_DistantContinent';t.automated=True;t.replace_existing=True;t.save=True;op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;t.options=op;T.import_asset_tasks([t])
mat=unreal.load_asset(R+'/Materials/M_IV_DistantMainland');n=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);code=n.get_editor_property('code')
if 'float3 normal' not in code:
 pins=list(n.get_editor_property('inputs'));pin=unreal.CustomInput();pin.set_editor_property('input_name','N');pins.append(pin);n.set_editor_property('inputs',pins);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);M.connect_material_expressions(normal,'',n,'N')
 code=code.replace('/2400.','/1850.').replace('float patch=.5+.5*sin(p.x/900.+sin(p.y/1700.))*cos(p.y/1300.);','float patch=saturate(.5+.25*sin(p.x/600.+sin(p.y/850.))*cos(p.y/710.)+.18*sin(p.x/133.+p.y/243.)+.08*sin(p.x/39.)*cos(p.y/51.));')
 code=code.replace('return lerp(c,float3(.035,.21,.29),river);','float3 normal=normalize(N);float shade=.50+.50*saturate(dot(normal,normalize(float3(-.5,-.3,1))));return lerp(c,float3(.025,.25,.34),river)*shade;')
 n.set_editor_property('code',code)
M.recompile_material(mat);A.save_loaded_asset(mat)
rock=unreal.load_asset(R+'/Materials/M_IV_FracturedIsland')
# A few irregular lower shards break the concentric silhouette.
for i in range(19):
 m=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Spire'+str(1+i%8).zfill(2));b=m.get_bounding_box();angle=rng.uniform(0,math.tau);rad=rng.uniform(80,390);loc=unreal.Vector((rad*math.cos(angle)-35)*100,(rad*math.sin(angle)+35)*100,rng.uniform(-740,-560)*100)
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,loc,unreal.Rotator(pitch=rng.uniform(-33,33),yaw=rng.uniform(0,360),roll=rng.uniform(155,205)));a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(rng.uniform(45,100)*100/(b.max.x-b.min.x),rng.uniform(45,95)*100/(b.max.y-b.min.y),rng.uniform(230,390)*100/(b.max.z-b.min.z)));o,e=a.get_actor_bounds(False);a.set_actor_location(a.get_actor_location()+loc-o,False,False);a.static_mesh_component.set_material(0,rock);a.set_actor_label('Asymmetric torn island shard');a.set_folder_path('Refinement/Underside');a.tags=[unreal.Name('IVRefine08')]
# Ensure the rim never leaves tall blank foundation faces at mountain elevations.
for a in E.get_all_level_actors():
 if a.get_actor_label()=='Continental mountains and river - 7km below':a.static_mesh_component.set_material(0,mat)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/refinement_final_art.json').write_text(json.dumps({'saved':True,'additional_shards':19,'mainland':'eroded ridges, shaded forest and river'}))
