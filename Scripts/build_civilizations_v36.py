"""v36: each kingdom gets its own street pattern and building kit. No more cloned rectangles."""
from pathlib import Path
import json, sys, shutil, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scipy.ndimage import map_coordinates, label, gaussian_filter1d
from scipy.spatial import cKDTree
from civilization_ground_v30 import ground
from build_civilization_assets_v30 import Mesh

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S = B / 'Saved/AdventureWorldSource'
O = S / 'Civilizations36'
O.mkdir(exist_ok=True)
# Reuse v34/v33/v30 landmark objs; only roads/foundations are new.
src34 = S / 'Civilizations34'
if (src34 / 'assets.json').exists():
    shutil.copy(src34 / 'assets.json', O / 'assets.json')
    isle = src34 / 'SM_Civ34_PleasureIsle.obj'
    if isle.exists():
        shutil.copy(isle, O / 'SM_Civ34_PleasureIsle.obj')

meta = json.loads((S / 'world_design_v34.json').read_text())
sites = meta['settlements']
D = dict(np.load(S / 'world_reference_v30.npz'))
cx, cy, mpp = float(D['cx']), float(D['cy']), float(D['mpp'])
rng = np.random.default_rng(36011)
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
    loose = {'Oak', 'Pine', 'Palm', 'DesertPalm', 'SM_Civ30_Reeds', 'Lamp', 'Fence', 'Barrel', 'Crate', 'Hay', 'Sack', 'Bench', 'Table', 'Lantern', 'Sign', 'Well', 'Cart', 'Market', 'Market2', 'Market3', 'Tent'}
    if key not in ('Boat', 'SM_Civ30_Boardwalk', 'SM_Civ34_PleasureIsle') and not wet and not onland(x, y, 35 if key in loose else 55):
        return False
    if z is None:
        z = h(x, y)
    sc = [scale] * 3 if np.isscalar(scale) else list(scale)
    rows[key].append([float(x), float(y), float(z), *map(float, sc), float(yaw), site])
    return True


def ribbon(points, width, mat='path', zf=None, check=True):
    p = np.array(points, float)
    if len(p) < 2:
        return
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


def street_yaw(x, y, culture):
    if culture == 'farming':
        return 0.0
    gx = field('height', x + 40, y) - field('height', x - 40, y)
    gy = field('height', x, y + 40) - field('height', x, y - 40)
    return float(np.degrees(np.arctan2(-gx, gy)))


def house_pick(culture, k):
    if culture in ('nomad', 'cult'):
        return 'Tent', rng.uniform(1.05, 1.4)
    if culture == 'arcane':
        if k % 5 == 0:
            return 'SM_Civ30_Manufactory', rng.uniform(.42, .55)
        if k % 7 == 0:
            return 'SM_Civ30_ArcaneTower', rng.uniform(.22, .32)
        return ('HouseD', 'HouseB', 'HouseF')[k % 3], rng.uniform(.95, 1.12)
    if culture in ('wetland', 'harbor', 'pleasure'):
        if k % 2 == 0:
            return 'SM_Civ30_StiltHouse', rng.uniform(.85, 1.05)
        return ('HouseA', 'HouseC', 'HouseE')[k % 3], rng.uniform(.92, 1.12)
    if culture in ('religious', 'citadel'):
        if k % 11 == 0:
            return 'SM_Civ30_SacredTower', rng.uniform(.35, .55)
        return ('HouseA', 'HouseC', 'HouseE', 'HouseB')[k % 4], rng.uniform(.96, 1.16)
    return ('HouseA', 'HouseB', 'HouseC', 'HouseD', 'HouseE', 'HouseF')[k % 6], rng.uniform(.96, 1.18)


