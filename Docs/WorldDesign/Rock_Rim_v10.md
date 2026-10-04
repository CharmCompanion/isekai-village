# Rock rim and fractured underside v10

Current map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.

This revision addresses the exposed flat left edge in the southeast overview (the island's eastern side) and the smooth clay-like underside.

## Terrain boundary

The native Landscape now has an uneven outer ridge with a steep inner scarp. The eastern mountain shoulder joins the ridge, replacing the flat strip between the old mountain face and the outer edge. The front has lower ridges to retain the plains and skyport view. The authored dock approach and waterfall channel remain open.

All 194,902 native height samples in the full future village rectangle remain exactly unchanged from v08. The farm, plaza and village layout were not moved. Vegetation was regrounded using each foliage type's own instance set; plants on the steepest new faces were removed. There are 101,359 foliage instances after the terrain revision.

## Bedrock

The v09 smooth bedrock and embedded boulders are archived, hidden and collision-disabled under `Archived/Organic Bedrock v09`.

The new shell has explicit per-face normals, 3,585 vertices and 7,040 triangles. The importer preserves those normals instead of smoothing the rock faces. The shape has a narrower, offset taper and stronger fractures. Twelve larger shear formations and sixty mostly embedded jointed faces reuse the SoStylized Spire meshes, without concentric placement rows. Project-owned material copies retain the pack's rock treatment and extend crack visibility for the distant overview. These actors are under `Floating Island/Fractured Bedrock`, tagged `IVRockRim10`.

## Checks and review

- 18 native terrain height/collision samples passed.
- Seven horizontal outward collision traces across the exposed eastern rim hit the new native ridge.
- Protected village height comparison passed.
- Overview, underside close view, left-edge walking-height view and reverse-side images are `RockRim_*.png` beside this document.

These are terrain collision checks, not a full player traversal test or a guarantee that no character movement ability can cross the boundary. The dock and waterfall are intentional openings. Packaged performance and full gameplay traversal remain untested in this visual revision.

## Recovery and authoring

Pre-revision map and Landscape material: `Saved/WorldBackups/BeforeRockRim_v10/`. Earlier underside actors are preserved in the map. Original asset-pack assets were not modified.

Current native terrain source is `Saved/AdventureWorldSource/height_rockrim_v10.npy` / `IV_RockRim_v10.r16`. The visibility mask remains the existing floating-island mask. Bedrock source: `SM_IV_FractureBedrock_v10.obj`.

Scripts: `build_rockrim_v10.py`, `build_fracture_bedrock_v10.py`, `apply_rockrim_v10.py`, `add_hero_fractures_v10.py`, `add_jointed_rock_faces.py`, `bedrock_surface_v10.py`, `verify_rockrim_v10.py`. These record a staged authoring sequence; do not rerun them as an unconditional full rebuild. In particular, `IV_RimPrevious_v10.r16` is a snapshot for incremental foliage height correction and must match the map before a subsequent terrain change. Reusing an old snapshot can apply offsets twice.

Validation records: `Saved/rockrim_validation.json`, `rockrim_protected_validation.json`, `rockrim_normals.json`, `rockrim_render_review.json`.
