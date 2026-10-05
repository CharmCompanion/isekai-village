"""Review renders for the v32 stylized landscape pass -> Docs/WorldDesign/Stylized32_*.png.
Run with Map_AnimeAdventure open; set IV_RENDER_QUIT=1 to quit the editor afterwards."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_anime_polish_v31 as R

VIEWS = [
    ('Village', (0, -20), None, (0, 200, None)),
    ('Plaza', (-30, -30), None, (0, 0, None)),
    ('Meadow', (60, -60), None, (90, -40, None)),
    ('Farm', (130, -110), None, (110, -181, None)),
    ('LakeBeach', (-240, -300), None, (-300, -340, 18)),
    ('LakeShore', (-250, -430), None, (-300, -380, 18)),
    ('LakeAcross', (-90, -330), None, (-400, -373, 18)),
    ('Spillway', (-200, -400), 45, (-285, -530, 16)),
    ('Forest', (-120, 150), None, (-200, 260, None)),
    ('Cliffs', (-300, -40), 110, (-520, 80, 70)),
    ('DungeonPath', (200, 400), None, (230, 445, None)),
    ('Aerial', (250, -350), 260, (0, 0, 30)),
    ('Island', (900, -1300), 650, (0, 30, 0)),
]

if __name__ == '__main__':
    assert R.world().get_path_name().startswith(R.MAP + '.'), 'open Map_AnimeAdventure first'
    R.start_render(prefix='Stylized32_', views=VIEWS, warmup=75.0)
