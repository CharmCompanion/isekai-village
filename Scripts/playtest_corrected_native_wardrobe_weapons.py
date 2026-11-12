import unreal as u,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for name in ['native_wardrobe_import_impl.py','playtest_native_weapons.py']:
  p=r/'Scripts'/name;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
except Exception:(r/'Saved/native_weapon_wardrobe_fix_error.txt').write_text(traceback.format_exc());raise
