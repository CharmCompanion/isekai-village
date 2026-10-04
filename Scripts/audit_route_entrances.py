import unreal,json
from pathlib import Path
paths=['/Game/StylizedIsland/Mesh/Props/SM_Arch/SM_Stylized_Arch_Mesh/SM_Stylized_Arch','/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_wood_gate_frame_01','/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_wood','/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_stone_small_01','/Game/Fantastic_Village_Pack/meshes/props/food/SM_PROP_food_carrot_01']
out=[]
for p in paths:
    a=unreal.load_asset(p)
    out.append({'path':p,'bounds':str(a.get_bounding_box()) if a else None})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/route_entrance_assets.json').write_text(json.dumps(out,indent=2))
eye=unreal.Vector(0,-78000,68000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,10000,5000)))