def put_house(p, yaw, culture, si, i, zf, floating):
    z = zf(*p)
    key, sc = house_pick(culture, i)
    if culture in ('nomad', 'cult'):
        add(key, *p, z=z, scale=sc, yaw=rng.uniform(0, 360), site=si, wet=floating)
        return
    if key == 'SM_Civ30_StiltHouse':
        add(key, *p, z=z + (0 if floating else 5), scale=sc, yaw=yaw, site=si, wet=floating)
        return
    if key in ('SM_Civ30_Manufactory', 'SM_Civ30_ArcaneTower', 'SM_Civ30_SacredTower'):
        add(key, *p, z=z, scale=sc, yaw=yaw, site=si, wet=floating)
        return
    add(key, *p, z=z, scale=sc, yaw=yaw + rng.uniform(-6, 6), site=si, wet=floating)
    if not floating:
        pad(*p, z)


def shop(p, yaw, si, zf, floating, k=0):
    add(('Market', 'Market2', 'Market3')[k % 3], *p, z=zf(*p), scale=rng.uniform(1.15, 1.45), yaw=yaw, site=si, wet=floating)


def prop(key, p, yaw, si, zf, floating, scale=1.0):
    add(key, *p, z=zf(*p), scale=scale, yaw=yaw, site=si, wet=floating)


def clip_poly(pts, margin, floating):
    if floating:
        return [np.array(p, float) for p in pts]
    out = [np.array(p, float) for p in pts if onland(*p, margin)]
    return out if len(out) >= 2 else []


def wavy(origin, d, s, t0, t1, off, amp, steps):
    pts = []
    for t in np.linspace(t0, t1, steps):
        u = (t - t0) / max(t1 - t0, 1e-5)
        wave = amp * np.sin(u * 2.2 * np.pi + off * .07)
        pts.append(origin + d * t + s * (off + wave))
    return pts


def layout_spec(culture, kind):
    """length_m, parallel streets, spacing, lot, plaza, wave amplitude."""
    if culture == 'farming':
        return {
            'capital': (420, 3, 34, 8.2, True, 4),
            'city': (260, 2, 32, 8.0, True, 3),
            'town': (160, 2, 30, 8.0, False, 2),
            'village': (90, 1, 0, 8.5, False, 1),
        }[kind]
    if culture == 'arcane':
        return {
            'capital': (320, 4, 40, 12.5, True, 2),
            'city': (210, 3, 38, 12.0, True, 2),
            'town': (140, 2, 36, 12.0, False, 1),
            'village': (80, 1, 0, 11.0, False, 1),
        }[kind]
    if culture in ('nomad', 'cult'):
        return {
            'capital': (380, 2, 28, 9.0, True, 10),
            'city': (220, 2, 26, 8.5, True, 8),
            'town': (140, 1, 0, 8.5, False, 6),
            'village': (70, 1, 0, 9.0, False, 4),
        }[kind]
    if culture in ('wetland', 'harbor', 'pleasure'):
        return {
            'capital': (300, 3, 26, 8.5, True, 6),
            'city': (200, 2, 24, 8.5, True, 5),
            'town': (140, 1, 0, 8.5, False, 4),
            'village': (80, 1, 0, 8.5, False, 3),
        }[kind]
    return {
        'capital': (280, 5, 26, 7.2, True, 7),
        'city': (180, 3, 26, 7.2, True, 5),
        'town': (120, 2, 24, 7.2, False, 4),
        'village': (70, 1, 0, 7.4, False, 3),
    }[kind]


