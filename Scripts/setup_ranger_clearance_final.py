from pathlib import Path
import json,traceback
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 p=r/'Scripts/setup_native_golem_weapons.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','only_keys':{'BodyA_Ranger','BodyB_Ranger'}})
 p=r/'Scripts/export_native_clipping_poses.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 (r/'Saved/native_ranger_clearance_final.json').write_text(json.dumps({'success':True},indent=2))
except Exception:(r/'Saved/native_ranger_clearance_final.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()},indent=2));raise
