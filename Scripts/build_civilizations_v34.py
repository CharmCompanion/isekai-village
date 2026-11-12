"""v34: real street towns (native house scale) and Vylfod floating pleasure city."""
from pathlib import Path
import json, sys, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scipy.ndimage import map_coordinates, label, gaussian_filter1d
from scipy.spatial import cKDTree
from civilization_ground_v30 import ground
from build_civilization_assets_v30 import Mesh

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S = B / 'Saved/AdventureWorldSource'
O = S / 'Civilizations34'
meta = json.loads((S / 'world_design_v30.json').read_text())
sites = meta['settlements']
D = dict(np.load(S / 'world_reference_v30.npz'))
cx, cy, mpp = float(D['cx']), float(D['cy']), float(D['mpp'])
rng = np.random.default_rng(34021)
landmask = ~D['water']
clearance = D['water_clearance']
yy, xx = np.mgrid[:landmask.shape[0], :landmask.shape[1]]
X = (cx - xx) * mpp
Y = (cy - yy) * mpp
comp, _ = label(landmask)

Pth = '/Game/IsekaiVillage/AdventureWorld/Meshes/Civilizations/'
assets = {q['name']: Pth + q['name'] for q in json.loads((O / 'assets.json').read_text())}
assets.update({
    'HouseA': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01',
    'HouseB': '/Game/AdvancedVillagePack/Meshes/SM_House_Var02',
    'HouseC': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01_Extra01',
    'HouseD': '/Game/AdvancedVillagePack/Meshes/SM_House_Var02_Extra',
    'HouseE': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01_Extra02',
    'HouseF': '/Game/AdvancedVillagePack/Meshes/SM_House_Var01_Extra03',
    'Tent': '/Game/StylizedIsland/Mesh/Props/SM_Tent/SM_Stylized_Tent_Mesh/SM_Stylized_Tent',
    'Market': '/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01',
    'Market2': '/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v02_01',
    'Market3': '/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v03_01',
    'Cart': '/Game/AdvancedVillagePack/Meshes/SM_Cart_Var01',
    'Well': '/Game/AdvancedVillagePack/Meshes/SM_Well',
    'Lamp': '/Game/AdvancedVillagePack/Meshes/SM_StreetLight',
    'Fence': '/Game/AdvancedVillagePack/Meshes/SM_Fence_Var01',
    'Barrel': '/Game/AdvancedVillagePack/Meshes/SM_Barrel',
    'Crate': '/Game/AdvancedVillagePack/Meshes/SM_Crate_Closed',
    'Hay': '/Game/AdvancedVillagePack/Meshes/SM_Hay_Stack',
    'Sack': '/Game/AdvancedVillagePack/Meshes/SM_Sack_Flour',
    'Bench': '/Game/Fantastic_Village_Pack/meshes/props/furniture/SM_PROP_bench_01',
    'Table': '/Game/Fantastic_Village_Pack/meshes/props/furniture/SM_PROP_table_01',
    'Lantern': '/Game/Fantastic_Village_Pack/meshes/props/light/SM_PROP_lantern_01',
    'Sign': '/Game/Fantastic_Village_Pack/meshes/props/deco/SM_PROP_signpost_01',
    'Boat': '/Game/AdvancedVillagePack/Meshes/SM_Boat',
    'Sails': '/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_windmill_sail',
    'Oak': '/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2',
    'Pine': '/Game/SoStylized/Environment/Trees/Pine/SM_Pine01',
    'Palm': '/Game/SoStylized/Environment/Trees/Coastal/SM_PalmTree01',
    'DesertPalm': '/Game/SoStylized/Environment/Trees/Desert/SM_DesertPalmTree01',
})
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
# West of the continent (map-west = +X), hanging in the sky as Vylfod's pleasure capital.
FLOAT = np.array([56800.0, -6200.0])
FLOAT_Z = -1680.0

by_c = {}
for q in sites:
    by_c.setdefault(q['country'], []).append(q)
