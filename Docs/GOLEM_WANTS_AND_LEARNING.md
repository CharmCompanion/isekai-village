# Golem wants and learning

Added 6 November 2026 in Tower of Elrhun. This extends the existing village worker and reserve systems.

## Choices

In the sky village, golems weigh work, recharging, practice and company. Personal diligence, interest in study and sociability are seeded once from each golem's identity, then saved. Fatigue, curiosity and loneliness grow during play. Decisions have a minimum commitment and a preference margin so characters do not change their minds every frame. Severe exhaustion can interrupt a delivery; otherwise a carried delivery or reserved recipe takes precedence over optional activities.

Recharge requires reaching the assigned home. Once recharging, a golem recovers to a safe fatigue level before returning to optional activities. Practice requires reaching a player-built training yard, or an academy for magic. Company requires reaching an inn or hall frontage and having another golem nearby; arriving alone does not satisfy the social need. Unproductive leisure visits have a cooldown. Route blockages never grant learning. Civilian jobs continue to respect homes, actual stock and physical transport.

Farm workers respond to the hall's wheat supply. Production workers consider available ingredients. Haulers choose a new source trip based on the hall's shortage, incoming cargo and travel distance, then keep that source for the trip. They do not change source every frame. Daily basic-resource refills also operate when all workers take a break.

Blueprint gameplay events can use SetGolemNeeds to adjust fatigue, curiosity, loneliness and practice interest; this does not grant learning or change the saved personality.

Nearby golem interaction text shows the current reason, need levels and latest learned ability. Adventurer dialogue shows this personal information rather than attempting a shop trade.

## Adventurers

Existing reserve members can appear as off-duty village golems when spare housing is available. Their roster ID, golem identity, personality, needs and learning remain linked. Civilians keep existing housing assignments; additional housing is needed for adventurers when beds are full. Members assigned to the legacy rampage system are excluded from village practice.

This uses the existing reserve; the new resource-based adventurer creation screen remains separate work. The sky village's normal save is not populated with test recruits.

## Learning

Only completed activity earns progress. Training time counts after physical arrival. Work contributes logistics or craft practice. Future combat Blueprints can call PartyReserve.RecordAdventurerPractice with the member's ID, a supported domain, effort and whether the action succeeded. An invalid or unsuccessful action grants nothing. A single event is capped, and inactive/absent characters do not receive offline learning.

| Practice | Skill at 120 effort | Passive at 300 effort |
|---|---|---|
| Guard | GuardStance | EnduringCore |
| Magic | ArcaneBolt | FocusedMind |
| Aid | FirstAid | CalmCore |
| Scout | EvasiveStep | FleetFooted |
| Logistics | CarefulHandling | FleetFooted |
| Craft | Repair | PractisedHands |

Repeated practice adds to the individual's saved progress. Unlocks are unique and deterministic; there is no per-frame skill lottery. A short personal log records discoveries. Thresholds and names are initial balancing values.

Passives already affect the current simulation: EnduringCore/CalmCore reduce fatigue growth by 25%; FocusedMind improves learning effort by 10%; FleetFooted improves village walking speed by 10%; PractisedHands improves production work rate by 10%. Benefits do not stack repeatedly when a save is reloaded.

Active skill IDs are personal unlocks. They now have real effects in the nonlethal [adventurer sparring controller](ADVENTURER_SPARRING.md): guarding, Arcane Bolt, First Aid and Evasive Step. Successful combat can add personal practice. LearnedArteDefinitions remains available for mapping earned IDs into the older KnownArtes asset list. Tower encounters, player participation and full party battle menus remain later work. The player Sphere Grid is preserved.

## Persistence and compatibility

The sky map enables UseOrganicGolemNeeds. Older maps keep the previous mode. Old construction saves receive default needs and a one-time personality seed; existing IDs, resources, cargo and player progression are retained. All new resident and reserve fields use the existing village save. The mode does not grant free starting recruits or special tower materials.

## Verification

Native tests cover choice priorities, exhaustion, distinct personalities, failed action rejection, per-character unlocks, passive effects, physical practice/recharge and save/reload. Live review uses isolated saves, accelerated game time, real street movement and a fresh editor process. See Saved/golem_organic_playtest.json and the current validation report for observed outcomes. Visual polish, training animations and full party combat are not certified by these tests.

Verified on the final build: **7 automated tests, 24 live checks and 7 fresh-session checks passed**. In the actual sky village, a housed reserve adventurer chose and walked to practice, earned Guard Stance and Enduring Core, then returned home to recharge after exhaustion. The peer had distinct learning, and civilian work continued. Identity, progress, skill, passive and personality survived the fresh process. The isolated save was removed and the normal map save-slot setting was preserved. Evidence: [Validation](VillageReview/2026-11-06/OrganicNeeds/Validation.json).

**7 November creation update:** use the [adventure hall](ADVENTURE_HALL_CREATION.md) to create housed adventurers with resources, choose class/body and select the active group. Individual learning continues through needs-driven activity and sparring.
