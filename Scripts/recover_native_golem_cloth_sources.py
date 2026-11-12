import unreal as u,json,time
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');src=r/'ArtSource/Golems/NativeWardrobe';manifest=json.loads((src/'manifest.json').read_text());T=u.AssetToolsHelpers.get_asset_tools();changed=[]
for path,info in manifest['assets'].items():
 original=u.load_asset(path);state=json.loads(u.GolemClothTools.inspect_clothing(original))
 if not any(s['cloth'] for s in state['sections']) or info.get('recovered_cloth_export'):continue
 name='SK_Export_'+original.get_name();dest='/Game/Elrhun/Golems/PlayerBody/ClothingSources';mesh=T.duplicate_asset(name,dest,original);assert mesh
 u.GolemClothTools.reset_cape_cloth(mesh)
 task=u.AssetExportTask();task.object=mesh;task.filename=info['file'];task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.SkeletalMeshExporterFBX();task.options=u.FbxExportOption();task.options.level_of_detail=False;assert u.Exporter.run_asset_export_task(task)
 info['recovered_cloth_export']=True;info['original_cloth_sections']=state['sections'];changed.append(path)
(src/'manifest.json').write_text(json.dumps(manifest,indent=2));(r/'Saved/native_cloth_sources_recovered.json').write_text(json.dumps({'success':True,'changed':changed}))
ready=r/'Saved/native_cloth_sources_ready.json';deadline=time.monotonic()+900
while not ready.exists() and time.monotonic()<deadline:time.sleep(1)
assert ready.exists()
p=r/'Scripts/import_native_golem_wardrobe.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
