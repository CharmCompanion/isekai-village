"""Packed Gosain city sources. No editor mutation.

Both walled islands get connected townhouse rows, streets, alleys, plazas,
castle terraces, a basilica, and the already-authored arcane tower's plaza.
El Ruhn and every other region stay out of the meshes.
"""
import sys
from pathlib import Path
import json
import math
import numpy as np
import shapely
from shapely.geometry import Point, LineString, Polygon
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gosain44_terraces as terraces
import gosain50_kingdom as kingdom

ROOT = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
OUT = ROOT / 'ArtSource/World/Gosain50'
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW = ROOT / 'Docs/WorldDesign/Gosain50'
PREVIEW.mkdir(parents=True, exist_ok=True)
SEA = terraces.SEA
PREVIEW_ONLY = '--preview' in sys.argv
MATS = ['limestone', 'ivory', 'aged', 'warmstone', 'foundation', 'trim', 'recess', 'roofstone', 'terracotta', 'paving']


def mix(a, b, c=0):
    n = (int(a) * 374761393 ^ int(b) * 668265263 ^ int(c) * 1442695041) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFFFFFFFF


def rot(points, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    x, y = points[:, 0], points[:, 1]
    return np.column_stack([x * c - y * s, x * s + y * c])


class Chunk:
    def __init__(self):
        self.v = []
        self.f = []
        self.n = 0
        self.tris = 0

    def add(self, verts, faces, mat):
        base = self.n
        self.v.extend((float(x), float(y), float(z)) for x, y, z in verts)
        self.f.extend((base + a, base + b, base + c, mat) for a, b, c in faces)
        self.n += len(verts)
        self.tris += len(faces)

    def quad(self, pts, mat):
        self.add(pts, [[0, 1, 2], [0, 2, 3]], mat)

    def ribbon(self, a, b, width, za, zb, mat, lift=0.28):
        a = np.asarray(a, float)
        b = np.asarray(b, float)
        d = b - a
        length = float(np.linalg.norm(d))
        if length < 0.4:
            return
        n = np.array([-d[1], d[0]]) / length * (width * 0.5)
        z0, z1 = za + lift, zb + lift
        # A thin surface only. The old underside slab is what stood up out of the hillside.
        self.quad([[a[0] + n[0], a[1] + n[1], z0], [a[0] - n[0], a[1] - n[1], z0], [b[0] - n[0], b[1] - n[1], z1], [b[0] + n[0], b[1] + n[1], z1]], mat)


def segments_from_line(line, step=28.0):
    if line is None or line.is_empty:
        return []
    parts = [line] if line.geom_type == 'LineString' else [g for g in line.geoms if g.geom_type == 'LineString']
    out = []
    for part in parts:
        if part.length < 8:
            continue
        n = max(2, int(part.length / step) + 1)
        pts = np.array([part.interpolate(d).coords[0] for d in np.linspace(0, part.length, n)])
        out.append(pts)
    return out


def min_segment_distance(points, segs):
    if len(points) == 0 or len(segs) == 0:
        return np.full(len(points), 1e9)
    best = np.full(len(points), 1e9)
    pts = np.asarray(points, float)
    for i in range(0, len(segs), 80):
        batch = np.asarray(segs[i:i + 80], float)
        a = batch[:, 0]
        b = batch[:, 1]
        ab = b - a
        den = np.sum(ab * ab, axis=1)
        den = np.maximum(den, 1e-8)
        for s in range(0, len(pts), 25000):
            p = pts[s:s + 25000]
            t = np.clip(np.sum((p[:, None, :] - a[None, :, :]) * ab[None, :, :], axis=2) / den, 0, 1)
            proj = a[None, :, :] + t[:, :, None] * ab[None, :, :]
            d = np.linalg.norm(p[:, None, :] - proj, axis=2).min(axis=1)
            best[s:s + len(p)] = np.minimum(best[s:s + len(p)], d)
    return best


def height_at(points):
    points = np.asarray(points, float).reshape(-1, 2)
    if len(points) == 0:
        return np.zeros(0)
    return terraces.planned(points, np.full(len(points), SEA))


def building(chunk, center, size, yaw, zmin, storeys, mat, windows):
    w, d = size
    c, s = math.cos(yaw), math.sin(yaw)
    local = np.array([[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]])
    xy = np.column_stack([center[0] + local[:, 0] * c - local[:, 1] * s, center[1] + local[:, 0] * s + local[:, 1] * c])
    base = zmin + 1.05
    top = base + storeys * 3.2
    wall = np.array([[*p, base] for p in xy] + [[*p, top] for p in xy])
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces += [[i, j, j + 4], [i, j + 4, i + 4]]
    faces += [[4, 5, 6], [4, 6, 7]]
    chunk.add(wall, faces, mat)
    skirt = np.array([[*p, zmin - 0.35] for p in xy] + [[*p, base] for p in xy])
    sfaces = []
    for i in range(4):
        j = (i + 1) % 4
        sfaces += [[i, j, j + 4], [i, j + 4, i + 4]]
    chunk.add(skirt, sfaces, 4)
    corn = xy + (xy - xy.mean(0)) * 0.035
    chunk.add([[*p, top - 0.15] for p in corn] + [[*p, top + 0.55] for p in corn], sfaces, 5)
    mid = xy.mean(0)
    reach = max(w, d, 1.0)
    roof_xy = mid + (xy - mid) * (1.0 + 1.3 / reach)
    peak = top + 4.6
    chunk.add([*[[*p, top + 0.02] for p in roof_xy], [mid[0], mid[1], peak]], [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]], 8)
    # Narrow punched openings, not a modern window band across the whole floor.
    for edge in range(4):
        if not (windows & (1 << edge)):
            continue
        a, b = xy[edge], xy[(edge + 1) % 4]
        tangent = b - a
        length = float(np.linalg.norm(tangent))
        if length < 3.2:
            continue
        tangent /= length
        nrm = np.array([tangent[1], -tangent[0]])
        if np.dot(nrm, a - center) < 0:
            nrm = -nrm
        count = 2
        for k in range(count):
            spot = a + tangent * length * ((k + 1) / (count + 1))
            for floor in range(storeys):
                z = base + floor * 3.2 + (0.25 if floor == 0 else 0.95)
                h = 2.25 if floor == 0 else 1.45
                half = 0.55 if floor == 0 else 0.38
                p0 = spot - tangent * half + nrm * 0.08
                p1 = spot + tangent * half + nrm * 0.08
                chunk.quad([[p0[0], p0[1], z], [p1[0], p1[1], z], [p1[0], p1[1], z + h], [p0[0], p0[1], z + h]], 6)


