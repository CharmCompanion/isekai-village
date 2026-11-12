"""v33: unique kingdom towns, no circle layouts. El Ruhn buildings are not touched."""
from pathlib import Path
import json, sys, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scipy.ndimage import map_coordinates, label, gaussian_filter1d
from world_reference_v30 import global_height
from civilization_ground_v30 import ground
from build_civilization_assets_v30 import Mesh

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S = B / 'Saved/AdventureWorldSource'
O = S / 'Civilizations33'
meta = json.loads((S / 'world_design_v30.json').read_text())
sites = meta['settlements']
D = dict(np.load(S / 'world_reference_v30.npz'))
cx, cy, m = float(D['cx']), float(D['cy']), float(D['mpp'])
rng = np.random.default_rng(33011)
landmask = ~D['water']
clearance = D['water_clearance']
yy, xx = np.mgrid[:landmask.shape[0], :landmask.shape[1]]
X = (cx - xx) * m
Y = (cy - yy) * m
comp, _ = label(landmask)

P = '/Game/IsekaiVillage/AdventureWorld/Meshes/Civilizations/'
assets = {q['name']: P + q['name'] for q in json.loads((O / 'assets.json').read_text())}
assets.update({
    'HouseA': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01',
    'HouseB': '/Game/AdvancedVillagePack/Meshes/SM_House_Var02',
    'HouseC': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01_Extra01',
    'HouseD': '/Game/AdvancedVillagePack/Meshes/SM_House_Var02_Extra',
    'Tent': '/Game/StylizedIsland/Mesh/Props/SM_Tent/SM_Stylized_Tent_Mesh/SM_Stylized_Tent',
    'Market': '/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01',
    'Cart': '/Game/AdvancedVillagePack/Meshes/SM_Cart_Var01',
    'Boat': '/Game/AdvancedVillagePack/Meshes/SM_Boat',
    'Sails': '/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_windmill_sail',
    'Oak': '/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2',
    'Pine': '/Game/SoStylized/Environment/Trees/Pine/SM_Pine01',
    'Palm': '/Game/SoStylized/Environment/Trees/Coastal/SM_PalmTree01',
    'DesertPalm': '/Game/SoStylized/Environment/Trees/Desert/SM_DesertPalmTree01',
})
bounds = json.loads((B / 'Saved/civilization_assets_v30.json').read_text())
rows = {k: [] for k in assets}
roads, foundations = Mesh(), Mesh()
landmarks = []

CAP = {
    'DivineEmpireofGosain': 'Northern island cathedral fortress',
    'YozuanDesert': 'Yozuan regional capital',
    'KelsinFederation': 'Kelsin regional capital',
    'RabaricRepublic': 'Rabaric regional capital',
    'VylfodDominion': 'Vylfod regional capital',
}
LESSER_NAMES = {
    'DivineEmpireofGosain': {'Gosain regional capital'},
    'YozuanDesert': set(),
    'KelsinFederation': set(),
    'RabaricRepublic': set(),
    'VylfodDominion': {'Vylfod tidal harbor'},
}


def onland(x, y, margin=80):
    px, py = int(round(cx - x / m)), int(round(cy - y / m))
    return 0 <= py < landmask.shape[0] and 0 <= px < landmask.shape[1] and bool(clearance[py, px] > margin)


def h(x, y):
    return ground(x, y)


def field(k, x, y):
    return float(map_coordinates(D[k], [[cy - y / m], [cx - x / m]], order=1, mode='nearest')[0])


def add(key, x, y, z=None, scale=1, yaw=0, height=None, site=None, wet=False):
    if key not in ['Boat', 'SM_Civ30_Boardwalk'] and not wet and not onland(x, y, 50 if key in ['Oak', 'Pine', 'Palm', 'DesertPalm', 'SM_Civ30_Reeds'] else 70):
        return
    if z is None:
        z = h(x, y)
    if height is not None:
        path = assets[key]
        if path not in bounds:
            path = assets['HouseA'] if 'Var01' in path else assets['HouseB']
        bb = bounds[path]
        scale = height * 100 / (bb['max'][2] - bb['min'][2])
        z -= bb['min'][2] * scale / 100
    sc = [scale] * 3 if np.isscalar(scale) else list(scale)
    rows[key].append([float(x), float(y), float(z), *map(float, sc), float(yaw), site])


