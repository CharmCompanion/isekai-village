"""Place the existing landmark complex on the summit; remove false terrain ripples."""
import unreal,json,shutil,time,math,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain43';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain43';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'visual_refine_applied.json').exists()
actors=E.get_all_level_actors();comps=[c for a in actors for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)]
def row(t):
    p=t.translation;s=t.scale3d;q=t.rotation;return [p.x,p.y,p.z,s.x,s.y,s.z,q.x,q.y,q.z,q.w]
def sig(rows):return hashlib.sha256(json.dumps(sorted(tuple(round(v,3 if i<3 else 5) for i,v in enumerate(r)) for r in rows),separators=(',',':')).encode()).hexdigest()
def foliage_state():
    groups={}
    for a in E.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.static_mesh:groups.setdefault(c.static_mesh.get_path_name(),[]).extend(row(c.get_instance_transform(i,True)) for i in range(c.get_instance_count()))
    return groups
def actor_state(a):
    p=a.get_actor_location();s=a.get_actor_scale3d();r=a.get_actor_rotation()
    return [a.get_name(),[p.x,p.y,p.z],[s.x,s.y,s.z],[r.pitch,r.yaw,r.roll],[[c.get_name(),c.static_mesh.get_path_name() if c.static_mesh else None,[m.get_path_name() if m else None for m in c.get_materials()]] for c in a.get_components_by_class(unreal.StaticMeshComponent)],a.is_hidden_ed()]
terrain=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainTerraces43')
precinct=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_Gosain37_PrecinctWalls_Relief40_Terraces43')
allowed={terrain.get_name(),precinct.get_name()};before={a.get_name():actor_state(a) for a in actors if a.get_class().get_name()!='InstancedFoliageActor' and a.get_name() not in allowed};oldfol=foliage_state();expected={k:list(v) for k,v in oldfol.items()}
plans=[];rollback=[];offset=unreal.Vector(30000,65000,8000)
endpoints=json.loads((B/'ArtSource/World/Gosain38/whole_island_plan.json').read_text())['bridge_endpoints_m'];ex=endpoints[1][0]-endpoints[0][0];ey=endpoints[1][1]-endpoints[0][1];length=math.hypot(ex,ey);ex/=length;ey/=length
for q in json.loads((O/'foliage_moves.json').read_text()):
    landmark='/Gosain37/Meshes/SM_Civ' in q['mesh']
    clutter=('/AdvancedVillagePack/Meshes/SM_House' in q['mesh'] or 'SM_Civ30_SacredTower.' in q['mesh'])
    if not landmark and not clutter:continue
    found=[c for c in comps if c.static_mesh and c.static_mesh.get_path_name()==q['mesh'] and c.get_instance_count()==q['count']];assert len(found)==1,(q['mesh'],len(found))
    c=found[0];ft=unreal.load_asset(q['foliage_type']);assert ft and ft.get_editor_property('mesh')==c.static_mesh
    old=[c.get_instance_transform(i,True) for i in range(c.get_instance_count())];new=[];removed=[]
    for i,t in enumerate(old):
        p=t.translation
        if landmark:
            n=c.get_instance_transform(i,True);n.translation=p+offset;new.append(n)
        else:
            dx=p.x/100-endpoints[0][0];dy=p.y/100-endpoints[0][1];along=dx*ex+dy*ey;side=abs(-dx*ey+dy*ex)
            if -350<along<length+350 and side<70 and p.z<-1800000:removed.append(i)
            else:new.append(t)
    if landmark or removed:
        plans.append((ft,old,new));rollback.append({'type':q['foliage_type'],'old':[row(t) for t in old],'removed':removed,'moved_to_summit':landmark})
        # Each selected type has a distinct mesh/count pairing; subtract only its rows.
        remaining=list(expected[q['mesh']])
        for t in old:remaining.remove(row(t))
        expected[q['mesh']]=remaining+[row(t) for t in new]
backup=B/'Saved/WorldBackups'/('BeforeGosain43Visual_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
(O/'visual_refine_rollback.json').write_text(json.dumps(rollback))
oldmat=terrain.static_mesh_component.get_material(0);path=D+'/Materials/M_Gosain43_RegionalTerrain';mat=A.duplicate_asset(oldmat.get_path_name().split('.')[0],path) if not A.does_asset_exist(path) else unreal.load_asset(path);assert mat
changed=[]
for n in M.get_material_expressions(mat):
    if isinstance(n,unreal.MaterialExpressionCustom) and 'float3 meadow=' in n.get_editor_property('code'):
        n.set_editor_property('code','''float3 q=P/100.;
float2 cell=floor(q.xy/1250.);float2 f=frac(q.xy/1250.);f=f*f*(3.-2.*f);
float a=frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);
float b=frac(sin(dot(cell+float2(1,0),float2(127.1,311.7)))*43758.5453);
float c=frac(sin(dot(cell+float2(0,1),float2(127.1,311.7)))*43758.5453);
float d=frac(sin(dot(cell+1.,float2(127.1,311.7)))*43758.5453);
float macro=lerp(lerp(a,b,f.x),lerp(c,d,f.x),f.y);
float3 meadow=float3(.029,.069,.025)*lerp(.94,1.06,macro);
meadow*=clamp(dot(G,float3(.3,.5,.2))*4.2,.92,1.08);
meadow=lerp(meadow,D*.16,.10);
float slope=1.-smoothstep(.66,.95,abs(N.z));
return lerp(meadow,R*float3(.40,.46,.49),slope);''');changed.append(n.get_name())
assert len(changed)==1;M.recompile_material(mat);assert A.save_loaded_asset(mat)
oldpos=precinct.get_actor_location()
try:
    terrain.static_mesh_component.set_material(0,mat);precinct.set_actor_location(oldpos+offset,False,False)
    for ft,old,new in plans:unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,new)
    actual=foliage_state();assert all(sig(v)==sig(actual.get(k,[])) for k,v in expected.items()),'Unexpected foliage change'
    after={a.get_name():actor_state(a) for a in E.get_all_level_actors() if a.get_name() in before};assert before==after,'Unexpected actor change'
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    terrain.static_mesh_component.set_material(0,oldmat);precinct.set_actor_location(oldpos,False,False)
    for ft,old,new in plans:unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,old)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();raise
report={'status':'saved','backup':str(backup),'moved_complex_m':[300,650,80],'landmark_instances_moved':sum(len(r['old']) for r in rollback if r['moved_to_summit']),'bridge_clutter_removed':sum(len(r['removed']) for r in rollback),'unrelated_actors_unchanged':len(before),'all_foliage_matches_expected':True,'material':mat.get_path_name(),'material_scope':'Copied regional material; only existing Gosain meadow custom node changed; regional blend mask and other outputs preserved.','remaining':'Castle architecture is still the existing landmark prototype. Engineer summit approach roads and final connected city architecture next.'}
(O/'visual_refine_applied.json').write_text(json.dumps(report,indent=2))
exec(compile((B/'Scripts/render_gosain_v43_world.py').read_text(),str(B/'Scripts/render_gosain_v43_world.py'),'exec'),{'__name__':'__main__'})
