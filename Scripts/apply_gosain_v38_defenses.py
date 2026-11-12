"""Apply backed-up regional defenses; retain all non-Gosain instance transforms."""
import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain38';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain38'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert (B/'Saved/WorldBackups/BeforeGosain38_20261014/Map_AnimeAdventure.umap').exists()
assert not any('Gosain38' in [str(t) for t in a.tags] for a in E.get_all_level_actors())
data=json.loads((O/'defenses.json').read_text());plan=json.loads((O/'whole_island_plan.json').read_text())
report={'stage':'preflight','removed':[]}
def status(stage):
    report['stage']=stage;(B/'Saved/Gosain38/apply_defenses_result.json').write_text(json.dumps(report,indent=2))
def regional(p):return 9000<p.x/100<30500 and 27500<p.y/100<47000 and p.z<-1800000
sources=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v36.json').read_text())['assets']
baseline=json.loads((B/'Saved/Gosain38/baseline_foliage.json').read_text())
components={c.get_name():c for a in E.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)}
removals=[]
for key in ('SM_Civ33_EmpireWall','SM_Civ30_Bastion','SM_Civ30_Banner','SM_Civ30_Gatehouse'):
    ft=unreal.load_asset(R+'/Foliage/Civilizations/FT_Civ36_'+key);assert ft
    rows=[r for r in baseline if r['mesh'].split('.')[0]==sources[key]];assert len(rows)==1
    c=components[rows[0]['name']];keep=[];count=0
    for i in range(c.get_instance_count()):
        t=c.get_instance_transform(i,True)
        if regional(t.translation):count+=1
        else:keep.append(t)
    removals.append((ft,keep,count))
meshes={}
for q in data['meshes']:
    name=q['name'];status('importing '+name)
    task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
    T.import_asset_tasks([task]);m=unreal.load_asset(D+'/Meshes/'+name);assert m
    for i,s in enumerate(m.static_materials):
        mat=unreal.load_asset(R+'/Gosain37/Materials/M_Gosain37_'+str(s.material_slot_name));assert mat
        m.set_material(i,mat)
    A.save_loaded_asset(m);meshes[name]=m
for ft,keep,count in removals:
    unreal.InstancedFoliageActor.remove_all_instances(W,ft)
    if keep:unreal.InstancedFoliageActor.add_instances(W,ft,keep)
    report['removed'].append({'type':ft.get_path_name(),'removed':count,'preserved':len(keep)})
for q in data['meshes']:
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in q['origin_m']]))
    a.static_mesh_component.set_static_mesh(meshes[q['name']]);a.tags=['Gosain38',q['name']];a.set_actor_label(q['name'].replace('SM_Gosain38_','Gosain | '));a.set_folder_path('Regional Civilizations/Gosain/Coastal38');a.set_actor_enable_collision(False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report['mesh_count']=len(meshes);status('saved')
