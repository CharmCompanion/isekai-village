# Gosain43 â€” terrain and fortifications first

2026-10-16. This supersedes the work order in Gosain40/41 and the unplaced42 district.

The user rejected repeated formal courtyard/arcade architecture. Gosain should have Vatican-like masonry and intensely overcrowded, irregular street-grown urban fabric. Their latest correction explicitly prioritizes substantially larger/thicker perimeter walls and flattening BOTH enclosed islands into broad buildable tiers, with the castle on the highest hill/platform. Stop spending work on district detail until this foundation is correct.

## Prepared changes
- Both existing island outlines preserved. Terrain inside their existing wall circuits is regraded into broad flat city levels, not merely a scaled-down version of the old hills.
- Capital tiers are 48, 80, 112, 144 metres above sea. Companion island tiers are 48, 72, 96, 120 metres. Smooth transitions separate the benches.
- Castle reserve is a distinct irregular upper platform at 224m above sea, centred 300m east and 650m north of the existing capital centre. This is the highest terrain in Gosain. No new castle building has yet been constructed.
- Wall footing is level at 48m above sea. New curtains are 28m across at their battered base and 18m at the crown. Wall walk is 55m above footing; merlons reach 59.9m. Towers reach 76.4m. The crown has continuous side parapets and a clear central walk, rather than solid transverse bars.
- The bridge is rebuilt for the new common abutment level, with a gentle 6m crown instead of the previous 32m crown. Existing roads, foundations and 14,561 existing placements receive coordinated height changes.
- Protected: El Ruhn, other regions, global lighting and shared materials.

## Application state
Sources are generated in ArtSource/World/Gosain43. Check applied.json and native_validation.json before claiming the map is saved or verified. Apply script: apply_gosain_v43_terraces.py. Native baseline: Saved/Gosain43. New native renders: Docs/WorldDesign/Gosain43. Source layout diagram is explicitly a terrain design preview, not a native Unreal screenshot.

## Deferred architecture
Gosain42 contains 104 original shared-wall masonry masses fitted to two old street blocks, two enclosed alley links, and narrow internal lanes. Its import/temporary preview was already running when the user changed the priority. It was NOT placed in the world. Do not run apply_gosain_v42_district.py: its heights are tied to obsolete terrain40. Gosain41 is also superseded and unplaced.

## Next acceptance and continuation
1. Finish native baseline/import/coordinated apply, then verify outside-region actors/foliage and retained topology.
2. Inspect both island silhouettes, capital terraces, castle platform, wall thickness/walk, towers, bridge/approaches from native views.
3. Existing streets have only been vertically conformed. Engineer switchbacks/ramps where terraces change; inspect slope transitions before claiming walkable gameplay roads. Existing house footing placements are temporary, not final city architecture.
4. Build the castle complex on the highest platform and develop the full street hierarchy on these terraces, then original connected stone city fabric around those streets. Do not mass-expand cottages or the rejected arcade prototype.
5. Broad flat levels are groundwork, not a claim that Gosain or the world is finished. The entire remaining regional queue stays in WORLD_REBUILD_CHECKLIST.md; Kelsin has no water, El Ruhn is protected.

Native42 review crashed before screenshots in Unreal ShadowSetup.cpp (draw-command index assertion); no map placement or save occurred. Editor restarted normally, Gosain43 baseline successfully captured. Gosain43 OBJ faces are grouped by material to reduce section fragmentation; this is a mitigation, not a proven root-cause diagnosis. Coordinated43 application requested; inspect apply_progress.json and applied.json for actual outcome.


## Saved result
Coordinated43 is SAVED in Map_AnimeAdventure. Native verification passed: 1,260 pre-existing actors checked, no unexpected actor changes, no foliage move failures, all outside-region foliage unchanged. Ten coordinated mesh replacements and 42 foliage types were updated. Backup: Saved/WorldBackups/BeforeGosain43_20261016. No new buildings were placed. Editor closed normally before the scheduled screenshots; reopening for visual capture. Native views remain unconfirmed until native_views_complete.json and its files are inspected.

## Native visual review and summit correction
All four initial native views were captured and inspected. The larger walls and bridge are visible. Review found that the regional meadow shader's strong periodic colour oscillation falsely makes flat terrain look bumpy, and the existing landmark precinct remained below the empty summit platform. A bounded follow-up is prepared in apply_gosain_v43_visual_refine.py: copy the regional terrain material and replace only the masked Gosain meadow colour with subdued nonperiodic variation; move the existing seven landmark instances and their precinct walls 300m east, 650m north and 80m upward onto the existing 224m summit; remove old house/tower clutter in the bridge and short gate approach corridor. Preserve all unrelated actor state and every other foliage transform. No new finished castle art is claimed. Check visual_refine_applied.json and refreshed screenshot timestamps for success.

After this refinement, the original verify_gosain_v43.py comparison intentionally predates the landmark relocation/material override. Do not treat those explicit differences as corruption, and do not rerun the initial43 apply. The follow-up records its own exact expected-state comparison and full rollback transforms. Source terrace geometry stays unchanged.


## Latest confirmed state — 2026-10-16, 19:19 local
The visual refinement is SAVED and all four refreshed native views have been inspected. Seven existing landmark instances and their precinct walls moved onto the 224m summit (offset +300m X, +650m Y, +80m Z). The copied regional ground material removes the strong false ripple pattern. 112 legacy house/tower pieces were removed from the bounded bridge/approach corridor. Exact-state checks passed for 1,258 unrelated actors and all expected foliage rows. Backup: Saved/WorldBackups/BeforeGosain43Visual_20261016_191706.

This completes this bounded foundation revision, not Gosain's art or city population. The native views still show the small temporary stock-house district, large empty city terraces, remaining legacy roadside rows outside the cleaned corridor, faceted coastal slope transitions, and the prototype landmark architecture. Do not describe these as finished AAA city art. The displaced old precinct space remains available for redevelopment.

Next bounded milestone: design and engineer the summit approach, terrace-to-terrace ramps, and bridge-to-city streets against the NEW terrain. Add retaining masonry where the coastal/terrace transitions need architectural treatment. Then replace the stock houses with original shared-wall, densely accumulated masonry blocks fitted around those streets, extending across both islands. Gosain42 is an unused exterior source experiment requiring regrading and native review, not a placement-ready approved district. Preserve El Ruhn and all other regions.
