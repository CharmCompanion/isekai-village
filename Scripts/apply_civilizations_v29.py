"""Import finished regional scenery and place batched native asset instances."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';O=S/'Civilizations29';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def status(stage,**kw):(B/'Saved/civilizations_applied_v29.json').write_text(json.dumps({'stage':stage,**kw},indent=2))
colors={'stone':(.48,.43,.34),'trim':(.62,.56,.43),'plaster':(.65,.57,.39),'roof':(.065,.13,.19),'tealroof':(.045,.25,.22),'wood':(.19,.105,.045),'gold':(.60,.36,.07),'window':(.018,.032,.04),'cloth':(.58,.45,.28),'darkstone':(.105,.068,.065),'arcane':(.04,.33,.42),'crystal':(.055,.65,.77),'amber':(.75,.25,.04),'mud':(.08,.13,.07),'reed':(.20,.32,.10),'seed':(.14,.074,.025),'path':(.32,.26,.17),'conduit':(.035,.36,.48),'crimson':(.38,.035,.055),'cropgold':(.43,.34,.095),'cropgreen':(.12,.30,.055)}
materials={}
for name,c in colors.items():
 path=R+'/Materials/Civilizations/M_Civ29_'+name;mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Civ29_'+name,R+'/Materials/Civilizations',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');n.set_editor_property('inputs',[pin]);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 code='float3 p=P/100.;float noise=.94+.045*sin(p.x*.31+sin(p.z*.43))*cos(p.y*.37)+.025*sin(p.x*2.3+p.z*1.7);'
 if name in ['stone','darkstone','trim']:
  code+='float course=1.-smoothstep(.03,.10,abs(frac(p.z/2.8)-.5));noise*=1.-course*.10;'
 if name in ['cropgold','cropgreen']:code+='noise*=.80+.20*smoothstep(-.4,.5,sin(p.x*.75+p.y*.35));'
 if name in ['wood','roof','tealroof']:code+='noise*=.93+.07*sin(p.x*2.8+p.z*1.3);'
 code+=f'return float3({c[0]},{c[1]},{c[2]})*noise;';n.set_editor_property('code',code);M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 glow=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);M.connect_material_expressions(n,'',glow,'A');glow.set_editor_property('const_b',1.2 if name in ['crystal','amber'] else .28 if name in ['arcane','conduit'] else .12);M.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 for prop,v in [(unreal.MaterialProperty.MP_ROUGHNESS,.52 if name in ['gold','arcane','crystal'] else .82),(unreal.MaterialProperty.MP_SPECULAR,.28)]:
  node=M.create_material_expression(mat,unreal.MaterialExpressionConstant);node.set_editor_property('r',v);M.connect_material_property(node,'',prop)
 mat.set_editor_property('two_sided',True);M.recompile_material(mat);A.save_loaded_asset(mat);materials[name]=mat
status('importing architecture')
manifest=json.loads((O/'assets.json').read_text());report={}
for q in manifest:
 name=q['name'];task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=R+'/Meshes/Civilizations';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);task.options=op;T.import_asset_tasks([task]);mesh=unreal.load_asset(task.destination_path+'/'+name)
 slots=[]
 for i,slot in enumerate(mesh.static_materials):
  key=str(slot.material_slot_name)
  if key not in materials:key=str(slot.material_slot_name)
  assert key in materials,(name,key,q['materials'])
  mesh.set_material(i,materials[key]);slots.append(key)
 bs=SS.get_lod_build_settings(mesh,0);bs.recompute_normals=False;bs.use_high_precision_tangent_basis=True;SS.set_lod_build_settings(mesh,0,bs);A.save_loaded_asset(mesh);report[name]={'slots':slots,'triangles':q['triangles']}
status('placing civilizations',mesh_assets=report)
data=json.loads((S/'civilization_instances_v29.json').read_text());counts={}
for key,instances in data['instances'].items():
 if not instances:continue
 mesh=unreal.load_asset(data['assets'][key]);assert mesh,key
 path=R+'/Foliage/Civilizations/FT_Civ29_'+key
 ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_Civ29_'+key,R+'/Foliage/Civilizations',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
 ft.set_editor_property('mesh',mesh);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));ft.set_editor_property('cast_shadow',key not in ['Oak','Pine','Palm','DesertPalm','SM_Civ29_Reeds']);A.save_loaded_asset(ft);unreal.InstancedFoliageActor.remove_all_instances(W,ft)
 transforms=[unreal.Transform(location=unreal.Vector(p[0]*100,p[1]*100,p[2]*100),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*p[3:6])) for p in instances]
 unreal.InstancedFoliageActor.add_instances(W,ft,transforms);counts[key]=len(instances);status('placing '+key,counts=counts)
for name in ['SM_Civ29_Roads','SM_Civ29_Foundations']:
 tag='Civ29_'+name;actor=next((a for a in E.get_all_level_actors() if tag in [str(t) for t in a.tags]),None)
 if actor is None:actor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.tags=[tag]
 actor.static_mesh_component.set_static_mesh(unreal.load_asset(R+'/Meshes/Civilizations/'+name));actor.set_actor_label('Regional '+('roads and arcane conduits' if name.endswith('Roads') else 'masonry building foundations'));actor.set_actor_enable_collision(False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();status('saved',counts=counts,mesh_assets=report,total=sum(counts.values()))
