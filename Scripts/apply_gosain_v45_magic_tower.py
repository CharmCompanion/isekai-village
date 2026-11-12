"""Add an isolated, recoverable tower landmark; never edit shared assets or unrelated actors."""
import unreal,json,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain45';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain45'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert (B/'ArtSource/World/Gosain44/applied.json').exists()
assert not (O/'applied.json').exists(),'Already applied'
q=json.loads((O/'tower.json').read_text())
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}))
def material(name,color,emission=0,metal=0):
    path=D+'/Materials/M_Gosain45_'+name
    assert not A.does_asset_exist(path),'Use a new version for existing materials'
    mat=T.create_asset('M_Gosain45_'+name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    c=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*color,1);M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    r=M.create_material_expression(mat,unreal.MaterialExpressionConstant);r.r=.30 if metal else .45;M.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
    if metal:
        n=M.create_material_expression(mat,unreal.MaterialExpressionConstant);n.r=metal;M.connect_material_property(n,'',unreal.MaterialProperty.MP_METALLIC)
    if emission:
        n=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);n.constant=unreal.LinearColor(*[v*emission for v in color],1);M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    M.recompile_material(mat);A.save_loaded_asset(mat);return mat
status('preparing private accent materials')
mats={k:unreal.load_asset(R+'/Gosain42/Materials/M_Gosain42_'+v) for k,v in {'stone':'ivory','trim':'trim','foundation':'foundation','recess':'recess'}.items()}
assert all(mats.values())
mats['gold']=material('Gold',(.58,.36,.09),metal=.65)
mats['glass']=material('CyanCrystal',(.015,.44,.65),1.7)
mats['magic']=material('ArcaneOrbit',(.03,.56,.85),3)
status('importing tower')
task=unreal.AssetImportTask();task.filename=str(O/(q['name']+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=q['name'];task.automated=True;task.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+q['name']);assert mesh
slots=list(mesh.static_materials)
for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name)])
mesh.set_editor_property('static_materials',slots)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
A.save_loaded_asset(mesh)
bb=mesh.get_bounding_box();assert abs(bb.max.z/100-427)<.2,(bb.min,bb.max)
def state(a):
    t=a.get_actor_transform();p=t.translation;r=t.rotation;s=t.scale3d;return [str(a.get_class().get_name()),[p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z],a.is_hidden_ed(),[str(x) for x in a.tags],[(c.static_mesh.get_path_name() if c.static_mesh else None,[m.get_path_name() if m else None for m in c.get_materials()]) for c in a.get_components_by_class(unreal.StaticMeshComponent)]]
# Object string representations can contain addresses; retained actor objects are compared in the same process.
before={a.get_name():state(a) for a in E.get_all_level_actors()}
backup=B/'Saved/WorldBackups'/('BeforeGosain45_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
actor=None
try:
    status('placing tower on second island')
    actor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[x*100 for x in q['origin_m']]))
    actor.static_mesh_component.set_static_mesh(mesh);actor.set_actor_label('Gosain | Great Arcane Tower 45');actor.set_folder_path('Regional Civilizations/Gosain/Arcane Landmark');actor.tags=['Gosain45','ApprovedConceptLandmark']
    after={a.get_name():state(a) for a in E.get_all_level_actors() if a.get_name() in before}
    # Explicit scalar transform comparison avoids transient Python wrapper addresses.
    for name in before:
        assert before[name]==after[name],name
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    if actor:E.destroy_actor(actor)
    raise
(O/'applied.json').write_text(json.dumps({'status':'saved','actor':actor.get_name(),'mesh':mesh.get_path_name(),'origin_m':q['origin_m'],'backup':str(backup),'existing_actor_properties_checked':len(before),'limitations':q['limitations'],'native_visual_review':'pending'},indent=2));status('saved')
