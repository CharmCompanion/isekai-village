"""Native outside-region comparison; never overwrite the baseline."""
import unreal,json,hashlib,math,re
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'Saved/Gosain38';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
baseline=json.loads((O/'baseline_actors.json').read_text());oldf=json.loads((O/'baseline_foliage.json').read_text())
actors={a.get_name():a for a in E.get_all_level_actors()}
def vec(v):return [v.x,v.y,v.z]
def local(row):return 9000<row[0]/100<30500 and 27500<row[1]/100<47000 and row[2]<-1800000
def signature(mesh,mats,rows):
    # Quantized only for serialization round trips, not geographic movement.
    q=sorted(tuple(round(v,3 if i<3 else 5) for i,v in enumerate(r)) for r in rows if not local(r))
    return hashlib.sha256(json.dumps([mesh,mats,q],separators=(',',':')).encode()).hexdigest(),len(q)
oldgroups={};newgroups={}
for c in oldf:
    key=(c['mesh'],tuple(c['materials']));oldgroups.setdefault(key,[]).extend(c['transforms'])
for a in actors.values():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh=c.static_mesh
        if not mesh:continue
        key=(mesh.get_path_name(),tuple(m.get_path_name() if m else None for m in c.get_materials()))
        rows=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,True);rows.append([*vec(t.translation),*vec(t.scale3d),t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
        newgroups.setdefault(key,[]).extend(rows)
foliage=[]
for key,old in oldgroups.items():
    a,na=signature(*key,old);b,nb=signature(*key,newgroups.get(key,[]));foliage.append({'mesh':key[0],'before_outside':na,'after_outside':nb,'equal':a==b})
changed=[];checked=0;allowed=set()
for row in baseline:
    if row['name'] in allowed or row['class']=='InstancedFoliageActor':continue
    a=actors.get(row['name'])
    if not a:changed.append({'name':row['name'],'problem':'missing'});continue
    now={'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),'rotation':str(a.get_actor_rotation()),'hidden':a.is_hidden_ed(),'tags':[str(t) for t in a.tags]}
    # Rotator string includes a process-specific memory address. Compare angles only.
    old_angles=[float(re.search(key+r': ([+-]?[0-9.]+)',row['rotation']).group(1)) for key in ('pitch','yaw','roll')]
    r=a.get_actor_rotation(); current_angles=[r.pitch,r.yaw,r.roll]
    different=[k for k,v in now.items() if k!='rotation' and v!=row[k]]
    if any(abs((x-y+180)%360-180)>0.00001 for x,y in zip(current_angles,old_angles)):different.append('rotation')
    current=[]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m=c.static_mesh;current.append({'name':c.get_name(),'mesh':m.get_path_name() if m else None,'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
    expected=[{k:c[k] for k in ('name','mesh','materials')} for c in row['components']]
    if current!=expected:different.append('component assets')
    if different:changed.append({'name':row['name'],'label':row['label'],'different':different})
    checked+=1
report={'checked_existing_actors':checked,'unexpected_actor_changes':changed,'outside_foliage':foliage,'outside_foliage_equal':all(c['equal'] for c in foliage),'new_actor_count':len(actors)-len(baseline),'terrain_geometry_report':json.loads((B/'ArtSource/World/Gosain37/terrain_report.json').read_text())}
(O/'native_validation.json').write_text(json.dumps(report,indent=2))
unreal.log('GOSAIN38_VERIFY '+json.dumps({'actors':checked,'unexpected':len(changed),'outside_foliage_equal':report['outside_foliage_equal']}))
