"""Configure Forest, SkyLake, and Whisperwood Mine worker routes, resource stations, and supply sites on Map_ElRuhnSky."""
from pathlib import Path
import heapq
import json
import math
import unreal as u

r = Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
art_dir = r / 'ArtSource/World/ElRuhnSky02'

# Ensure Map_ElRuhnMine's AMineRuntime points back to Map_ElRuhnSky (retiring Map_AnimeAdventure)
mine_world = u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnMine')
me = u.get_editor_subsystem(u.EditorActorSubsystem)
mine_dirty = False
for a in me.get_all_level_actors():
    if isinstance(a, u.MineRuntime):
        if str(a.get_editor_property('return_level')) != '/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky':
            a.modify()
            a.set_editor_property('return_level', '/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
            mine_dirty = True
if mine_dirty:
    assert u.EditorLoadingAndSavingUtils.save_map(mine_world, '/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnMine')

world = u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
e = u.get_editor_subsystem(u.EditorActorSubsystem)
v = next(a for a in e.get_all_level_actors() if isinstance(a, u.VillageRuntime))
routes = json.loads((art_dir / 'golem_street_routes.json').read_text(encoding='utf-8'))
nodes = [u.Vector(float(p[0]), float(p[1]), float(p[2])) for p in routes['nodes_cm']]
edges = [u.IntPoint(int(a), int(b)) for a, b in routes['edges']]
assert nodes

# Clean legacy depot & previous T3 resource markers BEFORE running UE ground/capsule traces
legacy_prefixes = ('Hall supply depot - ', 'Resource Site - ', 'T3 ')
for a in list(e.get_all_level_actors()):
    lbl = a.get_actor_label()
    if any(lbl.startswith(pref) for pref in legacy_prefixes):
        e.destroy_actor(a)

# Permanently destroy decorative plaza cobble cylinder (its 4 cm lip above VillageStreets snags horizontal sweeps)
cobbles_fixed = 0
for a in list(e.get_all_level_actors()):
    if a.get_actor_label() == 'Village plaza cobbles':
        e.destroy_actor(a)
        cobbles_fixed += 1

def ue_z(x_cm, y_cm, fallback_z=2500.0):
    h = u.SystemLibrary.line_trace_single(
        world,
        u.Vector(x_cm, y_cm, 12000.0),
        u.Vector(x_cm, y_cm, 500.0),
        u.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [],
        u.DrawDebugTrace.NONE,
        True,
    )
    if h:
        t = h.to_tuple()
        if t[0]:
            return float(t[4].z)
    return float(fallback_z)

ground_cache = {}

def ue_ground(xm, ym):
    k = (xm, ym)
    if k in ground_cache:
        return ground_cache[k]
    x, y = xm * 100.0, ym * 100.0
    h = u.SystemLibrary.line_trace_single(
        world,
        u.Vector(x, y, 12000.0),
        u.Vector(x, y, 500.0),
        u.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [],
        u.DrawDebugTrace.NONE,
        True,
    )
    val = None
    if h:
        t = h.to_tuple()
        if t[0] and t[6].z >= 0.72 and t[4].z >= 1860.0:
            c = u.SystemLibrary.capsule_trace_single(
                world,
                u.Vector(x, y, t[4].z + 101.0),
                u.Vector(x, y, t[4].z + 102.0),
                35.0,
                97.0,
                u.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False,
                [],
                u.DrawDebugTrace.NONE,
                True,
            )
            if not c or not c.to_tuple()[0]:
                val = (float(t[4].z), float(t[6].z))
    ground_cache[k] = val
    return val

def capsule_clear(ax, ay, az, bx, by, bz):
    c = u.SystemLibrary.capsule_trace_single(
        world,
        u.Vector(ax, ay, az + 101.0),
        u.Vector(bx, by, max(az, bz) + 101.0),
        35.0,
        97.0,
        u.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [],
        u.DrawDebugTrace.NONE,
        True,
    )
    return not c or not c.to_tuple()[0]

def solve_ue(sx, sy, goal_fn, bounds):
    if not ue_ground(sx, sy):
        raise RuntimeError(f'Start ({sx}, {sy}) is not walkable ground in UE')
    pq = [(0.0, sx, sy)]
    cost = {(sx, sy): 0.0}
    prev = {}
    x0, x1, y0, y1 = bounds
    while pq:
        g, cx, cy = heapq.heappop(pq)
        if g > cost.get((cx, cy), 1e18):
            continue
        if goal_fn(cx, cy):
            path = []
            cur = (cx, cy)
            while cur in prev:
                path.append(cur)
                cur = prev[cur]
            path.append(cur)
            path.reverse()
            return path
        cz = ue_ground(cx, cy)[0]
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if nx < x0 or nx > x1 or ny < y0 or ny > y1:
                    continue
                ng = ue_ground(nx, ny)
                if not ng:
                    continue
                sd = math.hypot(dx, dy) * 100.0
                if abs(ng[0] - cz) / sd > 0.35:
                    continue
                if not capsule_clear(cx * 100.0, cy * 100.0, cz, nx * 100.0, ny * 100.0, ng[0]):
                    continue
                nc = g + math.hypot(dx, dy)
                if nc < cost.get((nx, ny), 1e18):
                    cost[(nx, ny)] = nc
                    prev[(nx, ny)] = (cx, cy)
                    heapq.heappush(pq, (nc, nx, ny))
    raise RuntimeError(f'No UE capsule-clear trail from ({sx}, {sy})')

blocked_added_edges = []

def append_ue_trail(sx, sy, goal_fn, bounds):
    anchor_cm = u.Vector(sx * 100.0, sy * 100.0, ue_ground(sx, sy)[0])
    prev_idx = min(
        range(len(nodes)),
        key=lambda i: (nodes[i].x - anchor_cm.x) ** 2 + (nodes[i].y - anchor_cm.y) ** 2,
    )
    path_m = solve_ue(sx, sy, goal_fn, bounds)
    start_idx = 1 if math.hypot(nodes[prev_idx].x - path_m[0][0] * 100.0, nodes[prev_idx].y - path_m[0][1] * 100.0) < 25.0 else 0
    for ax, ay in path_m[start_idx:]:
        px_prev, py_prev = nodes[prev_idx].x / 100.0, nodes[prev_idx].y / 100.0
        pz_prev = ue_z(nodes[prev_idx].x, nodes[prev_idx].y, nodes[prev_idx].z)
        dist_m = math.hypot(ax - px_prev, ay - py_prev)
        steps = max(1, math.ceil(dist_m / 1.4))
        az = ue_ground(ax, ay)[0]
        for s in range(1, steps + 1):
            t = s / steps
            mx = px_prev + (ax - px_prev) * t
            my = py_prev + (ay - py_prev) * t
            mz = ue_z(mx * 100.0, my * 100.0, pz_prev + (az - pz_prev) * t)
            prev_z = ue_z(nodes[prev_idx].x, nodes[prev_idx].y, nodes[prev_idx].z)
            if not capsule_clear(nodes[prev_idx].x, nodes[prev_idx].y, prev_z, mx * 100.0, my * 100.0, mz):
                blocked_added_edges.append((prev_idx, len(nodes)))
            idx = len(nodes)
            nodes.append(u.Vector(mx * 100.0, my * 100.0, mz))
            edges.append(u.IntPoint(prev_idx, idx))
            prev_idx = idx
    return prev_idx, nodes[prev_idx]

# Extend street network from real unobstructed district exits & dock using UE line + capsule traces
forest_idx, forest_pt = append_ue_trail(
    -254, 20, lambda x, y: x <= -268 and 10 <= y <= 30, (-290, -240, -10, 50)
)
lake_idx, lake_pt = append_ue_trail(
    2, -230, lambda x, y: x < -60 and y < -250 and 1870.0 <= ue_ground(x, y)[0] <= 2200.0, (-200, 30, -350, -180)
)
mine_idx, mine_pt = append_ue_trail(
    -126, 240, lambda x, y: math.hypot(x - (-308), y - 279) <= 6.0, (-340, -110, 210, 320)
)
assert not blocked_added_edges, f'Blocked trail edges detected: {blocked_added_edges}'

v.modify()
v.set_editor_property('street_nodes', nodes)
v.set_editor_property('street_edges', edges)

targets = [
    ('Stone', 'Whisperwood Mine', 'Whisperwood Mine Quarry', mine_pt),
    ('Fish', 'SkyLake Pier', 'SkyLake Fishing Pier', lake_pt),
    ('Wood', 'Whispering Forest', 'Whispering Forest Lumber Camp', forest_pt),
]

sites = []
report = {
    'success': False,
    'cobbles_disabled': cobbles_fixed,
    'street_nodes': len(nodes),
    'street_edges': len(edges),
    'trail_endpoints': {
        'forest': [round(forest_pt.x, 1), round(forest_pt.y, 1), round(forest_pt.z, 1)],
        'lake': [round(lake_pt.x, 1), round(lake_pt.y, 1), round(lake_pt.z, 1)],
        'mine': [round(mine_pt.x, 1), round(mine_pt.y, 1), round(mine_pt.z, 1)],
    },
    'sites': [],
}
for item, tag, marker_text, pos in targets:
    site = u.VillageSupplySite()
    site.set_editor_property('item', item)
    site.set_editor_property('site_tag', tag)
    site.set_editor_property('location', pos)
    site.set_editor_property('stock', 60)
    site.set_editor_property('daily_restock', 60)
    sites.append(site)

    marker = e.spawn_actor_from_class(u.TextRenderActor, pos + u.Vector(0, 0, 210))
    marker.set_actor_label('Resource Site - ' + tag)
    marker.set_folder_path('Village/Resource Sites')
    c = marker.get_component_by_class(u.TextRenderComponent)
    c.set_text(u.Text(f'{marker_text} ({item})'))
    c.set_world_size(45)
    c.set_text_render_color(u.Color(180, 220, 255, 255))
    report['sites'].append({'item': item, 'tag': tag, 'location': list(pos.to_tuple()), 'stock': 60})

v.modify()
v.set_editor_property('supply_sites', sites)

# Spawn interactive Lake Fishing Spots (SkyLake Pier & Veil Falls Pool) on traced UE ground
# Offset SkyLake spot 450cm south of lake_pt so its InteractSphere (r=260) does not overlap the supply site goal
for label, x, y, fallback_z, title in [
    ('T3 SkyLake Fishing Spot', lake_pt.x - 300.0, lake_pt.y - 450.0, lake_pt.z, 'SkyLake Fishing Pier'),
    ('T3 Veil Falls Fishing Spot', -34900.0, 26300.0, 7580.0, 'Veil Falls Spring Pool'),
]:
    sz = ue_z(x, y, fallback_z)
    spot = e.spawn_actor_from_class(u.LakeFishingSpot, u.Vector(x, y, sz + 10.0))
    spot.set_actor_label(label)
    spot.set_folder_path('Village/Resource Sites')
    spot.set_editor_property('spot_title', title)

# Spawn respawning world Ore Veins at Whisperwood Mine Quarry on traced UE ground
for label, x, y, ore, lvl in [
    ('T3 Whisperwood Copper Vein', mine_pt.x - 250.0, mine_pt.y + 150.0, 'Copper', 1),
    ('T3 Whisperwood Iron Vein', mine_pt.x - 480.0, mine_pt.y + 260.0, 'Iron', 2),
]:
    vz = ue_z(x, y, mine_pt.z)
    vein = e.spawn_actor_from_class(u.MineOreVein, u.Vector(x, y, vz + 15.0))
    vein.set_actor_label(label)
    vein.set_folder_path('Village/Resource Sites')
    vein.set_editor_property('ore_id', ore)
    vein.set_editor_property('required_level', lvl)
    vein.set_editor_property('respawn_seconds', 45.0)

# Ensure MineReturn PlayerStart exists in Map_ElRuhnSky for clean return from Map_ElRuhnMine
has_mine_return = any(
    isinstance(a, u.PlayerStart) and str(a.get_editor_property('player_start_tag')) == 'MineReturn'
    for a in e.get_all_level_actors()
)
if not has_mine_return:
    mz = ue_z(-32800.0, 28600.0, 6811.0)
    ps = e.spawn_actor_from_class(u.PlayerStart, u.Vector(-32800.0, 28600.0, mz + 105.0))
    ps.set_actor_label('T3 Mine Return Start')
    ps.set_folder_path('Adventure/Hubs')
    ps.set_editor_property('player_start_tag', 'MineReturn')

# Ensure a DayBoard sits cleanly on the civic plaza terrace (away from Shop/Smith/Service plots)
if not any(isinstance(a, u.DayBoard) for a in e.get_all_level_actors()):
    db_z = ue_z(550.0, -6800.0, 2511.3)
    db = e.spawn_actor_from_class(u.DayBoard, u.Vector(550.0, -6800.0, db_z + 5.0))
    db.set_actor_label('T3 Village Day Board')
    db.set_folder_path('Village/Resource Sites')

plots = list(v.authored_plots)
for plot in plots:
    if str(plot.id) == 'ExistingFarm':
        plot.set_editor_property('scenery', True)
        target = plot.location + u.Vector(-4000, 0, 0)
        node = min(nodes, key=lambda p: (p.x - target.x) ** 2 + (p.y - target.y) ** 2)
        plot.set_editor_property('stake_offset', node - plot.location)
v.set_editor_property('authored_plots', plots)

assert u.EditorLoadingAndSavingUtils.save_map(world, '/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
report['success'] = True
(r / 'Saved/golem_hall_setup.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('T3_SETUP_HALLLOCATIONS_OK')