def dress_street(pts, culture, kind, si, zf, floating, start_i=0, lamps=True):
    n = start_i
    if len(pts) < 2:
        return n
    lot = layout_spec(culture, kind)[3]
    fence = culture in ('farming', 'religious', 'citadel')
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.array(a, float), np.array(b, float)
        seg = b - a
        length = np.linalg.norm(seg)
        if length < 6:
            continue
        tdir = seg / length
        side = np.array([-tdir[1], tdir[0]])
        face = float(np.degrees(np.arctan2(tdir[1], tdir[0])))
        t = 3.0
        k = 0
        while t < length - 3.0:
            for sgn, yaw in ((1, face - 90), (-1, face + 90)):
                p = a + tdir * t + side * sgn * 5.6
                if (not floating) and (not onland(*p, 55)):
                    continue
                put_house(p, yaw, culture, si, n, zf, floating)
                n += 1
                curb = p - side * sgn * 2.1
                if k % 2 == 0:
                    prop('Barrel', curb + tdir * 1.0, yaw, si, zf, floating, rng.uniform(.85, 1.1))
                if k % 3 == 0:
                    prop('Crate', curb - tdir * .9, yaw + 20, si, zf, floating, rng.uniform(.8, 1.05))
                if culture == 'farming' and k % 4 == 0:
                    prop('Sack', curb + tdir * .3, yaw, si, zf, floating)
                    if k % 8 == 0:
                        prop('Hay', p + side * sgn * 3.2, yaw, si, zf, floating, .7)
                if culture in ('nomad', 'cult') and k % 3 == 0:
                    shop(p + side * sgn * 1.2, yaw, si, zf, floating, k)
                if culture == 'arcane' and k % 4 == 0:
                    ribbon([p, p - side * sgn * 18], 1.8, 'conduit', zf=zf, check=not floating)
                if kind in ('capital', 'city') and k % 7 == 3:
                    shop(p + side * sgn * 1.3, yaw, si, zf, floating, k)
                if fence and k % 2 == 1:
                    prop('Fence', p + side * sgn * 3.8, yaw, si, zf, floating, .85)
            if lamps and k % 2 == 0:
                mid = a + tdir * t + side * 2.4
                prop('Lamp', mid, face, si, zf, floating)
            t += lot
            k += 1
    return n


def plaza_at(origin, yaw_deg, culture, si, zf, floating, radius=16):
    yaw = np.radians(yaw_deg)
    d = np.array([np.cos(yaw), np.sin(yaw)])
    s = np.array([-d[1], d[0]])

    def xy(u, v):
        return origin + d * u + s * v

    ring = [xy(radius * np.cos(a), radius * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 18)]
    ribbon(ring + ring[:1], 9, zf=zf, check=not floating)
    prop('Well', origin, yaw_deg, si, zf, floating, 1.3)
    nshop = 10 if culture != 'cult' else 4
    for k, ang in enumerate(np.linspace(0, 2 * np.pi, nshop, endpoint=False)):
        shop(xy(radius * .72 * np.cos(ang), radius * .72 * np.sin(ang)), np.degrees(ang) + 90, si, zf, floating, k)
    for u, v, yw in ((-7, 5, yaw_deg + 180), (7, 5, yaw_deg + 180), (-7, -6, yaw_deg), (7, -6, yaw_deg)):
        prop('Bench', xy(u, v), yw, si, zf, floating, 1.05)
        prop('Table', xy(u * 1.2, v * .4), yw, si, zf, floating)
    tree = 'Palm' if culture in ('wetland', 'harbor', 'pleasure') else 'DesertPalm' if culture in ('nomad', 'cult') else 'Pine' if culture in ('religious', 'citadel') else 'Oak'
    for u, v in ((-radius, -radius * .7), (radius, -radius * .7), (-radius, radius * .7), (radius, radius * .7)):
        prop(tree, xy(u, v), rng.uniform(0, 360), si, zf, floating)
    for k, (u, v) in enumerate(((-12, -5), (12, -5), (0, 12), (0, -12))):
        prop('Cart', xy(u, v), yaw_deg + (0 if k % 2 == 0 else 90), si, zf, floating)