def box(chunk, center, size, yaw, z, mat):
    building(chunk, center, size[:2], yaw, z, max(1, int(round(size[2] / 3.2))), mat, 0)


def lathe(chunk, center, radii, yaw, mat, n=14):
    rings = []
    c, s = math.cos(yaw), math.sin(yaw)
    for r, z in radii:
        ring = []
        for i in range(n):
            a = i * math.tau / n
            x, y = r * math.cos(a), r * math.sin(a)
            ring.append([center[0] + x * c - y * s, center[1] + x * s + y * c, z])
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        verts = a + b
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces += [[i, j, j + n], [i, j + n, i + n]]
        chunk.add(verts, faces, mat)
    top = rings[-1]
    faces = [[0, i, i + 1] for i in range(1, n - 1)]
    chunk.add(top, faces, mat)


def basilica(chunk, center, z):
    yaw = 0.0
    # South front faces the lower city. Masses are original, not stock houses.
    def place(offset, size, storeys, mat, windows=5):
        c, s = math.cos(yaw), math.sin(yaw)
        world = center + np.array([offset[0] * c - offset[1] * s, offset[0] * s + offset[1] * c])
        building(chunk, world, size, yaw, z, storeys, mat, windows)

    place((0, 18), (46, 108), 8, 0, 15)
    place((0, 18), (86, 34), 7, 1, 15)
    place((-40, 10), (18, 64), 4, 3, 5)
    place((40, 10), (18, 64), 4, 3, 5)
    place((-28, -42), (16, 16), 16, 0, 15)
    place((28, -42), (16, 16), 16, 0, 15)
    place((0, 78), (28, 22), 6, 1, 15)
    dome = z + 1.05 + 8 * 3.2
    lathe(chunk, center + np.array([0, 18]), [(20, dome - 2), (20, dome + 4), (16, dome + 10), (8, dome + 28), (2.2, dome + 40), (0.4, dome + 52)], 0, 0, 16)
    lathe(chunk, center + np.array([0, 18]), [(6.5, dome + 34), (6.5, dome + 40), (3.2, dome + 46)], 0, 5, 12)
    for i in range(8):
        y = -62 - i * 3.0
        depth = 2.6
        width = 40 - i * 1.2
        zz = z - i * 0.45
        chunk.quad([[center[0] - width / 2, center[1] + y, zz], [center[0] + width / 2, center[1] + y, zz], [center[0] + width / 2, center[1] + y + depth, zz + 0.45], [center[0] - width / 2, center[1] + y + depth, zz + 0.45]], 5)


