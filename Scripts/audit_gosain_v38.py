"""Read-only baseline of the actual world; capture assets and actor state."""
import unreal, json, hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O=B/'Saved/Gosain38'; O.mkdir(exist_ok=True)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
actors=[]; foliage=[]
def vec(v): return [v.x,v.y,v.z]
for a in E.get_all_level_actors():
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),'rotation':str(a.get_actor_rotation()),'tags':[str(t) for t in a.tags],'hidden':a.is_hidden_ed(),'folder':str(a.get_folder_path())}
    comps=[]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        q={'name':c.get_name(),'mesh':m.get_path_name() if m else None,'materials':[x.get_path_name() if x else None for x in c.get_materials()]}
        if isinstance(c,unreal.InstancedStaticMeshComponent):
            q['count']=c.get_instance_count()
            rows=[]
            for i in range(q['count']):
                t=c.get_instance_transform(i,True)
                rows.append([*vec(t.translation),*vec(t.scale3d),t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
            q['transforms_sha256']=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
            foliage.append({'actor':a.get_name(),**q,'transforms':rows})
        comps.append(q)
    row['components']=comps;actors.append(row)
(O/'baseline_actors.json').write_text(json.dumps(actors,indent=1))
(O/'baseline_foliage.json').write_text(json.dumps(foliage,separators=(',',':')))
assets=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v36.json').read_text())['assets']
reg=unreal.AssetRegistryHelpers.get_asset_registry()
for path in ['/Game/Fantastic_Village_Pack/meshes/buildings','/Game/Fantastic_Village_Pack/meshes/props/construction','/Game/SoStylized/Environment/Rocks']:
    for d in reg.get_assets_by_path(path,recursive=True):
        if str(d.asset_class_path.asset_name)=='StaticMesh': assets[str(d.asset_name)]=str(d.package_name)
meshes={}
for k,p in assets.items():
    if any(w in k.lower() for w in ('house','cathedral','bastion','wall','gate','stone','church','tower','bridge','stairs')):
        m=unreal.load_asset(p)
        if isinstance(m,unreal.StaticMesh):
            b=m.get_bounding_box();meshes[k]={'path':p,'min':vec(b.min),'max':vec(b.max),'materials':[x.material_interface.get_path_name() if x.material_interface else None for x in m.static_materials]}
(O/'mesh_audit.json').write_text(json.dumps(meshes,indent=2))
ma=[]
for a in E.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    mesh=a.static_mesh_component.static_mesh
    if not mesh or 'PuzzleContinent' not in mesh.get_name() or a.is_hidden_ed():continue
    for mat in a.static_mesh_component.get_materials():
        if not isinstance(mat,unreal.Material):continue
        nodes=[]
        for n in unreal.MaterialEditingLibrary.get_material_expressions(mat):
            q={'name':n.get_name(),'class':n.get_class().get_name()}
            if isinstance(n,unreal.MaterialExpressionCustom):q['code']=n.get_editor_property('code')
            if isinstance(n,unreal.MaterialExpressionTextureSample):
                t=n.get_editor_property('texture');q['texture']=t.get_path_name() if t else None
            nodes.append(q)
        out=unreal.MaterialEditingLibrary.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
        ma.append({'actor':a.get_name(),'material':mat.get_path_name(),'base_node':out.get_name() if out else None,'nodes':nodes})
(O/'continent_material.json').write_text(json.dumps(ma,indent=2))
try:
    s=unreal.load_object(None,'/Script/UnrealEd.Default__EditorPerformanceSettings')
    s.set_editor_property('bThrottleCPUWhenNotForeground',False)
    unreal.SystemLibrary.execute_console_command(W,'t.IdleWhenNotForeground 0')
except Exception: pass
unreal.log('GOSAIN38_AUDIT_DONE actors=%d foliage=%d meshes=%d'%(len(actors),len(foliage),len(meshes)))
