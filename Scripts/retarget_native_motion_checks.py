import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/NativeMotion';manifest=json.loads((out/'manifest.json').read_text());assert manifest['success'];T=u.AssetToolsHelpers.get_asset_tools();A=u.EditorAssetLibrary;base='/Game/Elrhun/Golems/PlayerBody/Animations';rigfolder=base+'/Retargeting'
def rig_for(label,mesh):
 name='IK_'+label;rig=u.load_asset(rigfolder+'/'+name) or T.create_asset(name,rigfolder,u.IKRigDefinition,u.IKRigDefinitionFactory());c=u.IKRigController.get_controller(rig);assert c.set_skeletal_mesh(mesh);assert c.apply_auto_generated_retarget_definition(),label;A.save_loaded_asset(rig,only_if_is_dirty=False);return rig
sources={'Magic':('/Game/CombatMagicAnims/Demo/Mannequins/Meshes/SKM_Manny_Simple',['/Game/CombatMagicAnims/Animations/AS_CastSpell','/Game/CombatMagicAnims/Animations/AS_StaffStrike+CastSpell']),'Melee':('/Game/CloseCombatAnimSet/Mannequin/Character/Mesh/SK_Mannequin',['/Game/CloseCombatAnimSet/Animations/InPlace/Attacks/NinjaLeftJab','/Game/CloseCombatAnimSet/Animations/InPlace/Attacks/NinjaRightCross'])}
for family,(sourcepath,paths) in sources.items():
 source=u.load_asset(sourcepath);assert source;sr=rig_for('Source_'+family,source)
 for body in ['BodyA','BodyB']:
  target=u.load_asset('/Game/StylizedCharacters/'+body+'/Body/SKM_'+body);tr=rig_for(body,target);name='RTG_'+family+'_'+body;rt=u.load_asset(rigfolder+'/'+name) or T.create_asset(name,rigfolder,u.IKRetargeter,u.IKRetargetFactory());ctrl=u.IKRetargeterController.get_controller(rt);ctrl.set_ik_rig(u.RetargetSourceOrTarget.SOURCE,sr);ctrl.set_ik_rig(u.RetargetSourceOrTarget.TARGET,tr);ctrl.add_default_ops();ctrl.auto_map_chains(u.AutoMapChainType.EXACT,True);ctrl.auto_align_all_bones(u.RetargetSourceOrTarget.TARGET);A.save_loaded_asset(rt,only_if_is_dirty=False)
  inputs=u.IKRetargetBatchOperationInputs();inputs.assets_to_retarget=[A.find_asset_data(p) for p in paths];inputs.source_mesh=source;inputs.target_mesh=target;inputs.ik_retarget_asset=rt;inputs.prefix=body+'_';inputs.target_path=base+'/'+body;inputs.overwrite_existing_files=True;inputs.include_referenced_assets=False
  assets=u.IKRetargetBatchOperation.run_batch_retarget(inputs);assert len(assets)==len(paths),(body,family,len(assets))
  for data in assets:
   anim=data.get_asset();assert anim.get_editor_property('skeleton')==target.get_editor_property('skeleton');A.save_loaded_asset(anim,only_if_is_dirty=False);file=out/(anim.get_name().replace('+','_')+'.fbx');task=u.AssetExportTask();task.object=anim;task.filename=str(file);task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.AnimSequenceExporterFBX();task.options=u.FbxExportOption();assert u.Exporter.run_asset_export_task(task)
   manifest['animations'][anim.get_name()]={'path':anim.get_path_name(),'file':str(file),'skeleton':anim.get_editor_property('skeleton').get_path_name(),'duration':anim.get_play_length(),'family':family,'retargeter':rt.get_path_name()}
  (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
(r/'Saved/native_motion_retarget.json').write_text(json.dumps({'success':True,'animation_count':len(manifest['animations'])}))