def write_obj(chunk, name):
    if chunk.tris == 0:
        return None
    v = np.asarray(chunk.v, float)
    faces = np.asarray(chunk.f, np.int32)
    f = faces[:, :3]
    m = faces[:, 3]
    norms = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    areas = np.linalg.norm(norms, axis=1)
    ok = areas > 1e-6
    f, m, norms = f[ok], m[ok], norms[ok] / areas[ok, None]
    path = OUT / f'{name}.obj'
    print(f'writing {name}: {len(v)} verts, {len(f)} tris', flush=True)
    with path.open('w', encoding='utf-8') as out:
        out.write(f'o {name}\n')
        for x, y, z in v:
            out.write(f'v {x * 100:.3f} {-y * 100:.3f} {z * 100:.3f}\n')
        for x, y, z in norms:
            out.write(f'vn {x:.5f} {-y:.5f} {z:.5f}\n')
        order = np.argsort(m, kind='stable')
        last = None
        for i in order:
            mat = int(m[i])
            if mat != last:
                out.write('usemtl ' + MATS[mat] + '\n')
                last = mat
            a, b, c = (int(x) + 1 for x in f[i, ::-1])
            out.write(f'f {a}//{i + 1} {b}//{i + 1} {c}//{i + 1}\n')
    return {'name': name, 'vertices': int(len(v)), 'triangles': int(len(f)), 'materials': sorted({MATS[int(i)] for i in m})}


def clip_existing_mesh(src_name, dst_name):
    src = ROOT / 'ArtSource/World/Gosain44' / f'{src_name}.obj'
    polys = [p.buffer(0) for p in terraces.POLYS]
    print('clipping', src.name, flush=True)
    verts = []
    faces = []
    with src.open('r', encoding='utf-8', errors='ignore') as handle:
        for line in handle:
            if line.startswith('v '):
                x, y, z = (float(q) for q in line.split()[1:4])
                verts.append((x / 100.0, -y / 100.0, z / 100.0))
            elif line.startswith('f '):
                idx = []
                for token in line.split()[1:]:
                    idx.append(int(token.split('/')[0]) - 1)
                if len(idx) >= 3:
                    faces.append(idx[:3])
    v = np.asarray(verts, float)
    f = np.asarray(faces, np.int32)
    cents = v[f].mean(axis=1)[:, :2]
    pts = shapely.points(cents)
    drop = np.zeros(len(f), bool)
    for poly in polys:
        inside = shapely.contains(poly, pts)
        deep = shapely.distance(pts, poly.boundary) > 22.0
        drop |= inside & deep
    keep = f[~drop]
    dst = OUT / f'{dst_name}.obj'
    with dst.open('w', encoding='utf-8') as out:
        out.write(f'o {dst_name}\n')
        for x, y, z in v:
            out.write(f'v {x * 100:.3f} {-y * 100:.3f} {z * 100:.3f}\n')
        for a, b, c in keep:
            out.write(f'f {a + 1} {b + 1} {c + 1}\n')
    print(f'kept {len(keep)}/{len(f)} faces -> {dst.name}', flush=True)
    return {'name': dst_name, 'source': src_name, 'faces_kept': int(len(keep)), 'faces_removed': int(drop.sum())}


