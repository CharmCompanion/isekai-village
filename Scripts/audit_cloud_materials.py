import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');M=unreal.MaterialEditingLibrary;d={}
for path in ['/Game/SoStylized/Environment/Sky/Materials/M_StylizedClouds_Lite','/Game/StylizedIsland/StylizedVFX/Fog/Materials/FogCard/M_StylizedFogCard']:
 mat=unreal.load_asset(path);rows=[]
 for n in M.get_material_expressions(mat):
  r={'class':n.get_class().get_name()}
  for p in ['code','texture','parameter_name','default_value','r','constant','value']:
   try:r[p]=str(n.get_editor_property(p))
   except:pass
  rows.append(r)
 d[path]=rows
tex=unreal.load_asset('/Game/StylizedIsland/StylizedVFX/Fog/Textures/StylizedCloud/03/T_StylizedClouds_03_RA');t=unreal.AssetExportTask();t.object=tex;t.filename=str(B/'Saved/cloud_reference.tga');t.automated=True;t.prompt=False;t.exporter=unreal.TextureExporterTGA();unreal.Exporter.run_asset_export_task(t)
(B/'Saved/cloud_material_audit.json').write_text(json.dumps(d,indent=2))
