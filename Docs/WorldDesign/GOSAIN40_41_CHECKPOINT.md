# Gosain 40 terrain / 41 architecture continuation

Updated 2026-10-16. Read this before older checkpoints.

## User direction
Gosain requires large connected multi-storey city buildings linked by alleys, corridors, courtyards and layered terraces. Stock detached houses are rejected as the final solution. Gosain39 population is temporary and must not be expanded. Entire enclosed area on both islands still needs dense city development. El Ruhn remains protected. Kelsin has no water. Other regional directions remain in REGIONAL_ARCHITECTURE_DIRECTION.md.

## Saved terrain40
The coordinated terrain update returned saved in Unreal. Land above Gosain sea level (-20600m) is reduced to 30% of its previous relief; high point changes from 1381m to 414m above sea. Island horizontal coordinates and triangle topology are unchanged. 797,383 terrain vertices changed vertically; 1,059,217 remained identical. Roads, foundations, walls and bridge use coordinated copies; 14,561 foliage/object placements across 42 types were rebased. Original assets remain available. Backup: Saved/WorldBackups/BeforeGosain40_20261016.

Sources and reports: ArtSource/World/Gosain40. Applied.json lists exact old/new asset paths. Source reports do not substitute for post-save native verification. Unreal exited after saving; verification was queued for the reopened editor. Check native_validation.json and the current response before claiming verification passed.

## Roads
Main-route candidates are SOURCES ONLY, not applied. Both the coarse and finer terrain surveys found steep sections beyond acceptable street grades. Do not import SM_Gosain40_MainRoutes as a finished solution. It also needs shared-segment/junction resolution. Solve switchbacks and localized engineered grades with actual triangle-surface validation before road application.

## Architecture41
Scripts/build_gosain_v41_urban_block.py creates original connected courtyard-block geometry, not stock houses. Includes connected wings, three-to-five occupied storeys, six-metre axial passages, upper links with 4.5m minimum planned clearance, covered front arcade, courtyard terrace/stair, facade windows/trim, roofs and awnings. External architecture prototype; upper-floor interiors are not authored. It needs native visual review and geometric clearance checks. Do not describe it as finished AAA art.

ArtSource/World/Gosain41/urban_block.json records the source. Scripts/apply_gosain_v41_block_review.py imports private materials/mesh and makes a TEMPORARY preview actor for four native screenshots, then removes it. It does not replace city districts or save that temporary actor. Check Docs/WorldDesign/Gosain41/review_complete.json and inspect every view; do not infer success merely from script_returned because screenshot work runs on callbacks.

## Next work
1. Verify saved40 against Saved/Gosain40 baseline; inspect lowered island, capital and bridge views.
2. Run/inspect connected-block41 preview, refine roof/wing junctions, facade proportions and passage routes. Keep all stock-house expansion stopped.
3. Develop multiple connected block arrangements and prepare supported district terraces/routes. Replace temporary stock buildings in bounded districts, with backups and outside-region invariance checks.
4. Complete both Gosain islands, citadel, religious precinct, harbor/street networks and performance validation before moving through the remaining regional queue.

Terrain40 native verification PASSED after reopen: 1,260 existing actors checked, zero unexpected changes, outside-Gosain foliage matches, all requested foliage rebases match their expected transforms. Native visual terrain40 review still pending.


Superseded work order: read GOSAIN43_CHECKPOINT.md. User requires massive walls and flattened, layered island interiors with castle highest before any more district work. Do not place41 or42 on obsolete40 elevations.
