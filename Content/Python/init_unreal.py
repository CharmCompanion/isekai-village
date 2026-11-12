"""Project Python startup. One-shot apply when a Saved/run_vXX.flag exists."""
from pathlib import Path
root = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
jobs = [
    (root / 'Saved/run_v38.flag', root / 'Scripts/run_mine_and_paths_v38.py'),
    (root / 'Saved/run_v37.flag', root / 'Scripts/run_hub_and_dungeon_v37.py'),
]
for flag, script in jobs:
    if flag.exists():
        flag.unlink()
        import runpy
        runpy.run_path(str(script), run_name=script.stem)
        break

