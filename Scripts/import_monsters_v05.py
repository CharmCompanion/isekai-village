"""Import new authored monsters and a separate review map; preserve game maps."""
import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'ArtSource/Monsters/Models_v05';R='/Game/IsekaiVillage/Monsters/Refined_v05'
A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);SS=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
manifest=json.loads((S/'model_manifest.json').read_text());assert len(manifest['models'])==9
report={'stage':'starting','models':[],'errors':[]}
def status(stage):
    report['stage']=stage;(B/'Saved/monster_import_v05.json').write_text(json.dumps(report,indent=2))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
for path in [R+'/Materials',R+'/Textures',R+'/Maps']:
    A.make_directory(path)
for file in (S/'Textures').glob('*.png'):
    task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=R+'/Textures';task.destination_name=file.stem;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
    tex=unreal.load_asset(R+'/Textures/'+file.stem)
    if 'Roughness' in file.stem or 'Normal' in file.stem:tex.set_editor_property('srgb',False)
    if 'Normal' in file.stem:
        tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('flip_green_channel',True)
    A.save_loaded_asset(tex)
tex=unreal.load_asset(R+'/Textures/T_IV_MonsterPalette_v05');assert tex

def scalar(mat,name,value):
    n=M.create_material_expression(mat,unreal.MaterialExpressionScalarParameter);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
def parent(name,gel=False):
    path=R+'/Materials/'+name
    mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);sample.set_editor_property('parameter_name','Palette');sample.set_editor_property('texture',tex)
    authored_uv=M.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);authored_uv.set_editor_property('coordinate_index',1);M.connect_material_expressions(authored_uv,'',sample,'UVs')
    M.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
    for pname,value,prop in [('Roughness',.55,unreal.MaterialProperty.MP_ROUGHNESS),('Metallic',0.,unreal.MaterialProperty.MP_METALLIC)]:M.connect_material_property(scalar(mat,pname,value),'',prop)
    normal=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);normal.set_editor_property('parameter_name','SurfaceNormal');normal.set_editor_property('texture',unreal.load_asset(R+'/Textures/T_IV_MonsterNormal_v05'));normal.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);M.connect_material_property(normal,'RGB',unreal.MaterialProperty.MP_NORMAL)
    rough=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);rough.set_editor_property('parameter_name','SurfaceRoughness');rough.set_editor_property('texture',unreal.load_asset(R+'/Textures/T_IV_MonsterRoughness_v05'));rough.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);M.connect_material_property(rough,'R',unreal.MaterialProperty.MP_ROUGHNESS)
    mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);M.connect_material_expressions(sample,'RGB',mul,'A');M.connect_material_expressions(scalar(mat,'Glow',0.),'',mul,'B');M.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if gel:
        mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);M.connect_material_property(scalar(mat,'Opacity',.68),'',unreal.MaterialProperty.MP_OPACITY)
        mat.set_editor_property('two_sided',False);mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    mat.set_editor_property('used_with_skeletal_mesh',True);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
solid=parent('M_IV_MonsterSurface_v05');gel=parent('M_IV_MonsterGel_v05',True)