for country, group in by_c.items():
    towns = [q for q in group if q['kind'] == 'town' and q['name'] not in LESSER_NAMES.get(country, ()) and 'island' not in q['name'].lower() and 'harbor' not in q['name'].lower()]
    towns.sort(key=lambda q: -q['radius_m'])
    for q in towns[:2]:
        LESSER_NAMES.setdefault(country, set()).add(q['name'])


def tier_of(q):
    if q['name'] == CAP.get(q['country']):
        return 'capital'
    if q['name'] in LESSER_NAMES.get(q['country'], ()) or (q['kind'] == 'city' and q['name'] != CAP.get(q['country'])):
        return 'city'
    return q['kind']


for q in sites:
    q['tier'] = tier_of(q)


def onland(x, y, margin=50):
    px, py = int(round(cx - x / mpp)), int(round(cy - y / mpp))
    return 0 <= py < landmask.shape[0] and 0 <= px < landmask.shape[1] and bool(clearance[py, px] > margin)


def h(x, y):
    return ground(x, y)


def field(k, x, y):
    return float(map_coordinates(D[k], [[cy - y / mpp], [cx - x / mpp]], order=1, mode='nearest')[0])


def add(key, x, y, z=None, scale=1, yaw=0, site=None, wet=False):
    loose = {'Oak', 'Pine', 'Palm', 'DesertPalm', 'SM_Civ30_Reeds', 'Lamp', 'Fence', 'Barrel', 'Crate', 'Hay', 'Sack', 'Bench', 'Table', 'Lantern', 'Sign', 'Well', 'Cart', 'Market', 'Market2', 'Market3'}
    if key not in ('Boat', 'SM_Civ30_Boardwalk', 'SM_Civ34_PleasureIsle') and not wet and not onland(x, y, 35 if key in loose else 55):
        return
    if z is None:
        z = h(x, y)
    sc = [scale] * 3 if np.isscalar(scale) else list(scale)
    rows[key].append([float(x), float(y), float(z), *map(float, sc), float(yaw), site])


def ribbon(points, width, mat='path', zf=None, check=True):
    p = np.array(points, float)
    out = []
    for a, b in zip(p[:-1], p[1:]):
        dist = np.linalg.norm(b - a)
        n = max(2, int(dist / 12) + 1)
        out.extend(a + (b - a) * t for t in np.linspace(0, 1, n, endpoint=False))
    out.append(p[-1])
    p = np.array(out)
    tan = np.gradient(p, axis=0)
    tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-5)
    side = np.column_stack([-tan[:, 1], tan[:, 0]]) * width * .5
    v, f = [], []
    for a, b in zip(p - side, p + side):
        za = (zf(*a) if zf else h(*a)) + .12
        zb = (zf(*b) if zf else h(*b)) + .12
        v.extend([[*a, za], [*b, zb]])
    for j in range(len(p) - 1):
        if check and zf is None and not all(onland(*q, 30) for q in (p[j], p[j + 1])):
            continue
        a = 2 * j
        f.extend([[a, a + 3, a + 1], [a, a + 2, a + 3]])
    if f:
        roads.part(v, f, mat)


def pad(x, y, z, w=5.2, d=5.2):
    foundations.box(x, y, z - 1.6, w, d, 1.8, 'stone', .15)


def house_key(culture, k):
    if culture in ('nomad', 'cult'):
        return 'Tent'
    if culture in ('wetland', 'harbor', 'pleasure'):
        return 'SM_Civ30_StiltHouse' if k % 3 == 0 else ('HouseA', 'HouseC', 'HouseE')[k % 3]
    return ('HouseA', 'HouseB', 'HouseC', 'HouseD', 'HouseE', 'HouseF')[k % 6]


def street_yaw(x, y, culture):
    if culture == 'farming':
        return 0.0
    gx = field('height', x + 30, y) - field('height', x - 30, y)
    gy = field('height', x, y + 30) - field('height', x, y - 30)
    return float(np.degrees(np.arctan2(-gx, gy)))


