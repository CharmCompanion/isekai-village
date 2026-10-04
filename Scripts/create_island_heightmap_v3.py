"""
Island heightmap v3 — proper archipelago layout for Height_DemoCopy.

Top-down (+Y north, +X east):
  SW  — crescent sandy beach (spawn / low)
  NE  — dramatic mountain range (snow/rock peaks)
  NW  — forested rolling highlands
  Center — inland lake (rim + depressed basin for depth)
  SE  — rocky foothills into mountains
  Ocean — 3 small satellite islands

Smooths output to reduce visible landscape grid lines.

Run: python Scripts/create_island_heightmap_v3.py
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

# Lake (keep feature — user wants depth inside)
LAKE_CX, LAKE_CY = 0.10, 0.12
LAKE_R = 0.11
LAKE_RIM = SEA + 820
LAKE_FLOOR = SEA - 1400  # deeper basin (~1100 world units below rim at scale 100)

SATELLITES = [
    (-0.82, 0.55, 0.055),   # NW islet
    (0.90, -0.15, 0.048),   # East islet
    (-0.25, -0.86, 0.042),  # South islet
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
    dist = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    coast = (
        np.sin(nx * 6.5) * np.cos(ny * 5.5) * 0.045
        + np.sin(nx * 13.0 + ny * 9.0) * 0.022
    )
    r = 0.78 + coast
    # SW crescent bay
    bay_d = np.sqrt((nx + 0.50) ** 2 + (ny + 0.50) ** 2)
    bay = smoothstep(0.40, 0.0, bay_d) * 0.30
    outside = dist - bay > r
    land = np.clip((r - (dist - bay)) / r, 0.0, 1.0) ** 0.42
    return outside, land, dist, bay


def satellite_mask(nx, ny):
    best = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr:
            t = 1.0 - d / sr
            best = max(best, t ** 0.55)
    return best


def sample_height(nx, ny):
    outside, land, dist, bay = main_island_mask(nx, ny)
    sat = satellite_mask(nx, ny)

    if outside and sat <= 0.0:
        depth = (dist - bay - 0.78) * 5500.0
        return max(0, int(SEA - 2800 - depth))

    if sat > 0.0 and outside:
        h = SEA + 350 + sat * 2200 + fbm(nx, ny, 3) * 180
        return int(h)

    micro = fbm(nx, ny, 4) * 220

    # Inland lake basin
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
    in_lake = lake_d < LAKE_R
    if in_lake:
        edge = smoothstep(LAKE_R, LAKE_R * 0.35, lake_d)
        floor_mix = smoothstep(LAKE_R * 0.85, LAKE_R * 0.15, lake_d)
        h = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.6)
        h += floor_mix * 120  # shallow shelf near shore
        return int(h + micro * 0.15)

    # SW beach — flat sandy crescent
    if nx < 0.02 and ny < 0.02:
        beach = smoothstep(-0.9, -0.1, nx) * smoothstep(-0.9, -0.1, ny)
        return int(SEA + 280 + beach * land * 520 + micro * 0.25)

    # NE mountains — dominant range
    if nx > 0.02 and ny > 0.02:
        mx = smoothstep(0.0, 0.80, (nx - 0.02) / 0.78)
        my = smoothstep(0.0, 0.80, (ny - 0.02) / 0.78)
        m = mx * my * land
        ridges = abs(math.sin(nx * 10.5 + ny * 6.5)) * 2800
        peaks = abs(math.sin(nx * 21.0) * math.cos(ny * 17.5)) * 2000
        tip = smoothstep(0.40, 0.98, nx) * smoothstep(0.40, 0.98, ny)
        h = SEA + 1400 + m * 24000 + (ridges + peaks) * m + tip * m * 9000
        return int(h + micro)

    # NW forest highlands
    if nx < 0.05 and ny > 0.05:
        t = smoothstep(0.0, 0.75, land)
        roll = math.sin(nx * 4.5) * math.cos(ny * 3.8) * 900
        return int(SEA + 900 + t * 3200 + roll * t + micro * 0.6)

    # SE rocky foothills
    if nx > 0.0 and ny < 0.05:
        t = smoothstep(0.0, 0.7, land)
        return int(SEA + 600 + t * 4500 + abs(micro) * 1.2 + nx * 1800 * t)

    # Interior rolling meadow
    roll = math.sin(nx * 4.8) * math.cos(ny * 4.2) * 1100
    valley = smoothstep(-0.1, 0.55, ny) * 1600
    return int(SEA + 750 + land * (3000 + valley) + roll * land + micro * 0.5)


def build():
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    data = np.zeros((SIZE, SIZE), dtype=np.float64)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            data[yi, xi] = sample_height(nx, ny)

    # Smooth to hide component/grid stepping — then restore lake basin depth
    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    lake_mask = np.zeros((SIZE, SIZE), dtype=np.float64)
    xs = np.linspace(-1.0, 1.0, SIZE)
    ys = np.linspace(-1.0, 1.0, SIZE)
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            if d < LAKE_R:
                lake_mask[yi, xi] = smoothstep(LAKE_R, 0.0, d)

    for _ in range(2):
        data = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, data)
        data = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, data)

    # Re-carve lake after blur so it keeps depth
    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            if lake_mask[yi, xi] <= 0:
                continue
            edge = lake_mask[yi, xi]
            d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            floor_mix = smoothstep(LAKE_R * 0.85, LAKE_R * 0.12, d)
            data[yi, xi] = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.5) + floor_mix * 80

    data = np.clip(data, 0, 65535).astype(np.uint16)
    return data


def write_outputs(data):
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.join(OUT_DIR, "Island_Heightmap_1009")
    with open(base + ".r16", "wb") as f:
        f.write(data.astype("<u2").tobytes())
    Image.fromarray(data, mode="I;16").save(base + ".png")
    hi = (data >> 8).astype(np.uint8)
    lo = (data & 0xFF).astype(np.uint8)
    rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    rgba[:, :, 0] = hi
    rgba[:, :, 1] = lo
    rgba[:, :, 3] = 255
    Image.fromarray(rgba, mode="RGBA").save(base + "_RG.png")
    mid = SIZE // 2
    sw, ne = data[:mid, :mid], data[mid:, mid:]
    print(f"Wrote {base}.r16 / .png / _RG.png")
    print(f"Range {data.min()}..{data.max()} avg={data.mean():.0f}")
    ix = int((LAKE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((LAKE_CY + 1) * 0.5 * (SIZE - 1))
    print(f"SW max={sw.max()} NE max={ne.max()} lake_center={data[iy, ix]}")


if __name__ == "__main__":
    write_outputs(build())