def organic_town(origin, yaw_deg, culture, kind, si, zf=None, floating=False, length=None, npar=None):
    origin = np.array(origin, float)
    zf = zf or h
    L, n_par, spacing, _lot, do_plaza, amp = layout_spec(culture, kind)
    if length is not None:
        L = length
    if npar is not None:
        n_par = npar
    yaw = np.radians(yaw_deg)
    d = np.array([np.cos(yaw), np.sin(yaw)])
    s = np.array([-d[1], d[0]])
    half = L * .5
    if n_par <= 1:
        offs = [0.0]
    else:
        offs = np.linspace(-.5 * (n_par - 1) * spacing, .5 * (n_par - 1) * spacing, n_par)
        offs = offs + rng.uniform(-spacing * .1, spacing * .1, n_par)
    streets = []
    steps = max(6, int(L / 16))
    for off in offs:
        pts = clip_poly(wavy(origin, d, s, -half, half, off, amp, steps), 50, floating)
        if len(pts) >= 2:
            ribbon(pts, 7.0 if abs(off) < 1 else 5.8, zf=zf, check=not floating)
            streets.append(pts)
    n_cross = 0 if n_par <= 1 else max(1, int(L / 85))
    for k in range(n_cross):
        t = -half + (k + .55) * L / (n_cross + .15)
        slant = rng.uniform(-8, 8)
        a = origin + d * t + s * (offs[0] - 10) + d * slant
        b = origin + d * t + s * (offs[-1] + 10) - d * slant
        pts = clip_poly([a, b], 50, floating)
        if len(pts) >= 2:
            ribbon(pts, 5.2, zf=zf, check=not floating)
            streets.append(pts)
    n = 0
    lamps = kind in ('capital', 'city', 'town')
    for pts in streets:
        n = dress_street(pts, culture, kind, si, zf, floating, n, lamps=lamps)
    if do_plaza:
        plaza_at(origin, yaw_deg, culture, si, zf, floating, 18 if kind == 'capital' else 14)
    if culture == 'arcane':
        ribbon([origin - d * half * .6, origin + d * half * .6], 2.6, 'conduit', zf=zf, check=not floating)
    return n


def lined_road(a, b, culture, si, zf=None, floating=False):
    a, b = np.array(a, float), np.array(b, float)
    zf = zf or h
    ribbon([a, b], 8, zf=zf, check=not floating)
    tan = b - a
    length = np.linalg.norm(tan)
    if length < 8:
        return
    tan /= length
    side = np.array([-tan[1], tan[0]])
    t = 5
    i = 0
    while t < length - 5:
        for sgn in (-1, 1):
            p = a + tan * t + side * sgn * 5.5
            if (not floating) and (not onland(*p, 55)):
                continue
            put_house(p, np.degrees(np.arctan2(tan[1], tan[0])) + (90 if sgn > 0 else -90), culture, si, i, zf, floating)
            i += 1
        t += 7.2


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


def island_axis(comp_id):
    msk = (comp == comp_id) & (clearance > 140)
    pts = np.column_stack([X[msk], Y[msk]])
    c = pts.mean(0)
    cov = np.cov((pts - c).T)
    w, v = np.linalg.eigh(cov)
    long = v[:, int(np.argmax(w))]
    yaw = float(np.degrees(np.arctan2(long[1], long[0])))
    proj = (pts - c) @ long
    return c, yaw, float(proj.max() - proj.min())


def fill_island(comp_id, origin, culture, si, n_par, wall_site):
    c, yaw, long_m = island_axis(comp_id)
    origin = np.array(origin, float)
    length = min(long_m * .72, 620)
    organic_town(origin, yaw, culture, 'capital', si, length=length, npar=n_par)


