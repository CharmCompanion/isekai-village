"""New landmark meshes for v33: impossibly tall capital spires and empire curtain wall."""
from pathlib import Path
import numpy as np, json
P = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts')
S = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
O = S / 'Civilizations33'; O.mkdir(exist_ok=True)
ns = {}
exec(compile((P / 'build_civilization_assets_v30.py').read_text().split('manifest=[]')[0], 'mesh', 'exec'), ns)
Mesh, tower = ns['Mesh'], ns['tower']
ns['O'] = O

manifest = json.loads((S / 'Civilizations30' / 'assets.json').read_text())
manifest = [q for q in manifest if q['name'] not in ('SM_Civ30_Roads', 'SM_Civ30_Foundations')]

m = Mesh()
# 240 m needle. Capitals instance this at scale 3.2 (~770 m) so it reads from El Ruhn.
m.rings([(-18, 28, 28), (-4, 28, 28), (6, 18, 18), (28, 16, 16), (140, 9, 9), (188, 7, 7), (214, 5.5, 5.5)], 48, 'stone')
m.cyl(0, 0, -18, 32, 8, 'trim', 48)
for z in (36, 88, 140, 188):
    m.cyl(0, 0, z, 11 if z < 150 else 8, 3.2, 'gold', 40)
    for a in np.arange(8) * np.pi / 4:
        m.box(9 * np.cos(a), 9 * np.sin(a), z + 8, 1.6, .55, 7, 'window', .15, a + np.pi / 2)
m.rings([(214, 8, 8), (222, 7, 7), (240, .4, .4)], 32, 'crystal')
m.torus(0, 0, 202, 14, 1.1, 'gold')
m.torus(0, 0, 236, 5, .7, 'gold', True)
manifest.append(m.write('SM_Civ33_MagicTower'))

m = Mesh()
# 88 m curtain: thicker, crenellated, meant to dwarf the old 38 m wall.
m.box(0, 0, -16, 48, 12, 78, 'stone', .9)
m.box(0, 0, 60, 50, 14, 4, 'trim')
for x in range(-20, 22, 8):
    m.box(x, 0, 64, 5, 13, 10, 'stone')
    m.box(x, 5.8, 18, 1.6, .8, 8, 'window', .2)
manifest.append(m.write('SM_Civ33_EmpireWall'))

for q in manifest:
    q.setdefault('folder', 'Civilizations30' if q['name'].startswith('SM_Civ30_') else 'Civilizations33')
(O / 'assets.json').write_text(json.dumps(manifest, indent=2))
print([(q['name'], q.get('triangles'), q['folder']) for q in manifest], flush=True)