def creature_skin(name,isbody,isogre):
    # Dedicated surface response avoids the player's pale skin shading on creatures.
    path=R+'/Materials/M_IV_'+name+'_v05'
    mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_IV_'+name+'_v05',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    prefix='/Game/StylizedCharacters/BodyA/Body/Textures/T_BodyA_01' if isbody else '/Game/StylizedCharacters/BodyA/Heads/Head_01/Textures/T_HeadA_01'
    # Resolve installed texture paths through the registry rather than assuming folders.
    stem='T_BodyA_01' if isbody else 'T_HeadA_01'
    paths=A.list_assets('/Game/StylizedCharacters/BodyA',recursive=True,include_folder=False)
    def find_texture(suffix):
        target=stem+suffix
        p=next(p for p in paths if p.split('/')[-1].split('.')[0]==target)
        return unreal.load_asset(p)
    painted_path=R+'/Textures/T_IV_'+('Ogre' if isogre else 'Goblin')+('Body' if isbody else 'Head')+'_Painted_v05'
    gray=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);gray.set_editor_property('parameter_name','CreaturePaint');gray.set_editor_property('texture',unreal.load_asset(painted_path));M.connect_material_property(gray,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
    authored_uv=M.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);authored_uv.set_editor_property('coordinate_index',1);M.connect_material_expressions(authored_uv,'',gray,'UVs')
    normal=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);normal.set_editor_property('parameter_name','AnatomyNormal');normal.set_editor_property('texture',find_texture('_N'));normal.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    flat=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);flat.set_editor_property('constant',unreal.LinearColor(0,0,1,1))
    blend=M.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate);M.connect_material_expressions(flat,'',blend,'A');M.connect_material_expressions(normal,'RGB',blend,'B');M.connect_material_expressions(scalar(mat,'AnatomyNormalStrength',.48 if isbody else .22),'',blend,'Alpha');M.connect_material_property(blend,'',unreal.MaterialProperty.MP_NORMAL)
    M.connect_material_property(scalar(mat,'SkinRoughness',.72),'',unreal.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property('used_with_skeletal_mesh',True);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
instances={}
for model in manifest['models']:
    for slot in model['materials']:
        name=slot['name']
        if name in instances:continue
        if name.startswith('EyeExisting'):
            eye=T.create_asset('MI_IV_ManhwaEyes_v05',R+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew()) if not A.does_asset_exist(R+'/Materials/MI_IV_ManhwaEyes_v05') else unreal.load_asset(R+'/Materials/MI_IV_ManhwaEyes_v05')
            M.set_material_instance_parent(eye,unreal.load_asset('/Game/StylizedCharacters/BodyA/Eyes/Eyes_01/MI_Eyes_01_a'))
            M.set_material_instance_vector_parameter_value(eye,'Iris',unreal.LinearColor(.9,.35,.015,1));M.set_material_instance_vector_parameter_value(eye,'Sclera',unreal.LinearColor(.26,.28,.24,1));A.save_loaded_asset(eye);instances[name]=eye;continue
        if name.endswith('Skin') and ('Body' in name or 'Head' in name):
            isbody='Body' in name;isogre=name.startswith('Ogre')
            instances[name]=creature_skin(name,isbody,isogre);continue
        path=R+'/Materials/MI_IV_'+name+'_v05'
        mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('MI_IV_'+name+'_v05',R+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
        M.set_material_instance_parent(mat,gel if 'Gel' in name else solid)
        for p,value in [('Roughness',slot['roughness']),('Metallic',slot['metallic']),('Glow',1.5 if name in ['Rune','Flame','PoisonCore'] else 0.),('Opacity',.68)]:M.set_material_instance_scalar_parameter_value(mat,p,value)
        A.save_loaded_asset(mat);instances[name]=mat

family_skeleton={};loaded={};animations={}
for model in manifest['models']:
    name=model['id'];family=model['family'];dest=R+'/'+family;A.make_directory(dest);status('importing '+name)
    op=unreal.FbxImportUI();op.set_editor_property('automated_import_should_detect_type',False);op.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;op.import_as_skeletal=True;op.import_mesh=True;op.import_animations=False;op.import_materials=False;op.import_textures=False;op.create_physics_asset=False
    if family in family_skeleton:op.skeleton=family_skeleton[family]
    op.skeletal_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
    task=unreal.AssetImportTask();task.filename=model['fbx'];task.destination_path=dest;task.destination_name='SK_'+name;task.options=op;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
    mesh=unreal.load_asset(dest+'/SK_'+name);assert isinstance(mesh,unreal.SkeletalMesh),(name,list(task.imported_object_paths))
    slots=mesh.get_editor_property('materials');assert len(slots)==len(model['materials']),(name,len(slots))
    for i,spec in enumerate(model['materials']):
        source_mat=instances[spec['name']];material=source_mat
        if not spec['name'].startswith('EyeExisting'):
            path=R+'/Materials/MI_'+name+'_'+spec['name']+'_v05'
            material=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('MI_'+name+'_'+spec['name']+'_v05',R+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
            M.set_material_instance_parent(material,source_mat)
            painted=unreal.load_asset(R+'/Textures/'+Path(model['authored_color_texture']).stem)
            M.set_material_instance_texture_parameter_value(material,'CreaturePaint' if spec['name'].endswith('Skin') else 'Palette',painted);A.save_loaded_asset(material)
        slot=slots[i];slot.set_editor_property('material_interface',material);slots[i]=slot
    mesh.set_editor_property('materials',slots)
    skeleton=mesh.get_editor_property('skeleton');family_skeleton[family]=skeleton;loaded[name]=mesh
    try:lod_ok=SS.regenerate_lod(mesh,3,False,False)
    except Exception as exc:lod_ok=False;report['errors'].append(name+' LOD: '+str(exc))
    A.save_loaded_asset(mesh)
    row={'id':name,'family':family,'asset':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'lods':SS.get_lod_count(mesh),'lod_vertices':[SS.get_num_verts(mesh,i) for i in range(SS.get_lod_count(mesh))],'animations':{}}
    for kind in model['animations']:
        aname='AN_'+name+'_'+kind;op=unreal.FbxImportUI();op.set_editor_property('automated_import_should_detect_type',False);op.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;op.import_mesh=False;op.import_animations=True;op.skeleton=skeleton;op.import_materials=False;op.import_textures=False
        task=unreal.AssetImportTask();task.filename=str(S/'FBX'/name/(aname+'.fbx'));task.destination_path=dest+'/Animations';task.destination_name=aname;task.options=op;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
        paths=list(task.imported_object_paths);asset=unreal.load_asset(dest+'/Animations/'+aname)
        if not isinstance(asset,unreal.AnimSequence):
            asset=next((unreal.load_asset(p) for p in paths if isinstance(unreal.load_asset(p),unreal.AnimSequence)),None)
        assert asset,(name,kind,paths)
        assert asset.get_editor_property('skeleton')==skeleton,(name,kind,'skeleton mismatch')
        row['animations'][kind]=asset.get_path_name()
        if kind=='Idle':animations[name]=asset
    report['models'].append(row);status('imported '+name)

status('creating review map')
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,700,-3));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));floor.set_actor_scale3d(unreal.Vector(40,40,1));floor.set_actor_label('Monster review stage')
stage=T.create_asset('M_IV_ReviewStage_v05',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew()) if not A.does_asset_exist(R+'/Materials/M_IV_ReviewStage_v05') else unreal.load_asset(R+'/Materials/M_IV_ReviewStage_v05')
M.delete_all_material_expressions(stage);c=M.create_material_expression(stage,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.09,.105,.13,1));M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(scalar(stage,'Roughness',.85),'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(stage);A.save_loaded_asset(stage);floor.static_mesh_component.set_material(0,stage)
light=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-35,-40,0));lc=light.get_editor_property('light_component');lc.set_editor_property('intensity',10.);lc.set_editor_property('forward_shading_priority',1)
fill=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-20,-130,0));fill.get_editor_property('light_component').set_editor_property('intensity',6.);fill.get_editor_property('light_component').set_editor_property('cast_shadows',False)
sky=E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500));sky.get_editor_property('light_component').set_editor_property('intensity',1.)
atmosphere=E.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,0));atmosphere.set_actor_label('Material review sky atmosphere')
sky.get_editor_property('light_component').set_editor_property('real_time_capture',True)
for actor in E.get_all_level_actors():
    if isinstance(actor,unreal.DirectionalLight):actor.get_editor_property('light_component').set_editor_property('atmosphere_sun_light',True)