# --- mainland towns ---
for si, q in enumerate(sites):
    x, y = q['xy_m']
    culture, kind = q['culture'], q['tier']
    q['instance_start'] = {k: len(v) for k, v in rows.items()}
    if q['name'] in ('Northern island cathedral fortress', 'Northern island monastery fortress', 'Vylfod regional capital'):
        q['instances'] = 0
        continue
    yaw = street_yaw(x, y, culture) + (0 if culture == 'farming' else rng.uniform(-8, 8))
    if culture == 'cult':
        organic_town((x, y), yaw, culture, 'village' if kind == 'village' else 'town', si)
        add('SM_Civ30_Sanctuary', x, y, scale=1.1 if kind != 'village' else .7, site=si)
        landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 80, 'tier': kind})
    elif culture == 'nomad':
        organic_town((x, y), yaw, culture, kind, si)
        if kind == 'capital':
            add('SM_Civ33_MagicTower', x, y, z=h(x, y), scale=2.6, site=si)
            add('SM_Civ30_Banner', x + 18, y, z=h(x, y) + 4, scale=1.1, site=si)
            landmarks.append({'name': 'Yozuan caravan capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 220, 'tier': 'capital'})
    else:
        organic_town((x, y), yaw, culture, kind, si)
        if kind == 'capital' and culture == 'arcane':
            add('SM_Civ30_ArcaneTower', x, y, z=h(x, y), scale=2.9, site=si)
            add('SM_Civ30_Manufactory', x - 55, y + 24, scale=.85, yaw=yaw, site=si)
            add('SM_Civ30_Manufactory', x - 55, y - 24, scale=.85, yaw=yaw, site=si)
            ribbon([[x, y], [x - 55, y + 24]], 2.6, 'conduit')
            ribbon([[x, y], [x - 55, y - 24]], 2.6, 'conduit')
            landmarks.append({'name': q['name'] + ' capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 220, 'tier': 'capital'})
        elif kind == 'capital':
            add('SM_Civ33_MagicTower', x, y, z=h(x, y), scale=2.5 if culture == 'farming' else 2.7, site=si)
            landmarks.append({'name': q['name'] + ' capital', 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 220, 'tier': 'capital'})
        if culture in ('religious', 'citadel'):
            add('SM_Civ30_Cathedral', x, y + 8, scale=.85 if kind == 'city' else .55, site=si)
            if kind == 'city':
                w, dlen = 90, 70
                for sx, sy, yw in ((-w, 0, 90), (w, 0, 90), (0, -dlen, 0), (0, dlen, 0)):
                    add('SM_Civ30_CurtainWall', x + sx, y + sy, scale=[(dlen if abs(sx) else w) / 21, .9, 1.1], yaw=yw, site=si)
            landmarks.append({'name': q['name'], 'xy_m': [x, y], 'z': q['ground_m'], 'culture': culture, 'radius': 160, 'tier': kind})
        elif culture == 'arcane' and kind in ('city', 'town'):
            add('SM_Civ30_ArcaneTower', x + 20, y, scale=.4, site=si)
            add('SM_Civ30_Manufactory', x - 36, y, scale=.55, yaw=yaw, site=si)
        elif culture == 'farming' and kind in ('capital', 'city', 'town'):
            add('SM_Civ30_Mill', x + 70, y - 8, scale=1.05, site=si)
            add('Sails', x + 70, y - 18, h(x + 70, y - 8) + 26, scale=1.6, site=si)
            add('SM_Civ30_Granary', x + 92, y - 8, scale=.9, site=si)
    q['instances'] = sum(len(rows[k]) - q['instance_start'][k] for k in rows)
    q.pop('instance_start')

# --- Gosain: both islands packed to the walls ---
cit = next(s for s in sites if s['name'] == 'Northern island cathedral fortress')
mon = next(s for s in sites if s['name'] == 'Northern island monastery fortress')
cid = int(comp[int(round(cy - cit['xy_m'][1] / mpp)), int(round(cx - cit['xy_m'][0] / mpp))])
mid = int(comp[int(round(cy - mon['xy_m'][1] / mpp)), int(round(cx - mon['xy_m'][0] / mpp))])
si_c, si_m = sites.index(cit), sites.index(mon)
fill_island(cid, cit['xy_m'], 'citadel', si_c, 9, si_c)
add('SM_Civ33_MagicTower', *cit['xy_m'], z=h(*cit['xy_m']), scale=3.2, site=si_c)
add('SM_Civ30_Cathedral', cit['xy_m'][0], cit['xy_m'][1] + 12, scale=1.55, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] - 36, cit['xy_m'][1] + 8, scale=1.2, site=si_c)
add('SM_Civ30_SacredTower', cit['xy_m'][0] + 36, cit['xy_m'][1] + 8, scale=1.2, site=si_c)
for sx, sy, yw, length in ((-200, 0, 90, 240), (200, 0, 90, 240), (0, -170, 0, 400), (0, 170, 0, 400)):
    add('SM_Civ33_EmpireWall', cit['xy_m'][0] + sx, cit['xy_m'][1] + sy, scale=[length / 48, 1.6, 1.8], yaw=yw, site=si_c)
add('SM_Civ30_Gatehouse', cit['xy_m'][0], cit['xy_m'][1] - 170, scale=1.5, yaw=0, site=si_c)
fill_island(mid, mon['xy_m'], 'religious', si_m, 7, si_m)
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

# --- Vylfod floating pleasure city ---
def fz(x, y):
    return FLOAT_Z + .35


si_v = next(i for i, q in enumerate(sites) if q['name'] == 'Vylfod regional capital')
add('SM_Civ34_PleasureIsle', *FLOAT, z=FLOAT_Z - 2, scale=1.0, yaw=12, site=si_v, wet=True)
organic_town(FLOAT, 12, 'pleasure', 'capital', si_v, zf=fz, floating=True, length=280, npar=3)
add('SM_Civ33_MagicTower', *FLOAT, z=FLOAT_Z, scale=2.4, site=si_v, wet=True)
for t in np.linspace(-110, 110, 24):
    add('SM_Civ30_Boardwalk', FLOAT[0] + t * np.cos(np.radians(12)), FLOAT[1] + t * np.sin(np.radians(12)), z=FLOAT_Z + 1.2, scale=1.35, yaw=12, site=si_v, wet=True)
for t in np.linspace(-100, 100, 18):
    p = FLOAT + np.array([np.cos(np.radians(12)), np.sin(np.radians(12))]) * t + np.array([-np.sin(np.radians(12)), np.cos(np.radians(12))]) * 7
    prop('Table', p, 12, si_v, fz, True, 1.05)
    prop('Lantern', p + np.array([1.4, 0.6]), 12, si_v, fz, True, 1.2)
for k, ang in enumerate(np.linspace(0, 2 * np.pi, 14, endpoint=False)):
    shop(FLOAT + 48 * np.array([np.cos(ang), np.sin(ang)]), np.degrees(ang) + 90, si_v, fz, True, k)
    add('SM_Civ30_Banner', *(FLOAT + 78 * np.array([np.cos(ang), np.sin(ang)])), z=FLOAT_Z + 8, scale=1.0, yaw=np.degrees(ang), site=si_v, wet=True)
    prop('Palm', FLOAT + rng.uniform(90, 160) * np.array([np.cos(ang), np.sin(ang)]), rng.uniform(0, 360), si_v, fz, True)
for k in range(16):
    a = rng.uniform(0, 2 * np.pi)
    add('Boat', *(FLOAT + rng.uniform(205, 255) * np.array([np.cos(a), np.sin(a)])), z=FLOAT_Z - 6, scale=1.15, yaw=rng.uniform(0, 360), site=si_v, wet=True)
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
roads.write('SM_Civ36_Roads')
foundations.write('SM_Civ36_Foundations')
A30.O = _old
manifest = json.loads((O / 'assets.json').read_text())
manifest = [q for q in manifest if q['name'] not in ('SM_Civ34_Roads', 'SM_Civ34_Foundations', 'SM_Civ33_Roads', 'SM_Civ33_Foundations', 'SM_Civ30_Roads', 'SM_Civ30_Foundations')]
for mesh, name in ((roads, 'SM_Civ36_Roads'), (foundations, 'SM_Civ36_Foundations')):
    manifest.append({'name': name, 'vertices': len(mesh.v), 'triangles': len(mesh.f), 'materials': sorted(set(mesh.mat)), 'folder': 'Civilizations36'})
(O / 'assets.json').write_text(json.dumps(manifest, indent=2))
assets.update({q['name']: Pth + q['name'] for q in manifest if q['name'] not in assets})
(S / 'civilization_instances_v36.json').write_text(json.dumps({'assets': assets, 'instances': rows, 'landmarks': landmarks}, indent=2))
meta['settlements'] = sites
meta['placed_instances'] = sum(map(len, rows.values()))
meta['regional_landmarks'] = landmarks
meta['content_version'] = 36
meta['pleasure_city'] = {'xy_m': FLOAT.tolist(), 'z': FLOAT_Z}
(S / 'world_design_v36.json').write_text(json.dumps(meta, indent=2))
print({'instances': meta['placed_instances'], 'counts': {k: len(v) for k, v in rows.items() if v}, 'houses': sum(len(rows[k]) for k in rows if k.startswith('House'))}, flush=True)
