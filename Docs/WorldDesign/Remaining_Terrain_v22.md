# Current continuation — remaining mainland terrain v22

Project: D:/DEVELOPMENT/Games/IsekaiVillage/IsekaiVillage.uproject
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
Date: 29 September 2026.

## Latest user direction
The hollow must belong to the same terrain as the island, with leftover mountains, forest and hills at ground level. It must not look like a standalone crater in a clearing. The island and cavity must still fit like puzzle pieces. Lower-world settlements are only implied; no literal lower-world houses or farm grids. Hide the outer continent edge in distance/haze. River must follow a coherent valley rather than cut through raised mountain geometry.

## Current saved work
v22 extends mainland terrain around the unchanged v21 matching cavity. Six connected remnant terrain branches continue north/northwest/west/east from the cut, with lower southern hills. Ridge slopes were broadened and lowered after reviewing an overly wall-like first render. Native SoStylized spire rocks dress the crests, and denser full-height native woodland reaches near the cut. Forest size/density tapers toward the older distant dressing. The cleared ring is removed.

Current mainland mesh: SM_IV_PuzzleContinent_v22. Material: M_IV_LivingContinent_Final22. Nearby terrain is lit for connected shading; far terrain uses scenic emissive readability. Native extra crest rocks have tag IVRemnant22. Water mesh/material are SM_IV_ContinentWater_v22 and M_IV_ContinentWater22.

The paired underside remains SM_IV_JoinedMountain_v21, using M_IV_JoinedGeology_v13. Its 8,192 landscape-overlap vertices were locked when the internal rock was smoothed in v21; playable Landscape is unchanged. The mainland cavity copies its 29,249 vertices at full size with a -20,000 m Z translation and 56,448 reversed faces. Main source topology checks still pass, with no internal open edges or nonmanifold edges.

The v21 river/lake layout remains: shared terrain/water function, sinuous western valley, irregular elongated lake centered (-1850,-1350) m, and downstream outlet. v22 exported terrain has 1,201 unobstructed river-centerline samples with at least 2.23 m water clearance. Native v21 join checks passed all 768 perimeter and 96 underside traces; v22 did not alter the island or cavity coordinates.

No lower-world houses/farm grids. The playable island's existing village and farm are preserved. Distant terrain stays flat toward the established horizon haze.

## Workflow
- Scripts/build_puzzle_continent_v22.py: mainland, exact cavity copy, shared water, atlas, foliage and remnant crest placement data.
- Scripts/apply_puzzle_continent_v22.py: imports/applies complete v22; invokes clean_puzzle_details_v22.py, apply_terrain_remnants_v22.py and final_continent_material_v22.py.
- Scripts/refresh_remnant_forest_v22.py: reapplies saved native forest rows without reimporting the mesh.
- Scripts/verify_watershed_mesh_v22.py: tests actual exported triangles beneath river.
- Scripts/render_puzzle_continent_v22.py: close, river, wide and village views.
- Source reports/data: Saved/AdventureWorldSource/puzzle_continent_v22_report.json, watershed_mesh_validation_v22.json, terrain_remnants_v22.json, puzzle_continent_v22_instances.json.
- Pre-v22 map: Saved/WorldBackups/BeforeRemnantTerrain_v22/Map_AnimeAdventure.umap. Previous assets remain available.
- Earlier paired refinement and island context: Docs/WorldDesign/Paired_Refinement_v21.md, Floating_Island_Handoff.md, Valley_And_Origin_v14.md. Historical v17-v21 visuals are superseded where described here.

## Session and limits
Hidden offscreen Unreal editor was PID 4088 when launched. Check before starting another writer. Scripts/adventure_editor_session.py polls Saved/adventure_request.json for new request ids. Last forest refresh id 167; final render request 168.

Current previews: Docs/WorldDesign/RemnantWorld_Rim.png, RemnantWorld_River.png, RemnantWorld_Context.png. Technical checks do not establish artistic approval. User feedback remains the basis for further refinement. Full traversal and packaged performance were not tested. Do not rerun early world generators over this map.