def ribbon(points, width, mat='path'):
    p = np.array(points, float)
    out = []
    for a, b in zip(p[:-1], p[1:]):
        dist = np.linalg.norm(b - a)
        n = max(2, int(dist / 38) + 1)
        out.extend(a + (b - a) * t for t in np.linspace(0, 1, n, endpoint=False))
    out.append(p[-1])
    p = np.array(out)
    tan = np.gradient(p, axis=0)
    tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-5)
    side = np.column_stack([-tan[:, 1], tan[:, 0]]) * width * .5
    v = []
    for a, b in zip(p - side, p + side):
        for q in [a, b]:
            v.append([*q, h(*q) + .35])
    f = []
    for j in range(len(p) - 1):
        if not all(onland(*q, 40) for q in [p[j], p[j + 1], (p[j] + p[j + 1]) * .5]):
            continue
        a = 2 * j
        f.extend([[a, a + 3, a + 1], [a, a + 2, a + 3]])
    if f:
        roads.part(v, f, mat)


def pad(x, y, z, w, d):
    foundations.box(x, y, z - 12, w, d, 12.8, 'stone', .4)


def stone_bridge(a, b, width=14, mat='stone'):
    a, b = np.array(a, float), np.array(b, float)
    length = np.linalg.norm(b - a)
    n = max(4, int(length / 28))
    pts = np.linspace(a, b, n)
    z0, z1 = h(*a) + 6, h(*b) + 6
    zz = np.maximum(np.linspace(z0, z1, n), -20588.)
    tan = b - a
    tan /= np.linalg.norm(tan)
    side = np.array([-tan[1], tan[0]]) * width * .5
    v = []
    for q, z in zip(pts, zz):
        v.extend([[*(q - side), z], [*(q + side), z]])
    f = []
    for k in range(n - 1):
        i = k * 2
        f.extend([[i, i + 3, i + 1], [i, i + 2, i + 3]])
        mid = (pts[k] + pts[k + 1]) * .5
        for s in (-1, 1):
            rail = mid + side * s * 1.05
            roads.box(*rail, (zz[k] + zz[k + 1]) * .5 + 2.2, length / n, .5, 1.1, 'trim', .08, np.arctan2(tan[1], tan[0]))
    roads.part(v, f, mat)
    yaw = np.degrees(np.arctan2(tan[1], tan[0]))
    add('SM_Civ30_Gatehouse', *a, scale=[1.6, 1.8, 2.2], yaw=yaw)
    add('SM_Civ30_Gatehouse', *b, scale=[1.6, 1.8, 2.2], yaw=yaw + 180)


def house_key(culture, k):
    if culture in ('nomad',):
        return 'Tent'
    if culture == 'cult':
        return 'Tent'
    if culture in ('wetland', 'harbor'):
        return 'SM_Civ30_StiltHouse'
    return ('HouseA', 'HouseB', 'HouseC', 'HouseD')[k % 4]


def drop_house(qxy, culture, kind, si, yaw, i):
    zz = h(*qxy)
    key = house_key(culture, i)
    if culture in ('wetland', 'harbor'):
        add(key, *qxy, z=zz + 7, scale=rng.uniform(.75, 1.1), yaw=0, site=si)
    elif culture in ('nomad', 'cult'):
        add(key, *qxy, height=rng.uniform(6, 10), yaw=rng.uniform(0, 360), site=si)
    else:
        ht = rng.uniform(28, 48) if kind == 'capital' else rng.uniform(22, 34) if kind == 'city' else rng.uniform(15, 24)
        add(key, *qxy, z=zz + 1, height=ht, yaw=yaw + rng.uniform(-7, 7), site=si)
        pad(*qxy, zz, ht * .8, ht * .8)


