# Isekai Village — building and dungeon systems currently in place

**El Ruhn sky map update, 31 October 2026.** `Map_ElRuhnSky` now uses a player-selected building catalogue. An empty parcel acquires its use when the player confirms a building there. The earlier fixed-plot audit below describes the original world. The sky map, founding buildings, controls, resource costs and construction save are documented in [El Ruhn sky kingdom](WorldDesign/EL_RUHN_SKY_MAP.md).

Reviewed 16 October 2026. This is a reading document, not a new design or a declaration that the systems are finished. It combines the current source code, saved planning data, design documents, and your later directions. No world assets or mechanics were changed for this review.

**Evidence:** “In source” means a behavior exists in the inspected C++ or Python. It does not mean it was playtested today. The dungeon map exists, and the v37 application report records that it was saved. Blueprint-only additions and current in-game behavior have not been exhaustively audited.

## 1. The overall building design

Your intended player settlement grows on El Ruhn, around a permanent fountain and civic square. The player chooses designated sites for the inherited house and Guild Hall; later housing, services and defenses occupy reserved land along roads. The whole eventual settlement must fit the existing island without replacing its terrain.

Your requested growth sequence is **Homestead → Village → Town → Barony → Kingdom**. The current GDD, placement data and runtime still use only **Village → Large Town → Kingdom**. The five-stage sequence has not yet been reconciled with that implementation.

The square should grow into gardens and grand civic space. Commoner and noble homes, church, bank, shop, smith, guild, inn, lord’s residence, academy, storage, training and defenses support growth. Farms sit on flat nearby land, with access to the farmhouse and service lanes between crops.

There are currently three separate foundations for construction:

1. **A settlement planning grid:** where larger buildings may eventually go.
2. **A fixed-plot town prototype:** spend resources at predetermined stakes to mark buildings as built.
3. **A modular piece editor:** place and alter individual structural pieces.

These are not yet one integrated construction system. A building visible in the environment is not automatically a functional player-owned building.

## 2. Settlement grid and building catalogue

The saved El Ruhn plan covers **520 × 530 metres**, using **10-metre cells**. The existing handoff records 2,756 cells, 849 available cells and 29 reserved building plots. The other cells include roads, existing structures, farmland, the square, unsuitable terrain and defense corridors. This is the El Ruhn plan, not a build grid for Gosain.

The Python validator checks building type, era, bounds, footprint, quarter-turn rotation, occupied cells, protected cells, matching reservation and terrain relief. Occupancy can be allocated and released in memory. It is not connected to the runtime plot purchase system or a persistent player construction interface.

| Building | Planned footprint | Earliest data era | Named visual progression in the catalogue |
|---|---:|---|---|
| Commoner house | 20 × 20 m | Village | Timber cottage → stone townhouse → kingdom artisan home |
| General shop | 20 × 20 m | Village | Timber provisioner → stone merchant shop → royal emporium |
| Blacksmith | 30 × 30 m | Village | Village forge → stone smithy → royal foundry |
| Adventurers Guild | 40 × 40 m | Village | Timber guildhall → stone adventurers hall → royal expedition guild |
| Inn | 30 × 30 m | Village | Country inn → town coaching inn → grand inn |
| Chapel/church | 30 × 30 m | Village | Timber chapel → stone church → grand sanctuary |
| Bank/treasury | 30 × 30 m | Large Town | Vault office → town bank → royal treasury |
| Lord’s manor | 40 × 40 m | Large Town | Steward residence → baron manor → ducal residence |
| Noble house | 30 × 30 m | Large Town | Country estate → stone villa → kingdom noble mansion |
| Bathhouse | 30 × 30 m | Large Town | Village bath → stone bathhouse → royal baths |
| Bakery | 20 × 20 m | Village | Timber bakery → town bakery → artisan patisserie |
| Warehouse | 30 × 30 m | Village | Timber barn → stone warehouse → royal storehouse |
| Academy | 40 × 40 m | Large Town | Apprentice lodge → magic academy → royal academy |
| Training ground | 40 × 40 m | Village | Practice yard → training court → royal barracks |
| Bell tower | 20 × 20 m | Large Town | Village bell → stone belfry → civic bell tower |
| Castle | 60 × 60 m | Kingdom | Reserved estate → reserved citadel → Kingdom / Domain+Architect castle |