def put_house(p, yaw, culture, si, i, zf, floating):
    z = zf(*p)
    key = house_key(culture, i)
    if culture in ('nomad', 'cult'):
        add(key, *p, z=z, scale=rng.uniform(1.05, 1.35), yaw=rng.uniform(0, 360), site=si, wet=floating)
        return
    sc = rng.uniform(.96, 1.18)
    if culture in ('wetland', 'harbor', 'pleasure') and key == 'SM_Civ30_StiltHouse':
        add(key, *p, z=z + (0 if floating else 5), scale=rng.uniform(.85, 1.05), yaw=yaw, site=si, wet=floating)
        return
    add(key, *p, z=z, scale=sc, yaw=yaw + rng.uniform(-4, 4), site=si, wet=floating)
    if not floating:
        pad(*p, z)


def shop(p, yaw, si, zf, floating, k=0):
    key = ('Market', 'Market2', 'Market3')[k % 3]
    add(key, *p, z=zf(*p), scale=rng.uniform(1.15, 1.45), yaw=yaw, site=si, wet=floating)


def prop(key, p, yaw, si, zf, floating, scale=1.0):
    add(key, *p, z=zf(*p), scale=scale, yaw=yaw, site=si, wet=floating)


def town(origin, yaw_deg, nx, ny, culture, kind, si, zf=None, floating=False, plaza=True):
    """Street grid, house rows, mid-block alleys, plaza shops, street furniture."""
    origin = np.array(origin, float)
    yaw = np.radians(yaw_deg)
    d = np.array([np.cos(yaw), np.sin(yaw)])
    s = np.array([-d[1], d[0]])
    px, py = 38.0, 26.0
    lot = 6.2
    setback = 5.35
    zf = zf or h

    def xy(u, v):
        return origin + d * u + s * v

    hu, hv = nx * px * .5, ny * py * .5
    for j in range(ny + 1):
        v = -hv + j * py
        ribbon([xy(-hu, v), xy(hu, v)], 7.4 if j in (0, ny) else 6.6, zf=zf, check=not floating)
    for i in range(nx + 1):
        u = -hu + i * px
        ribbon([xy(u, -hv), xy(u, hv)], 6.6, zf=zf, check=not floating)
    # Mid-block alleys and backyard fences
    for i in range(nx):
        for j in range(ny):
            uc = -hu + (i + .5) * px
            vc = -hv + (j + .5) * py
            if plaza and abs(uc) < px and abs(vc) < py:
                continue
            ribbon([xy(uc, vc - py * .32), xy(uc, vc + py * .32)], 2.1, zf=zf, check=not floating)
            for dv in (-py * .22, py * .22):
                prop('Fence', xy(uc - 6, vc + dv), yaw_deg, si, zf, floating, .9)
                prop('Fence', xy(uc + 6, vc + dv), yaw_deg, si, zf, floating, .9)
    n = 0

    def along(a, b, side_sign, face, axis='u'):
        nonlocal n
        a, b = np.array(a, float), np.array(b, float)
        seg = b - a
        length = np.linalg.norm(seg)
        if length < 8:
            return
        tdir = seg / length
        side = np.array([-tdir[1], tdir[0]]) * side_sign
        k = 0
        t = 3.0
        while t < length - 3.0:
            p = a + tdir * t + side * setback
            rel = p - origin
            u, v = np.dot(rel, d), np.dot(rel, s)
            if plaza and abs(u) < px * 1.05 and abs(v) < py * 1.05:
                t += lot
                continue
            if axis == 'u' and min(abs((u + hu) % px), px - abs((u + hu) % px)) < 4.2:
                t += lot
                continue
            if axis == 'v' and min(abs((v + hv) % py), py - abs((v + hv) % py)) < 4.2:
                t += lot
                continue
            if (not floating) and (not onland(*p, 55)):
                t += lot
                continue
            put_house(p, face, culture, si, n, zf, floating)
            n += 1
            curb = p - side * 2.2
            if k % 2 == 0:
                prop('Barrel', curb + tdir * 1.1, face, si, zf, floating, rng.uniform(.85, 1.1))
            if k % 3 == 0:
                prop('Crate', curb - tdir * 1.0, face + 15, si, zf, floating, rng.uniform(.8, 1.05))
            if culture == 'farming' and k % 4 == 0:
                prop('Sack', curb + tdir * .4, face, si, zf, floating, 1.0)
                if k % 8 == 0:
                    prop('Hay', p + side * 3.4, face, si, zf, floating, .7)
            if k % 5 == 4:
                t += 3.0
            if k % 6 == 2 and kind in ('capital', 'city', 'town'):
                shop(p + side * 1.4, face, si, zf, floating, k)
            t += lot
            k += 1

    for j in range(ny + 1):
        v = -hv + j * py
        if j < ny:
            along(xy(-hu, v), xy(hu, v), 1, yaw_deg - 90, 'u')
        if j > 0:
            along(xy(-hu, v), xy(hu, v), -1, yaw_deg + 90, 'u')
    for i in range(nx + 1):
        u = -hu + i * px
        if i < nx:
            along(xy(u, -hv), xy(u, hv), 1, yaw_deg + 180, 'v')
        if i > 0:
            along(xy(u, -hv), xy(u, hv), -1, yaw_deg, 'v')
    # Lamps and signs on every street
    for j in range(ny + 1):
        v = -hv + j * py
        for u in np.arange(-hu + 6, hu - 6, 14):
            prop('Lamp', xy(u, v + 2.6), yaw_deg, si, zf, floating)
            if int(u / 14) % 3 == 0:
                prop('Lantern', xy(u + 1.5, v - 2.4), yaw_deg, si, zf, floating, 1.1)
    for i in range(0, nx + 1, max(1, nx // 3)):
        u = -hu + i * px
        prop('Sign', xy(u + 2.2, 3.0), yaw_deg + 90, si, zf, floating, 1.15)
    if plaza:
        ribbon([xy(-px, -py), xy(px, -py), xy(px, py), xy(-px, py), xy(-px, -py)], 12, zf=zf, check=not floating)
        ribbon([xy(-px * .55, 0), xy(px * .55, 0)], 4.5, zf=zf, check=not floating)
        ribbon([xy(0, -py * .55), xy(0, py * .55)], 4.5, zf=zf, check=not floating)
        prop('Well', xy(0, 0), yaw_deg, si, zf, floating, 1.35)
        for k, ang in enumerate(np.linspace(0, 2 * np.pi, 14, endpoint=False)):
            shop(xy(13 * np.cos(ang), 13 * np.sin(ang)), np.degrees(ang) + 90, si, zf, floating, k)
        for k, ang in enumerate(np.linspace(.2, 2 * np.pi, 8, endpoint=False)):
            shop(xy(22 * np.cos(ang), 20 * np.sin(ang)), np.degrees(ang) + 90, si, zf, floating, k + 3)
        for k, (u, v) in enumerate(((-18, -8), (18, -8), (-18, 8), (18, 8), (0, -20), (0, 20), (-10, 0), (10, 0))):
            prop('Cart', xy(u, v), yaw_deg + (0 if k % 2 == 0 else 90), si, zf, floating)
        for u, v, yw in ((-8, 6, yaw_deg + 180), (8, 6, yaw_deg + 180), (-8, -7, yaw_deg), (8, -7, yaw_deg)):
            prop('Bench', xy(u, v), yw, si, zf, floating, 1.05)
            prop('Table', xy(u * 1.35, v * .35), yw, si, zf, floating, 1.0)
        for u, v in ((-11, 11), (11, 11), (-11, -11), (11, -11)):
            prop('Barrel', xy(u, v), yaw_deg, si, zf, floating)
            prop('Crate', xy(u * .7, v * 1.15), yaw_deg + 40, si, zf, floating)
        tree = 'Palm' if culture in ('wetland', 'harbor', 'pleasure') else 'DesertPalm' if culture in ('nomad', 'cult') else 'Pine' if culture in ('religious', 'citadel') else 'Oak'
        for u, v in ((-24, -18), (24, -18), (-24, 18), (24, 18)):
            prop(tree, xy(u, v), rng.uniform(0, 360), si, zf, floating)
    return n


def lined_road(a, b, culture, si, zf=None, floating=False):
    a, b = np.array(a, float), np.array(b, float)
    zf = zf or h
    ribbon([a, b], 8, zf=zf, check=not floating)
    tan = b - a
    length = np.linalg.norm(tan)
    tan /= length
    side = np.array([-tan[1], tan[0]])
    t = 4
    i = 0
    while t < length - 4:
        for sgn in (-1, 1):
            p = a + tan * t + side * sgn * 5.5
            if (not floating) and (not onland(*p, 55)):
                continue
            put_house(p, np.degrees(np.arctan2(tan[1], tan[0])) + (90 if sgn > 0 else -90), culture, si, i, zf, floating)
            i += 1
        t += 6.4


def stone_bridge(a, b, width=14, mat='stone'):
    a, b = np.array(a, float), np.array(b, float)
    length = np.linalg.norm(b - a)
    n = max(4, int(length / 22))
    pts = np.linspace(a, b, n)
    z0, z1 = h(*a) + 4, h(*b) + 4
    zz = np.maximum(np.linspace(z0, z1, n), -20588.)
    tan = (b - a) / length
    side = np.array([-tan[1], tan[0]]) * width * .5
    v = []
    for q, z in zip(pts, zz):
        v.extend([[*(q - side), z], [*(q + side), z]])
    f = []
    for k in range(n - 1):
        i = k * 2
        f.extend([[i, i + 3, i + 1], [i, i + 2, i + 3]])
    roads.part(v, f, mat)
    yaw = np.degrees(np.arctan2(tan[1], tan[0]))
    add('SM_Civ30_Gatehouse', *a, scale=1.4, yaw=yaw)
    add('SM_Civ30_Gatehouse', *b, scale=1.4, yaw=yaw + 180)


def coast_wall(comp_id, inset, wall_key, scale_xy, scale_z, site=None, every=5):
    msk = (comp == comp_id) & (np.abs(clearance - inset) < mpp * .7)
    if msk.sum() < 12:
        return
    pts = np.column_stack([X[msk], Y[msk]])
    c = pts.mean(0)
    order = np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))
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
            add('SM_Civ30_Bastion', *a, scale=scale_z * .55, site=site)