def along_street(origin, direction, half, spacing, width_wobble, culture, kind, si, taken, houses=True):
    d = np.array(direction, float)
    nrm = np.linalg.norm(d)
    if nrm < 1e-6:
        return
    d /= nrm
    side = np.array([-d[1], d[0]])
    n = max(2, int(2 * half / spacing))
    pts = []
    for t in np.linspace(-half, half, n):
        wob = width_wobble * np.sin(t / 70 + si)
        p = origin + d * t + side * wob
        if onland(*p, 70):
            pts.append(p)
    if len(pts) > 1:
        ribbon(pts, 11 if kind in ('capital', 'city') else 7)
    if not houses:
        return
    stagger = spacing * .45
    for i, p in enumerate(pts):
        yaw = np.degrees(np.arctan2(d[1], d[0])) + 90
        for sgn in (1, -1):
            qxy = p + side * sgn * stagger
            if any(np.hypot(qxy[0] - a, qxy[1] - b) < spacing * .7 for a, b in taken) or not onland(*qxy, 80):
                continue
            taken.append([qxy[0], qxy[1]])
            drop_house(qxy, culture, kind, si, yaw + (0 if sgn > 0 else 180), i)


def tier_of(q):
    if q['name'] == CAP.get(q['country']):
        return 'capital'
    if q['name'] in LESSER_NAMES.get(q['country'], ()) or (q['kind'] == 'city' and q['name'] != CAP.get(q['country'])):
        return 'city'
    return q['kind']


# Promote two largest towns per kingdom (except Gosain islands / already named) to lesser cities.
by_c = {}
for q in sites:
    by_c.setdefault(q['country'], []).append(q)
for country, group in by_c.items():
    towns = [q for q in group if q['kind'] == 'town' and q['name'] not in LESSER_NAMES.get(country, ()) and 'island' not in q['name'].lower() and 'harbor' not in q['name'].lower()]
    towns.sort(key=lambda q: -q['radius_m'])
    for q in towns[:2]:
        LESSER_NAMES.setdefault(country, set()).add(q['name'])

for q in sites:
    q['tier'] = tier_of(q)

# Street yaw: farming on the survey grid, others follow the local slope so towns sit in the terrain.
def street_yaw(x, y, culture):
    if culture == 'farming':
        return 0.
    gx = field('height', x + 40, y) - field('height', x - 40, y)
    gy = field('height', x, y + 40) - field('height', x, y - 40)
    return np.degrees(np.arctan2(-gx, gy))  # streets run along the contour


# Chamfered rectangles / lanes — never a radial ring and never a lone plus.
FOOT = {
    ('capital', 'arcane'): (460, 420, 30, 22),
    ('capital', 'farming'): (580, 300, 32, 24),
    ('capital', 'wetland'): (640, 150, 26, 20),
    ('capital', 'harbor'): (500, 130, 26, 16),
    ('capital', 'religious'): (420, 360, 28, 26),
    ('city', 'arcane'): (300, 270, 32, 16),
    ('city', 'farming'): (340, 200, 34, 16),
    ('city', 'wetland'): (360, 110, 28, 12),
    ('city', 'harbor'): (320, 100, 28, 12),
    ('city', 'religious'): (280, 240, 30, 18),
    ('town', 'arcane'): (200, 140, 34, 10),
    ('town', 'farming'): (220, 90, 34, 8),
    ('town', 'wetland'): (240, 70, 28, 8),
    ('town', 'religious'): (180, 140, 32, 12),
    ('village', 'arcane'): (120, 40, 32, 0),
    ('village', 'farming'): (140, 32, 34, 0),
    ('village', 'wetland'): (160, 28, 28, 0),
    ('village', 'religious'): (110, 50, 32, 0),
}