These variant names are design data, not proof that all those models or upgrades exist. The 29 reservations cover 13 named civic/residential landmark sites, four noble houses and twelve commoner houses. The bakery is among existing protected uses rather than an additional reservation in that count.

The overlay can be shown with `Scripts/toggle_iv_build_grid.py`. It is an editor planning aid, normally hidden. Historical handoffs record five grid tests passing; those tests were not rerun for this documentation review.

## 3. Fixed-plot town building: actual source behavior

`VillageRuntime` seeds **24 records**: ten already-built scenery/service records, eight unbuilt houses, five Large Town buildings and one castle. Plot location and building type are fixed; the player cannot choose any catalogue building for any stake through this system.

Already counted as built: inn, shop, blacksmith, guild, chapel, training yard, warehouse, bakery, farm and old homes. Inn and old homes contribute four beds each. Those scenery records do not receive construction stakes.

Approach an unbuilt stake and use **T**. If the era and resources qualify, construction is immediate: resources are consumed, the built flag is set, Trust rises by 3 (maximum 99), and the stake visual changes. There is no construction-duration or worker-assignment phase in this function.

| Buildable item | Base wood | Iron | Crystal | Beds |
|---|---:|---:|---:|---:|
| Each of eight houses | 8 | 0 | 0 | 2 |
| Bank | 10 | 4 | 0 | 0 |
| Bathhouse | 8 | 3 | 0 | 0 |
| Bell tower | 6 | 2 | 0 | 0 |
| Academy | 12 | 6 | 0 | 0 |
| Manor | 14 | 6 | 0 | 3 |
| Castle | 16 | 8 | 4 | 6 |

Large Town purchases require **Trust 50 and four unlocked sphere nodes**. Kingdom purchases require **Trust 80 and eight unlocked sphere nodes**. The code counts all unlocked nodes, not specifically Domain+Architect nodes. Separate town-era flags use Trust alone, so a town can be labelled Large Town before its purchase gate is met.

The value named “build speed” currently discounts **wood cost**, up to 50%, with rounding and a minimum cost of one. It does not make a timed building process faster. Iron and crystal costs are unchanged.

A built house can receive one loft upgrade for six base wood, discounted by the same rule, adding **one bed**. The GDD’s proposed second floor adds two beds; that differs from current code.

Building an academy and castle can each increase the active party cap, from a baseline of two to up to four. The construction function also updates total bed capacity.

**Visual limitation:** a completed stake becomes a larger colored basic cube. This function does not replace it with a finished house, interior or era-specific building model.

## 4. How buildings affect settlement life

The village’s attraction calculation includes these presence-based bonuses. They are score contributions, not percentages of production or per-building income:

| Buildings present | Effect in the attraction calculation |
|---|---|
| Bakery or farm | Food +0.25, once for either/both |
| Bathhouse | Food +0.10 |
| Inn; any house | Beds score +0.20; +0.15 |
| Training yard; bell tower; castle | Safety +0.15; +0.15; +0.20 |
| Shop; bank; warehouse | Coin score +0.15; +0.20; +0.08 |
| Guild; academy; castle | Purpose +0.20; +0.20; +0.15 |
| Chapel | Faith +0.25 |

Actual bed capacity separately sums beds from built plot records. Multiple houses add beds, but the presence-based house attraction bonus is not multiplied by house count. Other village systems modify these scores using food stock, coin, crime, festivals, strikes and weather.

The broader GDD connects construction to resource gathering, Trust, the Sphere Grid, shops, hospitality, adventurer supplies, defense and weekly hordes. This review does not establish that every part of that larger loop is complete.

## 5. Modular building editor

The player character owns a `BuildEditComponent`. Its source supports:

- Foundation, floor, wall, doorway, stair, roof and pillar pieces.
- Full, half, quarter and L-shaped occupancy.
- Sharp, diagonal and curved outer corners, plus corner offsets.
- A 2-metre placement grid, snapping X, Y and Z; default wall height 2.8 metres.
- Procedural collision on placed pieces.

| Control | Source behavior |
|---|---|
| B | Toggle piece editing |
| Left mouse | Select a hit build piece, or place on another hit surface |
| Right mouse | Delete selected piece; otherwise delete a hit build piece |
| Mouse wheel | Cycle piece type, also modifying a selected piece |
| Q | Cycle occupancy |
| E | Cycle a selected corner’s style, then advance active corner |
| Z / C | Pull active corner inward / outward |