def island_city(index):
    poly = kingdom.TOWNS[index]
    center = np.array(terraces.PLAN['islands'][index]['civic_center_m'])
    bounds = poly.bounds
    landmark = terraces.CASTLE_CENTER if index == 0 else np.array(terraces.PLAN['islands'][1]['civic_center_m']) + np.array([500.0, 800.0])
    bridge = None
    for end in terraces.PLAN['bridge_endpoints_m']:
        if poly.buffer(30).covers(Point(end)):
            bridge = np.array(end, float)
    S = 760.0
    ox, oy = bounds[0], bounds[1]
    nx = int((bounds[2] - bounds[0]) / S) + 1
    ny = int((bounds[3] - bounds[1]) / S) + 1
    roads = []
    segs = []

    def add_line(line, width):
        for pts in segments_from_line(line, 32):
            roads.append((pts, width))
            segs.extend([[pts[i], pts[i + 1], width] for i in range(len(pts) - 1)])

    # Only the wall road. Radial and terrace lines were cutting straight through the blocks.
    ring = poly.buffer(-46)
    if not ring.is_empty:
        add_line(ring.boundary, 10)
    plazas = [(*center, 78), (*landmark, 150 if index else 90)]
    if bridge is not None:
        plazas.append((*bridge, 62))
    records = []
    street_pts = []
    for ix in range(nx):
        for iy in range(ny):
            x0, y0 = ox + ix * S, oy + iy * S
            inner = shapely.box(x0 + 10, y0 + 10, x0 + S - 10, y0 + S - 10)
            if inner.is_empty or not inner.intersects(poly):
                continue
            h = mix(ix + 20 * index, iy + 3, 47)
            yaw = ((h % 1000) / 1000 - 0.5) * math.radians(28)
            row_pitch = 52 + (h % 7)
            front = 13 + ((h >> 5) % 6)
            depth = 15.5 + ((h >> 9) % 4)
            cross = 86 + ((h >> 12) % 28)
            half_x = (S - 20) * 0.5
            half_y = (S - 20) * 0.5
            origin = np.array([x0 + S / 2, y0 + S / 2])
            c, s = math.cos(yaw), math.sin(yaw)
            y = -half_y
            row_i = 0
            while y < half_y - 8:
                bands = [(y + 8.0, y + 8.0 + depth, 1 | 4), (y + 8.0 + depth + 3.1, y + 8.0 + depth + 3.1 + depth, 1 | 4)]
                y_next = y + row_pitch
                x = -half_x
                block = 0
                while x < half_x - 6:
                    x_build = x + 7.2
                    x_end = min(x + cross, half_x)
                    cursor = x_build
                    col = 0
                    while cursor + front < x_end:
                        width = front * (0.82 + ((mix(ix, iy, row_i * 17 + col) % 40) / 100))
                        if cursor + width >= x_end:
                            break
                        for y0b, y1b, windows in bands:
                            if y1b > half_y:
                                continue
                            bw, bd = width - 0.35, (y1b - y0b) - 0.4
                            local = np.array([cursor + width / 2, (y0b + y1b) / 2])
                            world = origin + np.array([local[0] * c - local[1] * s, local[0] * s + local[1] * c])
                            outside = False
                            for lx, ly in ((-bw / 2, -bd / 2), (bw / 2, -bd / 2), (bw / 2, bd / 2), (-bw / 2, bd / 2)):
                                wx = origin[0] + (local[0] + lx) * c - (local[1] + ly) * s
                                wy = origin[1] + (local[0] + lx) * s + (local[1] + ly) * c
                                if wx < x0 + 10 or wx > x0 + S - 10 or wy < y0 + 10 or wy > y0 + S - 10:
                                    outside = True
                                    break
                            if outside:
                                continue
                            storeys = 2 + (mix(int(world[0]), int(world[1]), col) % 3)
                            mat = (0, 2, 3)[mix(ix, iy, row_i) % 3]
                            records.append((world[0], world[1], bw, bd, yaw, storeys, mat, windows))
                        col += 1
                        cursor += width
                    x += cross
                    block += 1
                # Local street and alley centerlines, transformed after the rows are known.
                def clipped(p, q, width):
                    part = LineString([tuple(p), tuple(q)]).intersection(inner)
                    lines = [part] if part.geom_type == 'LineString' else [g for g in getattr(part, 'geoms', []) if getattr(g, 'geom_type', '') == 'LineString']
                    for line in lines:
                        coords = list(line.coords)
                        for u, v in zip(coords, coords[1:]):
                            street_pts.append((np.array(u), np.array(v), width))
                for local_y, width in ((y + 4.0, 7.2), (y + 8.0 + depth + 1.55, 2.6)):
                    a = origin + np.array([(-half_x) * c - local_y * s, (-half_x) * s + local_y * c])
                    b = origin + np.array([half_x * c - local_y * s, half_x * s + local_y * c])
                    clipped(a, b, width)
                if (h + row_i) % 5 == 0:
                    local = np.array([0, y + row_pitch * 0.5])
                    world = origin + np.array([local[0] * c - local[1] * s, local[0] * s + local[1] * c])
                    plazas.append((world[0], world[1], 24 + (h % 10)))
                y = y_next
                row_i += 1
            x = -half_x
            while x < half_x:
                local_x = x + 3.2
                a = origin + np.array([local_x * c - (-half_y) * s, local_x * s + (-half_y) * c])
                b = origin + np.array([local_x * c - half_y * s, local_x * s + half_y * c])
                clipped(a, b, 6.0)
                x += cross
            if (ix + iy) % 3 == 0:
                plazas.append((origin[0], origin[1], 34))
    print(f'island {index}: candidates {len(records)} road samples {len(segs)}', flush=True)
    if not records:
        return np.zeros((0, 8)), roads, plazas, bridge, landmark, street_pts
    rec = np.array(records, float)
    pts = rec[:, :2]
    inside = shapely.contains(poly, shapely.points(pts))
    edge = shapely.distance(shapely.points(pts), poly.boundary)
    keep = inside & (edge > 35)
    connections=[]
    for ki,kpoly in enumerate(kingdom.POLYS):
        end=next(e for e in terraces.PLAN['bridge_endpoints_m'] if kpoly.buffer(30).covers(Point(e)))
        connections.append(LineString([end,kingdom.CENTERS[ki]]))
    connections.extend([LineString([kingdom.CENTERS[1],kingdom.CENTERS[1]+[-500,800],kingdom.MINE]),LineString([kingdom.CENTERS[0],kingdom.CENTERS[0]+[1200,-1800],kingdom.LAKE_CENTER+[-850,100],kingdom.LAKE_CENTER+[0,-1000]])])
    for route in connections:keep &= shapely.distance(shapely.points(pts),route)>25

    for reserve in kingdom.RESERVES:
        keep &= shapely.distance(shapely.points(pts),reserve)>20
    if index == 0:
        keep &= shapely.distance(shapely.points(pts), terraces.CASTLE) > 250
    else:
        keep &= np.linalg.norm(pts - landmark, axis=1) > 155
    for px, py, radius in plazas:
        keep &= np.linalg.norm(pts - np.array([px, py]), axis=1) > radius
    if segs:
        seg_arr = np.array([[s[0], s[1]] for s in segs], float)
        widths = np.array([s[2] for s in segs])
        dist = min_segment_distance(pts, seg_arr)
        # Compare against the nearest segment's width. A global half-width is enough for avenues.
        keep &= dist > (widths.mean() * 0.5 + 8.0)
    rec = rec[keep]
    print(f'island {index}: kept {len(rec)}', flush=True)
    return rec, roads, plazas, bridge, landmark, street_pts


