import unreal as u,json,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/PlayerBody';out.mkdir(parents=True,exist_ok=True)
report={'classes':{},'assets':{},'maps':{}}
for path in ['/Game/IsekaiVillage/Input/BP_OverworldCharacter','/Game/IsekaiVillage/Input/BP_ThirdPersonCharacter','/Game/SpellCraft/Blueprints/Character/BP_MageCharacter']:
 cls=u.EditorAssetLibrary.load_blueprint_class(path)
 if not cls:continue
 cdo=u.get_default_object(cls);rows=[]
 for c in cdo.get_components_by_class(u.SkeletalMeshComponent):
  m=c.get_editor_property('skeletal_mesh_asset');abp=c.get_editor_property('anim_class');rows.append({'name':c.get_name(),'mesh':m.get_path_name() if m else None,'anim_class':abp.get_path_name() if abp else None,'materials':[v.get_path_name() if v else None for v in c.get_materials()]})
 report['classes'][path]=rows
world=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/Maps/Map_Village');mode=world.get_world_settings().get_editor_property('default_game_mode');report['maps']['village']={'mode':mode.get_path_name() if mode else None,'pawn':u.get_default_object(mode).get_editor_property('default_pawn_class').get_path_name() if mode else None}
for path in ['/Game/StylizedCharacters/BodyA/Body/SKM_BodyA','/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01']:
 mesh=u.load_asset(path);task=u.AssetExportTask();task.object=mesh;task.filename=str(out/(mesh.get_name()+'.fbx'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.SkeletalMeshExporterFBX();task.options=u.FbxExportOption();task.options.level_of_detail=False;ok=u.Exporter.run_asset_export_task(task)
 report['assets'][path]={'file':task.filename,'skeleton':mesh.get_editor_property('skeleton').get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name() if mesh.get_editor_property('physics_asset') else None,'materials':[{'slot':str(s.material_slot_name),'material':s.material_interface.get_path_name() if s.material_interface else None} for s in mesh.get_editor_property('materials')],'exported':ok}
(r/'Saved/golem_player_body_reference.json').write_text(json.dumps(report,indent=2))
