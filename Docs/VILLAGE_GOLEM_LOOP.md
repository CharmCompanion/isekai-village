# First golem village loop

The first village milestone connects player-built housing and shops to civilian golems. It applies to the dedicated El Ruhn sky village. Older maps keep their original citizen behaviour.

## Playing the loop

Place the inherited home or another home, then build a general shop. A shop gains one golem worker when a player-built home has an unused bed. One bed in the inherited home is reserved for the player. A loft adds another worker space. Existing scenery buildings are preserved; they do not supply owned worker housing in this milestone.

Use B for the catalogue, the mouse wheel or Page Up/Page Down to select, R to rotate, and T or left click to place. Completing a shop before housing leaves the shop waiting; adding a home later fills the vacancy. Repeated updates and reloads retain worker identities rather than making duplicate workers.

The shopkeeper walks along the authored streets and frontage access paths. Its collision capsule checks movement and ground height. If an obstacle blocks the route, it waits and resumes when the obstacle clears. The last time window is for going home; trade requires the shopkeeper to be at work. Each village time window lasts one minute.

At a staffed shop entrance, T sells one wood for two coins; Y buys one wood for two coins. The player and shop must have the required materials, coins and stock. Each shop has its own till and stock. This is the initial useful trade; additional goods and production jobs are later work.

## Persistence

F5 saves. The village also saves periodically and when leaving Play. The construction save now includes worker identities, home/work assignments and positions, per-shop stock and tills, player inventory/tools, skill-grid nodes/points/face state, the existing reserve list, and the village day/window, weather, Trust, food and daily tasks. Older construction-only saves retain their building choices and gain the new state when saved.

This is a village save foundation. It does not implement soul-stone inheritance, adventurer creation/death, tower floor state, depleted-resource persistence, combat encounter saves, or the final-boss story/revival system. Civilian staffing currently covers player-built general shops. Other building jobs and advanced housing/noble-house gates are later milestones.

## Files and recovery

- Runtime: `VillageGolemLoop.cpp`, `VillageGolemCitizen.h/.cpp`, `VillageGolemTypes.h` and the existing village/construction classes in `Source/IsekaiVillage`.
- Map configuration: `Scripts/setup_golem_village_loop.py`.
- Street data: `ArtSource/World/ElRuhnSky02/golem_street_routes.json`, generated from the existing village plan. Workers stop rather than using a long straight-line shortcut when no route is available.
- Live review: `Scripts/playtest_golem_village_loop.py`, followed in a fresh editor process by `Scripts/playtest_golem_village_reload.py`. These use an isolated verification save slot.
- Backups: `Saved/VillageLoopBackup`. The original sky map is retained as `Map_ElRuhnSky_BeforeGolemLoop.umap` before enabling the feature.

## Verified 6 November 2026

The construction and golem shop-loop automation tests passed. They cover housing limits, stable identities, duplicate prevention, trade conservation and rejected trades, construction-save migration, worker obstacle waiting/resuming and a small downward street seam.

The live village run passed 28 checks using actual catalogue, rotation, placement, trade and save inputs. The worker followed the authored streets to the shop. A second editor process passed 11 checks restoring the same identity, home, job, materials, coins, shop stock/till and grid points, with no duplicate worker. Verification purchases used an isolated save slot.

The shopkeeper's stopping point lies on its cleared frontage access path. Movement keeps forward travel separate from settling onto lower ground, so the capsule can cross small paving seams while maintaining floor collision. A shopkeeper remains outside the building in this first milestone; working interiors and crowd avoidance are later work.

The project's startup map now opens the current sky village. Engine debug bindings for Page Up, Page Down and F5 are removed from the game's input settings so the village controls receive those keys. The input review uses single-frame simulated presses; holding the engine's forced-input command emits repeated press events.

Results: `Saved/golem_village_validation.json` and `Docs/VillageReview/2026-11-06`. The older slime-combat automation test still has the same five failures in the original backed-up module and the updated module. That separate issue was recorded without changing combat behaviour.

The next delivery/production milestone is documented in [Village deliveries and production](VILLAGE_WORKER_PRODUCTION.md). It extends the housed worker system to the hall, warehouse, farm, bakery and smith.
