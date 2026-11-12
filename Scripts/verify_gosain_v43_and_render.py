from pathlib import Path
import json
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
exec(compile((B/'Scripts/verify_gosain_v43.py').read_text(),str(B/'Scripts/verify_gosain_v43.py'),'exec'),{'__name__':'__main__'})
r=json.loads((B/'ArtSource/World/Gosain43/native_validation.json').read_text())
assert not r['unexpected_actor_changes'] and r['outside_foliage_equal'] and not r['foliage_move_failures'], 'Native verification failed; inspect report'
exec(compile((B/'Scripts/render_gosain_v43_world.py').read_text(),str(B/'Scripts/render_gosain_v43_world.py'),'exec'),{'__name__':'__main__'})
