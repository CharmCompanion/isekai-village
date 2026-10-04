"""
Island heightmap v6 — curved BACK-EDGE mountain range (not a butte).

- Ridge follows northern/NE rim of the island (crescent massif)
- Soft foothills inward; no single Gaussian pillar
- Cave tunnel carved into south face of range
- Desert shelf + cliff face on SE of range
- Rolling south meadows (kill big flat rectangle)
- Lake + SW beach + satellites kept
"""
import math
import os

import numpy as np
from PIL import Image

SIZE = 1009
SEA = 32768
OUT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"

LAKE_CX, LAKE_CY, LAKE_R = 0.08, 0.08, 0.10
LAKE_RIM = SEA + 850
LAKE_FLOOR = SEA - 1500

# Cave mouth (south face of range) → tunnel deeper into mountain
CAVE_MX, CAVE_MY = 0.42, 0.38
CAVE_DIR_X, CAVE_DIR_Y = 0.55, 0.65  # into the ridge
CAVE_LEN = 0.18
CAVE_WIDTH = 0.045

SATELLITES = [
    (-0.82, 0.55, 0.055),
    (0.90, -0.15, 0.048),
    (-0.25, -0.86, 0.042),
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
    coast = math.sin(nx * 6.5) * math.cos(ny * 5.5) * 0.045 + math.sin(nx * 13 + ny * 9) * 0.022
    r = 0.78 + coast
    bay = smoothstep(0.40, 0.0, math.sqrt((nx + 0.50) ** 2 + (ny + 0.50) ** 2)) * 0.28
    outside = (dist - bay) > r
    land = max(0.0, min(1.0, (r - (dist - bay)) / r)) ** 0.42
    return outside, land, dist, bay, r, cx, cy


def satellite(nx, ny):
    best = 0.0
    for sx, sy, sr in SATELLITES:
        d = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if d < sr:
            best = max(best, (1.0 - d / sr) ** 0.55)
    return best


def mountain_arc(nx, ny, land, dist, cx, cy):
    """
    Crescent range along the BACK (north→NE→east) rim.
    Uses polar angle + radial band — NOT a circular Gaussian butte.
    """
    ang = math.atan2(nx - cx, ny - cy)  # 0 = +Y (north), + = toward east
    # Arc covering back edge: roughly NW through N to ESE
    along = smoothstep(-1.35, -0.35, ang) * smoothstep(1.55, 0.55, ang)
    along = along ** 0.85

    # Primary ridgeline near outer coast
    ridge_r = 0.60
    radial = dist - ridge_r
    # Asymmetric: steeper ocean face, gentler inland slopes
    if radial > 0:
        across = math.exp(-(radial ** 2) / 0.012)  # sharp ocean cliff face
    else:
        across = math.exp(-(radial ** 2) / 0.038)  # wider inland slope

    # Lower parallel foothill ridge inward
    foot = math.exp(-((dist - 0.42) ** 2) / 0.05) * 0.40

    # Height variation along arc (multiple peaks, not one pillar)
    along_var = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(ang * 5.5 + 0.8))
    along_var += 0.25 * (0.5 + 0.5 * math.sin(ang * 11.0))

    m = along * across * land * along_var
    h = m * 26000.0
    h += along * foot * land * 9000.0

    # Small spur peaks along ridge (elongated along arc, not round buttes)
    for a0, amp, sig_r, sig_a in (
        (0.15, 9000.0, 0.04, 0.18),
        (0.55, 11000.0, 0.035, 0.15),
        (0.95, 8500.0, 0.04, 0.16),
        (1.25, 7000.0, 0.045, 0.14),
    ):
        da = ang - a0
        peak = math.exp(-(da ** 2) / (sig_a ** 2)) * math.exp(-((dist - ridge_r) ** 2) / (sig_r ** 2))
        h += peak * amp * land

    return SEA + 1600 + h


def desert_shelf(nx, ny, land, dist, cx, cy):
    """Sandy shelf / mesa approach SE of the range."""
    ang = math.atan2(nx - cx, ny - cy)
    # SE quadrant of back range
    w = smoothstep(0.6, 1.1, ang) * smoothstep(1.7, 1.2, ang)
    band = math.exp(-((dist - 0.48) ** 2) / 0.035)
    return (SEA + 2200 + band * w * land * 5500.0), w * band


