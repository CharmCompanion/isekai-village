import unreal as u,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');a=u.load_asset('/Game/Elrhun/Golems/Animations/A_Golem_EquippedIdle')
controller=a.controller if hasattr(a,'controller') else a.get_controller() if hasattr(a,'get_controller') else None
r={'factory':str(u.FbxFactory),'controller_api':[v for v in dir(controller) if 'track' in v or 'frame' in v or 'bracket' in v], 'anim_api':[v for v in dir(a) if any(s in v for s in ['controller','data_model','bone'])]}
(root/'Saved/golem_grip_import_api.json').write_text(json.dumps(r,indent=2))