SIZE = {
    'capital': (12, 9),
    'city': (8, 6),
    'town': (6, 4),
    'village': (4, 2),
}

# --- mainland towns (skip Gosain islands and Vylfod capital; those are special) ---
for si, q in enumerate(sites):
    x, y = q['xy_m']
    culture, kind = q['culture'], q['tier']
    q['instance_start'] = {k: len(v) for k, v in rows.items()}
    if q['name'] in ('Northern island cathedral fortress', 'Northern island monastery fortress', 'Vylfod regional capital'):
        q['instances'] = 0
        continue
    yaw = street_yaw(x, y, culture) + (0 if culture == 'farming' else rng.uniform(-6, 6))
    nx, ny = SIZE[kind]
    if culture == 'cult':
        nx, ny = max(2, nx - 1), 1
        town((x, y), yaw, nx, ny, culture, kind, si, plaza=kind != 'village')
        add('SM_Civ30_Sanctuary', x, y, scale=1.1 if kind != 'village' else .7, site=si)
        landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 80, 'tier': kind})
    elif culture == 'nomad':
        town((x, y), yaw, nx, ny, culture, kind, si, plaza=True)
        if kind == 'capital':
            add('SM_Civ33_MagicTower', x, y, z=h(x, y), scale=2.6, site=si)
            landmarks.append({'name': 'Yozuan caravan capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 220, 'tier': 'capital'})
    else:
        town((x, y), yaw, nx, ny, culture, kind, si, plaza=kind != 'village')
        if kind == 'capital':
            add('SM_Civ33_MagicTower', x, y, z=h(x, y), scale=2.8 if culture == 'arcane' else 2.6, site=si)
            landmarks.append({'name': q['name'] + ' capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 220, 'tier': 'capital'})
        if culture in ('religious', 'citadel'):
            add('SM_Civ30_Cathedral', x, y + 8, scale=.85 if kind == 'city' else .55, site=si)
            if kind == 'city':
                w, dlen = 90, 70
                for sx, sy, yw in ((-w, 0, 90), (w, 0, 90), (0, -dlen, 0), (0, dlen, 0)):
                    add('SM_Civ30_CurtainWall', x + sx, y + sy, scale=[(dlen if abs(sx) else w) / 21, .9, 1.1], yaw=yw, site=si)
            landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 160, 'tier': kind})
        elif culture == 'arcane':
            add('SM_Civ30_ArcaneTower', x + 28, y, scale=.55 if kind == 'capital' else .35, site=si)
            if kind in ('capital', 'city'):
                add('SM_Civ30_Manufactory', x - 48, y + 20, scale=.7, yaw=yaw, site=si)
                add('SM_Civ30_Manufactory', x - 48, y - 20, scale=.7, yaw=yaw, site=si)
                ribbon([[x, y], [x - 48, y + 20]], 2.4, 'conduit')
                ribbon([[x, y], [x - 48, y - 20]], 2.4, 'conduit')
        elif culture == 'farming' and kind in ('capital', 'city', 'town'):
            add('SM_Civ30_Mill', x + nx * 19 + 18, y, scale=1.05, site=si)
            add('Sails', x + nx * 19 + 18, y - 10, h(x + nx * 19 + 18, y) + 26, scale=1.6, site=si)
            add('SM_Civ30_Granary', x + nx * 19 + 40, y, scale=.9, site=si)
    q['instances'] = sum(len(rows[k]) - q['instance_start'][k] for k in rows)
    q.pop('instance_start')

# --- Gosain: dense castle-city on both islands, walls, bridges ---
cit = next(s for s in sites if s['name'] == 'Northern island cathedral fortress')
mon = next(s for s in sites if s['name'] == 'Northern island monastery fortress')
cid = int(comp[int(round(cy - cit['xy_m'][1] / mpp)), int(round(cx - cit['xy_m'][0] / mpp))])
mid = int(comp[int(round(cy - mon['xy_m'][1] / mpp)), int(round(cx - mon['xy_m'][0] / mpp))])
si_c, si_m = sites.index(cit), sites.index(mon)
cyaw = street_yaw(*cit['xy_m'], 'religious')
myaw = street_yaw(*mon['xy_m'], 'religious')
town(cit['xy_m'], cyaw, 14, 11, 'religious', 'capital', si_c)
add('SM_Civ33_MagicTower', *cit['xy_m'], z=h(*cit['xy_m']), scale=3.2, site=si_c)
add('SM_Civ30_Cathedral', cit['xy_m'][0], cit['xy_m'][1] + 12, scale=1.55, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] - 36, cit['xy_m'][1] + 8, scale=1.2, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] + 36, cit['xy_m'][1] + 8, scale=1.2, site=si_c)
# Inner curtain around the city, not a 10 km circle of houses.
for sx, sy, yw, length in ((-230, 0, 90, 280), (230, 0, 90, 280), (0, -200, 0, 460), (0, 200, 0, 460)):
    add('SM_Civ33_EmpireWall', cit['xy_m'][0] + sx, cit['xy_m'][1] + sy, scale=[length / 48, 1.6, 1.8], yaw=yw, site=si_c)
