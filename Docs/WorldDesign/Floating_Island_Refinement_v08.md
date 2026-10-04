> Underside updated: see [Organic_Underside_v09.md](Organic_Underside_v09.md). Other v08 environment changes remain current.

# Floating island refinement v08 — 28 September 2026

Open `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.

This pass follows the latest floating-island direction. The earlier beach/ocean continent layout is historical. The permanent plaza, village layout, level farm, building reservations, mine/dungeon/trade approaches and airship landing remain in place.

## Changes saved in the map

- Replaced the visible blob clouds with the existing **SoStylized illustrated cloud dome** and 32 textured cloud banks using **StylizedIsland's animated cloud-card assets**. The original 48 blobs are retained under `Archived/Blob Clouds`, with component visibility and collision disabled.
- Added **306 SoStylized cliff/spire pieces** around the existing continuous underside: broken layers, inverted rock fangs and asymmetric lower shards. The core still closes the island; the reused rocks provide its visible surface depth. A project-owned rock material keeps the shaded underside readable.
- Added a **70 km distant continental backdrop**, roughly 5.3–7.4 km below the island, with irregular mountain ridges, forest/plain colour variation and a winding river. This is distant scenery, with collision disabled, rather than an additional playable region.
- Enlarged the southwest lake from approximately 146 × 118 m to **414 × 236 m**, with an irregular shoreline, a native Landscape basin, raised outer hills and the retained outlet/waterfall. Water remains at 18 m. The main basin is approximately 10–12 m high.
- Added gentle foothill variation outside the protected settlement and authored road surfaces. Revised terrain rock/snow coverage, matched the existing outcrop colours, and added moss to upward-facing ground-rock surfaces.
- Added **4,006 trees/saplings**, **15,044 other foliage/detail instances**, and **57,167 additional grass tufts**. These reuse SoStylized oaks, pines, ferns, shrubs, daisies, foxtails, rocks, fallen oak logs, branches and stumps. A woodland ground mask blends soil into forest areas.
- Dense trees remain outside the full future settlement rectangle, with clearance around roads and farm buildings/fields. Small meadow plants can occupy future building land and will need clearing by future construction gameplay.
- Grass has a 120 m cull distance; other ground plants use shorter ranges than major trees and rock forms. These are authoring choices, not a packaged performance certification.

## Validation and recovery

- **194,902 native height samples** inside X[-220,300], Y[-230,300] metres are exactly unchanged from v07.
- **16 native WorldStatic collision samples passed**, covering farm, plaza, lake floor, woodland routes, dock approach and the removed rectangular perimeter.
- **5 settlement-grid unit tests passed**. No new tree origins occupy the protected building grid.
- Map and generated materials/assets saved. Original asset packs and original project maps were not overwritten.
- Pre-pass recovery copy: `Saved/WorldBackups/BeforeRefinement_v08_20260928/AdventureWorld/` and its companion `AdventureWorldSource/`.
- Validation records: `Saved/refinement_validation.json`, `refinement_source_validation.json`, `refined_render_review.json`, `refinement_foliage_result.json`, `meadow_carpet_result.json`.

## Review images

The six `Refined_*.png` files beside this document are actual Unreal renders: whole-island overview, layout, lake, woodland road, altitude/underside and village. Older `Floating_*` images show the previous pass.

## Authoring sources

Current native terrain: `Saved/AdventureWorldSource/height_refined_v08.npy`, `IV_Refined_v08.r16`, `T_IV_RefinedHeight_RG.png`, `T_IV_Biome_Refined_v08.png`. Existing v07 visibility mask still applies. Generated water and background meshes are under `AdventureWorld/Meshes/Refinement`; material changes are project-owned under `AdventureWorld/Materials`.

The `Scripts/*refinement*`, `build_refinement_v08.py`, `blend_mountain_rock_palette.py`, and `add_meadow_carpet.py` scripts document the authoring sequence. They are targeted authoring tools, not a single safe full-world rebuild command. Do not rerun the original world generator or `apply_refinement_v08.py` indiscriminately: it replaces actors with the IVRefine08 tag, and later refinements must then be reapplied. Foliage refreshes must take care when multiple foliage types reuse the same source mesh.

## Production limits

This is an environment art refinement, not a claim of a finalized AAA release. Remaining work includes full character traversal and foliage collision review, navigation/edge-fall recovery, water interaction, packaged frame-time/memory profiling, cloud-card appearance from unrestricted flight angles, further close-range material/lighting polish, and the settlement/era/gameplay systems described in the master design. The distant continent is intentionally a non-playable backdrop. The village remains expandable rather than prefilled with final-era buildings.

