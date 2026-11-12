import unreal,json
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/ElRuhnSky01');M=unreal.MaterialEditingLibrary;mat=unreal.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud')
rows=[]
for n in M.get_material_expressions(mat):
 row={'class':n.get_class().get_name()}
 for k in ['parameter_name','default_value']:
  try:row[k]=str(n.get_editor_property(k))
  except Exception:pass
 if 'parameter_name' in row:rows.append(row)
(O/'volumetric_cloud_api.json').write_text(json.dumps({'parameters':rows,'component_docs':unreal.VolumetricCloudComponent.__doc__},indent=2))
exec(compile((O.parents[2]/'Scripts/verify_elruhn_sky01.py').read_text(),'verify_elruhn_sky01','exec'),{'__name__':'__main__'})
