"""
Island heightmap v7 — soft coasts, central lake, arc mountains, satellites, SW cliff.

Fixes:
- Soft beach + shelf (no hard drop into ocean)
- Soft island rim (no vertical hard sides)
- Central meadow lake (open grass between forest & mountains)
- Curved back-edge mountain (kept)
- Visible satellite islets
- Pronounced SW coastal cliff
- Extra lowland blur to kill 4-way / grid seams
- No thin height scars for paths (paths = tree clearings only)
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

# Central open-grass lake
LAKE_CX, LAKE_CY, LAKE_R = 0.05, -0.02, 0.11
LAKE_RIM = SEA + 780
LAKE_FLOOR = SEA - 1400

CAVE_MX, CAVE_MY = 0.42, 0.38
CAVE_DIR_X, CAVE_DIR_Y = 0.55, 0.65
CAVE_LEN = 0.18
CAVE_WIDTH = 0.045

# Bigger / taller satellites so they read offshore
SATELLITES = [
    (-0.85, 0.52, 0.07),
    (0.92, -0.12, 0.065),
    (-0.22, -0.88, 0.06),
    (0.75, 0.55, 0.05),
]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(1e-6, (e1 - e0)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def fbm(nx, ny, octaves=4):
    v = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(octaves):
        v += amp * math.sin(nx * 3.1 * freq + ny * 2.7 * freq)
        v += amp * 0.55 * math.cos(nx * 5.3 * freq - ny * 4.1 * freq)
        amp *= 0.5
        freq *= 2.0
    return v


def island_mask(nx, ny):
    cx, cy = 0.04, 0.06
    dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    coast = math.sin(nx * 6.2) * math.cos(ny * 5.2) * 0.04 + math.sin(nx * 12 + ny * 8) * 0.018
    r = 0.76 + coast
    bay = smoothstep(0.42, 0.0, math.sqrt((nx + 0.50) ** 2 + (ny + 0.48) ** 2)) * 0.26
    # Softer land falloff (was **0.42 — too cliffy)
    raw = (r - (dist - bay)) / max(0.05, r)
    land = max(0.0, min(1.0, raw)) ** 0.72
    outside = raw < 0.0
    return outside, land, dist, bay, r, cx, cy


def soft_coast_height(dist, bay, r, land):
    """Gradual shelf from deep ocean → beach → inland (kills hard drop)."""
    edge = dist - bay
    # deep ocean
    if edge > r + 0.12:
        return SEA - 3200 - (edge - r - 0.12) * 4000.0
    # wide shallow shelf / beach approach
    if edge > r - 0.02:
        t = smoothstep(r + 0.12, r - 0.05, edge)
        return (SEA - 900) * (1.0 - t) + (SEA + 180) * t
    # nearshore beach
    return SEA + 200 + land * 500


def satellite(nx, ny):
    best = 0.0
    best_h = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr * 1.35:
            # soft skirt into ocean
            core = max(0.0, 1.0 - d / sr) ** 0.5
            skirt = smoothstep(sr * 1.35, sr * 0.9, d)
            best = max(best, core)
            best_h = max(best_h, SEA - 400 + skirt * 800 + core * 2800)
    return best, best_h


def mountain_arc(nx, ny, land, dist, cx, cy):
    ang = math.atan2(nx - cx, ny - cy)
    along = smoothstep(-1.35, -0.35, ang) * smoothstep(1.55, 0.55, ang)
    along = along ** 0.85
    ridge_r = 0.60
    radial = dist - ridge_r
    if radial > 0:
        across = math.exp(-(radial ** 2) / 0.014)
    else:
        across = math.exp(-(radial ** 2) / 0.042)
    foot = math.exp(-((dist - 0.42) ** 2) / 0.055) * 0.38
    along_var = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(ang * 5.5 + 0.8))
    along_var += 0.22 * (0.5 + 0.5 * math.sin(ang * 11.0))
    m = along * across * land * along_var
    h = m * 24000.0 + along * foot * land * 8500.0
    for a0, amp, sig_r, sig_a in (
        (0.15, 8500.0, 0.045, 0.20),
        (0.55, 10000.0, 0.04, 0.17),
        (0.95, 8000.0, 0.045, 0.18),
        (1.25, 6500.0, 0.05, 0.16),
    ):
        da = ang - a0
        peak = math.exp(-(da ** 2) / (sig_a ** 2)) * math.exp(-((dist - ridge_r) ** 2) / (sig_r ** 2))
        h += peak * amp * land
    return SEA + 1500 + h


def sw_coastal_cliff(nx, ny, land):
    """Pronounced cliff on bottom-left (near beach) — keep & exaggerate."""
    # Localized spur around SW coastal corner
    d = math.sqrt((nx + 0.58) ** 2 + (ny + 0.38) ** 2)
    spur = math.exp(-(d ** 2) / 0.02) * land
    ridge = math.exp(-((ny + 0.42) ** 2) / 0.015) * smoothstep(-0.35, -0.70, nx) * land
    return (spur * 5200.0 + ridge * 3800.0), max(spur, ridge)


def carve_cave(nx, ny, h):
    dx = nx - CAVE_MX
    dy = ny - CAVE_MY
    al = math.sqrt(CAVE_DIR_X ** 2 + CAVE_DIR_Y ** 2)
    ux, uy = CAVE_DIR_X / al, CAVE_DIR_Y / al
    t = dx * ux + dy * uy
    if t < -0.02 or t > CAVE_LEN:
        return h
    px, py = dx - t * ux, dy - t * uy
    lateral = math.sqrt(px * px + py * py)
    if lateral > CAVE_WIDTH * (1.0 + t * 0.5):
        return h
    depth = smoothstep(0.0, CAVE_LEN * 0.85, t) * 5000.0 + 1000.0
    mouth = smoothstep(CAVE_WIDTH, 0.0, lateral)
    return h - depth * mouth


def sample(nx, ny):
    outside, land, dist, bay, r, cx, cy = island_mask(nx, ny)
    sat, sat_h = satellite(nx, ny)

    if outside and sat <= 0.0:
        return max(0, int(soft_coast_height(dist, bay, r, 0.0)))

    if sat > 0.0 and outside:
        return int(sat_h + fbm(nx, ny, 3) * 120)

    micro = fbm(nx, ny, 4) * 220

    # Soft coastal band even on land near rim
    if land < 0.35:
        shelf = soft_coast_height(dist, bay, r, land)
        inland = SEA + 600 + land * 1800 + micro * 0.3
        t = smoothstep(0.05, 0.35, land)
        h = shelf * (1.0 - t) + inland * t
    else:
        # Rolling meadow / forest floor — south rolls kill flat pad
        south = smoothstep(0.2, -0.65, ny)
        roll = math.sin(nx * 5.2) * math.cos(ny * 4.0) * (800 + south * 900)
        roll2 = math.sin(nx * 9.5 + ny * 6.5) * 280
        h = SEA + 750 + land * (2400 + south * 600) + roll * land + roll2 + micro * 0.4

    # SW beach preference
    beach_w = smoothstep(0.05, -0.45, nx) * smoothstep(0.05, -0.45, ny)
    beach_h = SEA + 160 + land * 420 + micro * 0.12
    h = h * (1.0 - beach_w * 0.85) + beach_h * (beach_w * 0.85)

    # Curved mountain
    mtn_h = mountain_arc(nx, ny, land, dist, cx, cy)
    ang = math.atan2(nx - cx, ny - cy)
    mtn_w = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang)
    mtn_w *= smoothstep(0.30, 0.52, dist)
    mw = (mtn_w ** 0.7) * land
    h = h * (1.0 - mw) + mtn_h * mw

    # Light desert shelf (height only — props sparse later)
    if ang > 0.7 and ang < 1.5 and 0.40 < dist < 0.58:
        dw = smoothstep(0.40, 0.48, dist) * smoothstep(0.58, 0.50, dist) * 0.45
        desert = SEA + 2000 + dw * land * 4000
        h = h * (1.0 - dw) + desert * dw

    # SW coastal cliff boost
    cliff_add, cw = sw_coastal_cliff(nx, ny, land)
    h += cliff_add

    # Central lake in open grass
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
    if lake_d < LAKE_R:
        edge = smoothstep(LAKE_R, 0.0, lake_d)
        lake_h = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.3)
        blend = smoothstep(LAKE_R, LAKE_R * 0.45, lake_d)
        h = h * (1.0 - blend) + lake_h * blend

    if mw > 0.15:
        h = carve_cave(nx, ny, h)

    return int(max(0, min(65535, h)))


def build():
    data = np.zeros((SIZE, SIZE), dtype=np.float64)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = sample(nx, ny)

    # Stronger lowland blur — kills 4-way / varicose scars; protect peaks+lake+satellites
    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    blur = data.copy()
    for _ in range(4):
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, blur)
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, blur)

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            _, land, dist, _, _, cx, cy = island_mask(nx, ny)
            ang = math.atan2(nx - cx, ny - cy)
            mtn = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang) * smoothstep(0.30, 0.52, dist)
            lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            sat, _ = satellite(nx, ny)
            if lake_d < LAKE_R * 0.92 or mtn > 0.5 or sat > 0.3:
                data[yi, xi] = 0.85 * data[yi, xi] + 0.15 * blur[yi, xi]
            else:
                data[yi, xi] = 0.30 * data[yi, xi] + 0.70 * blur[yi, xi]

    return np.clip(data, 0, 65535).astype(np.uint16)


def write_outputs(data):
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.join(OUT_DIR, "Island_Heightmap_1009")
    with open(base + ".r16", "wb") as f:
        f.write(data.astype("<u2").tobytes())
    Image.fromarray(data, mode="I;16").save(base + ".png")
    hi = (data >> 8).astype(np.uint8)
    lo = (data & 0xFF).astype(np.uint8)
    rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 3] = hi, lo, 255
    Image.fromarray(rgba, mode="RGBA").save(base + "_RG.png")
    print(f"Wrote {base}.* {int(data.min())}..{int(data.max())}")
    mid = SIZE // 2
    print(f"SW {int(data[:mid,:mid].max())} NE {int(data[mid:,mid:].max())}")
    lix = int((LAKE_CX + 1) * 0.5 * (SIZE - 1))
    liy = int((LAKE_CY + 1) * 0.5 * (SIZE - 1))
    print(f"Central lake {int(data[liy, lix])}")


if __name__ == "__main__":
    write_outputs(build())
