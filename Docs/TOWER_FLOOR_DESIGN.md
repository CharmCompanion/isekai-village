# Tower floors: The Tower Remembers

Design agreed with the user on 9 November 2026. Nothing here is implemented yet. It replaces hand-built floors with rule-driven floors so new content does not need new Unreal level work.

## Story fit

The tower is alive and feeds on the life force of the golems and the player. It studies how the party fights and adapts each floor against it. Its memory of the player survives failed runs, so later attempts face a tower that already knows them.

## Floors are rules, not maps

A floor is a reusable room set (currently Arrival, Garden, Hollow and Camp from `TOWER_EXPEDITION_SLICE.md`) with a theme plus rules. The rules choose enemy types, count, intelligence, stats and elements. The floor count is not fixed. 100 floors and a final boss are the working target; New Game Plus adds negative floors without a limit.

## 1. Floor log

While a floor is played, record:

| Habit | Measured from |
| --- | --- |
| Element | Damage dealt with Fire, Water, Earth and Wind |
| Style | Guard, Magic, Scout and Aid actions. These are the existing practice types. |
| Carry | Share of damage and actions per adventurer and class |
| Tempo | Turns per fight |
| Cushion | Healing, guarding, evasion and camp rests |
| Ease | Turns taken, damage taken, knockouts |

## 2. Threat budget

After a clear, Ease becomes the next floor's threat budget. An easy clear raises it. A near-wipe lowers it slightly, never below the floor's base difficulty. The budget buys:

- enemy count and stats
- an intelligence tier
- counter rules

## 3. Counter rules

Each counter shuts down a habit and opens a weakness, so the player is pushed to switch tactics rather than simply punished.

| Habit | Counter | Opening |
| --- | --- | --- |
| Fire | Water-aligned enemies, damp floor | Earth and Wind hit harder |
| Burst damage | Shields, enemies split on death | Damage over time, area hits |
| Healing | Wither: less healing received | Guard and evasion |
| Guarding | Guard-breaking attacks | Evasion, fast kills |
| Evasion | Area attacks that always hit | Guarding, healing |
| One carry | Enemies mark and focus that unit | Bait with the tank |
| Large party | Fewer, larger elites | Focused single-target damage |

Element wheel, provisional: Water beats Fire, Fire beats Wind, Wind beats Earth, Earth beats Water. The four elements are the existing `EElement` values.

## 4. Enemy intelligence

1. **Instinct:** random target and action.
2. **Hunter:** targets the lowest-health ally.
3. **Tactician:** kills the healer first, holds its guard for big hits, focuses one target.
4. **Mimic:** copies the party's most-used skill.

## 5. Telling the player

On arrival, the floor announces what the tower adapted, for example "The tower remembers your flame." The player should always know why a floor is harder and where the opening is.

## 6. Memory fades

Habits fade over a few floors. Varied play keeps the tower unsure and lowers the counter spend. Varied play can earn rarer tower materials, which feed golem creation.

## 7. Bosses & Floor 100 Finale

Milestone exam bosses every `5`/`10` floors build kits from the party's top habits over that stretch. Rising **Adventure Guild Rank** (`D -> C -> B -> A -> S`) and Town growth (`Village -> Large Town -> Kingdom`) unlock deeper party capacity, research, gear, and trip charges needed to survive up to **Floor 100**, where the **Crazed Immortal Wizard** guards the apex and unlocks NG+ negative floors.

## 8. Portals after a clear

| Portal | Appears | Effect |
| --- | --- | --- |
| Village | Always | Ends the run safely. See section 10. |
| Camp | When this run's camp is built | Pause: rest, resupply, return to the same point |
| Forward | Always | Next floor, normal budget |
| Leap | Only after a strong clear | Skip 2 floors, or 3 after a perfect clear. Harder, better rewards. |

There is no back-a-level portal. The village gate can send the party to any previously cleared floor for farming.

Leap rules:

- The skipped floors' budgets are added to the landing floor.
- Habits do not fade over skipped floors.
- Rewards are better tower materials, better soul-stone quality and progress toward the boss.
- Leap is not offered on the first few floors or right before a boss floor.
- Each portal shows its consequence before entry, for example "Leap +2: the tower will remember your Fire. Reward ×2."

## 9. Camp and respawns

Camp is the pause. Resting there, or returning through it, respawns regular enemies on the cleared floors of that stretch.

- Respawned enemies are re-picked using tower memory, not copied.
- Each rest makes the respawn a little stronger.
- Respawned enemies drop basic materials only.
- Bosses do not respawn while the run continues.

### Trips home from camp

Camp has a portal to the village that keeps the run. The number of trips per run comes from the adventurers' guild rank:

| Guild rank | Trips home per run |
| --- | --- |
| D | 1 |
| C | 2 |
| B and above | 3 |

Trips home are for restocking, selling, crafting and creating adventurers. On return, regular enemies have respawned.

Rank values D=0, C=1, B=2, A=3 already exist on individual adventurers in `IsekaiVillageTypes.h`. A guild-level rank still needs defining; one option is the highest or average rank of the guild's adventurers.

## 10. Ending a run

| Event | Bosses | Camp | Adventurers | Carried loot |
| --- | --- | --- | --- | --- |
| Rest at camp | Stay dead | Kept | Kept | Kept |
| Trip home from camp | Stay dead | Kept | Kept | Kept |
| Village portal | Respawn | Lost | All live | Kept |
| Main character dies | Respawn | Lost | The dead stay dead; their soul stones are kept | Partly lost |

Main character death means waking at the soul stone in the player's house. Tower memory is kept in both endings.

## 11. New Game Plus: negative floors

- No floor limit. Memory does not fade.
- Counter rules stack, two or three per floor.
- **Echoes:** fallen golems return as enemies with their soul-stone traits and skills.
- Difficulty keeps rising while clears stay easy.

## Implementation pieces

1. Floor log: habit counts from combat and the floor, saved with `FTowerFloorProgress`.
2. Counter rule table: data, editable without code.
3. Budget spender: picks enemies, intelligence tier and rules for the next floor from the log.
4. Portal choice after a clear, including Leap and its preview text.
5. Camp respawns and guild-rank trip charges.
6. Run end and failure handling: boss respawn, camp loss, death and soul stones.

## Open decisions

- Element wheel order.
- How strong a clear must be to offer Leap.
- Guild rank (`D -> C -> B -> A -> S`) rises from completed floor milestones, Trust, and standing Adventure Hall / Academy / Castle infrastructure; controls expedition trips home and party power ceilings.
- What portion of carried loot a death loses.
- Boss spacing across Floors 1–100 culminating in the Crazed Immortal Wizard on Floor 100.
