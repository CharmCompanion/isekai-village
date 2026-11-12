# Tower of Elrhun — village status

**7 November hall update:** H at an owned adventure hall opens resource creation and party selection. Four basic classes use the eight existing body/outfit combinations. Creation costs 6 stone and 4 wood plus a free bed; housing supports a reserve beyond six, while the existing progression limits the active party. Eleven automated tests, 34 live menu checks and 12 fresh-session checks passed. See [Adventure hall creation](ADVENTURE_HALL_CREATION.md). Earlier sections below preserve the original review findings.

**6 November combat update:** active reserve adventurers can now walk to a player-built Knight school and take part in nonlethal turn-based sparring. Learned skills and passives affect damage, defence, healing, evasion, TP and readiness; combat can award personal practice. Nine automated tests, 30 live checks, eight fresh-session checks and a rendered UI review passed. See [Adventurer sparring](ADVENTURER_SPARRING.md) for controls and remaining tower-combat work.

**6 November organic-behaviour update:** saved needs and personality now guide work, recharge, company and practice. Housed existing reserve members can practise and earn personal skill/passive unlocks. Seven automated tests, 24 live checks and seven fresh-session checks passed. See [Golem wants and learning](GOLEM_WANTS_AND_LEARNING.md) for the current behaviour and the remaining party-combat connection.

**6 November production update:** village collection depots, hall/warehouse haulers, the existing farm, bakery and smith production now have an implementation and automated coverage. See [Village deliveries and production](VILLAGE_WORKER_PRODUCTION.md) for recipes, controls, live verification and remaining limits. The slime damage fixture and immune-target ward handling are corrected.

**6 November update:** the first player-built home/shop/go-lem-worker loop is now implemented and verified, including real controls, street movement, trading and a fresh-session reload. See [First golem village loop](VILLAGE_GOLEM_LOOP.md). The remainder below preserves the 5 November review; its missing-work list predates that milestone.

Reviewed 5 November 2026 in the copied Tower of Elrhun project. This review inspected source, loaded the current village, entered Play, captured the actual player view, and ran the existing construction automation test. No gameplay code, maps, building purchases, or player saves were changed for this review.

The village has a substantial environment and construction prototype. The newer golem population, adventurer creation, soul inheritance and expedition systems are not yet connected to it. Most existing work can be reused.

## What is present

The current dedicated village is `/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky`. It has the floating island, tower exterior, streets, fountain area, forest, lake, farmland, existing building exteriors and reserved building land. The tower interior is unfinished.

The live village runtime has 37 plot records: 28 unassigned parcels and nine existing records, including the farm. There are 18 catalogue entries. Those include the inherited home, three ordinary home choices, the guild and service buildings, manor and castle. Several specialist buildings reuse the same exterior. There is no separate noble-house category or a housing-quality requirement system in the inspected runtime.

Construction source supports player selection of a building and parcel, quarter-turn rotation, a tinted preview, material costs, era gates, unique founding buildings and a house loft upgrade. Construction saving records built plots, selected catalogue IDs, orientation and lofts. Placed shops, guilds and smiths have service interaction hooks. These hooks are foundations, not complete staffed businesses or finished interiors.

The older town simulation includes residents, visitors, beds, job destinations, needs, shop stocks, Trust, weather and daily tasks. Tree chopping, ore gathering, tool upgrades, inventory, a reserve roster and the Sphere Grid also remain in the project.

## What the running village actually does

- It starts with two resident haulers and one visitor, all using the engine's cylinder mesh. The new male/female golem actors are not spawned by the village runtime.
- Residents are seeded at startup; additional visitors arrive on a timer. Completing a building does not create its golem staff.
- Beds influence visitor settlement. Town-era purchase gates use Trust and unlocked sphere-node counts, rather than required numbers or quality levels of houses and noble homes.
- Citizen movement directly moves actors toward destinations without collision sweeps or navigation. It needs proper routes around buildings before replacing the placeholders with finished characters.
- The reserve is capped at six recruits and starts empty. The initial active party cap is two including the player. This is an older recruitment list, not the intended flexible golem roster and party-selection system.
- The village spawns the native mannequin player pawn. The intended player appearance and any future race choices still need to be connected to the active game setup.
- The configured default startup/play map is still the older `/Game/IsekaiVillage/Maps/Map_Village`; the dedicated sky village must currently be opened explicitly.

