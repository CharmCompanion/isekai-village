# Anime overworld refinement — v31

Request: the El Ruhn overworld read as holes, floating objects and low-quality textures; it should look like a modern anime game. This pass found and fixed the actual causes rather than re-dressing the map. Reference renders: `Docs/WorldDesign/AnimePolish31_*.png` (1920 x 1080, editor viewport, Lumen).

## What was wrong and what changed

### 1. Lighting — the island sat in near-vacuum (`apply_anime_lighting_v31.py`)
- The SkyAtmosphere planet surface had been moved to mainland sea level, 20.6 km below the playable island. The island was physically in the exosphere: black zenith, a sky light capturing darkness, pitch-black shade. The atmosphere now sits 250 m under the village (`z = -25000`), aerial perspective scale 0.6.
- Sun: source angle 1.6°, soft angle 1.0°, shadow amount 0.9 (softer anime shadows). Sky light: warm-grey lower hemisphere, 256 px capture. Painted cloud meshes no longer cast shadow blobs.

### 2. Rim seams — the landscape ended on a cake-cut line (`apply_rim_collar_v31.py`)
- Seen from outside, the playable Landscape ended on a dead-straight horizontal line against the rock foundation, and the pale landscape boundary plate showed where the two did not meet (north and east rims).
- 720 rays are marched from the island centre; the outermost Landscape sample on each ray (looking through anything standing on it) defines the edge. A faceted rock collar (8,640 tris, `SM_IV_RimCollar_v31`, source `Saved/AdventureWorldSource/SM_IV_RimCollar_v31.obj`) rises out of the grass a few metres inside the edge, bulges over the rim with 0–3 m crags, and tucks back into the foundation 40 m below. Where a feature sits on the edge (airship quay, lake outflow, boulders; 8 rays) the collar is buried so it never cuts through anything.
- The collar uses a two-sided instance of the foundation material (`MI_IV_RimCollar_v31`) and complex collision. Note for future mesh scripts: the OBJ importer mirrors Y, so UE `(x, y, z)` must be written as `(x, -y, z)`; the script verifies this against expected bounds.

### 3. Rock texture — photo noise replaced with anime strata (`apply_anime_rock_material_v31.py`, `apply_anime_ground_fixes_v31.py`)
- `M_IV_SculptedGeology28` (foundation + collar) drew its colour from a 45 m tiled rock photo, which read as blue-grey noise over a 1.2 km shell. Base colour is now flat strata: two warm greys in horizontal bands warped by 130 m value noise, a fine 2.6 m band, a cool darkening gradient toward the underside, soil and moss on up-facing ledges within 25 m of the landscape surface, and only a ±10% texture breakup. Roughness .74 → .92, detail normal tiling 18 m → 42 m.
- `M_IV_CaveStone` (tunnels, portals, quay buttresses) gets the same two-tone banding, and its self-illumination goes from 9% to 30% so unlit tunnel interiors read as dim stone instead of black holes (`finalize_anime_polish_v31.py`).

### 4. Black grass — a missing RVT volume (`apply_anime_ground_fixes_v31.py`)
- Every SoStylized grass and flower instance had `UseRVTColor?` on, sampling `RVT_Landscape` for its colour, but the level has no RuntimeVirtualTextureVolume, so all ground foliage rendered as black shards. The RVT colour path is switched off on 60+ foliage instances; `MI_Grass*` get a flat anime green (0.235, 0.43, 0.085) with brighter tips.

### 5. Floating objects (`apply_anime_ground_fixes_v31.py`, `finalize_anime_polish_v31.py`)
- The 12 modular `BP_BLD_house_*` buildings were measured at 90% of their footprint corners: all sit on the Landscape within 2 cm. They were never floating.
- 21 props were hovering 0.3–3.5 m above the terrain (boulders, cliff piece, spring bank stones, supply crates, the dungeon spring pool) and are dropped onto the Landscape (8 cm sink). The Veil Falls spring pool is lowered by the same 3.35 m as its bank stones. Intentionally elevated items (passage lanterns, quay planks over the void, railings, the sky lake) are left alone and listed in `Saved/anime_ground_v31.json`.
- Collision for the 263k-triangle foundation is cooked asynchronously after load; audits that trace within ~20 s of map load miss it and report false "no ground" results. The v31 scripts wait 90 s before camera placement.

## Known remaining
- The dungeon/mine/trade-pass tunnels have no light actors; they now read as dim stone but are still dark. Lanterns are static meshes only.
- The collar is a single procedural ring; a hand-dressed scatter of rock meshes along the crest would add silhouette variety.
- Mainland far-field `SM_Civ30_*` instanced settlements were not audited.

## Continue work
Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure (single non-World-Partition level; safe to load and save from a script)
Scripts, in order: `apply_anime_lighting_v31.py`, `apply_rim_collar_v31.py`, `apply_anime_rock_material_v31.py`, `apply_anime_ground_fixes_v31.py`, `finalize_anime_polish_v31.py`; renders via `render_anime_polish_v31.py`.
Run pattern: `UnrealEditor.exe <uproject> <map> -unattended -nosplash -nop4 -ResX=1920 -ResY=1080 -ExecCmds="py <script>" -log -abslog=<log>` with `IV_RENDER_AFTER=1` to render and quit.
Backup before this pass: `Saved/WorldBackups/BeforeAnimePolish_v31/Map_AnimeAdventure.umap`.
Reports: `Saved/anime_lighting_v31.json`, `anime_rim_v31.json` (includes a dump of the rock materials), `anime_rock_v31.json` (house footprints, grass material graph), `anime_ground_v31.json`, `anime_finalize_v31.json`.
