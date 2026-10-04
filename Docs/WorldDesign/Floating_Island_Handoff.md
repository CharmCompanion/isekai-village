Current version: [Regional civilizations v29](Regional_Civilizations_v29.md). Fortified religious islands, separate desert groups, magic-technology cities, agricultural plains and tidal settlements. Earlier entries below are historical.

Current version: [Smooth stylized content v28](Smooth_Stylized_Content_v28.md). Refined paired foundation/cavity, smoother native rock copies, cubic mainland terrain and continuous surface normals. Earlier entries below are historical.

Current version: [Desert canyon cut v27](Desert_Canyon_v27.md). A deep winding cut through the desert replaces the raised escarpment; opposing layered walls, six side ravines and broad remnant ledges. Earlier entries below are historical.

Current version: [Whole-scene landscape polish v26](World_Polish_v26.md). More detailed shorelines and cliffs, softer roads, varied forests and settlements, lake depth colors, improved atmosphere and cloud placement. Earlier entries are historical.

Current version: [Desert and shoreline v25](Desert_Shoreline_v25.md). Irregularly scattered oases, sand meeting water, darker settlement indications and a sandstone escarpment with ledges. Earlier entries below are historical.

Current version: [Beaches and biome transitions v24](Ecology_Coasts_v24.md). Southern desert/oasis fringe, coastal shelves and beaches, high-elevation snow and smoother ecological transitions. Earlier entries are historical.

Current version: [Mapped world and neutral El Ruhn v23](Mapped_World_El_Ruhn_v23.md). Reference biomes, continuous northern ranges, distant settlement areas and neutral floating kingdom. Earlier entries below are historical.

Current version: [Remaining mainland terrain v22](Remaining_Terrain_v22.md). Connected remnant mountains, wooded slopes and hills around the matching cavity. Earlier descriptions below are historical.

Current version: [Paired refinement v21](Paired_Refinement_v21.md). Refined matching underside/cavity; rebuilt watershed. Earlier descriptions below are historical.

Current version: [Exact puzzle fit v18](Puzzle_Fit_v18.md). Full-size inverse underside, 20 km below; lower-world houses and farm grids removed. Verified and saved 29 September 2026. Earlier descriptions below are historical.

Current version: [Continental river valley and birthplace v17](Continental_World_v17.md). The barren continental background is replaced with forests, rocky hills, a lake and river, roads and farming hamlets. The v14 island hills and v13 repaired join remain intact.

Current refinement: [Island orbit refinement v12](Island_Orbit_Refinement_v12.md). This supersedes the v11 underside and completes the subsequent all-sides refinement.

Current refinement: [Shallow dish and inverted mountain v11](Shallow_Dish_Inverted_Peak_v11.md). This supersedes the v10 rim and underside.

> Current revision: [Rock_Rim_v10.md](Rock_Rim_v10.md). This document describes the pre-refinement floating island.

# Floating island adventure world

Open `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`. Updated 28 September 2026.

The user's floating-island references replace the earlier continental coast/ocean requirement. The GDD continues to guide settlement progression; the FFCC master documents guide the clearing, civic center, forest framing and outward routes.

## Current geography

The native Unreal Landscape retains the village, roads, level farm and the entire 520 × 530 metre town planning area. Northern and western mountains remain; a new eastern shoulder completes the rear crescent outside the construction boundary. The forest canopy is enlarged at the foothills. The front ground becomes grassland.

A roughly 146 × 118 metre lake lies front-left/southwest at (-285,-320) metres, water elevation 18 metres. A river flows south to a waterfall over the rim. The front-right/southeast landing stage, near (275,-535), has wood decking, rails, stone supports and mooring posts. North is +Y; east is +X. Unreal coordinates use centimetres.

A separate rock shell forms the sharp inverted mountain beneath the sculptable upper Landscape, reaching roughly 800 metres below it. Reused stylized cloud meshes surround the lower island. The old ocean, harbor, boat and tidal rocks are retained under `Archived/Continental Coast`, hidden with collision disabled.

## Preserved settlement and completed refinements

- Farmhouse (130,-98), elevation 24.5 metres. Four level fields remain at (110,-145), (146,-145), (110,-181), (146,-181). The road reaches the house; service lanes run between fields. Crops include wheat, pumpkins and cauliflower.
- The permanent fountain now has a stone-paved square and four planted garden beds.
- West-to-east mountain routes are trade pass, mine and sealed dungeon. The trade tunnel exits through a mountain spur. Mine entrance is (-328,294), height 68 metres; dungeon entrance is (230,445), height about 115 metres. Tunnel shells, arches, timber supports, lights and supplies are built. The dungeon seal remains an intentional barrier. The northwest waterfall is now a mine-side spring; the dungeon has a separate waterfall.
- `SettlementGrid.json` retains 2,756 ten-metre cells, including protected terrain, 849 available cells and 29 building reservations. These cover the castle, manor, academy, training ground, guild, chapel, bank, bathhouse, warehouse, inn, smith, bell tower, shop, four noble houses and twelve commoner houses.
- Future ramparts, towers and six open gates are built but saved hidden under `EraPreviews/LargeTown`. Hidden defenses have no collision. Run `Scripts/toggle_large_town_preview.py` to inspect them.
- Run `Scripts/toggle_iv_build_grid.py` to inspect/hide the editor planning overlay. The grid is saved hidden; player construction gameplay is not implemented.

## Files, recovery and validation

- Current map/assets: `Content/IsekaiVillage/AdventureWorld/`.
- Recovery copy: `Saved/WorldBackups/BeforeFloatingIsland_20260927/AdventureWorld/`.
- Original Map_Village, Map_Overworld and startup-map settings are unchanged.
- Current terrain sources: `Saved/AdventureWorldSource/height_floating_v07.npy`, `IV_Floating_v07.r16`, and Floating v07 masks.
- Rock and water sources: `SM_IV_FloatingUnderside.obj`, `SM_IV_SkyLake.obj`, `SM_IV_SkyRiver.obj` in that source directory.
- `IV_FloatingVisibility.raw` contains one byte per Landscape vertex. The additive `IslandLandscapeAuthoring` editor helper applies it without ordinary terrain-paint normalization. The saved map does not require runtime terrain generation.
- Final checks: `Saved/floating_collision_review.json` and `Saved/floating_render_review.json`. Rendered views are `Floating_Island_Overview.png`, `Floating_Island_Layout.png`, `Sky_Lake_Waterfall.png`, and `Airship_Landing.png` beside this document. Earlier coastal images are historical.

The editor build succeeded. All 194,902 height samples inside the ultimate settlement rectangle remain identical to the coastal source. Ten collision samples cover the farm, plaza, lake floor and removed perimeter. These tests query WorldStatic game geometry: Unreal deliberately supplies a separate hole-free Visibility collision surface for editor sculpting, which must not be mistaken for gameplay collision.

Do not rerun early gray-box, coastal or village generators over the current map. Authoring scripts have version-specific assumptions; some reject duplicate application.

## Remaining production work

This is a developed environment, not a finished AAA game. Further art and lighting polish (including distant shadow transitions), full character traversal/navigation, edge-fall recovery, underwater handling, airship docking gameplay, dungeon gameplay, packaged performance, construction UI, costs/ownership, NPC activity, horde gameplay and complete era-specific building models remain. The map reserves space for those systems.






