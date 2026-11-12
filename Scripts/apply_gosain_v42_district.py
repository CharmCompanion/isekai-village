"""Replace stock buildings only in two checked street blocks; preserve all roads."""
import unreal,json,shutil,hashlib,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain42';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain42'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists(),'Already applied; inspect checkpoint instead of replaying'
review=json.loads((B/'Docs/WorldDesign/Gosain42/review_complete.json').read_text());assert review['temporary_actor_removed'] and len(review['files'])==3 and not any('FAILED' in p for p in review['files'])
data=json.loads((O/'district.json').read_text());bounds=json.loads((O/'removal_boundary.json').read_text());origin=data['mesh']['origin_m']
def inside(p):
    x,y=p[0]-origin[0],p[1]-origin[1]
    for poly in bounds:
        hit=False
        for a,b in zip(poly,poly[1:]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
        if hit:return True
    return False
def row(t):
    p=t.translation;s=t.scale3d;q=t.rotation;return [p.x,p.y,p.z,s.x,s.y,s.z,q.x,q.y,q.z,q.w]
def signature(rows):return hashlib.sha256(json.dumps(sorted(tuple(round(v,4) for v in r) for r in rows),separators=(',',':')).encode()).hexdigest()
actors=E.get_all_level_actors();comps={c.get_name():c for a in actors for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)}
plans=[];back=[]
for q in json.loads((B/'ArtSource/World/Gosain40/foliage_moves.json').read_text()):
    if '/Gosain39/Foliage/' not in q['foliage_type']:continue
    ft=unreal.load_asset(q['foliage_type']);c=comps[q['component']];assert ft and ft.get_editor_property('mesh')==c.static_mesh
    assert c.get_instance_count()==q['count'],(q['component'],c.get_instance_count(),q['count'])
    bb=c.static_mesh.get_bounding_box();center=(bb.min+bb.max)*.5
    old=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())];keep=[];removed=[]
    for i,t in enumerate(old):
        p=unreal.MathLibrary.transform_location(t,center)
        if inside([p.x/100,p.y/100]) and p.z<-1800000:removed.append(i)
        else:keep.append(t)
    back.append({'foliage_type':q['foliage_type'],'mesh':c.static_mesh.get_path_name(),'old_transforms':[row(t) for t in old],'removed_indices':removed,'expected_keep_signature':signature([row(t) for t in keep])})
    if removed:plans.append((ft,old,keep))
assert sum(len(q['removed_indices']) for q in back)>0
replacements=[]
for q in json.loads((O/'foundation_cleanup.json').read_text()):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==q['old_name']];assert len(found)==1
    a=found[0];old=a.static_mesh_component.static_mesh
    task=unreal.AssetImportTask();task.filename=str(O/(q['name']+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=q['name'];task.automated=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;task.options=op
    T.import_asset_tasks([task]);m=unreal.load_asset(D+'/Meshes/'+q['name']);assert m
    for i,s in enumerate(m.static_materials):m.set_material(i,old.static_materials[0].material_interface)
    A.save_loaded_asset(m);replacements.append((a,old,m))
def actor_state(a):
    p=a.get_actor_location();s=a.get_actor_scale3d();r=a.get_actor_rotation()
    return [a.get_name(),[p.x,p.y,p.z],[s.x,s.y,s.z],[r.pitch,r.yaw,r.roll],[[c.get_name(),c.static_mesh.get_path_name() if c.static_mesh else None,[m.get_path_name() if m else None for m in c.get_materials()]] for c in a.get_components_by_class(unreal.StaticMeshComponent)],a.is_hidden_ed()]
allowed={a.get_name() for a,old,new in replacements}
before={a.get_name():actor_state(a) for a in actors if a.get_class().get_name()!='InstancedFoliageActor' and a.get_name() not in allowed}
changed_meshes={q['mesh'] for q in back}
def other_foliage():
    groups={}
    for a in E.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_path_name() in changed_meshes:continue
            key=c.static_mesh.get_path_name();groups.setdefault(key,[]).extend(row(c.get_instance_transform(i,True)) for i in range(c.get_instance_count()))
    return {k:signature(v) for k,v in groups.items()}
outside=other_foliage();backup=B/'Saved/WorldBackups'/('BeforeGosain42_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap');(O/'foliage_rollback.json').write_text(json.dumps(back));(O/'baseline.json').write_text(json.dumps({'actors':before,'other_foliage':outside}))
mesh=unreal.load_asset(D+'/Meshes/'+data['mesh']['name']);assert mesh
# OBJ importer must recover the world-source axes rather than mirror this district.
bb=mesh.get_bounding_box();assert bb.max.y<5000 and bb.min.y<-15000,(bb.min,bb.max)
newactor=None
try:
    newactor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in origin]));newactor.static_mesh_component.set_static_mesh(mesh);newactor.set_actor_label('Gosain | Street-grown masonry quarter 42');newactor.set_folder_path('Regional Civilizations/Gosain/Capital42');newactor.tags=['Gosain42','StreetGrownQuarter']
    for a,old,m in replacements:a.static_mesh_component.set_static_mesh(m)
    for ft,old,keep in plans:unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,keep)
    after={a.get_name():actor_state(a) for a in E.get_all_level_actors() if a.get_name() in before}
    assert before==after,'Unexpected actor changes'
    assert outside==other_foliage(),'Unexpected unrelated foliage change'
    expected={};actual={}
    for q in back:
        gone=set(q['removed_indices']);expected.setdefault(q['mesh'],[]).extend(t for i,t in enumerate(q['old_transforms']) if i not in gone)
    for a in E.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_path_name() in expected:actual.setdefault(c.static_mesh.get_path_name(),[]).extend(row(c.get_instance_transform(i,True)) for i in range(c.get_instance_count()))
    assert all(signature(v)==signature(actual.get(k,[])) for k,v in expected.items()),'Retained house transforms changed'
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    if newactor:E.destroy_actor(newactor)
    for a,old,m in replacements:a.static_mesh_component.set_static_mesh(old)
    for ft,old,keep in plans:unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,old)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();raise
report={'status':'saved','actor':newactor.get_name(),'buildings':len(data['buildings']),'removed_stock_houses':sum(len(q['removed_indices']) for q in back),'retained_houses_verified':True,'backup':str(backup),'replacements':[{'actor':a.get_name(),'old':old.get_path_name(),'new':m.get_path_name()} for a,old,m in replacements],'existing_actors_unchanged':len(before),'unrelated_foliage_unchanged':True,'street_intersection_m2':data['street_intersection_m2'],'limitations':data['limitations']}
(O/'applied.json').write_text(json.dumps(report,indent=2))
