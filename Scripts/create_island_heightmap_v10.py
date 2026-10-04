"""
Island heightmap v10 — organic lake, soft irregular satellites, moderate mountain.
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

LAKE_CX, LAKE_CY = 0.04, -0.03
LAKE_RIM = SEA + 2300
LAKE_FLOOR = SEA + 900

CAVE_MX, CAVE_MY = 0.42, 0.38
CAVE_DIR_X, CAVE_DIR_Y = 0.55, 0.65
CAVE_LEN = 0.16
CAVE_WIDTH = 0.04

# Irregular satellite blobs (cx, cy, base_r, stretch_x, stretch_y, rot)
SATELLITES = [
    (-0.84, 0.50, 0.08, 1.35, 0.75, 0.4),
    (0.90, -0.14, 0.07, 0.85, 1.30, -0.6),
    (-0.20, -0.86, 0.07, 1.20, 0.90, 0.9),
    (0.72, 0.52, 0.06, 1.10, 0.85, -0.3),
]

PEAK_CAP = SEA + 10800


def smoothstep(e0, e1, x):
    denom = e1 - e0
    if abs(denom) < 1e-12:
        return 0.0 if x < e0 else 1.0
    t = (x - e0) / denom
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return t * t * (3.0 - 2.0 * t)


def fbm(nx, ny, octaves=4, seed=0.0):
    v = 0.0
    amp = 1.0
    freq = 1.0
    for i in range(octaves):
        v += amp * math.sin(nx * 3.1 * freq + ny * 2.7 * freq + seed + i)
        v += amp * 0.55 * math.cos(nx * 5.3 * freq - ny * 4.1 * freq + seed * 1.7)
        amp *= 0.5
        freq *= 2.0
    return v


def island_mask(nx, ny):
    cx, cy = 0.04, 0.06
    dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    coast = (
        math.sin(nx * 6.2) * math.cos(ny * 5.2) * 0.045
        + math.sin(nx * 12 + ny * 8) * 0.022
        + fbm(nx, ny, 2, 2.1) * 0.012
    )
    r = 0.76 + coast
    bay = smoothstep(0.42, 0.0, math.sqrt((nx + 0.50) ** 2 + (ny + 0.48) ** 2)) * 0.26
    raw = (r - (dist - bay)) / max(0.05, r)
    land = max(0.0, min(1.0, raw)) ** 0.78
    outside = raw < 0.0
    return outside, land, dist, bay, r, cx, cy


def soft_coast_height(dist, bay, r, land):
    edge = dist - bay
    if edge > r + 0.26:
        return SEA - 2200 - (edge - r - 0.26) * 1800.0
    if edge > r - 0.12:
        t = smoothstep(r + 0.26, r - 0.14, edge)
        return (SEA - 450) * (1.0 - t) + (SEA + 300 + land * 550) * t
    return SEA + 300 + land * 850


def sat_field(nx, ny):
    """Organic satellite field strength + height (low flat mounds, not pillars)."""
    best = 0.0
    best_h = 0.0
    for sx, sy, sr, stx, sty, rot in SATELLITES:
        dx, dy = nx - sx, ny - sy
        c, s = math.cos(rot), math.sin(rot)
        rx = (dx * c + dy * s) / max(1e-6, sr * stx)
        ry = (-dx * s + dy * c) / max(1e-6, sr * sty)
        # noisy edge
        edge_n = 1.0 + 0.18 * fbm(nx * 2.5, ny * 2.5, 3, sx + sy)
        d = math.sqrt(rx * rx + ry * ry) / edge_n
        if d < 1.35:
            core = max(0.0, 1.0 - d) ** 0.7
            skirt = smoothstep(1.35, 0.75, d)
            best = max(best, core)
            # Flat-ish plateau then soft skirt — NO tall pillar
            plate = SEA + 250 + skirt * 400 + core * 900
            best_h = max(best_h, plate)
    return best, best_h


def lake_field(nx, ny):
    """Irregular organic lake (NOT a circle). Returns 0..1 inside-ness."""
    dx = (nx - LAKE_CX) * 1.15
    dy = (ny - LAKE_CY) * 0.92
    # Warp coordinates with noise
    wx = dx + 0.045 * fbm(nx * 3.0, ny * 3.0, 4, 1.3)
    wy = dy + 0.04 * fbm(nx * 3.2 + 2.0, ny * 2.8, 4, 4.7)
    # Soft blob radius varies by angle
    ang = math.atan2(wy, wx)
    rad = 0.11 + 0.035 * math.sin(ang * 2.3 + 0.5) + 0.025 * math.sin(ang * 5.1 - 1.2)
    rad += 0.02 * fbm(math.cos(ang), math.sin(ang), 3, 8.0)
    d = math.sqrt(wx * wx + wy * wy) / max(0.04, rad)
    if d >= 1.25:
        return 0.0
    return smoothstep(1.25, 0.15, d)


def mountain_arc(nx, ny, dist, cx, cy):
    ang = math.atan2(nx - cx, ny - cy)
    along = smoothstep(-1.35, -0.35, ang) * smoothstep(1.55, 0.55, ang)
    along = along ** 0.85
    ridge_r = 0.58
    radial = dist - ridge_r
    if radial > 0:
        across = math.exp(-(radial ** 2) / 0.018)
    else:
        across = math.exp(-(radial ** 2) / 0.05)
    foot = math.exp(-((dist - 0.40) ** 2) / 0.06) * 0.4
    along_var = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(ang * 5.5 + 0.8))
    along_var += 0.2 * (0.5 + 0.5 * math.sin(ang * 11.0))
    m = along * across * along_var
    h = m * 8500.0 + along * foot * 3200.0
    for a0, amp, sig_r, sig_a in (
        (0.15, 3200.0, 0.055, 0.22),
        (0.55, 3800.0, 0.05, 0.19),
        (0.95, 3000.0, 0.055, 0.20),
        (1.25, 2600.0, 0.06, 0.18),
    ):
        da = ang - a0
        peak = math.exp(-(da ** 2) / (sig_a ** 2)) * math.exp(-((dist - ridge_r) ** 2) / (sig_r ** 2))
        h += peak * amp
    # Break perfect ridge with noise
    h += along * across * fbm(nx * 4, ny * 4, 3, 0.5) * 400
    return SEA + 1700 + h


def sw_coastal_cliff(nx, ny, land):
    d = math.sqrt((nx + 0.58) ** 2 + (ny + 0.38) ** 2)
    spur = math.exp(-(d ** 2) / 0.02) * land
    ridge = math.exp(-((ny + 0.42) ** 2) / 0.015) * smoothstep(-0.30, -0.72, nx) * land
    return spur * 3800.0 + ridge * 2400.0


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
    depth = smoothstep(0.0, CAVE_LEN * 0.85, t) * 2600.0 + 500.0
    mouth = smoothstep(CAVE_WIDTH, 0.0, lateral)
    return h - depth * mouth


def apply_lake(nx, ny, h):
    w = lake_field(nx, ny)
    if w <= 0.0:
        return h
    # Vary floor depth organically
    floor = LAKE_FLOOR + fbm(nx * 5, ny * 5, 3, 3.3) * 180
    rim = LAKE_RIM + fbm(nx * 4, ny * 4, 2, 1.1) * 120
    lake_h = floor * w + rim * (1.0 - w) * 0.35 + h * (1.0 - w) * 0.65
    # Stronger pull toward basin in core
    lake_h = h * (1.0 - w) + (floor + (rim - floor) * (1.0 - w)) * w
    return lake_h


def sample_body(nx, ny):
    outside, land, dist, bay, r, cx, cy = island_mask(nx, ny)
    sat, sat_h = sat_field(nx, ny)

    if outside and sat <= 0.0:
        return max(0.0, soft_coast_height(dist, bay, r, 0.0))

    if sat > 0.0 and outside:
        return sat_h + fbm(nx, ny, 2, 0.2) * 40

    micro = fbm(nx, ny, 4, 0.0) * 200

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

    mtn_h = mountain_arc(nx, ny, dist, cx, cy)
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
            sat, _ = sat_field(nx, ny)
            lf = lake_field(nx, ny)
            if lf > 0.2:
                # light blur only — keep organic shoreline
                data[yi, xi] = 0.75 * data[yi, xi] + 0.25 * blur[yi, xi]
            elif mtn > 0.35 or sat > 0.2:
                data[yi, xi] = 0.88 * data[yi, xi] + 0.12 * blur[yi, xi]
            else:
                data[yi, xi] = 0.30 * data[yi, xi] + 0.70 * blur[yi, xi]

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = apply_lake(nx, ny, data[yi, xi])

    return np.clip(data, 0, PEAK_CAP).astype(np.uint16)


def write_weight_masks(height):
    sand = np.zeros((SIZE, SIZE), dtype=np.uint8)
    grass = np.zeros((SIZE, SIZE), dtype=np.uint8)
    rock = np.zeros((SIZE, SIZE), dtype=np.uint8)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            h = int(height[yi, xi])
            hx = abs(int(height[yi, min(SIZE - 1, xi + 1)]) - int(height[yi, max(0, xi - 1)]))
            hy = abs(int(height[min(SIZE - 1, yi + 1), xi]) - int(height[max(0, yi - 1), xi]))
            slope = hx + hy
            lf = lake_field(nx, ny)
            if h < SEA + 80:
                pass
            elif lf > 0.35:
                # muddy/sandy lake shore
                sand[yi, xi] = int(180 * lf)
                grass[yi, xi] = int(80 * (1.0 - lf))
            elif h < SEA + 950 or (nx < -0.25 and ny < -0.15 and h < SEA + 1700):
                sand[yi, xi] = 255
                grass[yi, xi] = 35
            elif slope > 900 or h > SEA + 6800:
                rock[yi, xi] = 255
                grass[yi, xi] = 50
            else:
                grass[yi, xi] = 255
                sand[yi, xi] = 15
                rock[yi, xi] = 20 if slope > 400 else 0
    base = os.path.join(OUT_DIR, "Island_Weight_")
    for name, arr in (("Sand", sand), ("Grass", grass), ("Rock", rock), ("Dirt", np.zeros_like(sand))):
        rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
        rgba[:, :, 0] = arr
        rgba[:, :, 1] = arr
        rgba[:, :, 2] = arr
        rgba[:, :, 3] = 255
        Image.fromarray(rgba, mode="RGBA").save(base + name + ".png")


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

    # Lake shape check: count basin cells, estimate circularity via bounding box fill
    lake_mask = np.zeros((SIZE, SIZE), dtype=bool)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            if data[yi, xi] < SEA + 1600 and lake_field(nx, ny) > 0.4:
                lake_mask[yi, xi] = True
    ys_i, xs_i = np.where(lake_mask)
    if len(xs_i) > 10:
        bw = xs_i.max() - xs_i.min() + 1
        bh = ys_i.max() - ys_i.min() + 1
        fill = len(xs_i) / max(1, bw * bh)
        print(f"Lake cells={len(xs_i)} bbox_fill={fill:.2f} (circle~0.78; organic lower)")
    print(f"Wrote {base}.* {int(data.min())}..{int(data.max())} peak_delta={int(data.max()) - SEA}")


if __name__ == "__main__":
    assert abs(smoothstep(0.11, 0.04, 0.0) - 1.0) < 1e-6
    write_outputs(build())
