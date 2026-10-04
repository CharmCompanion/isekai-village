"""
Island heightmap v4 — mountains that READ from the sky.

NE range peaks ~25k+ world units above sea (scaleZ=100).
Keeps: SW beach, inland lake basin, 3 satellites, smoothed coasts.
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

LAKE_CX, LAKE_CY = 0.10, 0.12
LAKE_R = 0.11
LAKE_RIM = SEA + 900
LAKE_FLOOR = SEA - 1600

# Village clearing south of lake (no forest paint here)
VILLAGE_CX, VILLAGE_CY = 0.05, -0.05
VILLAGE_R = 0.14

SATELLITES = [
    (-0.82, 0.55, 0.055),
    (0.90, -0.15, 0.048),
    (-0.25, -0.86, 0.042),
]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def fbm(nx, ny, octaves=4):
    v = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(octaves):
        v += amp * math.sin(nx * 3.1 * freq + ny * 2.7 * freq)
        v += amp * 0.5 * math.cos(nx * 5.3 * freq - ny * 4.1 * freq)
        amp *= 0.5
        freq *= 2.0
    return v


def main_island_mask(nx, ny):
    cx, cy = 0.06, 0.06
    dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    coast = math.sin(nx * 6.5) * math.cos(ny * 5.5) * 0.045 + math.sin(nx * 13.0 + ny * 9.0) * 0.022
    r = 0.78 + coast
    bay_d = math.sqrt((nx + 0.50) ** 2 + (ny + 0.50) ** 2)
    bay = smoothstep(0.40, 0.0, bay_d) * 0.30
    outside = dist - bay > r
    land = max(0.0, min(1.0, (r - (dist - bay)) / r)) ** 0.42
    return outside, land, dist, bay


def satellite_mask(nx, ny):
    best = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr:
            best = max(best, (1.0 - d / sr) ** 0.55)
    return best


def sample_height(nx, ny):
    outside, land, dist, bay = main_island_mask(nx, ny)
    sat = satellite_mask(nx, ny)

    if outside and sat <= 0.0:
        depth = (dist - bay - 0.78) * 5500.0
        return max(0, int(SEA - 2800 - depth))

    if sat > 0.0 and outside:
        return int(SEA + 400 + sat * 2400 + fbm(nx, ny, 3) * 200)

    micro = fbm(nx, ny, 4) * 280

    # Lake basin
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
    if lake_d < LAKE_R:
        edge = smoothstep(LAKE_R, LAKE_R * 0.25, lake_d)  # 1 at center
        return int(LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.4) + micro * 0.1)

    # SW beach
    if nx < 0.0 and ny < 0.0:
        beach = smoothstep(-0.9, -0.05, nx) * smoothstep(-0.9, -0.05, ny)
        return int(SEA + 250 + beach * land * 480 + micro * 0.2)

    # NE MOUNTAIN RANGE — tall enough to read from overhead
    # Target peak ~ SEA+32000 → world Z ≈ 25,000 uu above mid
    if nx > 0.0 and ny > 0.0:
        mx = smoothstep(0.05, 0.85, nx)
        my = smoothstep(0.05, 0.85, ny)
        m = (mx * my) ** 0.85 * land
        # Broad massif
        mass = m * 28000.0
        # Sharp ridgeline NE→SW across the range
        ridge = abs(math.sin((nx + ny) * 4.5)) * 8000.0 * m
        # Twin peaks
        p1 = math.exp(-((nx - 0.55) ** 2 + (ny - 0.60) ** 2) / 0.04) * 14000.0
        p2 = math.exp(-((nx - 0.72) ** 2 + (ny - 0.48) ** 2) / 0.03) * 11000.0
        # Cliff spur toward ocean (pointed jet)
        tip = smoothstep(0.55, 0.95, nx) * smoothstep(0.45, 0.90, ny) * 9000.0
        foothills = smoothstep(0.0, 0.45, nx) * smoothstep(0.0, 0.45, ny) * land * 4500.0
        h = SEA + 1800 + foothills + mass + ridge + p1 + p2 + tip + micro
        return int(min(65535, h))

    # NW forest highlands (moderate elevation)
    if nx < 0.05 and ny > 0.0:
        t = smoothstep(0.0, 0.8, land)
        return int(SEA + 1100 + t * 4800 + math.sin(nx * 5) * math.cos(ny * 4) * 1000 * t + micro)

    # SE foothills into mountains
    if nx > 0.0:
        t = land * smoothstep(-0.2, 0.4, nx)
        return int(SEA + 700 + t * 7000 + abs(micro) * 1.4)

    # Interior meadows / village plateau
    roll = math.sin(nx * 4.5) * math.cos(ny * 4.0) * 900
    return int(SEA + 800 + land * 2800 + roll * land + micro * 0.45)


def build():
    data = np.zeros((SIZE, SIZE), dtype=np.float64)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = sample_height(nx, ny)

    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    # Soft blur coasts only — preserve mountain peaks & lake
    blur = data.copy()
    for _ in range(2):
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, blur)
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, blur)

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            in_mtn = nx > 0.15 and ny > 0.15
            in_lake = lake_d < LAKE_R
            if in_mtn or in_lake:
                # lightly blend blur only at edges
                if in_lake:
                    edge = smoothstep(LAKE_R, 0.0, lake_d)
                    data[yi, xi] = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.4)
                # mountains keep raw height (no blur washout)
                continue
            data[yi, xi] = 0.65 * data[yi, xi] + 0.35 * blur[yi, xi]

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
    print(f"Wrote {base}.*")
    print(f"Range {data.min()}..{data.max()}")
    print(f"SW max={sw.max()} (~{beach_uu:.0f}uu)  NE max={ne.max()} (~{peak_uu:.0f}uu above mid)")
    print(f"Peak above beach ≈ {peak_uu - beach_uu:.0f} uu")


if __name__ == "__main__":
    write_outputs(build())