add('SM_Civ30_Gatehouse', cit['xy_m'][0], cit['xy_m'][1] - 200, scale=1.5, yaw=0, site=si_c)
town(mon['xy_m'], myaw, 10, 8, 'religious', 'city', si_m)
add('SM_Civ30_Cathedral', *mon['xy_m'], scale=.95, site=si_m)
add('SM_Civ30_SacredTower', mon['xy_m'][0] - 24, mon['xy_m'][1], scale=1.05, site=si_m)
coast_wall(cid, 110, 'SM_Civ33_EmpireWall', 2.4, 2.8, si_c, 4)
coast_wall(mid, 110, 'SM_Civ33_EmpireWall', 2.2, 2.5, si_m, 5)
landmarks.append({'name': 'Divine Empire of Gosain — island capital', 'xy_m': cit['xy_m'], 'z': cit['ground_m'], 'culture': 'citadel', 'radius': 280, 'tier': 'capital'})
landmarks.append({'name': 'Gosain monastery quarter', 'xy_m': mon['xy_m'], 'z': mon['ground_m'], 'culture': 'religious', 'radius': 200, 'tier': 'capital'})

rng2 = np.random.default_rng(4)


def sample_comp(i, n=2500):
    msk = comp == i
    pts = np.column_stack([X[msk], Y[msk]])
    return pts[rng2.choice(len(pts), min(n, len(pts)), replace=False)]


