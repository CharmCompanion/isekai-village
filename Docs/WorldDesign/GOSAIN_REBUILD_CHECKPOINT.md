# Gosain rebuild checkpoint

Status: capital layout/terrain checkpoint SAVED and reloaded in Unreal, 2026-10-13. Protection and geometry checks passed. Native aerial, precinct, market and gate views inspected. This is a verified first district pass, NOT a finished empire or final AAA art acceptance.

Baseline before this checkpoint: 2026-10-06, civilization pass v36. The older Civ33 screenshots are NOT proof of current appearance.

Important findings:
- The continent is an approximately 141 x 95 km scenic atlas, 20 km below El Ruhn. Native-size houses were mixed with massive fortifications and sparse broad forest.
- V36 caps each island town length at 620m while walls follow entire coastlines.
- V36 wall sections are 48m meshes stretched independently and set to a single center height; bridge meshes are open ribbons. These need direct inspection for discontinuity and support.
- V36 assets are shared foliage types across regions. Regional work must preserve outside-region transforms and shared asset materials.

## Current milestone (37)

User authorized terrain leveling within Gosain's walls. Start with the capital district: lower town at +1.5m, older middle town at +7.5m and cathedral precinct at +14.5m relative to the old city platform; broad graded approaches connect them. The complete original continent is retained outside this local edit. This is native terrain mesh work on the existing mesh-based continent; El Ruhn's Landscape is not touched.

Prepared a capital district using complete native houses (the old generator used separate house attachments as buildings), irregular blocks, major trade streets, market courts, gardens, and a rebuilt 14m precinct curtain. Cathedral and imperial spire have separate footprints. Coastal walls, bridges, harbor connections and the monastery remain NEXT, before moving to the desert.

- Backup: `Saved/WorldBackups/BeforeGosain37_20261013/Map_AnimeAdventure.umap` (original SHA256 `224C2409EC45620217E956A18D97B127A35C7131D6F5D063D823EEE5085EB21B`).
- Durable sources: `ArtSource/World/Gosain37/` (not only Saved).
- Scripts: `gosain37_geometry.py`, `build_gosain_terraces_v37.py`, `build_gosain_v37.py`, `apply_gosain_v37.py`.
- Audit: `Saved/Gosain37/baseline_actors.json`, `baseline_foliage.json`, `mesh_audit.json`, `continent_material.json`.
- Native before views: `Docs/WorldDesign/Gosain37/Before_*.png`. Before_Street is obstructed by existing geometry; this is a defect, not a useful beauty view.
- Plan: `Docs/WorldDesign/Gosain37/Capital_Layout_Plan.png`.
- Current editor request runner: `world_rebuild_editor_session.py`, reading `Saved/world_rebuild_request.json`. It only runs explicit region scripts, never legacy requests.
- Applying: `apply_gosain_v37.py` imports new assets before changing actors; refuses a second initial application after Gosain37 actors exist. Do not bypass that guard. Use a refinement script for subsequent changes.

## Applied and checked

