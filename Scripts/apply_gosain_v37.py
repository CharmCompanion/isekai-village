"""Apply a backed-up, capital-only milestone. Never run the global Civ36 clearer."""
import unreal,json,hashlib,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain37'
R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain37'
A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert (B/'Saved/WorldBackups/BeforeGosain37_20261013/Map_AnimeAdventure.umap').exists()
data=json.loads((O/'Gosain37.json').read_text());baseline=json.loads((B/'Saved/Gosain37/baseline_foliage.json').read_text())
assert not any('Gosain37' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Already applied; use a refinement script, not a second initial apply.'
report={'stage':'preflight'}
def status(stage,**kw):
    report.update(stage=stage,**kw);(B/'Saved/Gosain37/apply_result.json').write_text(json.dumps(report,indent=2));unreal.log('GOSAIN37 '+stage)
components={c.get_name():c for a in E.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent)}
source=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v36.json').read_text())
plans=[]
for row in baseline:
    if row['name'] not in data['remove']:continue
    c=components[row['name']];assert c.get_instance_count()==row['count'],row['name']
    matches=[k for k,p in source['assets'].items() if p==row['mesh'].split('.')[0] and len(source['instances'].get(k,[]))==row['count']]
    if len(matches)==1:ftpath=R+'/Foliage/Civilizations/FT_Civ36_'+matches[0]
    else:
        mapping={'FoliageInstancedStaticMeshComponent_166':'Oak','FoliageInstancedStaticMeshComponent_167':'OakVar','FoliageInstancedStaticMeshComponent_168':'Pine'}
        assert row['name'] in mapping,('Unresolved foliage type',row['name'],matches)
        ftpath=R+'/Foliage/FT_Continent17_'+mapping[row['name']]
    ft=unreal.load_asset(ftpath);assert ft and ft.get_editor_property('mesh')==c.static_mesh,ftpath
    removal=set(data['remove'][row['name']]);keep=[c.get_instance_transform(i,True) for i in range(c.get_instance_count()) if i not in removal]
    plans.append((ft,c,keep,len(removal)))
status('preflight passed',foliage_types=len(plans),remove_count=sum(p[3] for p in plans))

def create_node(mat,cls):return M.create_material_expression(mat,cls)
def custom(mat,code,inputs,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=create_node(mat,unreal.MaterialExpressionCustom);pins=[]
    for name in inputs:
        p=unreal.CustomInput();p.set_editor_property('input_name',name);pins.append(p)
    n.set_editor_property('inputs',pins);n.set_editor_property('output_type',typ);n.set_editor_property('code',code)
    for k,val in inputs.items():assert M.connect_material_expressions(val,'',n,k),k
    return n
def tex(mat,path,uv,linear=False):
    n=create_node(mat,unreal.MaterialExpressionTextureSample);n.texture=unreal.load_asset(path);assert n.texture,path
    n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR if linear else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR
    assert M.connect_material_expressions(uv,'',n,'UVs');return n
def constant(mat,v):n=create_node(mat,unreal.MaterialExpressionConstant);n.r=v;return n
def tiled_material(name,texture,tint=(1,1,1),scale=250):
    path=D+'/Materials/M_Gosain37_'+name
    mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Gosain37_'+name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    p=create_node(mat,unreal.MaterialExpressionWorldPosition);n=create_node(mat,unreal.MaterialExpressionVertexNormalWS);samples=[]
    for plane in ('yz','xz','xy'):
        uv=custom(mat,'return P.'+plane+f'/{float(scale)};',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2);samples.append(tex(mat,texture,uv))
    code='float3 w=pow(abs(N),4);w/=max(dot(w,1),.001);float3 c=A*w.x+B*w.y+C*w.z;float macro=.94+.06*sin(P.x/3100.+sin(P.y/1900.))*cos(P.z/2300.);'
    if name=='roof':code+='c=dot(c,float3(.3,.5,.2))*float3(.35,.72,1.05);'
    code+='return saturate(c*float3(%s,%s,%s)*macro);'%tint
    color=custom(mat,code,{'P':p,'N':n,'A':samples[0],'B':samples[1],'C':samples[2]})
    assert M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    M.connect_material_property(constant(mat,.84),'',unreal.MaterialProperty.MP_ROUGHNESS)
    M.connect_material_property(constant(mat,.25),'',unreal.MaterialProperty.MP_SPECULAR)
    M.recompile_material(mat);A.save_loaded_asset(mat);return mat
textures='/Game/Fantastic_Village_Pack/textures/'
mats={
 'stone':tiled_material('stone',textures+'T_stonebrick_01_BC',(1.2,1.13,1.0),330),
 'trim':tiled_material('trim',textures+'T_ENV_stone_BC',(1.38,1.31,1.16),250),
 'foundation':tiled_material('foundation',textures+'T_stonebrick_02_BC',(.9,.96,.94),260),
 'paving':tiled_material('paving',textures+'T_ENV_pavingstone_02_BC',(1.1,1.08,.97),400),
 'roof':tiled_material('roof',textures+'T_rooftiles_02_BC',(1,1,1),240),
}
status('private masonry materials created')
task=unreal.AssetImportTask();task.filename=str(O/'T_Gosain37_Region.png');task.destination_path=D+'/Textures';task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
mask=unreal.load_asset(D+'/Textures/T_Gosain37_Region');mask.set_editor_property('srgb',False);mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_GRAYSCALE);mask.set_editor_property('never_stream',True);mask.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);mask.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(mask)

