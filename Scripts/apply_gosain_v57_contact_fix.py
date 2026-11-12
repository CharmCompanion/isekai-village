import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';D='/Game/IsekaiVillage/AdventureWorld/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
assert (O/'refinement_applied.json').exists() and not (O/'contact_fix_applied.json').exists()
actors=E.get_all_level_actors();labels={a.get_actor_label():a for a in actors};shell=labels['Gosain | Mine hillside and adit'];rock=unreal.load_asset(D+'/Materials/M_Gosain57_WeatheredMine');name='SM_Gosain57_MineLandformJoined';path=D+'/Meshes/'+name
if not A.does_asset_exist(path):
 task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(path);assert mesh
slots=list(mesh.static_materials)
for slot in slots:slot.set_editor_property('material_interface',rock)
mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
backup=B/'Saved/WorldBackups'/('BeforeGosain57Contact_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
shell.static_mesh_component.set_static_mesh(mesh)
for q in json.loads((O/'props_refined.json').read_text()):
 if not q['label'].startswith('Mine weathered outcrop') or int(q['label'].split()[-1])>=4:continue
 a=labels['Gosain | '+q['label']];box=a.static_mesh_component.static_mesh.get_bounding_box();sc=a.get_actor_scale3d();loc=a.get_actor_location();loc.z=q['z']*100-box.min.z*sc.z;a.set_actor_location(loc,False,False)
plan=json.loads((O/'site_plan.json').read_text());C=plan['center'];F=plan['forward'];S=plan['side'];Z=plan['yard_floor_z'];yaw=math.degrees(math.atan2(F[1],F[0]))
def point(d,l,z):return unreal.Vector((C[0]+F[0]*d+S[0]*l)*100,(C[1]+F[1]*d+S[1]*l)*100,(Z+.012*d+z)*100)
for a in actors:
 if isinstance(a,unreal.PointLight) and 'Gosain57Mine' in [str(t) for t in a.tags]:a.point_light_component.set_intensity(70)
lampmesh=labels['Gosain | Mine lantern 4'].static_mesh_component.static_mesh;lamp=E.spawn_actor_from_class(unreal.StaticMeshActor,point(89,-4.4,4.2),unreal.Rotator(pitch=0,yaw=yaw,roll=0));lamp.static_mesh_component.set_static_mesh(lampmesh);lamp.set_actor_scale3d(unreal.Vector(1.6,1.6,1.6));lamp.set_actor_label('Gosain | Deeper workings gate lantern');lamp.tags=['Gosain57Mine'];lamp.set_folder_path('World/Gosain/Mine57')
light=E.spawn_actor_from_class(unreal.PointLight,point(89,-3.8,3.9),unreal.Rotator());light.set_actor_label('Gosain | Deeper workings gate lamplight');light.tags=['Gosain57Mine'];light.set_folder_path('World/Gosain/Mine57');c=light.point_light_component;c.set_intensity(55);c.set_attenuation_radius(900);c.set_light_color(unreal.LinearColor(1,.71,.44,1));c.set_editor_property('source_radius',16)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'contact_fix_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'landform':mesh.get_path_name(),'main_light_candelas':70,'gate_light_candelas':55,'new_actors':2,'native_review':'pending'},indent=2))