A, B = sample_comp(cid), sample_comp(mid)
tB = cKDTree(B)
d, j = tB.query(A)
k = int(d.argmin())
bridge_a, bridge_b = A[k], B[j[k]]
stone_bridge(bridge_a, bridge_b, 16)
lined_road(cit['xy_m'], bridge_a, 'religious', si_c)
lined_road(mon['xy_m'], bridge_b, 'religious', si_m)
mainland_id = int(comp[int(round(cy - 24425 / mpp)), int(round(cx - 1134 / mpp))])
C = sample_comp(mainland_id, 5000)
tC = cKDTree(C)
d, j = tC.query(B)
k = int(d.argmin())
stone_bridge(B[k], C[j[k]], 14)
lined_road(mon['xy_m'], B[k], 'religious', si_m)

# --- Vylfod floating pleasure city, west of the continent ---
def fz(x, y):
    return FLOAT_Z + .35


si_v = next(i for i, q in enumerate(sites) if q['name'] == 'Vylfod regional capital')
add('SM_Civ34_PleasureIsle', *FLOAT, z=FLOAT_Z - 2, scale=1.0, yaw=12, site=si_v, wet=True)
town(FLOAT, 12, 10, 6, 'pleasure', 'capital', si_v, zf=fz, floating=True)
add('SM_Civ33_MagicTower', *FLOAT, z=FLOAT_Z, scale=2.4, site=si_v, wet=True)
# Canal boardwalks, cafe tables, lanterns, extra stall rings
for t in np.linspace(-110, 110, 24):
    add('SM_Civ30_Boardwalk', FLOAT[0] + t * np.cos(np.radians(12)), FLOAT[1] + t * np.sin(np.radians(12)), z=FLOAT_Z + 1.2, scale=1.35, yaw=12, site=si_v, wet=True)
