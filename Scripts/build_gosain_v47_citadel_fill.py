"""Summit palace blocks for the empty citadel platform. Sources only."""
import sys
from pathlib import Path
import math
import numpy as np
import shapely
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gosain44_terraces as terraces
from build_gosain_v47_packed_city import Chunk, building, write_obj, MATS

OUT = Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain47')
center = terraces.CASTLE_CENTER
top = terraces.SEA + 224.0
court = terraces.CASTLE.buffer(-28)
chunk = Chunk()
count = 0
minx, miny, maxx, maxy = court.bounds
y = miny + 16
row = 0
while y < maxy - 16:
    x = minx + 18
    col = 0
    while x < maxx - 18:
        w = 22 + ((row * 3 + col) % 5) * 2
        d = 18 + ((row + col * 2) % 4) * 2
        px, py = x + w / 2, y + d / 2
        if court.covers(Point(px, py).buffer(max(w, d) / 2)) and math.hypot(px - center[0], py - center[1]) > 115:
            storeys = 6 + ((row + col) % 4)
            building(chunk, np.array([px, py]), (w - 0.4, d - 0.4), 0.0, top - 0.3, storeys, (row + col) % 4, 15)
            count += 1
        x += w + 4.5
        col += 1
    y += 24 + (row % 3)
    row += 1
info = write_obj(chunk, 'SM_Gosain47_CitadelDistrict')
print('citadel buildings', count, info)
