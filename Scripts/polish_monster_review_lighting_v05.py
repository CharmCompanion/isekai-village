import unreal,builtins,json,shutil
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/Monsters/Refined_v05';out=B/'ArtSource/Monsters/Models_v05/Previews'
holder=getattr(builtins,'iv_monster_capture_holder',None)
if holder:
    try:unreal.unregister_slate_post_tick_callback(holder['handle'])
    except:pass
old=out/'DirectionalLighting';old.mkdir(exist_ok=True)
for f in out.glob('*Unreal_v05.png'):shutil.copy2(f,old/f.name)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
unreal.EditorLevelLibrary.eject_pilot_level_actor()
for actor in E.get_all_level_actors():
    if actor.get_actor_label()=='Monster review camera':E.destroy_actor(actor)
    elif isinstance(actor,unreal.SkeletalMeshActor):actor.set_is_temporarily_hidden_in_editor(False)
    elif isinstance(actor,unreal.SkyLight):
        c=actor.get_editor_property('light_component');c.set_editor_property('real_time_capture',False);c.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);c.set_editor_property('cubemap',unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'));c.set_editor_property('intensity',1.3)
        c.set_editor_property('lower_hemisphere_is_black',True);c.set_editor_property('lower_hemisphere_color',unreal.LinearColor(.15,.17,.20,1))
    elif isinstance(actor,unreal.DirectionalLight):
        c=actor.get_editor_property('light_component')
        if not c.get_editor_property('cast_shadows'):c.set_editor_property('intensity',6.)
for family in ['Ogre','Goblin']:
    for kind in ['Head','Body']:
        # Set instance overrides so the dedicated source parent remains reusable.
        paths=A.list_assets(R+'/Materials',recursive=False,include_folder=False)
        for path in paths:
            if path.rsplit('/',1)[-1].startswith('MI_') and family+kind+'Skin_v05' in path:
                instance=unreal.load_asset(path);M.set_material_instance_scalar_parameter_value(instance,'AnatomyNormalStrength',.22 if kind=='Head' else .48);A.save_loaded_asset(instance)
path=R+'/Materials/M_IV_ReviewBackdrop_v05'
mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_IV_ReviewBackdrop_v05',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
M.delete_all_material_expressions(mat);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True)
c=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.18,.215,.27,1));M.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat)
backdrop=next((a for a in E.get_all_level_actors() if a.get_actor_label()=='Neutral monster review backdrop'),None)
if not backdrop:backdrop=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,700,0));backdrop.set_actor_label('Neutral monster review backdrop')
backdrop.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere'));backdrop.set_actor_scale3d(unreal.Vector(1000,1000,1000));backdrop.static_mesh_component.set_material(0,mat);backdrop.static_mesh_component.set_editor_property('cast_shadow',False);backdrop.set_actor_enable_collision(False)
(B/'Saved/monster_review_lighting_v05.json').write_text(json.dumps({'sky':'installed daylight cubemap','lower_hemisphere':'neutral fill','head_normal_strength':.22,'body_normal_strength':.48,'directional_comparison_views':str(old)},indent=2))
exec(compile((B/'Scripts/render_monsters_unreal_v05.py').read_text(),'neutral v05 native views','exec'),{'__name__':'__main__'})