for t in np.linspace(-100, 100, 18):
    p = FLOAT + np.array([np.cos(np.radians(12)), np.sin(np.radians(12))]) * t + np.array([-np.sin(np.radians(12)), np.cos(np.radians(12))]) * 7
    prop('Table', p, 12, si_v, fz, True, 1.05)
    prop('Lantern', p + np.array([1.4, 0.6]), 12, si_v, fz, True, 1.2)
    if int(t) % 28 == 0:
        prop('Bench', p - np.array([0, 2.2]), 12, si_v, fz, True, 1.0)
for k, ang in enumerate(np.linspace(0, 2 * np.pi, 18, endpoint=False)):
    shop(FLOAT + 42 * np.array([np.cos(ang), np.sin(ang)]), np.degrees(ang) + 90, si_v, fz, True, k)
    shop(FLOAT + 58 * np.array([np.cos(ang + .12), np.sin(ang + .12)]), np.degrees(ang) + 90, si_v, fz, True, k + 1)
    add('SM_Civ30_Banner', *(FLOAT + 78 * np.array([np.cos(ang), np.sin(ang)])), z=FLOAT_Z + 8, scale=1.0, yaw=np.degrees(ang), site=si_v, wet=True)
    prop('Lamp', FLOAT + 66 * np.array([np.cos(ang), np.sin(ang)]), np.degrees(ang), si_v, fz, True)
for k in range(16):
    a = rng.uniform(0, 2 * np.pi)
    add('Boat', *(FLOAT + rng.uniform(205, 255) * np.array([np.cos(a), np.sin(a)])), z=FLOAT_Z - 6, scale=1.15, yaw=rng.uniform(0, 360), site=si_v, wet=True)
    add('Palm', *(FLOAT + rng.uniform(85, 170) * np.array([np.cos(a), np.sin(a)])), z=FLOAT_Z, scale=1.1, yaw=rng.uniform(0, 360), site=si_v, wet=True)
landmarks.append({'name': 'Vylfod pleasure sky-city', 'xy_m': FLOAT.tolist(), 'z': FLOAT_Z, 'culture': 'pleasure', 'radius': 220, 'tier': 'capital'})
sites[si_v]['xy_m'] = FLOAT.tolist()
sites[si_v]['ground_m'] = FLOAT_Z
sites[si_v]['tier'] = 'capital'

