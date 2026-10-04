import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
paths=['/Game/AdvancedVillagePack/Meshes/SM_House_Var01','/Game/AdvancedVillagePack/Meshes/SM_House_Var02','/Game/StylizedIsland/Mesh/Props/SM_Tent/SM_Stylized_Tent_Mesh/SM_Stylized_Tent','/Game/StylizedIsland/Mesh/Props/SM_Docks/SM_Stylized_Docks/SM_Dock_Straight','/Game/AdvancedVillagePack/Meshes/SM_Boat','/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01','/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_windmill_sail','/Game/SoStylized/Environment/Trees/Coastal/SM_PalmTree01','/Game/SoStylized/Environment/Trees/Desert/SM_DesertPalmTree01','/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2','/Game/SoStylized/Environment/Trees/Pine/SM_Pine01','/Game/AdvancedVillagePack/Meshes/SM_Cart_Var01']
r={}
for p in paths:
 m=unreal.load_asset(p)
 if not m:continue
 bb=m.get_bounding_box();r[p]={'min':[bb.min.x,bb.min.y,bb.min.z],'max':[bb.max.x,bb.max.y,bb.max.z],'slots':[str(x.material_slot_name) for x in m.static_materials]}
(B/'Saved/civilization_assets_v29.json').write_text(json.dumps(r,indent=2))
