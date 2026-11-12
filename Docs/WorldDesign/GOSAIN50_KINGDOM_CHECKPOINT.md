# Gosain50 — forest kingdom conversion

User direction received 20 October 2026; work continued 21 October. This supersedes the full-island urban coverage in GOSAIN_APPROVED_TARGET.md and passes 47–49. The architectural palette remains approved; covering the entire islands with buildings is rejected.

## Revised layout

- Left/capital island: exactly 65% of its 34.545 km² enclosed outline allocated to a royal forest-and-lake zone (22.454 km²). This is land allocation, not a claim of exactly 65% canopy coverage.
- A 1.152 km² lake basin is inside that zone, with a level surface and a feathered shoreline. About 33,028 varied mature-tree instances leave lake margins, roads and occasional glades open.
- Castle town: 6 km², retaining the existing citadel, with a reserved royal-house precinct and exterior residences.
- Right/tower town: the same 6 km² footprint, preserving the existing giant magic tower. Knight-school compound includes wings around a parade/training court and a lower stable-like wing. These are exterior layout buildings, not finished interiors or functioning institutions.
- Behind the tower town: a mountain ridge on the actual terrain mesh, reaching approximately 544.5 m above the sea in the generated samples. Mining access runs toward its lower slope.
- The previous full-island flattened ground outside the towns becomes gently rolling countryside. Town terrain and the bridge abutments remain at their saved levels.
- New local town wall circuits replace the continuous coastline-wall presentation. Old defenses and older town overlays are hidden through their components, not deleted. The bridge stays.
- Port and mine locations are recorded in `ArtSource/World/Gosain50/kingdom.json`. Detailed harbor grading/docks and an actual mine entrance/interior are NOT yet built.

## Assets and evidence

Implementation: `Scripts/gosain50_kingdom.py`, `build_gosain_v50_terrain.py`, `build_gosain_v50_towns.py`, `build_gosain_v50_landscape.py`, `apply_gosain_v50_kingdom.py`.

Sources: `ArtSource/World/Gosain50/`. Map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.

Source validation confirms topology and horizontal coordinates retained, 102,221 terrain vertices changed, and every vertex outside the Gosain island polygons unchanged. Town generator leaves the regional approach corridors clear; 6,723 left-town and 8,353 right-town buildings are generated. Equal town area does not mean identical building counts, because the castle reserve occupies part of the left town.

Inspect `applied.json` and native views before claiming completion. The first apply attempt imported assets but stopped before level mutation on a material-expression API mismatch; the corrected second attempt reuses those imported assets. Do not rerun after `applied.json` exists.

## Remaining work, in order

1. Confirm saved application, unchanged unrelated actors/foliage and native views of both islands, lake, forest, mountain, school and tower.
2. Review the city/forest transition, wall shape and new route grades. The present towns use rounded planning footprints; final streets and defenses should be shaped to terrain and district history rather than left as perfect arcs.
3. Engineer a sheltered port with a genuinely graded route to water-level quays, docks, warehouses, customs, fish market and royal landing. Do not place a high-level dock on top of the old coastal cliff.
4. Build the mine entrance into the slope, with work yard, spoil, supports, route and interior/transition as appropriate.
5. Refine the knight school, royal houses, gardens, foresters' lodge and rural estates with complete native assets and architectural detail. Finish ramps and actual city entrances.
6. Audit navigation, collision, road crossings, foliage density/performance, shore detail and all-angle composition. No finished-game or final AAA claim.

Preserve El Ruhn and other regions. Keep recoverable source/assets and map backups. Do not resume whole-island infill or replay older world generators.
