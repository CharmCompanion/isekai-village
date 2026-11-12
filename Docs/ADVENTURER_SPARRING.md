# Learned skills in adventurer sparring

Added 6 November 2026 to Tower of Elrhun. This is the first command-based battle integration for the individual needs/learning system.

## Playing

Build the Knight school (training yard) and homes for your existing reserve adventurers. Select active members through the existing party state; the encounter respects its current companion capacity and requires housed village actors. Stand at the yard frontage and press **J**. Members walk to supported standing positions using their existing collision and street routes. Sparring begins after everyone arrives. J stops assembly or combat; on the result panel, J closes the result.

| Key | Action | Effect |
|---|---|---|
| 1 | Strike | 16 physical damage; no TP cost. Successful hits practise Guard. |
| 2 | Defend | Basic defence, available before learning a skill. Reduces incoming damage by 25%. |
| 3 | Guard Stance | Requires the personal unlock; costs 4 TP and reduces incoming damage by 65% until the next own turn. |
| 4 | Arcane Bolt | Requires the unlock; costs 8 TP and deals 30 damage to a visible target in range. |
| 5 | First Aid | Requires the unlock; costs 6 TP and restores up to 25 health to the most injured living ally. Blueprint menus can supply a specific friendly target. Cannot revive a knockout. |
| 6 | Evasive Step | Requires the unlock; costs 5 TP and evades the next incoming strike before the next own turn. |

The panel shows each participant's health and TP, the slime's health, current actor, readiness order, locked skills, actual TP costs and recent events. Time waits for the player's command. Action recovery costs affect readiness; Fleet Footed makes an adventurer ready sooner. Enemy commands have a short readable delay. This is an adventurer drill commanded by the player; the player character is an observer.

Existing passives have battle effects: Focused Mind reduces TP costs by 10%, Enduring Core reduces incoming damage by 10%, and Calm Core improves First Aid by 10%. Their previous village effects remain.

## Learning and safety boundaries

Successful strikes and actual guarded hits award personal Guard practice. Successful Arcane Bolt, First Aid and actual evasion award Magic, Aid and Scout practice respectively. Raising defence or evasion without being attacked awards no practice. Locked skills, invalid/full-health targets, failed hits, insufficient TP and commands outside the member's turn spend no TP, readiness or practice. Personal unlocks can become usable during the same encounter.

Sparring uses temporary health and TP. It produces no resource loot, permanent deaths or soul stones. A knockout ends that participant's contribution, rather than deleting the adventurer. Cancellation, victory and world shutdown release village actors. Normal village jobs and needs resume afterward. Combat-earned practice and fatigue use the existing roster/village save, including F5 and normal encounter-end saving. A saved game does not restart an unfinished sparring encounter.

The water-slime Blueprint is configured on the active sky map. Its autonomous real-time casting is disabled only on the spawned training instance; the existing slime magic demonstrations remain intact.

## Current limits

This is a safe training encounter, rather than the complete tower battle system. Expedition encounters, player participation, in-battle bench swaps, class statistics, permanent death, soul-stone recovery and battle transitions remain later work. The [adventure hall](ADVENTURE_HALL_CREATION.md) now creates adventurers from resources and lets the player select the active group before sparring. Combat animation and effects are preliminary: existing golem bodies and slime art are reused, with a rune burst for Arcane Bolt. No changes were made to clothing, hands or original asset packs.

## Verification

Native tests cover skill effects, TP, locked/invalid commands, real guarded/evaded hits, personal combat learning, two-member readiness order, friendly healing, victory/cancellation cleanup, no loot, no permanent roster deletion and persistence. Live tests use isolated saves, the real J and action keys, actual assembly walking and a fresh editor process. Starting practice is explicitly seeded as test-fixture data; only measured battle increments are described as live-earned. See the current validation and live reports for observed results.

Verified: **9 automated tests passed, 30 live checks passed and 8 checks passed in a fresh editor process**. Actual J and 1–6 command inputs assembled the adventurer, rejected a locked skill, learned Guard Stance from a real block, applied the learned damage/healing/evasion effects, resolved victory, released the village actor and saved combat growth. The rendered panel was visually reviewed in a small court, moved to the bottom right and cleared of the normal NPC proximity prompt. The normal map save slot was preserved and isolated saves removed. Evidence: [Validation](VillageReview/2026-11-06/Sparring/Validation.json), [rendered controls](VillageReview/2026-11-06/Sparring/Controls.png).