## Work still required for the new plan

| Area | Needed work |
|---|---|
| Civilian golems | Connect the approved bodies/outfits to village citizens; spawn staff from completed buildings; assign persistent homes and jobs; respect housing capacity. |
| Village progression | Add house counts, housing quality/noble residences and service requirements to settlement progression. Reconcile these with the existing Trust and grid gates. |
| Economy | Turn service hooks into staffed shops/workplaces with clear production, stock, resource use and player interactions. Keep basic village resources available and distinguish special tower materials. |
| Adventurer creation | Add creation recipes and resource costs, persistent individual golem records, class/body choice and a roster/party-selection screen. Remove the old six-recruit assumption from the new design. |
| Soul stones | Store individual stones in inventory, with their rolled trait, skill, stats and growth history. Let the player choose which stone to implant. Connect adventurer death, stone recovery and later hybrid inheritance. Gem colours currently provide appearance, not this gameplay. |
| Player revival | Connect death to the soul stone in the player's chosen house. The story explanation and final-boss reveal are not gameplay implemented by the current house system. |
| Persistence | Save and restore residents, home/work assignments, inventories, economy, roster, stones and relevant character/grid progression together. The inspected village save covers construction only. Broader legacy save code is retained under Migration and is not proof of an integrated current save. |
| Tower connection | Finish a usable entrance and one small expedition floor, then connect departure, return, resources and recovery to the village. The old dungeon graph prototype is reusable groundwork, not the new modular floor/camp/resource system. |
| Presentation | Finish the ground/road and grass materials, building identity, useful interiors and player appearance. The player view is lit; initial single-frame capture darkness was not a reliable measure of gameplay exposure. |

## Recommended next milestone

Finish one small village loop before expanding the catalogue:

1. Place a home and a shop on the existing parcels.
2. Completing the shop creates one civilian golem, provided a home is available.
3. The golem receives a stable identity, a home and a shop job, and walks safely between them.
4. The shop supports one useful trade or production cycle.
5. Quit and reload: the buildings, golem, assignments, inventory and shop stock return correctly.

After that, add a small adventurer-creation station and one craftable class, then connect that adventurer and a recoverable soul stone to one tower expedition. This builds on the existing systems without committing to a large floor count or constructing every planned building first.

## Verification and limits

- The current sky map loaded and entered Play successfully. The captured player had PartyReserve, BuildEdit, GatherInventory and TreeChop components.
- `IsekaiVillage.Construction.AuthoredPlots` passed, with temporary test-world cleanup warnings. Its checks cover charging, era restrictions, placement, unique deeds, lofts and save/reload. No test failures were reported.
- The older `ElRuhnSky02/play_verification.json` still records a timeout while simulating catalogue scrolling. The complete mouse/keyboard construction flow was not re-certified in this review. A passing logic test does not resolve that historical input-test gap.
- The village map's SHA-256 was identical before and after the inspection.
- Native material warnings include the foothill-rock instancing usage flag. The actual player capture shows grey grass and checkerboard ground surfaces; a material pass and packaged rendering check remain necessary.
- The source review does not establish that every Blueprint or migrated feature is finished. The findings above describe the inspected active runtime and the observed current map.

Evidence: `Source/IsekaiVillage/VillageRuntime.cpp`, `TownBuildingCatalog.cpp`, `TownPlot.cpp`, `VillageCitizen.cpp`, `PartyReserveComponent.h/.cpp`, `TownConstructionSave.h`, `TreeChopComponent.cpp`, `Config/DefaultEngine.ini`, and the saved map inspection. The original source packs and older village/maps remain preserved.
