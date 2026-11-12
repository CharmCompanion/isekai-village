"""Measure city grounding against the exported terrain triangles, not the design function."""
import json,numpy as np
from scipy.spatial import cKDTree
import gosain37_geometry as g
d=json.loads((g.OUT/'Gosain37.json').read_text());surf=np.load(g.OUT/'terrace_surface.npz')
g.TRI=surf['vertices'][surf['triangles']];g.TREE=cKDTree(g.TRI[:,:,:2].mean(axis=1))
points=[]
for line in (g.OUT/'SM_Gosain37_CityStreets.obj').open():
    if line.startswith('v '):
        x,y,z=map(float,line.split()[1:]);points.append(np.array([x/100,-y/100,z/100])+d['origin_m'])
p=np.array(points);h=g.original_ground_many(p[:,:2]);delta=p[:,2]-h
houses=np.array(d['instances']['HouseA']+d['instances']['HouseB']);ground=g.original_ground_many(houses[:,:2]);gap=houses[:,2]-ground
report={'road_vertices':len(p),'road_clearance_m_min':float(delta.min()),'road_clearance_m_max':float(delta.max()),'road_vertices_buried_more_than_2cm':int((delta<-.02).sum()),'road_vertices_over_30cm':int((delta>.3).sum()),'houses':len(houses),'house_origin_above_terrain_m_min':float(gap.min()),'house_origin_above_terrain_m_max':float(gap.max()),'terrain':json.loads((g.OUT/'terrain_report.json').read_text())}
(g.OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if (delta<-.02).any():
    np.savez_compressed(g.OUT/'road_clearance_corrections.npz',vertices=p,ground=h)
