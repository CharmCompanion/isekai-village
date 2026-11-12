import unreal
R='/Game/IsekaiVillage/Monsters/Refined_v02';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
stage=T.create_asset('M_IV_ReviewStage_v02',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew()) if not A.does_asset_exist(R+'/Materials/M_IV_ReviewStage_v02') else unreal.load_asset(R+'/Materials/M_IV_ReviewStage_v02')
M.delete_all_material_expressions(stage)
c=M.create_material_expression(stage,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.09,.105,.13,1));M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=M.create_material_expression(stage,unreal.MaterialExpressionConstant);r.set_editor_property('r',.85);M.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(stage);A.save_loaded_asset(stage)
for actor in E.get_all_level_actors():
    if actor.get_actor_label()=='Monster review stage':actor.static_mesh_component.set_material(0,stage)
front=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-20,-90,0));front.get_editor_property('light_component').set_editor_property('intensity',3.);front.get_editor_property('light_component').set_editor_property('cast_shadows',False)
front.set_actor_label('Manhwa review front fill')
