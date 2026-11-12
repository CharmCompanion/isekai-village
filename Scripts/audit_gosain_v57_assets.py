import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage'); O=B/'ArtSource/World/Gosain57';O.mkdir(exist_ok=True)
paths=[
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v03_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_stone_small_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_fence_v02_01',
'/Game/Fantastic_Village_Pack/meshes/props/furniture/SM_PROP_table_01',
'/Game/Fantastic_Village_Pack/meshes/props/container/SM_PROP_crate_01',
'/Game/Fantastic_Village_Pack/meshes/props/container/SM_PROP_barrel_01',
'/Game/Fantastic_Village_Pack/meshes/props/container/SM_PROP_box_03',
'/Game/AdvancedVillagePack/Meshes/SM_Logs_Var01',
'/Game/AdvancedVillagePack/Meshes/SM_GrassPatch_Var01',
'/Game/AdvancedVillagePack/Meshes/SM_Stone_Medium_Var01',
'/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_body_v01_01']

a=[]
for p in paths:
 m=unreal.load_asset(p)
 if not m:a.append({'path':p,'missing':True});continue
 b=m.get_bounding_box();a.append({'path':p,'lo':[b.min.x,b.min.y,b.min.z],'hi':[b.max.x,b.max.y,b.max.z],'materials':[str(v.material_interface.get_path_name()) if v.material_interface else None for v in m.static_materials]})
(O/'asset_audit.json').write_text(json.dumps(a,indent=2))
