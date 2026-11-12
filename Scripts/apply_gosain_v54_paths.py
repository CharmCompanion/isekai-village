"""Recoverable Gosain kingdom conversion. Imports before changing the level."""
import unreal,json,shutil,time,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain54';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain54'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();M=unreal.MaterialEditingLibrary
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
def status(s):(O/'apply_progress.json').write_text(json.dumps({'stage':s}));unreal.log('GOSAIN50 '+s)
actors=E.get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
pairs=[(bymesh('SM_Gosain47_'+n),'SM_Gosain54_'+n) for n in ['RoadsOutsideCity','FoundationsOutsideCity']]+[(bymesh('SM_Gosain51_KingdomRoutes'),'SM_Gosain54_KingdomRoutes')]
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



path=D+'/Materials/M_Gosain54_ForestTrail'
trail=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Gosain54_ForestTrail',D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
for node in M.get_material_expressions(trail):M.delete_material_expression(trail,node)
if True:
 pos=M.create_material_expression(trail,unreal.MaterialExpressionWorldPosition)
 mask=M.create_material_expression(trail,unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',True);mask.set_editor_property('b',False);mask.set_editor_property('a',False);M.connect_material_expressions(pos,'',mask,'Input')
 factor=M.create_material_expression(trail,unreal.MaterialExpressionConstant);factor.set_editor_property('r',.0025)
 uv=M.create_material_expression(trail,unreal.MaterialExpressionMultiply);M.connect_material_expressions(mask,'',uv,'A');M.connect_material_expressions(factor,'',uv,'B')
 tex=M.create_material_expression(trail,unreal.MaterialExpressionTextureSample);tex.texture=unreal.load_asset('/Game/AdvancedVillagePack/Textures/Landscape/T_Landscape_Soil_DH');M.connect_material_expressions(uv,'',tex,'Coordinates')
 tint=M.create_material_expression(trail,unreal.MaterialExpressionConstant3Vector);tint.constant=unreal.LinearColor(.5,.4,.28,1)
 mul=M.create_material_expression(trail,unreal.MaterialExpressionMultiply);M.connect_material_expressions(tex,'RGB',mul,'A');M.connect_material_expressions(tint,'',mul,'B');M.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=M.create_material_expression(trail,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.95);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(trail);A.save_loaded_asset(trail)
new={}
for a,n in pairs:
 mats={str(v.material_slot_name):v.material_interface for v in a.static_mesh_component.static_mesh.static_materials};mats['foresttrail']=trail
 new[n]=loadmesh(n,mats)
changes=[];groups=[[] for _ in range(5)]
for x,y,z,yaw,scale,index in json.loads((O/'forest_instances.json').read_text()):groups[int(index)].append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(scale,scale,scale)))
for i,rows in enumerate(groups):
 ft=unreal.load_asset(R+'/Gosain50/Foliage/FT_Gosain50_Tree'+str(i));cs=[c for a in E.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.static_mesh==ft.get_editor_property('mesh')];assert len(cs)==1
 c=cs[0];old=[c.get_instance_transform(j,True) for j in range(c.get_instance_count())];changes.append((ft,old,rows))
assert sum(len(old) for ft,old,rows in changes)==30074
backup=B/'Saved/WorldBackups'/('BeforeGosain54_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
rollback=[(a,a.static_mesh_component.static_mesh) for a,n in pairs]
try:
 for a,n in pairs:a.static_mesh_component.set_static_mesh(new[n])
 for ft,old,rows in changes:
  unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for a,m in rollback:a.static_mesh_component.set_static_mesh(m)
 for ft,old,rows in changes:
  unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,old)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'meshes':[n for a,n in pairs],'forest_trees':sum(map(len,groups)),'native_review':'pending'},indent=2))
