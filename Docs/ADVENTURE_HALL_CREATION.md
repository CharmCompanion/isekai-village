# Adventure hall: creation and party selection

At an owned, completed adventure hall, press **H**. Collect delivered supplies, choose Tank, Mage, Ranger or Healer, choose the existing male or female body, optionally name the adventurer, then create it. The basic recipe is **6 stone + 4 wood**, with one spare housing bed required. Class choices reuse the approved outfits and set Guard, Magic, Scout or Aid as the starting practice focus. They do not grant free learned skills or passives.

The first available companion slot fills automatically. Use **Bench** and **Make active** to choose the group for the existing Knight School sparring drill (**J** there). Housing supports a larger reserve; resource creation does not impose the legacy six-recruit hiring limit. Active companion capacity still follows the existing skill-grid and town progression. Members away on missions cannot change party status.

Identity, class, body, name, personality, individual learning and active selection use the existing village save. A failed save cancels creation and refunds its materials. Both materials are checked before either is charged. The menu rechecks location, housing, resources and capacity; combat must finish and close before changing the roster. Older recruits keep their prior appearance behavior until given an explicit body choice.

## Implementation

`GolemHall.cpp` owns authoritative creation, housing and selection checks. `GolemHallWidget` supplies a native UMG menu that Blueprints can extend. `VillageRuntime.AdventurerMeshes` maps the eight existing class/body outfits; the setup script configures those references on Map_ElRuhnSky. The original body, clothing and source packs are reused without editing their geometry.

This completes village-side preparation for expeditions. A modular tower floor, departure/return flow, permanent death, inherited soul stones, rare crafting recipes, class combat statistics and in-battle reserve swaps still require implementation. This menu does not imply those systems are finished.

## Verification

Eleven automated tests passed (one existing construction test reports cleanup warnings), 34 live menu checks passed, and 12 checks passed after a fresh editor restart. The final rendered menu was visually reviewed after increasing roster space. Tests use isolated saves; the normal map slot is preserved. Evidence: [Validation](VillageReview/2026-11-07/AdventureHall/Validation.json), [rendered menu](VillageReview/2026-11-07/AdventureHall/Controls.png).