def emit_island(index, rec, roads, plazas, street_pts, landmark):
    # Split the long companion island so each OBJ stays importable.
    split = float(np.median(rec[:, 1])) if index == 1 and len(rec) else 0
    chunks = [Chunk(), Chunk()] if index == 1 else [Chunk()]
    zs = height_at(rec[:, :2])
    # Four-corner relief, sampled once.
    corners = []
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        offsets = np.column_stack([rec[:, 2] * dx * 0.5, rec[:, 3] * dy * 0.5])
        yaw = rec[:, 4]
        c, s = np.cos(yaw), np.sin(yaw)
        corners.append(np.column_stack([rec[:, 0] + offsets[:, 0] * c - offsets[:, 1] * s, rec[:, 1] + offsets[:, 0] * s + offsets[:, 1] * c]))
    corner_z = np.vstack([height_at(p) for p in corners])
    zmin = corner_z.min(0)
    relief = corner_z.max(0) - zmin
    use = relief < 4.5
    rec, zs, zmin = rec[use], zs[use], zmin[use]
    print(f'island {index}: building {len(rec)} after slope cull', flush=True)
    for i, row in enumerate(rec):
        chunk = chunks[0 if index == 0 or row[1] < split else 1]
        near = min(np.linalg.norm(row[:2] - landmark), np.linalg.norm(row[:2] - np.array(terraces.PLAN['islands'][index]['civic_center_m'])))
        storeys = int(np.clip(row[5] + (1 if near < 420 else 0), 2, 5))
        building(chunk, row[:2], row[2:4], row[4], zmin[i], storeys, int(row[6]), int(row[7]))
        if i and i % 20000 == 0:
            print(f'  houses {i}', flush=True)
    pieces = []
    for pts, width in roads:
        for a, b in zip(pts, pts[1:]):
            pieces.append((np.asarray(a, float), np.asarray(b, float), width))
    for a, b, width in street_pts:
        pieces.append((np.asarray(a, float), np.asarray(b, float), width))
    ends = []
    meta = []
    for a, b, width in pieces:
        if float(np.linalg.norm(b - a)) < 0.4:
            continue
        ends.append(a)
        ends.append(b)
        meta.append((a, b, width))
    road_jobs = []
    if meta:
        stacked = np.asarray(ends, float)
        inside = shapely.contains(kingdom.TOWNS[index], shapely.points(stacked))
        zz = height_at(stacked)
        segs = []
        for i, (a, b, width) in enumerate(meta):
            if not (inside[i * 2] and inside[i * 2 + 1]):
                continue
            segs.append((a, b, float(zz[i * 2]), float(zz[i * 2 + 1]), width))
        # Split only where a straight ribbon would leave the hillside. Flat streets stay one surface.
        for _ in range(6):
            mids = []
            which = []
            for i, (a, b, za, zb, width) in enumerate(segs):
                if float(np.linalg.norm(b - a)) < 16:
                    continue
                mids.append((a + b) * 0.5)
                which.append(i)
            if not which:
                break
            zm = height_at(np.asarray(mids, float))
            split_at = {}
            for i, z in zip(which, zm):
                a, b, za, zb, width = segs[i]
                if abs(float(z) - (za + zb) * 0.5) > 0.28:
                    split_at[i] = float(z)
            if not split_at:
                break
            nxt = []
            for i, seg in enumerate(segs):
                if i not in split_at:
                    nxt.append(seg)
                    continue
                a, b, za, zb, width = seg
                mid = (a + b) * 0.5
                z = split_at[i]
                nxt.append((a, mid, za, z, width))
                nxt.append((mid, b, z, zb, width))
            segs = nxt
        mids = np.asarray([(a + b) * 0.5 for a, b, za, zb, width in segs], float)
        on_land = shapely.contains(kingdom.TOWNS[index], shapely.points(mids))
        castle = terraces.CASTLE_CENTER
        for (a, b, za, zb, width), mid, ok in zip(segs, mids, on_land):
            if not ok:
                continue
            if index == 0 and float(np.linalg.norm(mid - castle)) < 260:
                continue
            if index == 1 and float(np.linalg.norm(mid - landmark)) < 160:
                continue
            road_jobs.append((a, b, width, za, zb, 0.04))
    plaza_xy = [[] for _ in chunks]
    for px, py, radius in plazas:
        ci = 0 if index == 0 or py < split else 1
        if not terraces.POLYS[index].contains(Point(px, py)):
            continue
        circle = Point(px, py).buffer(radius, quad_segs=6)
        for tri in shapely.constrained_delaunay_triangles(circle).geoms:
            plaza_xy[ci].append(np.array(tri.exterior.coords)[:3])
    for chunk, tris in zip(chunks, plaza_xy):
        if tris:
            xy = np.asarray(tris, float)
            zz = height_at(xy.reshape(-1, 2)).reshape(-1, 3) + 0.04
            for i in range(len(tris)):
                chunk.add([[xy[i, k, 0], xy[i, k, 1], float(zz[i, k])] for k in range(3)], [[0, 1, 2]], 9)
        for a, b, width, za, zb, lift in road_jobs:
            midy = (a[1] + b[1]) * 0.5
            if index == 1 and (midy >= split) != (chunk is chunks[1]):
                continue
            chunk.ribbon(a, b, width, za, zb, 9, lift)
    return chunks, split