def fill_district(si, q):
    x, y = q['xy_m']
    culture, kind = q['culture'], q['tier']
    hu, hv, sp, plaza = FOOT.get((kind, culture), (140, 48, 34, 8))
    yaw = np.radians(street_yaw(x, y, culture) + (0 if culture == 'farming' else rng.uniform(-5, 5)))
    d = np.array([np.cos(yaw), np.sin(yaw)])
    svec = np.array([-d[1], d[0]])
    taken = q.setdefault('taken', [])
    origin = np.array([x, y], float)
    i = 0
    for u in np.arange(-hu, hu + sp * .5, sp):
        for v in np.arange(-hv, hv + sp * .5, sp):
            if abs(u) / max(hu, 1) + abs(v) / max(hv, 1) > 1.28:
                continue
            if abs(u) < plaza and abs(v) < plaza:
                continue
            if culture == 'farming' and (int(round(u / sp)) + int(round(v / sp))) % 8 == 0:
                continue
            if kind != 'village' and rng.random() < .07:
                continue
            qxy = origin + d * u + svec * (v + 7 * np.sin(u / 60.0))
            if not onland(*qxy, 80):
                continue
            yaw_h = np.degrees(yaw) + (90 if abs(v) > abs(u) * .35 else 0)
            taken.append([qxy[0], qxy[1]])
            drop_house(qxy, culture, kind, si, yaw_h, i)
            i += 1
    step_u = sp * (3 if kind in ('capital', 'city') else 4)
    step_v = sp * (2 if culture in ('wetland', 'harbor') else 3)
    for v in np.arange(-hv, hv + 1, step_v):
        ribbon([origin + svec * v - d * hu, origin + svec * v + d * hu], 9 if kind == 'capital' else 6)
    if culture not in ('wetland', 'harbor'):
        for u in np.arange(-hu, hu + 1, step_u):
            ribbon([origin + d * u - svec * hv, origin + d * u + svec * hv], 7 if kind == 'capital' else 5)
    return taken


def capital_tower(si, q, scale=3.2):
    x, y = q['xy_m']
    add('SM_Civ33_MagicTower', x, y, scale=scale, site=si)
    landmarks.append({'name': q['name'] + ' — capital spire', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': q['culture'], 'radius': q['radius_m'], 'tier': 'capital'})


def fill_island(comp_id, si, q, core, core_r, spacing=22):
    """Dense streets along the island spine, packed keep around the cathedral — not a dotted field."""
    msk = (comp == comp_id) & (clearance > 70) & (D['cliff'] < .16)
    pts = np.column_stack([X[msk], Y[msk]])
    taken = q.setdefault('taken', [])
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis, cross = vt[0], vt[1]
    u0, v0 = np.dot(np.array(core) - c, axis), np.dot(np.array(core) - c, cross)
    umin, umax = pts.dot(axis).min(), pts.dot(axis).max()
    laterals = np.linspace(v0 - 380, v0 + 380, 5)
    grid = set()
    for p in pts:
        u, v = np.dot(p - c, axis), np.dot(p - c, cross)
        in_keep = abs(u - u0) < core_r and abs(v - v0) < core_r * .75
        sp = 18 if in_keep else 40
        su, sv = round(u / sp) * sp, round(v / sp) * sp
        qxy = c + axis * su + cross * sv
        g = (round(qxy[0] / 14), round(qxy[1] / 14))
        if g in grid or not onland(*qxy, 70):
            continue
        if abs(u - u0) < 40 and abs(v - v0) < 40:
            continue
        grid.add(g)
        taken.append([qxy[0], qxy[1]])
        yaw = np.degrees(np.arctan2(axis[1], axis[0])) + (90 if abs(sv - v0) > 40 else 0)
        zz = h(*qxy)
        ht = rng.uniform(32, 52) if in_keep else rng.uniform(18, 30)
        add(house_key('religious', len(taken)), *qxy, z=zz + 1, height=ht, yaw=yaw + rng.uniform(-6, 6), site=si)
        pad(*qxy, zz, ht * .75, ht * .75)
    along_street(c + axis * u0 + cross * v0, axis, (umax - umin) * .42, 28, 8, 'religious', 'capital', si, taken, houses=False)
    along_street(c + axis * u0 + cross * v0, cross, 420, 28, 6, 'religious', 'capital', si, taken, houses=False)
    for lat in laterals[::2]:
        along_street(c + cross * lat, axis, (umax - umin) * .35, 32, 6, 'religious', 'capital', si, taken, houses=False)


def coast_wall(comp_id, inset, wall_key, scale_xy, scale_z, site=None, bastion='SM_Civ30_Bastion', every=5):
    msk = (comp == comp_id) & (np.abs(clearance - inset) < m * .7)
    if msk.sum() < 12:
        return
    pts = np.column_stack([X[msk], Y[msk]])
    c = pts.mean(0)
    ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0])
    order = np.argsort(ang)
    ring = gaussian_filter1d(pts[order], 1.1, axis=0, mode='wrap')
    for k, (a, b) in enumerate(zip(ring, np.roll(ring, -1, axis=0))):
        mid = (a + b) * .5
        if field('coast', *mid) < 40:
            continue
        length = np.linalg.norm(b - a)
        yaw = np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0]))
        add(wall_key, *mid, scale=[max(.4, length / 48), scale_xy, scale_z], yaw=yaw, site=site)
        if k % (every * 3) == 0:
            add('SM_Civ30_Banner', *mid, z=h(*mid) + 28 * scale_z, scale=scale_z * .45, site=site)
        if k % every == 0:
            add(bastion, *a, scale=scale_z * .55, site=site)


