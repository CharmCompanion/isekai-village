"""
Island heightmap v5 — blended biomes (no axis seams), real mountains, deep lake.
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

LAKE_CX, LAKE_CY, LAKE_R = 0.10, 0.12, 0.11
LAKE_RIM = SEA + 900
LAKE_FLOOR = SEA - 1600

SATELLITES = [
    (-0.82, 0.55, 0.055),
    (0.90, -0.15, 0.048),
    (-0.25, -0.86, 0.042),
]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(1e-6, (e1 - e0)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def fbm(nx, ny, octaves=4):
    v = amp = 1.0
    freq = 1.0
    v = 0.0
    for _ in range(octaves):
        v += amp * math.sin(nx * 3.1 * freq + ny * 2.7 * freq)
        v += amp * 0.55 * math.cos(nx * 5.3 * freq - ny * 4.1 * freq)
        amp *= 0.5
        freq *= 2.0
    return v


def island_mask(nx, ny):
    cx, cy = 0.05, 0.05
    dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    coast = math.sin(nx * 6.5) * math.cos(ny * 5.5) * 0.045 + math.sin(nx * 13 + ny * 9) * 0.022
    r = 0.78 + coast
    bay = smoothstep(0.40, 0.0, math.sqrt((nx + 0.50) ** 2 + (ny + 0.50) ** 2)) * 0.28
    outside = (dist - bay) > r
    land = max(0.0, min(1.0, (r - (dist - bay)) / r)) ** 0.42
    return outside, land, dist, bay


def satellite(nx, ny):
    best = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr:
            best = max(best, (1.0 - d / sr) ** 0.55)
    return best


def h_ocean(dist, bay):
    return SEA - 2800 - max(0.0, dist - bay - 0.78) * 5500.0


def h_beach(nx, ny, land, micro):
    beach = smoothstep(-0.95, 0.05, nx) * smoothstep(-0.95, 0.05, ny)
    return SEA + 250 + beach * land * 500 + micro * 0.2


def h_meadow(nx, ny, land, micro):
    roll = math.sin(nx * 4.2) * math.cos(ny * 3.8) * 700
    return SEA + 850 + land * 2600 + roll * land + micro * 0.4


def h_highland(nx, ny, land, micro):
    t = land
    roll = math.sin(nx * 5) * math.cos(ny * 4) * 900
    return SEA + 1400 + t * 4200 + roll * t + micro * 0.5


def h_foothills(nx, ny, land, micro):
    t = land * smoothstep(-0.1, 0.55, nx)
    return SEA + 900 + t * 6500 + abs(micro)


def h_mountain(nx, ny, land, micro):
    """Real massif — peaks near max uint16."""
    mx = smoothstep(0.0, 0.9, nx)
    my = smoothstep(0.0, 0.9, ny)
    m = (mx * my) ** 0.7 * land
    mass = m * 22000.0
    ridge = abs(math.sin((nx + ny) * 3.8)) * 7000.0 * m
    p1 = math.exp(-((nx - 0.58) ** 2 + (ny - 0.62) ** 2) / 0.035) * 18000.0
    p2 = math.exp(-((nx - 0.75) ** 2 + (ny - 0.50) ** 2) / 0.028) * 15000.0
    p3 = math.exp(-((nx - 0.48) ** 2 + (ny - 0.72) ** 2) / 0.04) * 12000.0
    tip = smoothstep(0.50, 0.98, nx) * smoothstep(0.40, 0.95, ny) * 10000.0
    return SEA + 2000 + mass + ridge + p1 + p2 + p3 + tip + micro


def sample(nx, ny):
    outside, land, dist, bay = island_mask(nx, ny)
    sat = satellite(nx, ny)
    if outside and sat <= 0:
        return max(0, int(h_ocean(dist, bay)))
    if sat > 0 and outside:
        return int(SEA + 400 + sat * 2400 + fbm(nx, ny, 3) * 180)

    micro = fbm(nx, ny, 4) * 260

    # Lake carved after blend
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)

    # Soft biome weights — NO hard if/else on axes (fixes center cross seams)
    w_beach = smoothstep(0.15, -0.35, nx) * smoothstep(0.15, -0.35, ny)
    w_mtn = smoothstep(-0.05, 0.40, nx) * smoothstep(-0.05, 0.40, ny)
    w_high = smoothstep(0.2, -0.4, nx) * smoothstep(-0.2, 0.5, ny)
    w_foot = smoothstep(-0.15, 0.5, nx) * smoothstep(0.35, -0.25, ny)
    w_meadow = 0.55

    weights = np.array([w_beach, w_mtn, w_high, w_foot, w_meadow], dtype=np.float64)
    # Mountain dominates NE strongly so blend can't wash peaks into hills
    weights[1] = weights[1] ** 0.65 * 2.8
    s = weights.sum()
    if s > 1e-6:
        weights /= s

    vals = np.array([
        h_beach(nx, ny, land, micro),
        h_mountain(nx, ny, land, micro),
        h_highland(nx, ny, land, micro),
        h_foothills(nx, ny, land, micro),
        h_meadow(nx, ny, land, micro),
    ], dtype=np.float64)
    h = float(np.dot(weights, vals))

    # Additive peak spikes (survive blending)
    if nx > 0.2 and ny > 0.2:
        p1 = math.exp(-((nx - 0.58) ** 2 + (ny - 0.62) ** 2) / 0.03) * 16000.0
        p2 = math.exp(-((nx - 0.75) ** 2 + (ny - 0.50) ** 2) / 0.025) * 14000.0
        h += p1 + p2
        h = min(65535.0, h)

    if lake_d < LAKE_R:
        edge = smoothstep(LAKE_R, 0.0, lake_d)  # 1 center
        lake_h = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.35)
        blend = smoothstep(LAKE_R, LAKE_R * 0.55, lake_d)
        h = h * (1.0 - blend) + lake_h * blend

    return int(max(0, min(65535, h)))


def build():
    data = np.zeros((SIZE, SIZE), dtype=np.float64)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = sample(nx, ny)

    # Mild blur on lowlands only (kill residual seams) — protect peaks & lake
    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    blur = data.copy()
    for _ in range(3):
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, blur)
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, blur)

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            mtn_w = smoothstep(-0.05, 0.45, nx) * smoothstep(-0.05, 0.45, ny)
            if lake_d < LAKE_R * 0.95:
                continue  # keep carved lake
            if mtn_w > 0.55:
                # peaks: tiny blur only
                data[yi, xi] = 0.92 * data[yi, xi] + 0.08 * blur[yi, xi]
            else:
                data[yi, xi] = 0.45 * data[yi, xi] + 0.55 * blur[yi, xi]

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
    mid = SIZE // 2
    sw, ne = data[:mid, :mid], data[mid:, mid:]
    peak_uu = (int(ne.max()) - SEA) * 100.0 / 128.0
    beach_uu = (int(sw.max()) - SEA) * 100.0 / 128.0
    print(f"Wrote {base}.* range {data.min()}..{data.max()}")
    print(f"SW max={int(sw.max())} ({beach_uu:.0f}uu) NE max={int(ne.max())} ({peak_uu:.0f}uu)")
    print(f"Peak above beach {peak_uu - beach_uu:.0f} uu")


if __name__ == "__main__":
    write_outputs(build())
