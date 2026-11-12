from pathlib import Path
import traceback
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for name in ['setup_golem_village_loop.py','playtest_golem_village_loop.py']:
  p=r/'Scripts'/name;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
except Exception:
 (r/'Saved/golem_village_start_error.txt').write_text(traceback.format_exc());raise
