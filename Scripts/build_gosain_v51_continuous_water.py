"""Continuous water under the graded lake banks; terrain defines visible shoreline."""
from pathlib import Path
from shapely.ops import triangulate
import gosain51_kingdom as k
import build_gosain_v50_towns as g
g.OUT=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain51');water=g.Chunk();boundary=k.LAKE.buffer(220)
for tri in triangulate(boundary):
 if boundary.covers(tri):water.add([[x,y,k.LAKE_LEVEL] for x,y in list(tri.exterior.coords)[:3]],[[0,1,2]],0)
g.write_obj(water,'SM_Gosain51_RoyalLakeContinuous')
