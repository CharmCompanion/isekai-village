# Stylized landscape — v32

Request: put water, sand, rock and grass where they belong on El Ruhn, matching or beating the SoStylized Demonstration map (`Content/SoStylized/Maps/CompleteVol1/Demonstration.umap`). Reference renders: `Docs/WorldDesign/Stylized32_*.png` (1920 × 1080, editor viewport, Lumen).

## What was wrong and what changed

### 1. Landscape layers — one flat shader, no paint API (`build_biome_layers_v32.py`, `apply_stylized_landscape_v32.py`)
- The playable island used `M_IV_FloatingLandscape`, a custom world-position colourer with no grass / dirt / sand / rock layers, no AutoCliff, no wet shoreline, no LandscapeGrassOutput.
- UE 5.8 Python cannot add landscape paint target layers (`target_layers` is read-only). The SoStylized `M_Landscape` graph is duplicated to `M_IV_StylizedLandscape32` and every `LandscapeLayerBlend` / `LandscapeLayerSample` is driven by a packed weight texture (`T_IV_Layer32_Weights`, RGBA = Grass / Dirt / Sand / Rock) sampled from world XY at the landscape's own 1.19 m texel size.
- Weights are baked from the authored biome + height: dirt on roads, plaza and the four farm plots; sand on the lake/river beach band; rock on authored cliffs, steep slopes and high ground; grass fills the rest. Priorities Dirt > Sand > Rock > Grass, sum = 1 (Grass .633, Dirt .175, Sand .046, Rock .146).
- The material is converted to masked so `LandscapeVisibilityMask` still cuts the 1.2 km square to the island outline. AutoCliff, sand sparkle, wet shoreline, RVT output and `LG_Grass` stay wired.
- Instance `MI_IV_StylizedLandscape32` keeps the demo tints (brighter grass / sand / dirt) and is assigned as both landscape and hole material.

### 2. Ground grass colour — RVT volumes (`apply_stylized_landscape_v32.py`)
- v31 had turned `UseRVTColor?` off because the level had no RuntimeVirtualTextureVolume. v32 adds `RVTV_Landscape` + `RVTV_LandscapeHeight` covering the island and turns `UseRVTColor?` back on (except `*_NoRVT*` variants). Blades pick up the dirt roads, sand beaches and grass tint from the landscape instead of a flat green.

### 3. Lake surface, bed and spillway (`build_sky_lake_grid_v32.py`, `apply_sky_lake_v32.py`)
- The v08 lake was a 256-triangle fan; the shared centre tangent showed as a shading wedge. It is now a 3 m Delaunay grid (9,122 verts / 17,730 tris) with a 512-point outline.
- The old `SM_IV_SkyRiver` ribbon started at y = −363 and sat co-planar under the southern bay (a second hard water edge). It now starts on the lake outline (~y = −504) and runs to the fall at y = −544.
- West of x ≈ −437 the landscape is visibility-masked, so the western bay had no bed and `M_Water` shaded it as bottomless. A sand floor (`SM_IV_LakeBed` / `M_IV_LakeBed32`) sits at 9.3 m, just under the landscape bed minimum.
- `MI_IV_SkyLake` is cleared toward the demo look: Murkiness .22, Scattering .14, Caustic Strength 48, Foam Multiply 1.25.

### 4. Foundation GI cave (`apply_sky_lake_v32.py`, also in the landscape apply)
- The inverted-mountain foundation is a closed 1.2 km volume under the playable surface. Lumen treated it as a cave: a hard dark wedge on the western lake and a pitch-black dungeon path. The mesh stays for the underside view; `Affect Distance Field Lighting` and `Affect Dynamic Indirect Lighting` are off on the live foundation, the rim collar, and leftover Archived shells (those are hidden in-game again).

### 5. Plaza cobbles
- The old custom shader painted the village square. The layered material cannot. A 36 m `MI_Stone_Floor` disc sits 3 cm above the landscape median.

## Known remaining
- Farm fences use the Advanced Village pack atlas (`T_Pack_01_D`); the posts are authored black, same as v31.
- The Spillway review camera is a shore view of the sandy beach rather than a look down the waterfall.
- Caustics on the sandy bed are easier to see in-editor than in these sun-facing stills.
- Mainland far-field `SM_Civ30_*` settlements were not audited.

## Continue work
Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`
Scripts, in order: `build_biome_layers_v32.py`, `apply_stylized_landscape_v32.py` (delayed slate runner; MaterialEditingLibrary crashes at frame 0), `build_sky_lake_grid_v32.py`, `apply_sky_lake_v32.py`; renders via `render_stylized_v32.py`.
Reports: `Saved/stylized_landscape_v32_result.json`, `Saved/sky_lake_v32_result.json`, `Saved/AdventureWorldSource/sky_lake_grid_v32.json`.
