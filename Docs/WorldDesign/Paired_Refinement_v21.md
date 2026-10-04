# Current project continuation — paired refinement v21

Project: D:/DEVELOPMENT/Games/IsekaiVillage/IsekaiVillage.uproject
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
Updated: 29 September 2026.

## User direction
The floating island and hollow must fit as two parts of one whole. The continent is tiny, distant scenery; towns are only implied by clearings/routes, without literal lower-world houses or farms. Obscure the continent boundary. The user rejected the river crossing a mountain and repeatedly asked for a more convincing, refined hollow. Latest pass v21 is ready for visual review; do not treat technical validation as artistic approval.

## Current saved state
- Paired rock geometry: SM_IV_JoinedMountain_v21 and SM_IV_PuzzleContinent_v21. Exact same 29,249 cavity vertices, translated 20 km down; 56,448 reversed faces. Export comparison error is zero cm.
- The underside was refined along with its inverse cavity, using restrained smoothing (2.06 m RMS internal displacement, maximum 22.02 m). All 8,192 landscape-overlap vertices are locked. The playable Landscape is unchanged. Both pieces retain their full size and orientation.
- Removed the repeated rock bands, added outer spurs and scattered rim talus from v19. Smoothed the terrain continuation beyond the exact seam. The cavity now uses physically lit, rough rock with subdued triplanar source-pack color; distant ground remains emissive for scenic readability.
- Water and terrain now share a watershed function. River follows the western valley around the hill belt, bends toward an elongated lake with uneven bays at (-1850,-1350) m, then exits downstream. Lake is separate from the extraction scar. Old v17 water geometry is replaced, not layered beneath it.
- Native water: SM_IV_ContinentWater_v21, M_IV_ContinentWater21. Native continent material: M_IV_LivingContinent_Final21. Island material stays M_IV_JoinedGeology_v13 on its refined rock shell.
- Distant terrain continues flat into the established v19 ground-level haze. No lower-world house or farm instances. The playable island's village and farm are preserved.

## Checks completed
- 1,201 samples on the exported triangulated riverbed: no centerline obstructions, minimum water clearance 2.23 m.
- 3,001 analytical watershed samples: water elevation never rises downstream.
- 768 native island perimeter traces and 96 underside traces passed after the paired refinement.
- Fresh close-up, river, wide and island views inspected. No full traversal or packaged-performance test.

## Rebuild and verification
Scripts/build_paired_rock_v21.py generates the refined underside.
Scripts/build_puzzle_continent_v21.py builds inverse cavity, surrounding terrain, atlas, water and instance data from that underside.
Scripts/apply_puzzle_continent_v21.py imports/applies everything, invoking clean_puzzle_details_v21.py, apply_paired_rock_v21.py and final_continent_material_v21.py.
Scripts/verify_watershed_mesh_v21.py checks the exported riverbed.
Scripts/verify_paired_join_v21.py checks native seam/underside collision coverage.
Reports: Saved/AdventureWorldSource/paired_refinement_v21.json, paired_fit_validation_v21.json, puzzle_continent_v21_report.json, watershed_mesh_validation_v21.json; Saved/paired_join_validation_v21.json.

Fresh images: Docs/WorldDesign/PairedWorld_Rim.png, PairedWorld_River.png, PairedWorld_Context.png, PairedWorld_Island.png.

## Recovery and session
Backup before paired underside changes: Saved/WorldBackups/BeforePairedRefinement_v21/Map_AnimeAdventure.umap. v13 underside and previous continent/water assets remain available.
A hidden offscreen Unreal editor (PID 4088 when launched) may still run. Check before launching another writer. Scripts/adventure_editor_session.py polls Saved/adventure_request.json for a new id and script. Last request id: 163.
Earlier island context: Docs/WorldDesign/Floating_Island_Handoff.md, Valley_And_Origin_v14.md. Earlier v17-v20 visual descriptions are historical. Never run the early world generators over the current map.
