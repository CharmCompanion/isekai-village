"""v32: replace the 256-triangle fan lake surface with an evenly tessellated grid mesh.

The v08 fan shares one centre vertex with every triangle, so the averaged centre
tangent skews the water normal map per triangle and shows as a visible wedge on
the surface. This writes the same 1.03x lake outline (see build_refinement_v08.py)
as a ~3 m interior grid plus a 512-point boundary ring, Delaunay triangulated and
clipped to the outline, so every triangle has consistent tangents. It also
rebuilds the SM_IV_SkyRiver spillway ribbon so it starts on the lake outline
instead of lying co-planar beneath the lake.
"""
import math, json
import numpy as np
from pathlib import Path
from scipy.spatial import Delaunay

S = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
CX, CY, Z = -285.0, -373.0, 18.0
RX, RY, OVER = 207.0, 118.0, 1.03
STEP = 3.0
RING = 512


def edge(t):
    return 1 + .055 * np.sin(t * 3) + .025 * np.sin(t * 7 + .4)


def inside(x, y, shrink=1.0):
    u, v = (x - CX) / RX, (y - CY) / RY
    t = np.arctan2(v, u)
    return np.hypot(u, v) / edge(t) < OVER * shrink


# Interior grid, kept at least one step away from the boundary so no slivers appear.
xs = np.arange(CX - RX * OVER - STEP, CX + RX * OVER + 2 * STEP, STEP)
ys = np.arange(CY - RY * OVER - STEP, CY + RY * OVER + 2 * STEP, STEP)
GX, GY = np.meshgrid(xs, ys)
# Jitter breaks the perfectly regular grid so Delaunay is unambiguous (no cocircular quads).
rng = np.random.default_rng(3208)
GX = GX + rng.uniform(-.15, .15, GX.shape) * STEP
GY = GY + rng.uniform(-.15, .15, GY.shape) * STEP
keep = inside(GX, GY, 1 - STEP / (RY * OVER))
P = np.column_stack([GX[keep], GY[keep]])

t = 2 * np.pi * np.arange(RING) / RING
B = np.column_stack([CX + RX * edge(t) * OVER * np.cos(t), CY + RY * edge(t) * OVER * np.sin(t)])
P = np.vstack([P, B])

tri = Delaunay(P)
cen = P[tri.simplices].mean(1)
F = tri.simplices[inside(cen[:, 0], cen[:, 1])]

name = 'SM_IV_GrandSkyLake'
with (S / (name + '.obj')).open('w') as f:
    f.write('o ' + name + '\n')
    for x, y in P:
        f.write(f'v {x*100:.3f} {-y*100:.3f} {Z*100:.3f}\n')
    for x, y in P:
        f.write(f'vt {x/15000+.5:.6f} {y/15000+.5:.6f}\n')
    for a, b, c in F:
        # Qhull does not guarantee winding: orient every triangle CCW in maths
        # space, then reverse (as the v08 fan did) so the Y mirror yields an
        # upward-facing surface in Unreal.
        (ax, ay), (bx, by), (cx, cy) = P[a], P[b], P[c]
        if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0:
            b, c = c, b
        f.write(f'f {c+1}/{c+1} {b+1}/{b+1} {a+1}/{a+1}\n')

lake_stats = {'vertices': int(len(P)), 'triangles': int(len(F)), 'grid_step_m': STEP, 'ring_points': RING}
print(f'{name}: {len(P)} vertices, {len(F)} triangles on a {STEP} m grid')

# Sand floor: the landscape is masked out west of x ~ -437 (island outline), so
# the western bay had no bed and M_Water shaded it as bottomless deep water with
# a hard edge against the shallow sandy east. Same triangulation, dropped just
# below the landscape bed minimum (9.59 m) so it only shows where the bed is missing.
BED_Z = 9.3
with (S / 'SM_IV_LakeBed.obj').open('w') as f:
    f.write('o SM_IV_LakeBed\n')
    for x, y in P:
        f.write(f'v {x*100:.3f} {-y*100:.3f} {BED_Z*100:.3f}\n')
    for x, y in P:
        f.write(f'vt {x/400+.5:.6f} {y/400+.5:.6f}\n')
    for a, b, c in F:
        (ax, ay), (bx, by), (cx, cy) = P[a], P[b], P[c]
        if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0:
            b, c = c, b
        f.write(f'f {c+1}/{c+1} {b+1}/{b+1} {a+1}/{a+1}\n')
print(f'SM_IV_LakeBed: sand floor at {BED_Z} m')

# Spillway ribbon (v07 ran it from y=-363, co-planar beneath the whole southern
# bay, which double-rendered the water as a hard-edged wedge). Start each column
# exactly on the lake outline and run it south to the fall at y=-544.


def outline_y(x, y_guess):
    """Southern lake boundary y for a given x, by bisection on inside()."""
    lo, hi = y_guess - 60, y_guess + 60   # lo is outside (south), hi inside
    for _ in range(40):
        mid = .5 * (lo + hi)
        if inside(np.array(x), np.array(mid)):
            hi = mid
        else:
            lo = mid
    return .5 * (lo + hi)


cols = np.linspace(-6, 6, 5)
seam_x = -285 + 18 * math.sin((-504 + 355) / 55)
seam = [(seam_x + c, outline_y(seam_x + c, -504)) for c in cols]
rows = [seam]
for y in np.linspace(min(y for _, y in seam) - 1.5, -544, 24):
    x0 = -285 + 18 * math.sin((y + 355) / 55)
    rows.append([(x0 + c, y) for c in cols])
V = [(x, y, Z) for row in rows for x, y in row]
F = []
n = len(cols)
for j in range(len(rows) - 1):
    for i in range(n - 1):
        a, b, c, d = j * n + i, j * n + i + 1, (j + 1) * n + i, (j + 1) * n + i + 1
        F.extend([(a, b, c), (b, d, c)])
rname = 'SM_IV_SkyRiver'
with (S / (rname + '.obj')).open('w') as f:
    f.write('o ' + rname + '\n')
    for x, y, z in V:
        f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
    for x, y, z in V:
        f.write(f'vt {x/15000+.5:.6f} {y/15000+.5:.6f}\n')
    for a, b, c in F:
        (ax, ay), (bx, by), (cx, cy) = V[a][:2], V[b][:2], V[c][:2]
        if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0:
            b, c = c, b
        f.write(f'f {c+1}/{c+1} {b+1}/{b+1} {a+1}/{a+1}\n')
assert all(not inside(np.array(x), np.array(y)) for x, y, _ in V[n:]), 'river rows must lie outside the lake'
(S / 'sky_lake_grid_v32.json').write_text(json.dumps({'lake': lake_stats, 'river': {'vertices': len(V), 'triangles': len(F), 'seam_y': [round(y, 2) for _, y in rows[0]]}}, indent=2))
print(f'{rname}: {len(V)} vertices, {len(F)} triangles; seam y = {[round(y, 1) for _, y in rows[0]]}')
