"""Recoverable Gosain kingdom conversion. Imports before changing the level."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain50';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain50'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();M=unreal.MaterialEditingLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN50 '+s)
actors=E.get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
terrain=bymesh('SM_IV_Continent_GosainWallInfill44')
pairs=[(bymesh('SM_Gosain48_'+n),'SM_Gosain50_'+n) for n in ['Capital','FarSouth','FarNorth']]+[(terrain,'SM_IV_Continent_GosainKingdom50')]
townmats={str(s.material_slot_name):s.material_interface for s in pairs[0][0].static_mesh_component.static_mesh.static_materials}
townmats['ivory']=unreal.load_asset(R+'/Gosain42/Materials/M_Gosain42_ivory')
lake=unreal.load_asset('/Game/AdvancedVillagePack/Materials/M_Inst_Water');assert lake
def loadmesh(name,mats,single=None,collision=False):
    if A.does_asset_exist(D+'/Meshes/'+name):return unreal.load_asset(D+'/Meshes/'+name)
    status('importing '+name);task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
    T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
    slots=list(mesh.static_materials)
    for s in slots:s.set_editor_property('material_interface',single if single else mats[str(s.material_slot_name)])
    mesh.set_editor_property('static_materials',slots)
    if collision:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    A.save_loaded_asset(mesh);return mesh
new={}
for actor,name in pairs:
    old=actor.static_mesh_component.static_mesh
    mats={str(s.material_slot_name):s.material_interface for s in old.static_materials}
    new[name]=loadmesh(name,mats,old.static_materials[0].material_interface if actor==terrain else None,actor==terrain)
extra=['SM_Gosain50_KingdomRoutes','SM_Gosain50_TownWalls','SM_Gosain50_RoyalAndKnightGrounds','SM_Gosain50_RoyalLake']
for name in extra:new[name]=loadmesh(name,townmats,lake if name.endswith('RoyalLake') else None,name.endswith('TownWalls'))
status('preparing forest assets')
fts=[]
for i in range(5):
    source='/Game/AdvancedVillagePack/Meshes/SM_Tree_Var0'+str(i+1);path=D+'/Meshes/SM_Gosain50_Tree'+str(i)
    mesh=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(source,path);assert mesh
    ftpath=D+'/Foliage/FT_Gosain50_Tree'+str(i)
    ft=unreal.load_asset(ftpath) if A.does_asset_exist(ftpath) else T.create_asset('FT_Gosain50_Tree'+str(i),D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',mesh);A.save_loaded_asset(ft);fts.append(ft)
# Copy regional terrain material; blend only its existing Gosain meadow output to rock at high elevation.
oldmat=terrain.static_mesh_component.get_material(0);matpath=D+'/Materials/M_Gosain50_RegionalTerrain'
mat=unreal.load_asset(matpath) if A.does_asset_exist(matpath) else A.duplicate_asset(oldmat.get_path_name().split('.')[0],matpath)
changed=0
for node in M.get_material_expressions(mat):
    if isinstance(node,unreal.MaterialExpressionCustom):
        code=node.get_editor_property('code')
        if 'float3 meadow=' in code:
            code=code.replace('return lerp(meadow,R*float3(.40,.46,.49),slope);','float high=smoothstep(180.,380.,q.z+20600.); return lerp(meadow,R*float3(.58,.57,.53),max(slope,high));')
            node.set_editor_property('code',code);changed+=1
assert changed==1,changed
M.recompile_material(mat);A.save_loaded_asset(mat)
def actorstate(a):
    t=a.get_actor_transform();p=t.translation;r=t.rotation;s=t.scale3d
    return [a.get_actor_label(),[p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z],[(c.static_mesh.get_path_name() if c.static_mesh else None,c.get_editor_property('visible'),[m.get_path_name() if m else None for m in c.get_materials()]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]]
hide_labels=['Gosain | CoastalWalls','Gosain | CityStreets','Gosain | PrecinctWalls','Gosain | HouseFootings','Gosain | Capital infill foundations']
hidden=[a for a in actors if a.get_actor_label() in hide_labels]
allowed={a.get_name() for a,n in pairs}|{a.get_name() for a in hidden}
before={a.get_name():actorstate(a) for a in actors if a.get_name() not in allowed and a.get_class().get_name()!='InstancedFoliageActor'}
def foliage_signature():
    out={}
    for a in E.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if not c.static_mesh or '/Gosain50/' in c.static_mesh.get_path_name():continue
            rows=[]
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,True);p=t.translation;r=t.rotation;s=t.scale3d;rows.append(tuple(round(v,4) for v in [p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z]))
            out.setdefault(c.static_mesh.get_path_name(),[]).extend(rows)
    return {k:hashlib.sha256(json.dumps(sorted(v)).encode()).hexdigest() for k,v in out.items()}
oldfoliage=foliage_signature();backup=B/'Saved/WorldBackups'/('BeforeGosain50_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
rollback=[(a,a.static_mesh_component.static_mesh) for a,n in pairs];vis=[(c,c.get_editor_property('visible'),c.get_collision_enabled()) for a in hidden for c in a.get_components_by_class(unreal.StaticMeshComponent)];spawned=[]
trees=json.loads((O/'forest_instances.json').read_text())
try:
    status('applying kingdom terrain and compact towns')
    for a,name in pairs:a.static_mesh_component.set_static_mesh(new[name])
    terrain.static_mesh_component.set_material(0,mat)
    for c,visible,collision in vis:c.set_visibility(False,True);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    for name in extra:
        a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.static_mesh_component.set_static_mesh(new[name]);a.set_actor_label('Gosain | '+name);a.set_folder_path('Regional Civilizations/Gosain/Kingdom50');a.tags=['Gosain50'];spawned.append(a)
    status('planting royal forest')
    groups=[[] for _ in range(5)]
    for x,y,z,yaw,scale,index in trees:groups[int(index)].append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(yaw=yaw,pitch=0,roll=0),scale=unreal.Vector(scale,scale,scale)))
    for ft,rows in zip(fts,groups):unreal.InstancedFoliageActor.add_instances(W,ft,rows)
    after={a.get_name():actorstate(a) for a in E.get_all_level_actors() if a.get_name() in before};assert before==after,'Unrelated actor changed'
    assert oldfoliage==foliage_signature(),'Existing foliage changed'
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    for a,mesh in rollback:a.static_mesh_component.set_static_mesh(mesh)
    terrain.static_mesh_component.set_material(0,oldmat)
    for c,v,col in vis:c.set_visibility(v,True);c.set_collision_enabled(col)
    for a in spawned:E.destroy_actor(a)
    for ft in fts:unreal.InstancedFoliageActor.remove_all_instances(W,ft)
    raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'trees':len(trees),'existing_foliage_unchanged':True,'unrelated_actors_checked':len(before),'hidden_old_actors':[a.get_actor_label() for a in hidden],'new_actors':[a.get_name() for a in spawned],'native_visual_review':'pending'},indent=2));status('saved')
