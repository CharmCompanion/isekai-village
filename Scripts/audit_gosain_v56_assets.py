import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage'); O=B/'ArtSource/World/Gosain56';O.mkdir(exist_ok=True)
paths=[
'/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB02',
'/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB03',
'/Game/SoStylized/Environment/Rocks/Cubic/SM_CubicCliff04',
'/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_beam_big_v01_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_wood_gate_frame_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_planks_01',
'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_planks_02',
'/Game/Fantastic_Village_Pack/meshes/props/vehicles/SM_PROP_cart_01',
'/Game/AdvancedVillagePack/Meshes/SM_Cart_Var01',
'/Game/Fantastic_Village_Pack/meshes/props/light/SM_PROP_lantern_01',
'/Game/IsekaiVillage/AdventureWorld/Meshes/Routes/SM_Mine_Tunnel']
a=[]
for p in paths:
 m=unreal.load_asset(p)
 if not m:a.append({'path':p,'missing':True});continue
 b=m.get_bounding_box();a.append({'path':p,'lo':[b.min.x,b.min.y,b.min.z],'hi':[b.max.x,b.max.y,b.max.z],'materials':[str(v.material_interface.get_path_name()) if v.material_interface else None for v in m.static_materials]})
(O/'asset_audit.json').write_text(json.dumps(a,indent=2))
