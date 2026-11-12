"""Check land access, road clearance and the protected farm against the source footprints."""
import json
from pathlib import Path
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

out = Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/ElRuhnSky02')
plan = json.loads((out/'village_plan.json').read_text())
farm = box(*plan['farm_reserved_bounds'])
plots = {p['id']:Polygon(p['corners_xy']) for p in plan['plots']}
roads = [(r['name'],LineString(r['points']).buffer(r['width']/2)) for r in plan['roads']]
farm_crossings = [name for name,shape in roads if shape.intersection(farm).area>.01]
lot_crossings = [(name,plot_id) for name,road in roads for plot_id,shape in plots.items() if road.intersection(shape).area>.25]
districts = unary_union([shape for name,shape in roads if not name.endswith(' access')])
orphan_spurs = [name for name,shape in roads if name.endswith(' access') and shape.distance(districts)>.1]
missing_spurs = [plot_id for plot_id in plots if not any(name==plot_id+' access' for name,_ in roads)]
report = {'farm_crossings':farm_crossings,'road_plot_intersections':lot_crossings,'disconnected_access_roads':orphan_spurs,'missing_plot_access':missing_spurs,'unassigned_parcels':plan['purchase_slots']}
(out/'geometry_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
