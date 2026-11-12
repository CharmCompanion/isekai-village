> 31 October 2026 update: the user explicitly approved the tested shared sky correction. It is saved and native Gosain/El Ruhn views were checked in `Gosain58_ApprovedSky`. Any pending-approval wording below is historical. Current new-map work: `EL_RUHN_SKY_MAP.md`.

# Gosain58 — terrain and road fidelity repair

26 October 2026. Latest user priority: remove unintended sharp angles/points and improve terrain fidelity toward Tales of Zestiria/Berseria while retaining anime stylization. This supersedes immediate port construction. El Ruhn and unrelated regions remain protected.

## Current application status

**Applied, saved and inspected in Unreal.** Six matching before/after cameras are complete. `ArtSource/World/Gosain58/applied.json`, `source_verification.json` and `native_verification.json` confirm this stage. Do not replay the successful apply script. The geometry/shading repair improves the visible defects, but the world has not reached the requested Tales visual quality.

## Changes prepared

- Local height smoothing on both Gosain islands. Town ground, the lake bank, mine and bridge ends retain protected areas. Most height corrections are small; the maximum initial correction is 20.43 m, with the 95th percentile under 0.89 m.
- Shoreline triangulation refined with 164,834 added vertices. New coastal edges have two incident faces. Total continent terrain has 5,099,290 triangles. This remains a static mesh, not Unreal Landscape.
- Corrected normals across Gosain, including protected road shoulders where prior partial normal calculations were retained. 19,225 normals needed corrections exceeding one degree; the largest correction was 131.84 degrees.
- Existing road centerlines retained, with 1,432 shared cross-sections joined. The same 1,440 active segments are retained; the removed mine-yard paving stays removed. Roads now use closer ground samples and smooth vertex normals; 50,281 vertices / 80,392 triangles, 0.15 m nominal clearance. Maximum lateral join adjustment is 2.99 m at a sharp turn.
- Private terrain material: closer stone texture projection, more visible grass detail and a less uniform rock/grass transition on the right mountain. No shared pack material or global lighting edit.
- Forest heights resampled to the repaired surface. Left 30,177 and right 9,706 trees retain XY positions, variants, rotations and scales.

## Sources and assets

- Source: `ArtSource/World/Gosain58`.
- Build scripts: `build_gosain_v58_terrain.py`, `build_gosain_v58_coast.py`, `build_gosain_v58_surface_finish.py`. These are sequential stages; do not replay them over finished source files.
- Apply: `apply_gosain_v58_terrain.py`.
- Review: `render_gosain_v58_terrain.py`, `verify_gosain_v58_native.py`.
- Target terrain: `/Game/IsekaiVillage/AdventureWorld/Gosain58/Meshes/SM_IV_Continent_GosainRefined58`.
- Target routes: `/Game/IsekaiVillage/AdventureWorld/Gosain58/Meshes/SM_Gosain58_ContinuousRoutes`.
- Target material: `/Game/IsekaiVillage/AdventureWorld/Gosain58/Materials/M_Gosain58_TerrainDetail`.
- Native views: `Docs/WorldDesign/Gosain58_Before` and `Gosain58_After`. Compare identical cameras; do not substitute generated concept art.
- Map backup: `Saved/WorldBackups/BeforeGosain58_20261026_051840`.

## Verification and limits

Source reports: `terrain_validation.json`, `coast_validation.json`, `surface_finish_validation.json`, `forest_validation.json`. The 28% reduction in steep-face area in the first report is measured before coastal subdivision; it is not a final visual metric.

The apply script records a matching signature of other static actors (mesh, transform and materials), excluding only the terrain and route actors. It restores prior mesh/material and forest positions on a mutation failure. A saved map backup also exists before mutation.

Main-continent collision is inherited as disabled and remains disabled. The mine has its own local collision grid and a tested short passage; this does not establish whole-world traversal, navigation or gameplay. Runtime and performance testing remain outstanding.

Final source verification: original vertices outside the Gosain buffer, inside town footprints and within 185 m of the mine match Gosain57 exactly. Road mesh has no degenerate faces or edges with more than two incident faces. The final mine mesh has 1,202 vertices / 2,400 faces and every edge has two incident faces.

Native verification: forest counts 30,177 / 9,706; mine 195 actors, six lights; isolated floor support sweeps 13/13; seven centerline segments and three entrance lanes clear; deeper gate blocks. Other static actor signatures match. This is editor verification, not runtime certification.

## Visual review

- `Mine_Road`: stretched dark/gray surface bands are gone, paving joins are continuous and local grass detail reads more clearly. A conspicuous near/far blue color boundary affects terrain and props. Subsequent controlled comparison established that correcting the shared SkyAtmosphere ground level removes it; see Gosain59 below. That change is previewed and restored, not saved.
- `Right_Coast`: the main sawtooth shoreline projections are substantially smoother. Isolated triangular offshore shapes and some mountain creases remain; inspect those closely in the next terrain refinement.
- `Right_Mountains`: grass/stone transitions are less uniformly gray. Broad slopes are still too smooth/empty, and towns remain visibly repetitive and abruptly bounded.
- `Lake_Shore`: retained basin and border are intact; minor streaks/creases near the bank, overly regular vegetation limits and water treatment remain unfinished.
- `Mine_Yard`: final mine and yard are retained. The mine's broad artificial mound, repeated rocks, sparse ground detail and abrupt blue color boundary remain art defects.
- `Kingdom`: retained land use and bridge layout; this is a region-scale continuity check, not evidence of finished local art.

The read-only `surface_actor_audit.json` found one visible main continent mesh, not duplicate overlapping continent actors. `fog_audit.json` records the existing global fog; it was not altered. El Ruhn and global lighting remain protected.

Subsequent continuation: `GOSAIN59_CHECKPOINT.md` records applied local understory and the pending shared-atmosphere decision. `sky_audit.json` found the sky actor at -250 m, about 20.35 km above continent sea level. `Docs/WorldDesign/Gosain58_AtmosphereStudy` contains native before/after comparisons and confirmation that the original position was restored. Do not apply `apply_gosain_v58_atmosphere_fix.py` without the user's answer to the specific question.

## Continue

1. Start from Gosain59, which retains this saved terrain and adds local understory. Compare the six native before/after views and `Gosain58_After/review.json`; do not rerun terrain58 generation.
2. Resolve the pending shared sky decision, then continue remaining offshore triangular forms, lake-bank creases, foothill relief and material scale. Further density alone is not the target: readable terrain forms and coherent shading matter.
3. Refine ground vegetation, rock exposures and woodland transitions; current tree placement and distant towns remain repetitive. The broad mine mound still needs art refinement.
4. Build the sheltered port after these terrain defects are resolved, then royal houses/knight school and compact district transitions. Do not restore full-island urban infill.
5. Continue other regions in the master checklist. Preserve El Ruhn.

Reference direction supplied by user: Tales of Zestiria and Tales of Berseria. Official reference pages: https://en.bandainamcoent.eu/tales-of/tales-of-zestiria and https://en.bandainamcoent.eu/tales-of/tales-of-berseria . Current work does not claim to have reached their finished visual quality.
