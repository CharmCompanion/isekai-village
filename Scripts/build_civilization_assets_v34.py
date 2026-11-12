"""Floating pleasure-isle rock for the Vylfod sky city."""
from pathlib import Path
import numpy as np, json
P = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts')
S = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
O = S / 'Civilizations34'
O.mkdir(exist_ok=True)
ns = {}
exec(compile((P / 'build_civilization_assets_v30.py').read_text().split('manifest=[]')[0], 'mesh', 'exec'), ns)
Mesh = ns['Mesh']
ns['O'] = O

# Reuse v33 landmark list (magic tower, empire wall) plus v30 architecture.
prev = json.loads((S / 'Civilizations33' / 'assets.json').read_text())
manifest = [q for q in prev if q['name'] not in ('SM_Civ33_Roads', 'SM_Civ33_Foundations', 'SM_Civ30_Roads', 'SM_Civ30_Foundations')]

m = Mesh()
# Local top deck at z=0, 400 x 260 m, rock keels below, canal down the long axis.
n = 48
v, f = [], []
for i in range(n):
    a = 2 * np.pi * i / n
    v.append([198 * np.cos(a), 128 * np.sin(a), 2])
    v.append([210 * np.cos(a) * (1 + .04 * np.sin(3 * a)), 138 * np.sin(a) * (1 + .05 * np.cos(2 * a)), -8])
    v.append([150 * np.cos(a), 90 * np.sin(a), -55])
    v.append([40 * np.cos(a), 24 * np.sin(a), -95])
    v.append([8 * np.cos(a), 5 * np.sin(a), -108])
for j in range(4):
    for i in range(n):
        a = j * n + i
        b = j * n + (i + 1) % n
        f.extend([[a, b, b + n], [a, b + n, a + n]])
m.part(v, f, 'stone')
# Flat paved deck with a canal trench.
m.box(0, 0, -1.2, 390, 250, 2.4, 'path', .4)
m.box(0, 0, -4.5, 22, 230, 5, 'tealroof', .2)  # canal water slot
for y in (-90, 0, 90):
    m.box(-8, y, 0.2, 6, 18, 1.1, 'wood', .15)
    m.box(8, y, 0.2, 6, 18, 1.1, 'wood', .15)
for x, y in ((-170, -90), (170, -90), (-170, 90), (170, 90), (0, -115), (0, 115)):
    m.cyl(x, y, -6, 9, 14, 'stone', 16)
    m.cyl(x, y, 8, 10, 2, 'gold', 16)
manifest.append(m.write('SM_Civ34_PleasureIsle'))
for q in manifest:
    if 'folder' not in q:
        q['folder'] = 'Civilizations34' if q['name'].startswith('SM_Civ34_') else ('Civilizations33' if q['name'].startswith('SM_Civ33_') else 'Civilizations30')
(O / 'assets.json').write_text(json.dumps(manifest, indent=2))
print([(q['name'], q.get('triangles'), q.get('folder')) for q in manifest if q['name'].startswith('SM_Civ3')], flush=True)
