# Historical coastal-world handoff

**Superseded by `Floating_Island_Handoff.md` on 27 September 2026.** The ocean geography, northwest dungeon location, crop stand-in, and unfinished defenses described below are historical. Use the newer handoff for the current map.

Updated 27 September 2026. Open `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure` in Unreal. The original Map_Village and Map_Overworld maps were preserved; the startup map setting was not changed.

## Current world

The adventure map contains a native Unreal Landscape with grass, paths, sand, rock and mountain materials, a southern shore and harbor, eastern coastal cliffs, northern/western mountains, forest routes, a fountain village, reused stylized building assets, foliage, lighting, and a northwest magical entrance. This is an environment implementation, not a finished playable settlement game.

## Farm correction

The farmhouse now sits at world XY (130, -98) metres, close to the village. Its four 24 × 26 metre fields are centered at (110,-145), (146,-145), (110,-181), and (146,-181). The farm terrace is level at elevation 24.5 metres with blended terrain edges. Unreal collision measurements confirmed the same height at the farmhouse, all four field centers and the access lane.

The village road reaches the farmhouse. A separate service lane and cross lane run between fenced fields instead of through planted beds. Wheat and pumpkins reuse existing project assets. The former southern farm soil and road have been returned to grass. One crop variation currently uses shorter wheat as a visual stand-in rather than a distinct vegetable asset.

## Full settlement construction plan

See `Settlement_Master_Plan.png` in this directory. The logical grid uses 10 metre cells across a 520 × 530 metre planning area (X -220 to 300 metres, Y -230 to 300 metres). Its 2,756 cells include protected land; 849 cells are currently available and 29 designated building reservations are defined. The irregular planned rampart boundary sits inside this rectangle, stepping around the relocated farm. Roads, occupied buildings, steep ground, farmland, the grand square and defense corridors are excluded from ordinary placement.

The 29 reservations cover castle, lord's manor, academy, training ground, adventurers guild, chapel/church, bank/treasury, bathhouse, warehouse, inn, blacksmith, bell tower and general shop, plus four noble-house and twelve commoner-house plots. Existing village buildings such as the bakery remain protected. Smaller buildings use 20 metre footprints, civic buildings generally 30–40 metres, and the future castle 60 metres. Future streets and gate approaches are reserved without replacing the meadows with paved roads.

The GDD's timber Village, stone Large Town and regal Kingdom stages drive the construction catalogue. Homestead/Barony progression labels and full unlock balancing still need gameplay integration. Era entries describe intended variants; complete models for every era have not been created.

## Grid display and validation

In Unreal, use **Tools → Execute Python Script** and select `D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/toggle_iv_build_grid.py`. Run it again to hide the overlay. Green marks available cells, amber reserved cells and red protected cells. The overlay is saved OFF and its actors are editor-only. When explicitly shown, it may also be visible during an editor play session; hide it before playtesting.

Plot markers are in the Outliner under `BuildGrid/Reserved Plots`; gate markers are under `BuildGrid/Defense Reservations`. The grid supports placement checks for bounds, protected land, era, footprint, reserved building type, occupation and foundation relief. It is currently a Python planning/validation layer, not a player-operated building interface. Five automated tests pass, covering reservations, era restrictions, occupancy/release, protected cells and overlap. The editor overlay was visually checked and its OFF/ON/OFF toggle verified.

## Northwest route

Follow the Whisperwood route from the village toward the northwest forest and mountain ridge. The magical seal now sits around XY (-349,276) metres, screened from the main settlement. Veil Falls uses the existing SoStylized animated waterfall mesh, with a roughly 21 metre fall feeding a spring pool at XY (-349,263), water elevation 78.8 metres. The native Landscape basin has a 77.5 metre floor and raised/blended banks. Only 518 height samples changed, confined to the basin; the village and flat farm terrain were preserved. Forty-three foliage instances were cleared from the basin area. The seal remains behind the falls with a dry northern approach. A playable cave/dungeon interior and expedition interactions remain unfinished.

The waterfall and farmhouse were visually inspected in Unreal, including a farmhouse road view at player height. `Waterfall_Review.png` shows the saved environment. Unreal closed during the subsequent farmhouse image export, so no farmhouse image was produced; the editor was left closed. These are environment inspections, not a completed character/navigation playtest.

## Files and recovery

- Map and generated assets: `Content/IsekaiVillage/AdventureWorld/`.
- Grid/catalogue/reservations: `Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json`.
- Plan checks: `Content/IsekaiVillage/AdventureWorld/Design/PlanValidation.json`.
- Farm terrain and source masks: `Saved/AdventureWorldSource/`, including `IV_Adventure_Farm_v02.r16` and `T_IV_Biome_Farm_v02.png`.
- Latest terrain source (includes both farm and waterfall): `Saved/AdventureWorldSource/IV_Adventure_Waterfall_v03.r16`; imported height texture `Content/IsekaiVillage/AdventureWorld/Textures/T_IV_WaterfallHeight_RG.uasset`.
- Waterfall actors: `Adventure/Waterfall` Outliner folder. The existing `Ancient Magical Seal` actor was repositioned behind the water curtain.
- Waterfall verification: `Saved/waterfall_build.json` and `Saved/waterfall_collision_review.json`; reopened-map collision checks confirm the farm remains level at 24.5 metres.
- Collision verification: `Saved/farm_grid_verification.json`.
- Placement logic and tests: `Scripts/settlement_grid.py` and `Scripts/test_settlement_grid.py`.
- Recovery copies: `Saved/WorldBackups/BeforeFarmGrid_20260926/`, including the pre-relocation map and world assets.
- Pre-waterfall map recovery copy: `Saved/WorldBackups/BeforeWaterfall_20260927/Map_AnimeAdventure.umap`.

Do not rerun the original world-dressing generator over this map: the current farm and soil refinements are newer. Plan/apply scripts are authoring tools, not startup scripts.

## Remaining production work

Grand square upgrades, rampart and gate geometry, additional era-specific buildings, player construction UI, saved ownership, costs/unlocks, NPC activity and horde gameplay remain to be built. The grid protects their intended space now. Collision samples and planning tests passed; a full character traversal, navigation and packaged-game performance pass remains necessary. The next practical step is connecting placement previews and validation to the game's construction interaction, then authoring the reserved civic buildings and defenses in stages.