def carve_cave(nx, ny, h):
    """Lower a tunnel from cave mouth into the mountain."""
    # Project point onto cave axis
    dx = nx - CAVE_MX
    dy = ny - CAVE_MY
    axis_len = math.sqrt(CAVE_DIR_X ** 2 + CAVE_DIR_Y ** 2)
    ux, uy = CAVE_DIR_X / axis_len, CAVE_DIR_Y / axis_len
    t = dx * ux + dy * uy  # distance along axis
    if t < -0.02 or t > CAVE_LEN:
        return h
    px = dx - t * ux
    py = dy - t * uy
    lateral = math.sqrt(px * px + py * py)
    if lateral > CAVE_WIDTH * (1.0 + t * 0.5):
        return h
    # Depth increases deeper into mountain; mouth is open
    depth = smoothstep(0.0, CAVE_LEN * 0.85, t) * 5500.0 + 1200.0
    mouth = smoothstep(CAVE_WIDTH, 0.0, lateral)
    return h - depth * mouth


def sample(nx, ny):
    outside, land, dist, bay, r, cx, cy = island_mask(nx, ny)
    sat = satellite(nx, ny)
    if outside and sat <= 0:
        return max(0, int(SEA - 2800 - max(0.0, dist - bay - 0.78) * 5500.0))
    if sat > 0 and outside:
        return int(SEA + 400 + sat * 2400 + fbm(nx, ny, 3) * 180)

    micro = fbm(nx, ny, 4) * 240

    # Base rolling land — south gets stronger rolls to kill flat rectangle
    south = smoothstep(0.25, -0.7, ny)
    roll = math.sin(nx * 5.5) * math.cos(ny * 4.2) * (900 + south * 1100)
    roll2 = math.sin(nx * 11.0 + ny * 7.0) * 350 * south
    base = SEA + 700 + land * (2200 + south * 800) + roll * land + roll2 + micro * 0.45

    # Beach SW
    beach_w = smoothstep(0.10, -0.40, nx) * smoothstep(0.10, -0.40, ny)
    beach_h = SEA + 220 + land * 450 + micro * 0.15

    # Curved mountain arc
    mtn_h = mountain_arc(nx, ny, land, dist, cx, cy)
    ang = math.atan2(nx - cx, ny - cy)
    mtn_w = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang)
    mtn_w *= smoothstep(0.28, 0.50, dist)  # only outer/back half

    desert_h, desert_w = desert_shelf(nx, ny, land, dist, cx, cy)

    # Blend
    h = base
    h = h * (1.0 - beach_w) + beach_h * beach_w
    # mountain overrides strongly along arc
    mw = (mtn_w ** 0.7) * land
    h = h * (1.0 - mw) + mtn_h * mw
    # desert shelf soft mix
    dw = desert_w * land * 0.65
    h = h * (1.0 - dw) + desert_h * dw

    # Lake
    lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
    if lake_d < LAKE_R:
        edge = smoothstep(LAKE_R, 0.0, lake_d)
        lake_h = LAKE_FLOOR + (LAKE_RIM - LAKE_FLOOR) * ((1.0 - edge) ** 1.35)
        blend = smoothstep(LAKE_R, LAKE_R * 0.5, lake_d)
        h = h * (1.0 - blend) + lake_h * blend

    # Cave carve (after mountain so it cuts into rock)
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

    # Mild lowland blur only
    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64)
    kernel /= kernel.sum()
    blur = data.copy()
    for _ in range(2):
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 1, blur)
        blur = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="same"), 0, blur)

    for yi, ny in enumerate(ys):
        for xi, nx in enumerate(xs):
            _, _, dist, _, _, cx, cy = island_mask(nx, ny)
            ang = math.atan2(nx - cx, ny - cy)
            mtn = smoothstep(-1.4, -0.2, ang) * smoothstep(1.6, 0.4, ang) * smoothstep(0.28, 0.50, dist)
            lake_d = math.sqrt((nx - LAKE_CX) ** 2 + (ny - LAKE_CY) ** 2)
            if lake_d < LAKE_R * 0.9 or mtn > 0.45:
                continue
            data[yi, xi] = 0.5 * data[yi, xi] + 0.5 * blur[yi, xi]

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
    print(f"Wrote {base}.* {data.min()}..{data.max()}")
    print(f"SW {data[:mid,:mid].max()} NE {data[mid:,mid:].max()}")
    # sample cave mouth vs peak along ridge
    ix = int((CAVE_MX + 1) * 0.5 * (SIZE - 1))
    iy = int((CAVE_MY + 1) * 0.5 * (SIZE - 1))
    print(f"Cave mouth height {data[iy, ix]}")


if __name__ == "__main__":
    write_outputs(build())