# --- place every mainland settlement ---
for si, q in enumerate(sites):
    x, y = q['xy_m']
    r = q['radius_m']
    culture, kind = q['culture'], q['tier']
    q['instance_start'] = {k: len(v) for k, v in rows.items()}
    # Gosain capital islands are filled as one city below.
    if q['name'] in ('Northern island cathedral fortress', 'Northern island monastery fortress'):
        q['instances'] = 0
        continue
    if culture == 'cult':
        # Processional approach into the sanctuary, not a ring of tents.
        yaw = np.radians(street_yaw(x, y, culture))
        d = np.array([np.cos(yaw), np.sin(yaw)])
        taken = q.setdefault('taken', [])
        along_street(np.array([x, y]) - d * r * .2, d, r * .9, 22, 6, culture, kind, si, taken)
        add('SM_Civ30_Sanctuary', x, y, scale=1.4 if kind != 'village' else .8, site=si)
        add('SM_Civ30_Bastion', *(np.array([x, y]) + d * r * .55), scale=.7, site=si)
        add('SM_Civ30_Bastion', *(np.array([x, y]) - d * r * .55), scale=.7, site=si)
        landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
    elif culture == 'nomad':
        taken = q.setdefault('taken', [])
        yaw = np.radians(street_yaw(x, y, culture))
        d = np.array([np.cos(yaw), np.sin(yaw)])
        svec = np.array([-d[1], d[0]])
        hu, hv = (520, 180) if kind == 'capital' else (200, 80) if kind == 'town' else (90, 40)
        ribbon([np.array([x, y]) - d * hu, np.array([x, y]) + d * hu], 8)
        for u in np.arange(-hu, hu, 16):
            for v in np.arange(-hv, hv, 14):
                if abs(u) < 36 and abs(v) < 36:
                    continue
                if abs(u) / hu + abs(v) / hv > 1.2:
                    continue
                if rng.random() < .22:
                    continue
                qxy = np.array([x, y]) + d * u + svec * v
                if not onland(*qxy, 70):
                    continue
                add('Tent', *qxy, height=rng.uniform(6, 10), yaw=rng.uniform(0, 360), site=si)
        for o in (-.4, 0, .4)[: 3 if kind != 'village' else 1]:
            add('Market', *(np.array([x, y]) + d * o * hu * .8), height=8, site=si)
            add('Cart', *(np.array([x, y]) + d * o * hu * .8 + svec * 16), height=3, site=si)
        if kind == 'capital':
            capital_tower(si, q, 2.8)
            landmarks[-1]['name'] = 'Yozuan caravan capital'
    else:
        fill_district(si, q)
        if kind == 'capital':
            capital_tower(si, q, 3.2 if culture == 'arcane' else 3.0)
        if culture in ('religious', 'citadel'):
            add('SM_Civ30_Cathedral', x, y + 40, scale=1.4 if kind == 'capital' else .9 if kind == 'city' else .55, site=si)
            if kind in ('capital', 'city'):
                # Rectangular precinct, not a ring.
                w, dlen = r * .55, r * .4
                for sx, sy, yaw in ((-w, 0, 90), (w, 0, 90), (0, -dlen, 0), (0, dlen, 0)):
                    add('SM_Civ30_CurtainWall', x + sx, y + sy + 40, scale=[(dlen if abs(sx) else w) / 21, 1.1, 1.4], yaw=yaw, site=si)
                add('SM_Civ30_Gatehouse', x, y - dlen + 40, scale=1.2, yaw=0, site=si)
                add('SM_Civ30_SacredTower', x - w * .7, y + 40, scale=1.3, site=si)
                add('SM_Civ30_SacredTower', x + w * .7, y + 40, scale=1.3, site=si)
            landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
        elif culture == 'arcane':
            add('SM_Civ30_ArcaneTower', x, y, scale=.4 if kind != 'capital' else .55, site=si)
            # Manufactories as a workshop row along the main avenue, not a heptagon.
            yaw = np.radians(street_yaw(x, y, culture))
            d = np.array([np.cos(yaw), np.sin(yaw)])
            for t in (-.55, -.28, .28, .55)[: 4 if kind != 'village' else 2]:
                p = np.array([x, y]) + d * t * r
                add('SM_Civ30_Manufactory', *p, scale=.9 if kind == 'capital' else .55, yaw=np.degrees(yaw) + 90, site=si)
                ribbon([[x, y], p.tolist()], 3, 'conduit')
            if kind == 'capital':
                landmarks.append({'name': 'Kelsin arcane capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
        elif culture == 'farming':
            add('SM_Civ30_Mill', x + r * .35, y, scale=1.4 if kind == 'capital' else 1.0, site=si)
            add('Sails', x + r * .35, y - 10, h(x + r * .35, y) + 26, scale=2, site=si)
            add('SM_Civ30_Granary', x + r * .35 + 50, y, scale=1.3 if kind == 'capital' else .9, site=si)
            if kind == 'capital':
                for k in range(8):
                    add('Market', x - 40 + k * 14, y - 50, height=6, site=si)
                landmarks.append({'name': 'Rabaric farming capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
        elif culture in ('wetland', 'harbor'):
            # Boardwalks as the streets, houses already placed facing them.
            span = FOOT.get((kind, culture), (160, 28, 28, 0))[0]
            for s in (-1, 1):
                yaw = street_yaw(x, y, culture)
                d = np.array([np.cos(np.radians(yaw)), np.sin(np.radians(yaw))])
                side = np.array([-d[1], d[0]]) * 28 * s
                pts = [np.array([x, y]) + d * t + side for t in np.linspace(-span, span, 18)]
                for p in pts:
                    add('SM_Civ30_Boardwalk', *p, z=h(*p) + 6, yaw=yaw, site=si)
            if kind == 'capital':
                landmarks.append({'name': 'Vylfod tidal capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
            if culture == 'harbor':
                landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': r, 'tier': kind})
        if culture not in ('nomad', 'cult', 'harbor', 'wetland'):
            for k in range(4 if kind == 'capital' else 2):
                add('Market', x - r * .12 + k * 16, y - r * .2, height=6, site=si)
            tree = 'Pine' if culture in ('religious', 'citadel') else 'Oak'
            for k in range(40 if kind == 'capital' else 16 if kind == 'city' else 6):
                a = rng.uniform(0, 2 * np.pi)
                rr = rng.uniform(r * .2, r * .95)
                xx, yy = x + rr * np.cos(a), y + rr * np.sin(a)
                if any(np.hypot(xx - a, yy - b) < 26 for a, b in q.get('taken', [])):
                    continue
                add(tree, xx, yy, height=rng.uniform(13, 22), site=si)
    q.pop('taken', None)
    q['instances'] = sum(len(rows[k]) - q['instance_start'][k] for k in rows)
    q.pop('instance_start')

# --- Gosain empire city: both northern islands ---
cit = next(s for s in sites if s['name'] == 'Northern island cathedral fortress')
mon = next(s for s in sites if s['name'] == 'Northern island monastery fortress')
cid, mid = int(comp[int(round(cy - cit['xy_m'][1] / m)), int(round(cx - cit['xy_m'][0] / m))]), int(comp[int(round(cy - mon['xy_m'][1] / m)), int(round(cx - mon['xy_m'][0] / m))])
si_c, si_m = sites.index(cit), sites.index(mon)
cit['taken'] = []
mon['taken'] = []
# Keep a plaza around the tower / cathedral.
cit['taken'].extend([[cit['xy_m'][0] + dx, cit['xy_m'][1] + dy] for dx in range(-80, 81, 20) for dy in range(-80, 81, 20)])
fill_island(cid, si_c, cit, cit['xy_m'], 380, 20)
fill_island(mid, si_m, mon, mon['xy_m'], 280, 22)
# Landmarks: cathedral + cloister on the citadel, monastery keep on the sister island, one spire.
add('SM_Civ33_MagicTower', *cit['xy_m'], scale=3.6, site=si_c)
add('SM_Civ30_Cathedral', cit['xy_m'][0], cit['xy_m'][1] + 90, scale=3.2, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] - 140, cit['xy_m'][1] + 40, scale=2.4, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] + 140, cit['xy_m'][1] + 40, scale=2.4, site=si_c)
add('SM_Civ30_Cathedral', *mon['xy_m'], scale=1.6, site=si_m)
add('SM_Civ30_SacredTower', mon['xy_m'][0] - 80, mon['xy_m'][1], scale=1.8, site=si_m)
coast_wall(cid, 110, 'SM_Civ33_EmpireWall', 2.4, 2.8, si_c, 'SM_Civ30_Bastion', 4)
coast_wall(mid, 110, 'SM_Civ33_EmpireWall', 2.2, 2.5, si_m, 'SM_Civ30_Bastion', 5)
# Inner precinct around the cathedral — a rectangle of the taller wall.
cx0, cy0 = cit['xy_m']
for sx, sy, yaw, length in ((-220, 90, 90, 380), (220, 90, 90, 380), (0, -100, 0, 440), (0, 280, 0, 440)):
    add('SM_Civ33_EmpireWall', cx0 + sx, cy0 + sy, scale=[length / 48, 2.0, 2.2], yaw=yaw, site=si_c)
add('SM_Civ30_Gatehouse', cx0, cy0 - 100, scale=[2.2, 2.4, 2.6], yaw=0, site=si_c)
landmarks.append({'name': 'Divine Empire of Gosain — island capital', 'xy_m': cit['xy_m'], 'z': cit['ground_m'], 'culture': 'citadel', 'radius': 4200, 'tier': 'capital'})
landmarks.append({'name': 'Gosain monastery quarter', 'xy_m': mon['xy_m'], 'z': mon['ground_m'], 'culture': 'religious', 'radius': 2800, 'tier': 'capital'})

# Closest island-island and monastery-mainland landings.
rng2 = np.random.default_rng(4)


def sample_comp(i, n=2500):
    msk = comp == i
    pts = np.column_stack([X[msk], Y[msk]])
    return pts[rng2.choice(len(pts), min(n, len(pts)), replace=False)]


from scipy.spatial import cKDTree
A, B = sample_comp(cid), sample_comp(mid)
tB = cKDTree(B)
d, j = tB.query(A)
k = int(d.argmin())
stone_bridge(A[k], B[j[k]], 18)
mainland_id = int(comp[int(round(cy - 24425 / m)), int(round(cx - 1134 / m))])
C = sample_comp(mainland_id, 5000)
tC = cKDTree(C)
d, j = tC.query(B)
k = int(d.argmin())
stone_bridge(B[k], C[j[k]], 16)
cit.pop('taken', None)
mon.pop('taken', None)

# National routes and farms (unchanged world network).
for q in meta['routes'] + meta['farm_lanes']:
    ribbon(q['points_m'], q['width_m'])
for bridge in meta.get('bridges', []):
    p = np.array(bridge['points_m'])
    stone_bridge(p[0], p[-1], 12, 'wood')
for k, q in enumerate(meta['agricultural_parcels']):
    pts = np.array(q['corners'])
    ax, ay = pts[0]
    bx, by = pts[2]
    nx, ny = 4, 8
    v = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            xx = ax + (bx - ax) * i / nx
            yy = ay + (by - ay) * j / ny
            v.append([xx, yy, h(xx, yy) + .12])
    f = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            f.extend([[a, a + 1, a + nx + 2], [a, a + nx + 2, a + nx + 1]])
    roads.part(v, f, 'crop' + str(q['crop']))
    if k % 4 == 0:
        for yy in np.arange(ay + 50, by - 35, 105):
            add('Oak', ax - 11, yy, height=rng.uniform(6, 9), yaw=rng.uniform(0, 360))
    if k % 25 == 0:
        add('SM_Civ30_Granary', ax + 30, ay + 32, scale=.65)
        add('Cart', ax + 55, ay + 30, height=3, yaw=90)

# Wetland reeds / oasis palms / boats — same ecology dressing as v30.
wet = D['wetland']
valid = (wet > .25) & (D['channel'] < .2) & (D['height'] > -20599) & (D['height'] < -20565)
py, px = np.where(valid)
for k in range(3600):
    j = int(rng.integers(len(px)))
    x = (cx - px[j]) * m + rng.uniform(-35, 35)
    y = (cy - py[j]) * m + rng.uniform(-35, 35)
    z = h(x, y)
    if z < -20599:
        continue
    add('SM_Civ30_Reeds', x, y, z=z, scale=rng.uniform(3, 6), yaw=rng.uniform(0, 360))
    if k % 7 == 0:
        add('Palm', x + 12, y + 15, height=rng.uniform(20, 34), yaw=rng.uniform(0, 360))
q = next(q for q in sites if q['culture'] == 'harbor')
x, y = q['xy_m']
py, px = np.where((D['channel'] > .90) & (D['height'] < -20599))
wx, wy = (cx - px) * m, (cy - py) * m
j = int(np.argmin((wx - x) ** 2 + (wy - y) ** 2))
target = np.array([wx[j], wy[j]])
start = np.array([x, y])
length = np.linalg.norm(target - start)
direction = (target - start) / length
yaw = np.degrees(np.arctan2(direction[1], direction[0])) - 90
for t in np.linspace(0, 1, max(2, int(length / 23) + 1)):
    xy = start + (target - start) * t
    add('SM_Civ30_Boardwalk', *xy, z=max(-20595., h(*xy) + 5), yaw=yaw, wet=True)
for side in (-1, 1):
    add('Boat', target[0] + direction[1] * 22 * side, target[1] - direction[0] * 22 * side, z=-20599.3, height=4, yaw=yaw + 90)
for spring in meta['oasis_sites']:
    x, y = spring['xy_m']
    rx, ry = spring['radius_m']
    for j in range(45):
        a = rng.uniform(0, 2 * np.pi)
        rr = rng.uniform(1.10, 1.8)
        add('DesertPalm', x + rx * rr * np.cos(a), y + ry * rr * np.sin(a), height=rng.uniform(15, 25), yaw=rng.uniform(0, 360))
py, px = np.where((D['channel'] > .97) & (D['coast'] > 300))
for k in range(min(32, len(px))):
    j = int(rng.integers(len(px)))
    add('Boat', (cx - px[j]) * m, (cy - py[j]) * m, z=-20599.3, height=3.5, yaw=rng.uniform(0, 360))

for p in rows['SM_Civ33_EmpireWall'] + rows['SM_Civ30_CurtainWall']:
    a = np.radians(p[6])
    dx, dy = 20 * p[3] * np.cos(a), 20 * p[3] * np.sin(a)
    variation = max(abs(h(p[0] + dx, p[1] + dy) - p[2]), abs(h(p[0] - dx, p[1] - dy) - p[2]))
    p[5] = max(p[5], (variation + 3) / 40)

ns = {}
# Mesh.write looks up O in build_civilization_assets_v30; point it at v33 for roads/foundations.
import build_civilization_assets_v30 as A30
_old = A30.O
A30.O = O
roads.write('SM_Civ33_Roads')
foundations.write('SM_Civ33_Foundations')
A30.O = _old

manifest = json.loads((O / 'assets.json').read_text())
for mesh, name in ((roads, 'SM_Civ33_Roads'), (foundations, 'SM_Civ33_Foundations')):
    manifest.append({'name': name, 'vertices': len(mesh.v), 'triangles': len(mesh.f), 'materials': sorted(set(mesh.mat)), 'folder': 'Civilizations33'})
(O / 'assets.json').write_text(json.dumps(manifest, indent=2))
assets.update({q['name']: P + q['name'] for q in manifest if q['name'] not in assets})
(S / 'civilization_instances_v33.json').write_text(json.dumps({'assets': assets, 'instances': rows, 'landmarks': landmarks}, indent=2))
meta['settlements'] = sites
meta['placed_instances'] = sum(map(len, rows.values()))
meta['regional_landmarks'] = landmarks
meta['content_version'] = 33
(S / 'world_design_v33.json').write_text(json.dumps(meta, indent=2))
print({'instances': meta['placed_instances'], 'counts': {k: len(v) for k, v in rows.items() if v}, 'capitals': [q['name'] for q in sites if q['tier'] == 'capital'], 'lesser': [q['name'] for q in sites if q['tier'] == 'city'][:12]}, flush=True)