- `apply_gosain_v37.py` and `apply_gosain_v37_terrace_refine.py` both completed and saved. Final native terrain contains the restrained valley-preserving refinement, not the superseded valley-fill prototype.
- 3,229 complete A/B house instances, markets, wells, lamps, gardens, separate cathedral/spire footprints, locally graded streets, and a 14m precinct curtain with an open south gate.
- Three terrain levels are +1.5m, +7.5m and +14.5m relative to the old platform. Maximum terrain displacement is 14.50003m; 1,073,706 original vertices outside the edited area are unchanged. Adaptive subdivision adds detail locally. No new nonmanifold edges; local patch boundary edge count remains 242, matching the original patch boundary. This is not a claim that the entire old continent has no holes.
- 32,576 road vertices checked against the actual exported triangle surface: clearance 0.0209–0.1362m, none buried more than 2cm or floating over 30cm. House origins are -0.00065–1.36173m above terrain; raised homes use foundations. No gameplay traversal/navmesh acceptance has been performed.
- Reloaded native scene comparison: 1,250 existing actors match baseline locations, scales, angles, hidden state, tags and mesh/material assignments, excluding the three intentionally replaced mesh actors and foliage container. Outside-capital foliage transform/material groups match. Three new district mesh actors. Rotation comparison uses numeric angles because Unreal's printed Rotator includes a process-specific memory address; baseline is not rewritten.
- Private Gosain materials only: tiled masonry/paving/roofs, regional mask confined to the two Gosain islands, three-axis rock projection, darker and more varied grass/stone after screenshot review. Existing global lighting and El Ruhn materials were not edited. No material compile failure reported after the fixes.
- Final material sequence: `apply_gosain_v37_material_fix.py`, then `apply_gosain_v37_ground_color.py`. Do not rerun the initial apply to refine materials.
- Native evidence: `Gosain37/After_Capital.png`, `After_Precinct.png`, `After_Market.png`, `After_Gate.png`, `After_Terraces.png`, `After_Reverse.png`, `After_ElRuhn_Protected.png`. These are actual Unreal captures, not concept images.
- Geometry/native reports are copied to `Docs/WorldDesign/Gosain37/` for durable continuation.

## Remaining defects and exact next work

1. **Next checkpoint: coastal defenses and access on Gosain's capital island.** Inspect the existing coast-wall segments and both bridge ends from multiple angles. The current outer walls remain oversized, repeated white geometry on abrupt slopes; original terrain around them still has coarse facets. Replace only the affected Gosain components with grounded, continuous walls, deliberate gate openings, abutments and supported bridge geometry. Preserve other regions and the newly terraced city.
2. Connect the three new radial approach roads to the real coast gates/bridge network. The current city street ends and clipped short lanes are not proof of a finished connected regional route. Add deliberate alley endings/courts where appropriate.
3. Rebuild the monastery quarter on the second island with the same scale discipline, but a distinct cloister/harbor arrangement.
4. Return for capital art polish: the two house types still repeat visibly; wide lawn spaces, especially inside the precinct, need planted cloisters, service courts, retaining details, garden walls, wear and additional appropriate native building variation. Cathedral and spire still show simple generated forms. Do not call this AAA-final without addressing those visible limitations.
5. Check distant readability from El Ruhn, close views, intersections and performance. Existing startup warns about non-Nanite shadow workload and old collision mesh complexity; performance has not been benchmarked. Mainland remains scenic, without new interiors, population AI or navigation systems.
6. Complete Gosain before Yozuan desert; El Ruhn remains protected throughout.

## Session recovery

`world_rebuild_editor_session.py` now guards against nested requests and remembers the last completed request on startup. Use a new request ID for each intentional action. It reads UTF-8 with or without BOM. Its session-only background throttle setting is obtained via `/Script/UnrealEd.Default__EditorPerformanceSettings`; `unreal.EditorPerformanceSettings` is not exposed in this installation. Custom material input fields require `set_editor_property`. Do not repeat the resolved API errors or overwrite baseline audits.

## Latest direction — 2026-10-15
King's Landing is now the primary Gosain city reference. See GOSAIN_KINGS_LANDING_DIRECTION.md for research, whole-two-island scope, current Gosain38 status and ordered next steps. This supersedes the limited capital-only scope above. Dense whole-island infill remains unfinished.


2026-10-15 application: bridge cleanup saved in Unreal. StaticMeshActor_560 now uses the Gosain38 filtered road copy; 77 obsolete bridge faces removed. Original mesh retained. Backup: Saved/WorldBackups/BeforeGosain38BridgeCleanup_20261015. Dense whole-island streets/buildings remain the next substantive stage; regional references are in REGIONAL_ARCHITECTURE_DIRECTION.md. Kelsin explicitly has no water.


Latest saved scene checkpoint: GOSAIN39_CHECKPOINT.md. Capital now has 3,609 houses across five assembled designs; full-island urban expansion remains pending. Read that checkpoint before continuing.

