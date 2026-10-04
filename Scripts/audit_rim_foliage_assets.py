import unreal,json
from pathlib import Path
R='/Game/IsekaiVillage/AdventureWorld';d={}
for kind in ['Rocks','Talus','Bush','Grass','Flowers','MeadowCarpet','Fern']:
 ft=unreal.load_asset(R+'/Foliage/FT_R08_'+kind);mesh=ft.get_editor_property('mesh');b=mesh.get_bounding_box();d[kind]={'mesh':mesh.get_path_name(),'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z],'cull':str(ft.get_editor_property('cull_distance'))}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/rim_foliage_assets.json').write_text(json.dumps(d,indent=2))