def emit_citadel():
    chunk = Chunk()
    center = terraces.CASTLE_CENTER
    top = SEA + 224.0
    basilica(chunk, center, top - 0.2)
    court = terraces.CASTLE.buffer(-18)
    if court.geom_type == 'Polygon':
        for tri in shapely.constrained_delaunay_triangles(court).geoms:
            xy = np.array(tri.exterior.coords)[:3]
            chunk.add([[xy[i, 0], xy[i, 1], top + 0.15] for i in range(3)], [[0, 1, 2]], 9)
    # Stepped retaining around the mound. The underlying mesh slopes; these walls make the climb architectural.
    for distance, crest in ((24, 220), (78, 196), (138, 172), (198, 152)):
        ring = terraces.CASTLE.buffer(distance).exterior
        pts = np.array(ring.coords)
        if len(pts) > 280:
            pts = pts[:: max(1, len(pts) // 220)]
        zz = height_at(pts)
        crest_z = SEA + crest
        for a, b, za, zb in zip(pts, np.roll(pts, -1, axis=0), zz, np.roll(zz, -1)):
            if crest_z < max(za, zb) + 1.2:
                continue
            chunk.quad([[a[0], a[1], za], [b[0], b[1], zb], [b[0], b[1], crest_z], [a[0], a[1], crest_z]], 0)
            chunk.ribbon(a, b, 7.5, crest_z, crest_z, 9, 0.05)
    # Switchback from the 144m bench to the citadel gate, graded near 8 percent.
    path = [center + np.array(p) for p in [(0, -690), (210, -690), (210, -560), (-190, -560), (-190, -450), (160, -450), (160, -360), (0, -340)]]
    samples = []
    for a, b in zip(path, path[1:]):
        n = max(2, int(np.linalg.norm(b - a) / 18))
        for t in np.linspace(0, 1, n, endpoint=False):
            samples.append(a * (1 - t) + b * t)
    samples.append(path[-1])
    samples = np.array(samples)
    ground = height_at(samples)
    grades = np.linspace(SEA + 146, top, len(samples))
    for a, b, za, zb, ga, gb in zip(samples, samples[1:], ground, ground[1:], grades, grades[1:]):
        chunk.ribbon(a, b, 11, ga, gb, 5, 0.2)
        # Embankment down to the hillside where the ramp is above the mesh.
        if ga > za + 0.8 or gb > zb + 0.8:
            chunk.quad([[a[0], a[1], za], [b[0], b[1], zb], [b[0], b[1], gb], [a[0], a[1], ga]], 4)
    return chunk


def preview(records):
    pads = []
    for index, rec in enumerate(records):
        if len(rec) == 0:
            continue
        pads.append(rec[:, :2])
    if not pads:
        return
    pts = np.vstack(pads)
    minx, miny = pts.min(0)
    maxx, maxy = pts.max(0)
    span = max(maxx - minx, maxy - miny)
    scale = 1600 / span
    image = Image.new('RGB', (1700, 1700), (28, 40, 48))
    draw = ImageDraw.Draw(image)

    def uv(p):
        return (40 + (p[0] - minx) * scale, 1640 - (p[1] - miny) * scale)

    for poly in terraces.POLYS:
        draw.line([uv(p) for p in poly.exterior.coords], fill=(186, 170, 140), width=2)
    step = max(1, len(pts) // 180000)
    for p in pts[::step]:
        x, y = uv(p)
        draw.point((x, y), fill=(196, 122, 78))
    image.save(PREVIEW / 'Packed_City_Plan.png')
    print('preview', PREVIEW / 'Packed_City_Plan.png', flush=True)


def main():
    all_records = []
    payloads = []
    for index in (0, 1):
        rec, roads, plazas, bridge, landmark, street_pts = island_city(index)
        all_records.append(rec if len(rec) else np.zeros((0, 2)))
        payloads.append((index, rec, roads, plazas, street_pts, landmark, bridge))
    preview([r[:, :2] if len(r) else r for r in all_records])
    if PREVIEW_ONLY:
        print(json.dumps({'preview_only': True, 'buildings': [int(len(r)) for r in all_records]}))
        return
    meshes = []
    names = {0: ['SM_Gosain50_Capital'], 1: ['SM_Gosain50_FarSouth', 'SM_Gosain50_FarNorth']}
    for index, rec, roads, plazas, street_pts, landmark, bridge in payloads:
        chunks, split = emit_island(index, rec, roads, plazas, street_pts, landmark)
        for chunk, name in zip(chunks, names[index]):
            info = write_obj(chunk, name)
            if info:
                info['split_y_m'] = split
                meshes.append(info)
    citadel = write_obj(emit_citadel(), 'SM_Gosain50_Citadel')
    if citadel:
        meshes.append(citadel)
    report = {
        'status': 'source_only',
        'buildings': [int(len(r)) for r in all_records],
        'meshes': meshes,
        'replaces': ['SM_Gosain47_Capital', 'SM_Gosain47_FarSouth', 'SM_Gosain47_FarNorth', 'SM_Gosain47_Citadel'],
        'tower_origin_m': json.loads((ROOT / 'ArtSource/World/Gosain45/tower.json').read_text())['origin_m'],
        'limitations': [
            'Exterior townhouses: warm stone, terracotta hips, narrow vertical openings. No furnished interiors.',
            'Chunk meshes are authored without per-building collision so the map can load.',
            'Castle ramps and ring walls are architectural overlays on the saved Gosain44 terrain.',
        ],
    }
    (OUT / 'city.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ('buildings', 'meshes')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