# A private material copy changes only the two Gosain islands. Every other region
# keeps the old material outputs with a precisely zero blend mask.
continent=next(a for a in E.get_all_level_actors() if a.get_name()=='StaticMeshActor_1128')
oldmat=continent.static_mesh_component.get_material(0)
landpath=D+'/Materials/M_Gosain37_RegionalTerrain'
land=unreal.load_asset(landpath) if A.does_asset_exist(landpath) else A.duplicate_asset(oldmat.get_path_name().split('.')[0],landpath)
assert land
oldbase=M.get_material_property_input_node(land,unreal.MaterialProperty.MP_BASE_COLOR);oldem=M.get_material_property_input_node(land,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
p=create_node(land,unreal.MaterialExpressionWorldPosition);n=create_node(land,unreal.MaterialExpressionVertexNormalWS);cam=create_node(land,unreal.MaterialExpressionCameraPositionWS)
uv=custom(land,'return float2((-P.x/8000.+814.174101)/1758.,(638.308916-P.y/8000.)/1185.);',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
masknode=tex(land,D+'/Textures/T_Gosain37_Region',uv,True)
masknode.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE
guv=custom(land,'return P.xy/450.;',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
grass=tex(land,'/Game/SoStylized/Environment/Landscape/Textures/T_Grass1_BC',guv)
dirt=tex(land,'/Game/SoStylized/Environment/Landscape/Textures/T_Dirt1_BC',guv)
ruv=custom(land,'return P.xy/1650.;',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
rock=tex(land,'/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC',ruv)
color=custom(land,'float3 q=P/100.;float macro=.5+.24*sin(q.x/165.+sin(q.y/215.))+.20*cos(q.y/120.+q.x/390.);float3 meadow=lerp(float3(.10,.205,.09),float3(.26,.36,.14),saturate(macro));float lum=clamp(dot(G,float3(.3,.5,.2))*3.6,.62,1.24);meadow*=lum;float worn=.12+.1*(1.-saturate(macro));meadow=lerp(meadow,D*.72,worn);float slope=1.-smoothstep(.66,.95,abs(N.z));float3 stone=R*float3(.88,.98,1.03);return lerp(meadow,stone,slope);',{'P':p,'N':n,'G':grass,'D':dirt,'R':rock})
close=custom(land,'return 1.-smoothstep(350000.,850000.,distance(P,C));',{'P':p,'C':cam},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
base=custom(land,'return lerp(Old,New*lerp(.65,1.,Close),Mask.r);',{'Old':oldbase,'New':color,'Mask':masknode,'Close':close})
em=custom(land,'return lerp(Old,New*lerp(.28,.025,Close),Mask.r);',{'Old':oldem,'New':color,'Mask':masknode,'Close':close})
M.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
oldnormal=M.get_material_property_input_node(land,unreal.MaterialProperty.MP_NORMAL)
if oldnormal:
    normal=custom(land,'return normalize(lerp(Old,N,Mask.r));',{'Old':oldnormal,'N':n,'Mask':masknode});M.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
M.recompile_material(land);A.save_loaded_asset(land)
status('regional terrain material created')

def import_mesh(name,material_map=None):
    task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);task.options=op
    T.import_asset_tasks([task]);m=unreal.load_asset(D+'/Meshes/'+name);assert m,name
    if material_map:
        for i,s in enumerate(m.static_materials):
            k=str(s.material_slot_name);assert k in material_map,(name,k);m.set_material(i,material_map[k])
    bs=SS.get_lod_build_settings(m,0);bs.recompute_normals=False;bs.use_high_precision_tangent_basis=True;SS.set_lod_build_settings(m,0,bs)
    A.save_loaded_asset(m);return m
meshes={}
for q in data['meshes']:meshes[q['name']]=import_mesh(q['name'],mats);status('imported '+q['name'])
legacy_mats={}
for pth in A.list_assets(R+'/Materials/Civilizations',recursive=False):
    if '/M_Civ30_' in pth:legacy_mats[pth.split('M_Civ30_')[-1].split('.')[0]]=unreal.load_asset(pth)
for q in data['filtered']:meshes[q['name']]=import_mesh(q['name'],legacy_mats);status('imported '+q['name'])
terrain=import_mesh('SM_IV_Continent_GosainTerraces37');terrain.set_material(0,land);A.save_loaded_asset(terrain)
status('terrain imported; applying capital layout')

# All inputs are now ready. No shared assets are edited below.
removed=[]
for ft,c,keep,count in plans:
    name=c.get_name();unreal.InstancedFoliageActor.remove_all_instances(W,ft)
    if keep:unreal.InstancedFoliageActor.add_instances(W,ft,keep)
    removed.append({'component':name,'type':ft.get_path_name(),'removed':count,'preserved':len(keep)})
continent.static_mesh_component.set_static_mesh(terrain);continent.static_mesh_component.set_material(0,land)
for q in data['filtered']:
    a=next(a for a in E.get_all_level_actors() if q['replaces_tag'] in [str(t) for t in a.tags]);a.static_mesh_component.set_static_mesh(meshes[q['name']])
for q in data['meshes']:
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in q['origin_m']]))
    a.static_mesh_component.set_static_mesh(meshes[q['name']]);a.tags=['Gosain37',q['name']];a.set_actor_label(q['name'].replace('SM_Gosain37_','Gosain | '));a.set_folder_path('Regional Civilizations/Gosain/Capital37');a.set_actor_enable_collision(False)

counts={}
for key,instances in data['instances'].items():
    mesh=unreal.load_asset(data['assets'][key]);assert mesh,key
    if key.startswith('SM_Civ'):
        newpath=D+'/Meshes/'+key+'_Gosain37';mesh=unreal.load_asset(newpath) if A.does_asset_exist(newpath) else A.duplicate_asset(mesh.get_path_name().split('.')[0],newpath)
        for i,s in enumerate(mesh.static_materials):
            k=str(s.material_slot_name)
            if k in mats:mesh.set_material(i,mats[k])
        A.save_loaded_asset(mesh)
    ftpath=D+'/Foliage/FT_Gosain37_'+key
    ft=unreal.load_asset(ftpath) if A.does_asset_exist(ftpath) else T.create_asset('FT_Gosain37_'+key,D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));ft.set_editor_property('cast_shadow',True);A.save_loaded_asset(ft)
    transforms=[unreal.Transform(location=unreal.Vector(p[0]*100,p[1]*100,p[2]*100),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*p[3:6])) for p in instances]
    unreal.InstancedFoliageActor.add_instances(W,ft,transforms);counts[key]=len(instances)
    status('placed '+key,counts=counts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
status('saved',counts=counts,removed=removed,material_original=oldmat.get_path_name(),protected_region='El Ruhn untouched; verify next',terrain_asset=terrain.get_path_name())
