# Village deliveries and production

Added 6 November 2026 to the active Tower of Elrhun sky village. Existing characters, outfits, skill grid and older maps are retained.

## Playing

Build the Adventurers guild (the adventure hall) and enough homes. Each workplace needs one free bed. The inherited home reserves one bed for the player. Existing workers retain their identities and housing priority. The hall hires its courier before new production jobs. Production jobs require a built hall; they wait for housing when capacity is full.

| Workplace | Work |
|---|---|
| Adventure hall | Courier gathers stone, fish and wood at village collection depots, then physically returns each bundle to the hall. |
| Warehouse | Adds a second resource hauler using the same depots and hall store. |
| Existing farm | Farmer makes 2 wheat per 20 seconds at the farm frontage, then carries it to the hall. Requires a hall and a bed. |
| Bakery | Collects 2 wheat and 1 wood from the hall, makes 2 bread at the bakery in 20 work seconds, then delivers the bread. |
| Smith | Collects 2 stone and 1 wood from the hall, makes 1 tool part at the smith in 20 work seconds, then delivers it. |
| Shop | Existing staffed wood trade remains available. |

At the hall frontage, **T collects the delivered stock into your inventory**. The stock display shows what is available. F5 saves. Workers go home during the sleep window; carried cargo and reserved ingredients survive rest and reload. Empty stores pause production at the worker's own workplace instead of granting free items or blocking the hall queue. Stocks and individual cargo are saved alongside the existing village/player state. Worker capsules remain solid; approaching workers keep right on the street. Hall exchanges use a 1.8 m arrival area to avoid a single occupied standing point blocking deliveries.

## Supply depots

The initial implementation uses three labelled collection points on the connected village street network. They represent village-side supply depots, rather than fully animated fishing, quarrying or tree cutting. Each starts with 60 basic resources, gathers in bundles of up to 3 after four seconds at the depot, and refills to at least 60 once on each new village day. It never refills on a same-day reload. The item, location, stock and daily refill amount are editable on VillageRuntime. Set DailyRestock to zero for finite supplies; special tower resources should remain finite.

The street graph now connects the fountain bypass and excludes its solid base; all 36 parcel frontages share one connected network (4,411 nodes). The distant lake and mine still need dedicated worker routes, harvesting animations and direct integration with their resource actors. Bread and tool parts are stored/craftable resource outputs; their later food/tool consumption features are not claimed complete. No adventurer crafting or soul inheritance was added in this milestone.

## Implementation

VillageGolemLoop handles housing/job reconciliation, actual source pickup, recipe input reservation, work timers, return/deposit and hall withdrawal. VillageGolemTypes and TownConstructionSave persist per-worker cargo, reserved inputs, depot budgets and hall storage. Existing saves without the new supply payload retain the map's configured starting depots. The mode remains opt-in for the sky village.

Slime battle tests now use an authority game mode and game instance, so normal pawn damage rules operate in the synthetic test world. Slime damage also checks damage eligibility before consuming its ward. Immune targets keep both their ward and health.

## Verification

See Saved/golem_hall_playtest.json and the current automation export for actual outcomes. The native tests cover housing, trade, routes/collision, delivery conservation, mid-trip saving, production inputs and outputs, rest, daily refills, migration and slime combat. The live script uses a unique test slot and the real sky map, with accelerated test walking/time, then checks collection controls and a fresh editor-process reload. It does not purchase buildings or alter inventory in the player's normal save.

Verified on the final build: **5 automated tests passed, 21 live checks passed, and 5 checks passed in a fresh editor process**. The five workers delivered stone, fish, wood, wheat, bread and tool parts without teleporting. T collected all delivered stock, F5 saved it, and the fresh session restored all five identities, inventory and depleted depot stocks while leaving the withdrawn hall store empty. The isolated test save was removed. Evidence: [Validation](VillageReview/2026-11-06/WorkerProduction/Validation.json).