front=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-20,-90,0));front.get_editor_property('light_component').set_editor_property('intensity',3.);front.get_editor_property('light_component').set_editor_property('cast_shadows',False)
for family,cy,spacing in [('Slime',0,140),('Skeleton',400,220),('Goblin',850,170),('Ogre',1350,420)]:
    models=[m for m in manifest['models'] if m['family']==family]
    for i,m in enumerate(models):
        name=m['id'];actor=E.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(spacing*(i-(len(models)-1)/2),cy,0));actor.set_actor_label(name)
        comp=actor.get_editor_property('skeletal_mesh_component');comp.set_skeletal_mesh_asset(loaded[name]);comp.play_animation(animations[name],True)
        try:comp.set_editor_property('update_animation_in_editor',True)
        except:pass
        actor.set_folder_path('Monsters/'+family);actor.set_actor_enable_collision(False)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(900,-1300,1000),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(900,-1300,1000),unreal.Vector(0,650,110)))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,R+'/Maps/Map_MonsterReview_v05')
report['review_map']=R+'/Maps/Map_MonsterReview_v05';report['animation_count']=sum(len(r['animations']) for r in report['models']);status('complete')
exec(compile((B/'Scripts/polish_monster_review_lighting_v05.py').read_text(),'monster neutral studio review','exec'),{'__name__':'__main__'})



