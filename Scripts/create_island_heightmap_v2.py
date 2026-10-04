"""
Island heightmap for SoStylized demo-scale landscape (1009 x 1009).

Layout (top-down, +Y = north, +X = east):
  - Front-left (SW): crescent sandy beach bay
  - Back-right (NE): mountain range
  - Interior: rolling demo-style hills

Outputs:
  Content/SpellCraft/Textures/Island_Heightmap_1009.r16
  Content/SpellCraft/Textures/Island_Heightmap_1009.png  (16-bit grayscale for UE import)
"""
import math
import os
import struct

import numpy as np
from PIL import Image

SIZE = 1009
# Landscape height values are mapped to world Z.
# Your current island looks like the back/mountains are getting submerged,
# so we raise the overall sea level a bit.
# Midpoint 32768 ≈ landscape actor Z. Keep land clearly above mid.
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def sample_height(nx, ny):
    """nx, ny in [-1, 1]. West=-X, South=-Y, NE=back-right mountains, SW=front-left beach."""
    # Organic island edge, slightly shifted NE so SW has more coast
    cx, cy = 0.08, 0.08
    dx, dy = nx - cx, ny - cy
    dist = math.sqrt(dx * dx + dy * dy)

    coast_noise = (
        math.sin(nx * 7.0) * math.cos(ny * 6.0) * 0.05
        + math.sin(nx * 15.0 + ny * 11.0) * 0.025
    )
    island_r = 0.76 + coast_noise

    # Crescent bay bites into SW coast (front-left)
    bay_x, bay_y = -0.52, -0.52
    bay_dist = math.sqrt((nx - bay_x) ** 2 + (ny - bay_y) ** 2)
    bay_bite = smoothstep(0.42, 0.0, bay_dist) * 0.28

    if dist - bay_bite > island_r:
        depth = (dist - bay_bite - island_r) * 5000.0
        return max(0, int(SEA - 2500 - depth))

    land = (island_r - (dist - bay_bite)) / island_r
    land = max(0.0, min(1.0, land))
    land = land ** 0.48

    micro = math.sin(nx * 18.0) * math.cos(ny * 16.0) * 90.0

    # --- SW crescent beach (front-left): flat, low, sandy ---
    if nx < 0.05 and ny < 0.05:
        beach_in = smoothstep(-0.85, -0.15, nx) * smoothstep(-0.85, -0.15, ny)
        shore = smoothstep(0.0, 0.35, land)
        h = SEA + 400 + beach_in * shore * 600 + micro * 0.3
        return int(h)

    # --- NE mountain range (back-right) — strong relief so it reads from the sky ---
    if nx > 0.05 and ny > 0.05:
        mx = smoothstep(0.0, 0.75, (nx - 0.05) / 0.75)
        my = smoothstep(0.0, 0.75, (ny - 0.05) / 0.75)
        m = mx * my
        ridges = abs(math.sin(nx * 11.0 + ny * 7.0)) * 2200.0
        peaks = abs(math.sin(nx * 22.0) * math.cos(ny * 19.0)) * 1600.0
        # Peak spur toward NE tip (pointed mountain nose)
        tip = smoothstep(0.35, 0.95, nx) * smoothstep(0.35, 0.95, ny)
        h = SEA + 1200 + m * land * 18000 + (ridges + peaks) * land + tip * land * 6000
        return int(h)

    # --- Interior: demo-like rolling hills ---
    roll = math.sin(nx * 5.0) * math.cos(ny * 4.5) * 800.0
    valley = smoothstep(-0.2, 0.6, ny) * 1400.0
    h = SEA + 700 + land * (2800 + valley) + roll * land
    return int(h)


def build_heightmap():
    data = np.zeros((SIZE, SIZE), dtype=np.uint16)
    for y in range(SIZE):
        ny = (y / (SIZE - 1)) * 2.0 - 1.0
        for x in range(SIZE):
            nx = (x / (SIZE - 1)) * 2.0 - 1.0
            h = sample_height(nx, ny)
            data[y, x] = max(0, min(65535, h))
    return data


def write_r16(path, data):
    with open(path, "wb") as f:
        f.write(data.astype("<u2").tobytes())


def write_png16(path, data):
    img = Image.fromarray(data, mode="I;16")
    img.save(path)


def write_png_rg8(path, data):
    """UE landscape import expects 16-bit height split across R and G (RGBA8)."""
    hi = (data >> 8).astype(np.uint8)
    lo = (data & 0xFF).astype(np.uint8)
    rgba = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = hi
    rgba[:, :, 1] = lo
    rgba[:, :, 3] = 255
    Image.fromarray(rgba, mode="RGBA").save(path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = build_heightmap()
    r16 = os.path.join(OUT_DIR, "Island_Heightmap_1009.r16")
    png = os.path.join(OUT_DIR, "Island_Heightmap_1009.png")
    png_rg = os.path.join(OUT_DIR, "Island_Heightmap_1009_RG.png")
    write_r16(r16, data)
    write_png16(png, data)
    write_png_rg8(png_rg, data)
    print(f"Wrote {r16} ({data.nbytes} bytes)")
    print(f"Wrote {png}")
    print(f"Wrote {png_rg}")
    print(f"Height range: {data.min()} - {data.max()}")


if __name__ == "__main__":
    main()