Corner movement is 12 cm per press, limited to 45% of cell size. A yaw-snapping helper exists, but the inspected placement function spawns pieces at zero rotation; this is not a completed rotation tool.

The El Ruhn restriction is currently a height check: entering build mode is blocked below Z = -500 metres. It is not a robust ownership, plot-boundary or region check.

**Missing from the inspected editor:** resource charges, plot-grid validation, overlap/support checks, a full construction catalogue UI, finished materials, ownership, undo/redo, construction jobs and persistent saved buildings. No C++ `SaveGameToSlot`/`LoadGameFromSlot` path was found in the Source search. Blueprint persistence was not verified.

## 6. Rooms gain a function from furnishings

A manually placed `RoomVolume` checks overlapping prop tags every 0.75 seconds. When a recipe matches, it updates its room function and label. It chooses the matching recipe with the most required tags; equal-size matches retain the first matching recipe in the list.

| Furnishings/tags | Recognized function |
|---|---|
| Forge + anvil | Blacksmith |
| Bed + counter | Inn |
| Counter + crate | Shop |
| Desk + board | Adventurers Guild |
| Chest | Treasure room |
| Spawner | Monster den |
| Boss | Boss lair |
| Vault | Vault |

This is a useful foundation for furnishing-based buildings. It does **not** automatically detect an enclosed room from walls, establish a business, hire workers or connect that room to the town plot economy. Props use simple cube-based visuals unless a different mesh is assigned.

The adventurer hub source demonstrates four furnished spaces—guild, shop, inn and smith—and sample editable pieces. Its gate targets the dungeon map. Those spaces are prototype demonstrations rather than finished interiors.

## 7. Dungeon design versus current dungeon

**Design update (supersedes original GDD):** Player dungeon carving (`Dungeon Master`) is out of scope — `Map_ElRuhnDungeon.umap` / `DungeonGraphData` are legacy prototypes, replaced by the living floor-by-floor tower in [Tower floor design](TOWER_FLOOR_DESIGN.md). In [IsekaiVillage_GDD.md](IsekaiVillage_GDD.md), `Architect` merged into `Domain+Architect` (Town Main) and the freed DLC slots are now **Soulsmith** and **Artificer**.

**Historical design note:** Originally, a sealed mountain dungeon threatened the settlement and the GDD proposed a postgame `Dungeon Master` 12-node sphere (3×3 rooms, 1×6 corridors, 5×5 boss room, vault +5% yield, `.sav` sigil sharing).

Those dimensions, bonuses, unlocking and sharing are **GDD proposals**, not implemented features of the current graph generator. The early GDD’s northwest waterfall coordinates are historical; later floating-island documentation places the dungeon on the right/eastern mountain route, separately from the mine and trade pass.

**Existing asset:** `Map_ElRuhnDungeon.umap` is present. `Saved/hub_dungeon_applied_v37.json` records a saved dungeon and adventure-map hub setup. The generator uses an editable graph asset, or creates a default graph in memory at BeginPlay.

### Starter dungeon layout

Entrance → Fork → three branches: Cache, Den and Boss.

| Room | Nominal size | Function |
|---|---:|---|
| Entrance | 9 × 9 m | Arrival/return area |
| Fork | 7 × 7 m | Junction with trap marker |
| Cache | 8 × 8 m | Treasure marker |
| Den | 8 × 8 m | Two monster-spawn markers |
| Boss | 12 × 12 m | Boss and vault markers |

Four halls link these five rooms. Eight markers comprise entrance, exit, trap, treasure, two monster spawns, boss and vault. Both entrance and exit markers currently create return portals to the adventure map, using the `DungeonReturn` start tag.

The generator creates 2-metre floor pieces, perimeter walls and floor strips between room centers. It stores a hall-width field of 2.8 metres, but the hall generation does not use that field; it places half-occupancy floor pieces instead.

### Important dungeon limitations

