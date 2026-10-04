"""
Island heightmap v9 — moderate mountain (not a chimney), soft coasts, inland lake.

Fixes vs v8/v11:
- Cap peaks ~SEA+11000 (readable mountain, not skyscraper)
- Fixed smoothstep (decreasing ramps work)
- Lake ABOVE sea level
- Soft wide beach shelf
- Low soft satellites (not tilted pillars)
- Soft island rim
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

LAKE_CX, LAKE_CY, LAKE_R = 0.05, -0.02, 0.12
LAKE_RIM = SEA + 2200
LAKE_FLOOR = SEA + 850

CAVE_MX, CAVE_MY = 0.42, 0.38
CAVE_DIR_X, CAVE_DIR_Y = 0.55, 0.65
CAVE_LEN = 0.16
CAVE_WIDTH = 0.04

SATELLITES = [
    (-0.85, 0.52, 0.075),
    (0.92, -0.12, 0.07),
    (-0.22, -0.88, 0.065),
    (0.75, 0.55, 0.06),
]

PEAK_CAP = SEA + 11200  # hard cap — no more chimney


def smoothstep(e0, e1, x):
    denom = e1 - e0
    if abs(denom) < 1e-12:
        return 0.0 if x < e0 else 1.0
    t = (x - e0) / denom
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
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
    raw = (r - (dist - bay)) / max(0.05, r)
    land = max(0.0, min(1.0, raw)) ** 0.78
    outside = raw < 0.0
    return outside, land, dist, bay, r, cx, cy


def soft_coast_height(dist, bay, r, land):
    edge = dist - bay
    if edge > r + 0.24:
        return SEA - 2400 - (edge - r - 0.24) * 2000.0
    if edge > r - 0.10:
        t = smoothstep(r + 0.24, r - 0.12, edge)
        return (SEA - 500) * (1.0 - t) + (SEA + 320 + land * 500) * t
    return SEA + 320 + land * 800


def satellite(nx, ny):
    best = 0.0
    best_h = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr * 1.45:
            core = max(0.0, 1.0 - d / sr) ** 0.65
            skirt = smoothstep(sr * 1.45, sr * 0.8, d)
            best = max(best, core)
            # Low soft islets — not tall pillars
            best_h = max(best_h, SEA + 180 + skirt * 500 + core * 1400)
    return best, best_h


def mountain_arc(nx, ny, land, dist, cx, cy):
    """Crescent back-edge range — multiple peaks, moderate height."""
    ang = math.atan2(nx - cx, ny - cy)
    along = smoothstep(-1.35, -0.35, ang) * smoothstep(1.55, 0.55, ang)
    along = along ** 0.85
    ridge_r = 0.58
    radial = dist - ridge_r
    if radial > 0:
        across = math.exp(-(radial ** 2) / 0.016)
    else:
        across = math.exp(-(radial ** 2) / 0.048)
    foot = math.exp(-((dist - 0.40) ** 2) / 0.06) * 0.42
    along_var = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(ang * 5.5 + 0.8))
    along_var += 0.2 * (0.5 + 0.5 * math.sin(ang * 11.0))
    m = along * across * along_var
    h = m * 9000.0 + along * foot * 3500.0
    for a0, amp, sig_r, sig_a in (
        (0.15, 3500.0, 0.055, 0.22),
        (0.55, 4200.0, 0.05, 0.19),
        (0.95, 3200.0, 0.055, 0.20),
        (1.25, 2800.0, 0.06, 0.18),
    ):
        da = ang - a0
        peak = math.exp(-(da ** 2) / (sig_a ** 2)) * math.exp(-((dist - ridge_r) ** 2) / (sig_r ** 2))
        h += peak * amp
    return SEA + 1800 + h


def sw_coastal_cliff(nx, ny, land):
    d = math.sqrt((nx + 0.58) ** 2 + (ny + 0.38) ** 2)
    spur = math.exp(-(d ** 2) / 0.018) * land
    ridge = math.exp(-((ny + 0.42) ** 2) / 0.014) * smoothstep(-0.30, -0.72, nx) * land
    return spur * 4200.0 + ridge * 2800.0


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
    depth = smoothstep(0.0, CAVE_LEN * 0.85, t) * 2800.0 + 600.0
    mouth = smoothstep(CAVE_WIDTH, 0.0, lateral)
    return h - depth * mouth


def apply_lake(nx, ny, h):
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
    if lake_d >= LAKE_R:
        return h
    edge = smoothstep(LAKE_R, 0.0, lake_d)
    lake_h = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.15)
    blend = smoothstep(LAKE_R, LAKE_R * 0.35, lake_d)
    return h * (1.0 - blend) + lake_h * blend


def sample_body(nx, ny):
    outside, land, dist, bay, r, cx, cy = island_mask(nx, ny)
    sat, sat_h = satellite(nx, ny)

    if outside and sat <= 0.0:
        return max(0.0, soft_coast_height(dist, bay, r, 0.0))

    if sat > 0.0 and outside:
        return sat_h + fbm(nx, ny, 2) * 60

    micro = fbm(nx, ny, 4) * 180

    if land < 0.40:
        shelf = soft_coast_height(dist, bay, r, land)
        inland = SEA + 700 + land * 1900 + micro * 0.3
        t = smoothstep(0.05, 0.40, land)
        h = shelf * (1.0 - t) + inland * t
    else:
        south = smoothstep(0.2, -0.65, ny)
        roll = math.sin(nx * 5.2) * math.cos(ny * 4.0) * (700 + south * 800)
        roll2 = math.sin(nx * 9.5 + ny * 6.5) * 240
        h = SEA + 900 + land * (2400 + south * 500) + roll * land + roll2 + micro * 0.35

    beach_w = smoothstep(0.05, -0.45, nx) * smoothstep(0.05, -0.45, ny)
    beach_h = SEA + 220 + land * 450 + micro * 0.1
    h = h * (1.0 - beach_w * 0.88) + beach_h * (beach_w * 0.88)

    mtn_h = mountain_arc(nx, ny, land, dist, cx, cy)
    ang = math.atan2(nx - cx, ny - cy)
    mtn_w = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang)
    mtn_w *= smoothstep(0.28, 0.48, dist) * smoothstep(0.78, 0.62, dist)
    mw = min(1.0, (mtn_w ** 0.6) * 1.05)
    if not outside:
        h = h * (1.0 - mw) + mtn_h * mw

    h += sw_coastal_cliff(nx, ny, land)
    if mw > 0.25 and not outside:
        h = carve_cave(nx, ny, h)

    return float(max(0.0, min(PEAK_CAP, h)))


def build():
    data = np.zeros((SIZE, SIZE), dtype=np.float64)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = sample_body(nx, ny)

    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    blur = data.copy()
    for _ in range(5):
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, blur)
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, blur)

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            _, land, dist, _, _, cx, cy = island_mask(nx, ny)
            ang = math.atan2(nx - cx, ny - cy)
            mtn = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang) * smoothstep(0.28, 0.48, dist)
            sat, _ = satellite(nx, ny)
            if mtn > 0.35 or sat > 0.2:
                data[yi, xi] = 0.88 * data[yi, xi] + 0.12 * blur[yi, xi]
            else:
                data[yi, xi] = 0.30 * data[yi, xi] + 0.70 * blur[yi, xi]

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = apply_lake(nx, ny, data[yi, xi])

    return np.clip(data, 0, PEAK_CAP).astype(np.uint16)


def write_weight_masks(height):
    """Procedural sand/grass/rock masks to restore ground textures after the v11 wipe."""
    sand = np.zeros((SIZE, SIZE), dtype=np.uint8)
    grass = np.zeros((SIZE, SIZE), dtype=np.uint8)
    rock = np.zeros((SIZE, SIZE), dtype=np.uint8)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            h = int(height[yi, xi])
            # slope proxy from neighbors
            hx = abs(int(height[yi, min(SIZE - 1, xi + 1)]) - int(height[yi, max(0, xi - 1)]))
            hy = abs(int(height[min(SIZE - 1, yi + 1), xi]) - int(height[max(0, yi - 1), xi]))
            slope = hx + hy
            if h < SEA + 100:
                sand[yi, xi] = 0
                grass[yi, xi] = 0
                rock[yi, xi] = 0
            elif h < SEA + 900 or (nx < -0.25 and ny < -0.15 and h < SEA + 1600):
                sand[yi, xi] = 255
                grass[yi, xi] = 40
                rock[yi, xi] = 0
            elif slope > 900 or h > SEA + 7000:
                rock[yi, xi] = 255
                grass[yi, xi] = 60
                sand[yi, xi] = 0
            else:
                grass[yi, xi] = 255
                sand[yi, xi] = 20
                rock[yi, xi] = 15 if slope > 400 else 0
    base = os.path.join(OUT_DIR, "Island_Weight_")
    for name, arr in (("Sand", sand), ("Grass", grass), ("Rock", rock), ("Dirt", np.zeros_like(sand))):
        rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
        rgba[:, :, 0] = arr
        rgba[:, :, 1] = arr
        rgba[:, :, 2] = arr
        rgba[:, :, 3] = 255
        Image.fromarray(rgba, mode="RGBA").save(base + name + ".png")
    print(f"Wrote weight masks {base}*.png")


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
    write_weight_masks(data)

    lix = int((LAKE_CX + 1) * 0.5 * (SIZE - 1))
    liy = int((LAKE_CY + 1) * 0.5 * (SIZE - 1))
    lake_h = int(data[liy, lix])
    ring = int(data[liy, min(SIZE - 1, lix + 80)])
    print(f"Wrote {base}.* {int(data.min())}..{int(data.max())}")
    print(f"Peak delta sea {int(data.max()) - SEA}, lake {lake_h} rim {ring} drop {ring - lake_h}")
    assert lake_h > SEA + 200
    assert lake_h < ring - 500
    assert int(data.max()) <= PEAK_CAP
    assert int(data.max()) > SEA + 6000


if __name__ == "__main__":
    assert abs(smoothstep(0.11, 0.04, 0.0) - 1.0) < 1e-6
    write_outputs(build())
