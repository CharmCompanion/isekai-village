"""Setup ruined village prologue debris, charred timbers, and salvageable rubble around Map_ElRuhnSky."""
from pathlib import Path
import unreal as u

try:
    world = u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
except Exception as ex:
    print(f"Handled load exception: {ex}")
    world = u.EditorLevelLibrary.get_editor_world()

e = u.get_editor_subsystem(u.EditorActorSubsystem)

# Find VillageRuntime to anchor the village coordinates
v = next((a for a in e.get_all_level_actors() if isinstance(a, u.VillageRuntime)), None)
origin = v.get_actor_location() if v else u.Vector(0.0, 0.0, 2000.0)
print(f"VillageRuntime origin: ({origin.x:.1f}, {origin.y:.1f}, {origin.z:.1f})")

# Clean existing prologue debris actors
prefix = "Prologue Debris - "
cleaned = 0
for a in list(e.get_all_level_actors()):
    if a.get_actor_label().startswith(prefix):
        e.destroy_actor(a)
        cleaned += 1
if cleaned > 0:
    print(f"Cleaned {cleaned} previous prologue debris actors.")

def trace_ground_z(x, y, fallback=2200.0):
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
    if h:
        t = h.to_tuple()
        if t[0]:
            return float(t[4].z)
    return float(fallback)

debris_class = u.DebrisActor.static_class()

# Scattered debris clusters around the destroyed village perimeter
debris_specs = [
    # North-East ruined ward
    ("Charred Timber A1", origin.x + 350.0, origin.y + 400.0, u.DebrisType.CHARRED_TIMBER, 25.0),
    ("Charred Timber A2", origin.x + 420.0, origin.y + 380.0, u.DebrisType.CHARRED_TIMBER, -45.0),
    ("Stone Rubble A1",   origin.x + 480.0, origin.y + 450.0, u.DebrisType.STONE_RUBBLE, 10.0),
    ("Ruined Foundation A", origin.x + 550.0, origin.y + 520.0, u.DebrisType.RUINED_STRUCTURE, 0.0),
    
    # South-East workshop ruins
    ("Scrap Metal B1",    origin.x + 300.0, origin.y - 350.0, u.DebrisType.SCRAP_METAL, 60.0),
    ("Stone Rubble B1",   origin.x + 380.0, origin.y - 420.0, u.DebrisType.STONE_RUBBLE, -15.0),
    ("Charred Timber B1", origin.x + 250.0, origin.y - 480.0, u.DebrisType.CHARRED_TIMBER, 80.0),
    ("Ruined Smithy B",   origin.x + 420.0, origin.y - 500.0, u.DebrisType.RUINED_STRUCTURE, 45.0),

    # South-West residential ruins
    ("Stone Rubble C1",   origin.x - 350.0, origin.y - 300.0, u.DebrisType.STONE_RUBBLE, 30.0),
    ("Charred Timber C1", origin.x - 420.0, origin.y - 360.0, u.DebrisType.CHARRED_TIMBER, -70.0),
    ("Scrap Metal C1",    origin.x - 480.0, origin.y - 280.0, u.DebrisType.SCRAP_METAL, 15.0),
    ("Ruined Cottage C",  origin.x - 520.0, origin.y - 400.0, u.DebrisType.RUINED_STRUCTURE, -30.0),

    # North-West watchtower collapse
    ("Ruined Tower D",    origin.x - 400.0, origin.y + 420.0, u.DebrisType.RUINED_STRUCTURE, 15.0),
    ("Stone Rubble D1",   origin.x - 460.0, origin.y + 360.0, u.DebrisType.STONE_RUBBLE, -40.0),
    ("Charred Timber D1", origin.x - 340.0, origin.y + 490.0, u.DebrisType.CHARRED_TIMBER, 55.0),
    ("Scrap Metal D1",    origin.x - 500.0, origin.y + 460.0, u.DebrisType.SCRAP_METAL, 90.0),
]

spawned_count = 0
for name, x, y, dtype, yaw in debris_specs:
    gz = trace_ground_z(x, y, fallback=origin.z)
    loc = u.Vector(x, y, gz + 15.0)
    rot = u.Rotator(0.0, yaw, 0.0)
    actor = e.spawn_actor_from_class(debris_class, loc, rot)
    if actor:
        actor.set_actor_label(f"{prefix}{name}")
        actor.setup_debris(dtype)
        spawned_count += 1

print(f"Spawned {spawned_count} atmospheric prologue debris actors around pristine cottage.")

saved = u.EditorLoadingAndSavingUtils.save_map(world, '/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
print(f"Level save result: {saved}")
