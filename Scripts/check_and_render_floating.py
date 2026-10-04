import unreal,traceback
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts')
try:exec(compile((B/'verify_floating_island.py').read_text(),str(B/'verify_floating_island.py'),'exec'),{'__name__':'__main__'})
except:unreal.log_error(traceback.format_exc())
exec(compile((B/'render_floating_views.py').read_text(),str(B/'render_floating_views.py'),'exec'),{'__name__':'__main__'})
