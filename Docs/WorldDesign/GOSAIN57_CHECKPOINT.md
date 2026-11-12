# Gosain57 — mountain mine and work yard

Saved in Unreal on 25–26 October 2026. The mine stage is applied and checked. Read `ArtSource/World/Gosain57/applied.json`, `refinement_applied.json`, `contact_fix_applied.json`, `rim_finish_applied.json`, `collision_grid_applied.json` and `native_verification.json`. The latest user direction prioritizes terrain defects and Tales of Zestiria/Berseria visual fidelity: continue with Gosain58 before port construction. Do not replay guarded apply scripts.

## Current scene

Map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.

- Mine site center: (15950, 41900, -20295.545) metres; forward direction (0.759257, -0.650791). This supersedes the old reserved mine coordinate in Gosain50.
- A loading court of roughly 80 × 62 metres joins the existing mountain road. Sorting shelters, benches, carts, timber stocks, supply containers, ore and verge detail reuse Fantastic Village, Advanced Village and SoStylized assets.
- A 68-metre adit has interior rock surfaces, timber supports, six warm lights and a closed gate at the deeper workings. It is a scenic exterior and short accessible passage. Resource extraction, interactive mine management and a deeper dungeon transition are **not implemented**.
- The final covering is a broad, closed rock landform that tapers into the hillside, with partly buried native rock clumps and restrained moss/stone texture. Initial freestanding cliff columns were replaced after native inspection. Two initial ground-overlay actors are retained but hidden through component visibility; terrain material now blends the yard into the surrounding ground.
- The paved strip inside the loading court was removed; six covered route faces changed. Other route faces remain.
- There are 195 mine-tagged actors, including six point lights, two hidden ground-overlay actors and one hidden local ground collider.

## Final assets and sources

- Terrain: `/Game/IsekaiVillage/AdventureWorld/Gosain57/Meshes/SM_IV_Continent_GosainMine57`.
- Mine: `/Game/IsekaiVillage/AdventureWorld/Gosain57/Meshes/SM_Gosain57_MineLandformFinal`.
- Local ground collider: `Gosain57/Meshes/SM_Gosain57_MineGroundCollisionGrid`, 6,655 vertices / 12,960 triangles. Its sampled height deviation is at most 0.461 m overall and 0.117 m in the yard. The main continent actor retains its inherited disabled collision; this local collider does not make the whole world traversable.
- Routes: `/Game/IsekaiVillage/AdventureWorld/Gosain57/Meshes/SM_Gosain57_KingdomRoutesRefined`.
- Private materials: `Gosain57/Materials/M_Gosain57_WeatheredMine` and `M_Gosain57_YardTerrain`. Shared pack materials and global lighting were not edited.
- Sources: `ArtSource/World/Gosain57`. The terrain is still a static mesh, not a native Unreal Landscape.
- Build scripts: `build_gosain_v57_mine_terrain.py`, `build_gosain_v57_mine_detail.py`, `build_gosain_v57_refinement.py`.
- Applied scripts in order: `apply_gosain_v57_mine.py`, `apply_gosain_v57_refinement.py`, `apply_gosain_v57_contact_fix.py`, `apply_gosain_v57_rim_finish.py`, `apply_gosain_v57_collision_grid.py`. They intentionally reject replay after their saved reports exist.
- Review/verification: `render_gosain_v57_mine.py`, `verify_gosain_v57_source.py`, `verify_gosain_v57_native.py`.

## Recovery

The map was backed up at each significant step:

- `Saved/WorldBackups/BeforeGosain57_20261025_232334` — saved Gosain56 before the mine.
- `Saved/WorldBackups/BeforeGosain57Refinement_20261025_233620` — initial mine.
- `Saved/WorldBackups/BeforeGosain57Contact_20261025_234208` — before the final contact/winding correction.
- `Saved/WorldBackups/BeforeGosain57RimFinish_20261025_235634` — before final landform and fitted supports.
- `Saved/WorldBackups/BeforeGosain57CollisionGrid_20261026_045338` — before the optimized local collider.

Earlier meshes/materials and source files remain. Do not delete shared asset packs or replay whole-world generators to recover one site.

## Checks completed

- Terrain: 2,015 original vertices changed; 89,141 local vertices added. All original positions outside 170 metres of the site match Gosain56 exactly. All 270,100 edges involving new vertices have two incident faces.
- Final mine shell: 1,202 welded vertices, 2,400 triangles; all 3,600 edges have two incident faces, consistent winding, finite coordinates and no degenerate faces. Topology closure is not proof that every visual intersection is perfect.
- No existing forest stems occupy the new mine footprint. Native counts remain 30,177 left-island trees and 9,706 right-island trees.
- Editor collision: 13/13 downward sphere sweeps hit the isolated mine ground/landform; seven centerline segments and three entrance lanes are clear; the deeper gate blocks the sweep. Sweeps use a 0.4-metre radius. General world support is not established: the main continent has collision disabled. Runtime movement, navigation and performance remain untested.
- Source locality plus private materials protect El Ruhn, the left island and other regions. This pass does not claim a fresh whole-world playtest or byte-for-byte map comparison.

## Continue in this order

1. Follow Gosain58 terrain repairs and native comparison views first. The final mine yard image is `Docs/WorldDesign/Gosain58_Before/Mine_Yard.png`; older Gosain57 views predate the final rim correction. The landform is grounded better, but its smooth mound and repeated rock treatment still need an art pass. Do not call this final-quality scenery.
2. Build the sheltered port. The old reservation at (20648.928, 41324.713) metres is a survey starting point only. Inspect the current shoreline and height first; make a graded route down to actual water-level quays, then docks, warehouses, customs, fish market and royal landing. Do not put the harbor on top of a high cliff.
3. Refine the knight school, royal houses and compact town/countryside transitions. Rounded town footprints, repeated architecture and abrupt walls are still unfinished.
4. Review remaining road/coastal terrain creases, mountain detail, water treatment, runtime traversal and foliage performance.
5. Other regions remain queued: Yozuan oasis/cliff towns, waterless Kelsin, agricultural/export nation, coastal resort and floating pleasure city. Preserve El Ruhn. Do not resume full-island urban infill.

This is an applied mine environment checkpoint, not a finished-world or AAA-quality certification.
