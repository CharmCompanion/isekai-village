"""v32: bake Grass / Dirt / Sand / Rock landscape weight layers for El Ruhn.

Reads the current island height (height_valley_v14.npy, metres) and the hand-authored biome mask
(T_IV_Biome_Valley_v14.png: R=path dirt, G=lake bed, B=rock, A=high rock) and writes one 8-bit greyscale
PNG per landscape layer into Saved/AdventureWorldSource/. apply_stylized_landscape_v32.py imports them
as weightmaps so the SoStylized landscape material can blend real grass / dirt / sand / rock the same way
the SoStylized Demonstration map does.

Layer rules (priority Dirt > Sand > Rock > Grass):
* Dirt  - authored routes, the village plaza (r < 18 m), the four farm plots, and a soft forest-floor wash.
* Sand  - beach band around the Grand Sky Lake (water level 18 m) and along the spillway river.
* Rock  - authored rock mask plus steep ground (slope > ~40 deg); the material's AutoCliff adds the rest.
* Grass - whatever remains.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S = Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
WATER_LEVEL = 18.0  # metres, SM_IV_GrandSkyLake plane


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


H = np.load(S / 'height_valley_v14.npy')
X, Y = np.meshgrid(np.linspace(-600, 600, 1009), np.linspace(-600, 600, 1009))
biome = np.asarray(Image.open(S / 'T_IV_Biome_Valley_v14.png')).astype(np.float32) / 255.0
forest = np.asarray(Image.open(S / 'T_IV_ForestFloor_v08.png')).astype(np.float32)
forest = (forest[..., 0] if forest.ndim == 3 else forest) / 255.0

dy, dx = np.gradient(H, 1200 / 1008)
slope = np.hypot(dx, dy)  # rise/run

# --- Dirt -----------------------------------------------------------------------------------------
dirt = smooth(0.12, 0.55, biome[..., 0])
dirt = np.maximum(dirt, 1 - smooth(17.5, 18.5, np.hypot(X, Y)))  # village plaza
for fx, fy in [(110, -145), (146, -145), (110, -181), (146, -181)]:
    plot = (1 - smooth(11.3, 12.2, np.abs(X - fx))) * (1 - smooth(12.3, 13.2, np.abs(Y - fy)))
    dirt = np.maximum(dirt, plot)
dirt = np.maximum(dirt, gaussian_filter(forest, 1.5) * 0.55)  # leaf-litter wash under the woods

# --- Sand -----------------------------------------------------------------------------------------
theta = np.arctan2((Y + 373) / 118, (X + 285) / 207)
edge = 1 + .055 * np.sin(theta * 3) + .025 * np.sin(theta * 7 + .4)
lake_r = np.hypot((X + 285) / 207, (Y + 373) / 118) / edge
near_lake = 1 - smooth(1.18, 1.42, lake_r)
beach = (1 - smooth(WATER_LEVEL + 1.6, WATER_LEVEL + 4.2, H)) * near_lake
rx = -285 + 18 * np.sin((Y + 355) / 55)
river_band = (1 - smooth(10, 19, np.abs(X - rx))) * smooth(-575, -555, Y) * (1 - smooth(-458, -440, Y))
sand = np.maximum(beach, river_band * (1 - smooth(WATER_LEVEL + 1.0, WATER_LEVEL + 3.5, H)))
sand = np.maximum(sand, biome[..., 1] * (1 - smooth(WATER_LEVEL - 2, WATER_LEVEL + 0.5, H)))  # lake bed stays sandy
sand = gaussian_filter(sand, 0.8)

# --- Rock -----------------------------------------------------------------------------------------
rock = np.maximum(biome[..., 2], biome[..., 3])
rock = np.maximum(rock, smooth(0.70, 1.25, slope))
rock = np.maximum(rock, smooth(205, 240, H) * 0.85)  # high alpine shoulders
rock = gaussian_filter(rock, 0.7)
rock *= 1 - (1 - smooth(16.0, 19.5, H)) * near_lake  # never rock on the lake bed / beach

# --- Resolve priorities ---------------------------------------------------------------------------
dirt = np.clip(dirt, 0, 1)
sand = np.clip(sand, 0, 1) * (1 - dirt)
rock = np.clip(rock, 0, 1) * (1 - dirt) * (1 - sand / np.maximum(1 - dirt, 1e-5))
rock = np.clip(rock, 0, 1 - dirt - sand)
grass = np.clip(1 - dirt - sand - rock, 0, 1)

total = dirt + sand + rock + grass
assert np.allclose(total, 1, atol=1e-4), (total.min(), total.max())

for name, w in [('Grass', grass), ('Dirt', dirt), ('Sand', sand), ('Rock', rock)]:
    u8 = np.rint(w * 255).astype(np.uint8)
    Image.fromarray(np.stack([u8, u8, u8, np.full_like(u8, 255)], -1)).save(S / f'T_IV_Layer32_{name}.png')
    print(f'{name:5s} mean {w.mean():.3f}  >50%: {(w > .5).mean() * 100:5.1f}% of island texels')
# Packed RGBA weights (R=Grass G=Dirt B=Sand A=Rock) - this is what the landscape material samples by world
# position, because UE 5.8's Python API cannot add paint target layers to an existing landscape.
packed = np.stack([np.rint(c * 255).astype(np.uint8) for c in (grass, dirt, sand, rock)], -1)
Image.fromarray(packed, 'RGBA').save(S / 'T_IV_Layer32_Weights.png')

# Review composite (not imported): dirt brown, sand yellow, rock grey, grass green.
img = (grass[..., None] * np.array([.36, .66, .26]) + dirt[..., None] * np.array([.46, .33, .20])
       + sand[..., None] * np.array([.90, .84, .56]) + rock[..., None] * np.array([.58, .62, .66]))
Image.fromarray((img * 255).astype(np.uint8)).save(S / 'T_IV_Layer32_Preview.png')
print('wrote', S / 'T_IV_Layer32_*.png')