# National routes and farms
for q in meta['routes'] + meta['farm_lanes']:
    ribbon(q['points_m'], q['width_m'])
for bridge in meta.get('bridges', []):
    p = np.array(bridge['points_m'])
    stone_bridge(p[0], p[-1], 10, 'wood')
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
            add('Oak', ax - 11, yy, scale=.55, yaw=rng.uniform(0, 360))
    if k % 25 == 0:
        add('SM_Civ30_Granary', ax + 30, ay + 32, scale=.65)
        add('Cart', ax + 55, ay + 30, scale=1.0, yaw=90)

wet = D['wetland']
valid = (wet > .25) & (D['channel'] < .2) & (D['height'] > -20599) & (D['height'] < -20565)
py, px = np.where(valid)
for k in range(2800):
    j = int(rng.integers(len(px)))
    x = (cx - px[j]) * mpp + rng.uniform(-35, 35)
    y = (cy - py[j]) * mpp + rng.uniform(-35, 35)
    z = h(x, y)
    if z < -20599:
        continue
    add('SM_Civ30_Reeds', x, y, z=z, scale=rng.uniform(3, 6), yaw=rng.uniform(0, 360))
    if k % 7 == 0:
        add('Palm', x + 12, y + 15, scale=1.0, yaw=rng.uniform(0, 360))
q = next(q for q in sites if q['culture'] == 'harbor')
x, y = q['xy_m']
py, px = np.where((D['channel'] > .90) & (D['height'] < -20599))
wx, wy = (cx - px) * mpp, (cy - py) * mpp
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
    add('Boat', target[0] + direction[1] * 22 * side, target[1] - direction[0] * 22 * side, z=-20599.3, scale=1.1, yaw=yaw + 90)
for spring in meta['oasis_sites']:
    x, y = spring['xy_m']
    rx, ry = spring['radius_m']
    for j in range(45):
        a = rng.uniform(0, 2 * np.pi)
        rr = rng.uniform(1.10, 1.8)
        add('DesertPalm', x + rx * rr * np.cos(a), y + ry * rr * np.sin(a), scale=rng.uniform(.9, 1.2), yaw=rng.uniform(0, 360))
py, px = np.where((D['channel'] > .97) & (D['coast'] > 300))
for k in range(min(24, len(px))):
    j = int(rng.integers(len(px)))
    add('Boat', (cx - px[j]) * mpp, (cy - py[j]) * mpp, z=-20599.3, scale=1.0, yaw=rng.uniform(0, 360))

import build_civilization_assets_v30 as A30
_old = A30.O
A30.O = O
roads.write('SM_Civ34_Roads')
foundations.write('SM_Civ34_Foundations')
A30.O = _old
manifest = json.loads((O / 'assets.json').read_text())
for mesh, name in ((roads, 'SM_Civ34_Roads'), (foundations, 'SM_Civ34_Foundations')):
    manifest.append({'name': name, 'vertices': len(mesh.v), 'triangles': len(mesh.f), 'materials': sorted(set(mesh.mat)), 'folder': 'Civilizations34'})
(O / 'assets.json').write_text(json.dumps(manifest, indent=2))
assets.update({q['name']: Pth + q['name'] for q in manifest if q['name'] not in assets})
(S / 'civilization_instances_v34.json').write_text(json.dumps({'assets': assets, 'instances': rows, 'landmarks': landmarks}, indent=2))
meta['settlements'] = sites
meta['placed_instances'] = sum(map(len, rows.values()))
meta['regional_landmarks'] = landmarks
meta['content_version'] = 34
meta['pleasure_city'] = {'xy_m': FLOAT.tolist(), 'z': FLOAT_Z}
(S / 'world_design_v34.json').write_text(json.dumps(meta, indent=2))
print({'instances': meta['placed_instances'], 'counts': {k: len(v) for k, v in rows.items() if v}, 'houses': sum(len(rows[k]) for k in rows if k.startswith('House'))}, flush=True)
