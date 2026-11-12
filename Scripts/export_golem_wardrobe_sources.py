import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
out=root/'ArtSource/Golems/WardrobeSources';out.mkdir(exist_ok=True,parents=True)
sets={
 'Tank':[
 '/Game/WarriorSet01/BodyA/WarriorSet_01/SKM_BodyA_Warrior_01_Top',
 '/Game/WarriorSet01/BodyA/WarriorSet_01/SKM_BodyA_Warrior_01_Pants_a',
 '/Game/WarriorSet01/BodyA/WarriorSet_01/SKM_BodyA_Warrior_01_Shoulder_l',
 '/Game/WarriorSet01/BodyA/WarriorSet_01/SKM_BodyA_Warrior_01_Shoulder_r',
 '/Game/WarriorSet01/BodyA/WarriorSet_01/SKM_BodyA_Warrior_01_Boots'],
 'Mage':[
 '/Game/MageSet01/BodyA/Mage_Set_01/SKM_BodyA_Mage_01_Top',
 '/Game/MageSet01/BodyA/Mage_Set_01/SKM_BodyA_Mage_01_Pants_a',
 '/Game/MageSet01/BodyA/Mage_Set_01/SKM_BodyA_Mage_Cape_01',
 '/Game/MageSet01/BodyA/Mage_Set_01/SKM_BodyA_Mage_01_Boots'],
 'Ranger':[
 '/Game/CasualSet04_Elves/BodyA/SKM_BodyA_Casual_04_Top_b',
 '/Game/AdventurersKit/BodyA/Armor_01/SKM_BodyA_Armor_01_Pants',
 '/Game/AdventurersKit/BodyA/Armor_01/SKM_BodyA_Armor_01_Pants_Bags',
 '/Game/AdventurersKit/BodyA/Armor_01/SKM_BodyA_Armor_01_Boots'],
 'Healer':[
 '/Game/CasualSet_06_Noble/BodyA/SKM_BodyA_Casual_06_Top',
 '/Game/CasualSet_06_Noble/BodyA/SKM_BodyA_Casual_06_Coat',
 '/Game/CasualSet_06_Noble/BodyA/SKM_BodyA_Casual_06_Pants_a',
 '/Game/CasualSet_06_Noble/BodyA/SKM_BodyA_Casual_06_Boots']}
weapons={
 'Sword':'/Game/WarriorSet01/Weapons/Sword_02/SKM_Sword_02',
 'Shield':'/Game/WarriorSet01/Weapons/Shield_02/SKM_Shield_02_L',
 'Staff':'/Game/MageSet01/Weapons/Staff_01/SKM_Staff_01',
 'Wand':'/Game/MageSet01/Weapons/Wand_01/SKM_Wand_01',
 'Bow':'/Game/AdventurersKit/Weapons/Bow_01/SKM_Bow_01'}
manifest={'sets':sets,'weapons':weapons,'assets':{},'failures':[]}
for path in dict.fromkeys([p for paths in sets.values() for p in paths]+list(weapons.values())):
 try:
  mesh=u.load_asset(path);assert isinstance(mesh,u.SkeletalMesh),path
  filename=out/(mesh.get_name()+'.fbx')
  task=u.AssetExportTask();task.object=mesh;task.filename=str(filename);task.automated=True;task.prompt=False
  task.exporter=u.SkeletalMeshExporterFBX()
  options=u.FbxExportOption();options.set_editor_property('ascii',False);options.set_editor_property('level_of_detail',False)
  task.options=options
  assert u.Exporter.run_asset_export_task(task),path
  manifest['assets'][path]={'file':str(filename),'materials':[{'slot':str(m.material_slot_name),'path':m.material_interface.get_path_name() if m.material_interface else None} for m in mesh.get_editor_property('materials')]}
 except Exception:manifest['failures'].append({'path':path,'error':traceback.format_exc()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
(root/'Saved/golem_wardrobe_export.json').write_text(json.dumps({'count':len(manifest['assets']),'failures':manifest['failures']},indent=2))
