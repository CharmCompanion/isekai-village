"""Additive setup: native spell data, reusable slime blueprints, isolated review map."""
import unreal,json,traceback
from pathlib import Path
B=Path(__file__).resolve().parents[1];R='/Game/IsekaiVillage/Magic/Slimes'
A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=json.loads((B/'ArtSource/Magic/SlimeRunes/spells.json').read_text());models={r['id']:r for r in json.loads((B/'Saved/monster_import_v01.json').read_text())['models']}
def asset(name,cls,factory):return unreal.load_asset(R+'/'+name) if A.does_asset_exist(R+'/'+name) else T.create_asset(name,R,cls,factory)
def param(mat,cls,name,value):
 n=M.create_material_expression(mat,cls);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
def material(name,textured):
 mat=asset(name,unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_ADDITIVE);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True)
 color=param(mat,unreal.MaterialExpressionVectorParameter,'EmissiveColor',unreal.LinearColor(1,1,1,1));glow=param(mat,unreal.MaterialExpressionScalarParameter,'GlowIntensity',2.0)
 mult=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);M.connect_material_expressions(color,'RGB',mult,'A');M.connect_material_expressions(glow,'',mult,'B');M.connect_material_property(mult,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if textured:
  tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);tex.set_editor_property('parameter_name','CircleTexture');tex.set_editor_property('texture',unreal.load_asset(R+'/T_Runes_Meadow'));M.connect_material_property(tex,'A',unreal.MaterialProperty.MP_OPACITY)
 M.recompile_material(mat);A.save_loaded_asset(mat);return mat
A.make_directory(R)
for row in rows:
 task=unreal.AssetImportTask();task.filename=str(B/'ArtSource/Magic/SlimeRunes'/('T_Runes_'+row['prefix']+'.png'));task.destination_path=R;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task])
 tex=unreal.load_asset(R+'/T_Runes_'+row['prefix']);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(tex)
rune=material('M_RunicSentence',True);stroke=material('M_RunicStroke',False)
blueprints={};spells={};report={'spells':[]}
for row in rows:
 f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',unreal.RunicSlimeSpell)
 s=asset('DA_'+row['prefix']+'Spell',unreal.RunicSlimeSpell,f)
 for key in ('effect_word','incantation','damage','cast_time','cooldown','tp_cost','speed','duration','power'):s.set_editor_property(key,row[key])
 s.set_editor_property('spell_name',row['name']);s.set_editor_property('element',getattr(unreal.Element,row['element']));s.set_editor_property('effect',getattr(unreal.RunicEffect,row['effect']));s.set_editor_property('color',unreal.LinearColor(*row['color'],1));s.set_editor_property('rune_texture',unreal.load_asset(R+'/T_Runes_'+row['prefix']))
 family={'Poison':'Dark','Crystal':'Ice'}.get(row['fx'],row['fx'])
 bolt=f'/Game/SlashTrail_SoftTofu/Niagara/{family}/NS_Sword_{family}'
 impact=f'/Game/SlashTrail_SoftTofu/Niagara/{family}/NS_Hit_{"water" if family=="Water" else family}_Once'
 s.set_editor_property('bolt_fx',unreal.load_asset(bolt));s.set_editor_property('impact_fx',unreal.load_asset(impact));assert s.get_editor_property('bolt_fx') and s.get_editor_property('impact_fx'),row
 assert s.get_sentence()==row['sentence'];A.save_loaded_asset(s);spells[row['id']]=s
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.SlimeRunicMage)
 bp=asset('BP_'+row['id']+'Mage',unreal.Blueprint,f);cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('spell',s)
 cdo.get_editor_property('mesh').set_skeletal_mesh_asset(unreal.load_asset(models[row['id']]['asset']))
 for kind in ('Idle','Attack','Death'):cdo.set_editor_property(kind.lower()+'_animation',unreal.load_asset(models[row['id']]['animations'][kind]))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);A.save_loaded_asset(bp);blueprints[row['id']]=bp.generated_class()
 report['spells'].append({'slime':row['id'],'sentence':s.get_sentence(),'asset':s.get_path_name(),'blueprint':bp.get_path_name(),'bolt_fx':bolt,'impact_fx':impact})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/Engine.GameModeBase'))
floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,250,-15));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(27,18,.3));floor.set_actor_label('Runic training court')
fm=asset('M_TrainingCourt',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(fm)
c=param(fm,unreal.MaterialExpressionVectorParameter,'Color',unreal.LinearColor(.018,.03,.055,1));M.connect_material_property(c,'RGB',unreal.MaterialProperty.MP_BASE_COLOR);M.recompile_material(fm);A.save_loaded_asset(fm);floor.static_mesh_component.set_material(0,fm)
light=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,600),unreal.Rotator(-50,-30,0));light.light_component.set_editor_property('intensity',4.)
fill=E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,300));fill.light_component.set_editor_property('intensity',1.)
fill.light_component.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);fill.light_component.set_editor_property('cubemap',unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
for i,row in enumerate(rows):
 x=(i%3-1)*720;y=(i//3)*650
 actor=E.spawn_actor_from_class(blueprints[row['id']],unreal.Vector(x,y,43));actor.set_actor_label(row['id']+' | '+row['name']);actor.set_editor_property('target_player',False);actor.set_folder_path('Active Slimes')
 # Target is a native mage with no mesh/spell/faction; it uses real damage receiving logic.
 dummy=E.spawn_actor_from_class(unreal.SlimeRunicMage,unreal.Vector(x,y+290,43));dummy.set_actor_label('Target_'+row['id']);dummy.set_editor_property('tags',[]);dummy.set_editor_property('auto_cast',False);dummy.set_editor_property('max_health',100000.);dummy.set_folder_path('Training Targets');actor.set_editor_property('target',dummy)
 marker=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y+290,45));marker.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cylinder'));marker.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE);marker.set_actor_scale3d(unreal.Vector(.65,.65,.9));marker.set_actor_enable_collision(False);marker.set_actor_label('Target visual '+row['prefix']);marker.attach_to_actor(dummy,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 mi=asset('MI_'+row['prefix']+'Runes',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(mi,rune);M.set_material_instance_texture_parameter_value(mi,'CircleTexture',spells[row['id']].get_editor_property('rune_texture'));M.set_material_instance_vector_parameter_value(mi,'EmissiveColor',unreal.LinearColor(*row['color'],1));M.set_material_instance_scalar_parameter_value(mi,'GlowIntensity',1.6);A.save_loaded_asset(mi)
 plate=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,2));plate.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));plate.static_mesh_component.set_material(0,mi);plate.set_actor_scale3d(unreal.Vector(3.3,3.3,1));plate.set_actor_enable_collision(False);plate.set_actor_hidden_in_game(True);plate.set_actor_label('Editor rune preview '+row['prefix']);plate.set_folder_path('Editor previews - hidden in play')
 label=E.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector(x-240,y-230,5),unreal.Rotator(90,90,0));tc=label.text_render;tc.set_text(row['id']+'\n'+row['sentence']);tc.set_world_size(21);label.set_actor_label('Spell legend '+row['prefix'])
start=E.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,-550,150))
eye=unreal.Vector(150,-1500,1650);aim=unreal.Vector(0,320,0);rot=unreal.MathLibrary.find_look_at_rotation(eye,aim)
cam=E.spawn_actor_from_class(unreal.CameraActor,eye,rot);cam.set_actor_label('Slime magic overview');cam.camera_component.set_editor_property('field_of_view',65.)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,rot)
report['map']=R+'/Map_SlimeMagic';assert unreal.EditorLoadingAndSavingUtils.save_map(world,report['map']);report['status']='complete'
(B/'Saved/slime_magic_setup.json').write_text(json.dumps(report,indent=2));unreal.log('SLIME MAGIC SETUP COMPLETE')
