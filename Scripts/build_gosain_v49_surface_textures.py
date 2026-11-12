"""Tileable plaster-damage and ivy maps for the Gosain palazzi. No editor work."""
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain49')
OUT.mkdir(parents=True, exist_ok=True)


def tile_noise(n, cells, seed):
    grid = np.random.default_rng(seed).random((cells + 1, cells + 1))
    grid[-1, :] = grid[0, :]
    grid[:, -1] = grid[:, 0]
    xs = np.linspace(0, cells, n, endpoint=False)
    ys = np.linspace(0, cells, n, endpoint=False)
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
    xf = xs - x0
    yf = ys - y0
    xf = xf * xf * (3 - 2 * xf)
    yf = yf * yf * (3 - 2 * yf)
    x0g, y0g = np.meshgrid(x0, y0)
    xf, yf = np.meshgrid(xf, yf)
    n00 = grid[y0g, x0g]
    n10 = grid[y0g, x0g + 1]
    n01 = grid[y0g + 1, x0g]
    n11 = grid[y0g + 1, x0g + 1]
    return n00 * (1 - xf) * (1 - yf) + n10 * xf * (1 - yf) + n01 * (1 - xf) * yf + n11 * xf * yf


def plaster_break():
    broad = tile_noise(1024, 4, 49)
    chips = tile_noise(1024, 9, 50)
    # Mostly intact plaster. Bright islands are the broken patches.
    mask = np.clip((broad - 0.52) * 3.2, 0, 1)
    mask = np.maximum(mask, np.clip((chips - 0.78) * 5.0, 0, 1))
    image = Image.fromarray((mask * 255).astype(np.uint8), 'L')
    path = OUT / 'T_Gosain49_Break.png'
    image.save(path)
    print(path, 'mean', round(float(mask.mean()), 3))


def splat(rgba, cx, cy, rx, ry, ang, rgb, alpha):
    n = rgba.shape[0]
    rad = int(max(rx, ry) + 2)
    c, s = np.cos(ang), np.sin(ang)
    yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
    lx = xx * c + yy * s
    ly = -xx * s + yy * c
    cover = 1 - ((lx / rx) ** 2 + (ly / ry) ** 2)
    keep = cover > 0
    px = (np.rint(cx).astype(np.int32) + xx[keep]) % n
    py = (np.rint(cy).astype(np.int32) + yy[keep]) % n
    cov = (alpha * np.clip(cover[keep], 0, 1) ** 0.55).astype(np.float32)
    stronger = cov > rgba[py, px, 3]
    rgba[py[stronger], px[stronger], 0] = rgb[0]
    rgba[py[stronger], px[stronger], 1] = rgb[1]
    rgba[py[stronger], px[stronger], 2] = rgb[2]
    rgba[py[stronger], px[stronger], 3] = cov[stronger]


def ivy():
    n = 1024
    rgba = np.zeros((n, n, 4), np.float32)
    rng = np.random.default_rng(49)
    greens = [(22, 78, 28), (14, 58, 22), (38, 104, 36), (18, 70, 24)]
    for v in range(7):
        x = (v + 0.35) * n / 7 + rng.uniform(-20, 20)
        y = rng.uniform(0, 80)
        phase = rng.uniform(0, 6)
        color = greens[v % len(greens)]
        for i in range(90):
            y += 12.5
            x += 18 * np.sin(i * 0.28 + phase)
            splat(rgba, x, y, 7.0, 5.0, 0, color, 0.98)
            if i % 2 == 0:
                side = 1 if (i // 2) % 2 == 0 else -1
                ang = side * (0.7 + 0.2 * np.sin(i))
                ox = 28 * np.cos(ang + phase)
                oy = 8 * np.sin(ang)
                leaf = greens[(v + i) % len(greens)]
                splat(rgba, x + ox, y + oy, 36, 18, ang, leaf, 0.95)
                splat(rgba, x - ox * 0.7, y + 10, 28, 14, ang + 0.9, leaf, 0.92)
    image = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    path = OUT / 'T_Gosain49_Ivy.png'
    image.save(path)
    print(path, 'coverage', round(float((rgba[:, :, 3] > 0.2).mean()), 3))


if __name__ == '__main__':
    plaster_break()
    ivy()