- Room walls are built continuously; hallway connections do not cut door openings. Traversability needs correction and a playtest.
- Room dimensions are rounded to 2-metre floor counts, while walls use the nominal room size, so alignment is not guaranteed.
- Trap, monster, treasure, boss and vault markers become tagged props. Their labels do not trigger trap damage, monster spawning, loot or a boss encounter in this code.
- Room function data is stored, but the dungeon generator does not create corresponding functional room volumes.
- Calling `BuildFromGraph` again does not clear previously spawned pieces.
- No player-facing graph editor, core-clear unlock, dungeon save/export, multiplayer challenge flow, balancing or dungeon progression is established by these files.

## 8. FFCC reference document

The supplied FFCC master specification describes an Architek building catalogue with housing, castle levels, shops, research, training, magic institutions, gardens, fountains, monuments and civic structures. It connects population, services and adventurer expeditions to settlement growth.

Its building registry and detailed tables remain available in the original document, linked below. Its Elementite costs, Gil economy, named FF classes, dungeon counts and claimed original-game formulas should not be presented as implemented Isekai Village mechanics. This review treats it as the supplied reference document and has not independently verified its claims about the released FFCC game.

## 9. World architecture and the current Gosain work

Gosain’s walls, terrain terraces, roads and placed buildings are environment authoring, distinct from the El Ruhn player construction systems above. Your current Gosain direction is two densely built fortified islands joined by a bridge; thick high perimeter walls; tiered interior ground; castle on the highest layer; interconnected masonry buildings arranged around streets, with deep alleys and crowded growth.

The latest requested wall-gap correction has prepared Gosain44 sources and a baseline audit. At this review, the editor response still records `gosain44-baseline-1`; no Gosain44 applied report was found. **Do not treat the prepared wall-infill pass as already applied or verified.** It remains a separate pending world task.

El Ruhn remains protected from that regional rebuild. Other nations’ architecture is tracked separately in the regional direction and rebuild checklist.

## 10. Decisions and integration still needed

1. Reconcile five requested settlement eras with the three eras in code and data.
2. Unify the large building grid, fixed purchase plots and modular piece editor.
3. Define how selecting the inherited house/Guild site works, rather than relying on fixed seeded plots.
4. Decide whether furnishing-recognized rooms activate services, and connect that to the economy.
5. Resolve Domain+Architect node unlocks, wood discounts versus construction speed, and loft bed counts.
6. Add persistent ownership/building saves and validated placement rules.
7. Replace placeholder completed-building cubes with the appropriate authored models and variants.
8. Legacy dungeon generator (`DungeonGraphData`/`DungeonRuntime`) superseded by floor-by-floor `ATowerExpedition`; keep unused or remove when ready.
9. ~~Postgame dungeon-design unlock and editing/sharing tools~~ — Out of scope; replaced in [IsekaiVillage_GDD.md](IsekaiVillage_GDD.md) by `Soulsmith` and `Artificer` Endgame/DLC discs.

## Source index

- [Current GDD](IsekaiVillage_GDD.md)
- [Supplied FFCC master specification](FFCC_My_Life_as_a_King_Master_Docs/FFCC_My_Life_as_a_King_Master_Specification.md)
- [Settlement catalogue and grid](../Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json)
- [Grid validation](../Scripts/settlement_grid.py)
- [Town construction and settlement effects](../Source/IsekaiVillage/VillageRuntime.cpp)
- [Plot interaction and placeholder appearance](../Source/IsekaiVillage/TownPlot.cpp)
- [Modular editor](../Source/IsekaiVillage/BuildEditComponent.cpp)
- [Structural geometry](../Source/IsekaiVillage/BuildPiece.cpp)
- [Player controls](../Source/IsekaiVillage/IsekaiVillageCharacter.cpp)
- [Room detection](../Source/IsekaiVillage/RoomVolume.cpp)
- [Room recipes](../Source/IsekaiVillage/LinchpinRecipe.cpp)
- [Dungeon graph](../Source/IsekaiVillage/DungeonGraphData.cpp)
- [Dungeon generation](../Source/IsekaiVillage/DungeonRuntime.cpp)
- [Adventurer hub](../Source/IsekaiVillage/AdventurerHub.cpp)
- [Historical settlement planning handoff](WorldDesign/World_Build_Handoff.md)
- [Floating-island handoff and revision links](WorldDesign/Floating_Island_Handoff.md)
- [Regional architecture](WorldDesign/REGIONAL_ARCHITECTURE_DIRECTION.md)
- [World work checklist](WorldDesign/WORLD_REBUILD_CHECKLIST.md)
