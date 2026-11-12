from pathlib import Path
import json,traceback
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 assert json.loads((r/'ArtSource/Golems/NativeClipping/garment_fit.json').read_text())['success']
 for name in ['apply_native_clearance_poses.py','native_wardrobe_import_impl.py','setup_native_clearance_physics.py','export_native_clipping_poses.py']:
  p=r/'Scripts'/name;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 (r/'Saved/native_clipping_setup.json').write_text(json.dumps({'success':True},indent=2))
except Exception:(r/'Saved/native_clipping_setup.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()},indent=2));raise
