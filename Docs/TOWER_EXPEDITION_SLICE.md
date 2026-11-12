# First tower expedition: Rootbound Threshold

This is the first playable exploration prototype for the hybrid tower. It preserves Elrhun, the village and existing systems. Four configurable modules form the Arrival Terrace, Root Garden, Crystal Hollow and Quiet Camp, connected by supported bridges. It is one floor, with no fixed commitment to 100 floors or the eventual endgame floor count.

## Playing

Create and select a housed adventurer at the adventure hall (H), and pack **2 bread**. At the rune near the foot of the existing tower steps, press **G** to depart. The selected adventurers travel with the player and follow the explored route; villagers continue their work. The entry gate accepts G or V to return.

G gathers a nearby deposit. Garden stone is accessible immediately. Hollow crystals require defeating this visit's slime guardian. Approach the guardian rune with the party, then G begins the command encounter. Commands 1-6 use the learned battle skills from the existing sparring system; J retreats or closes the result. Guardian health and damage vary deterministically with floor seed and visit. The first expedition remains nonlethal and does not generate inherited soul stones.

At Quiet Camp, G establishes a persistent camp for **4 wood + 2 stone**. G again rests the travelling party, reducing fatigue by 35 once per visit. V returns to Elrhun from an established camp. Later departures arrive at that camp. Resources deplete for the village day and renew on later days; leaving and re-entering does not refresh them. The same saved floor seed keeps deposit identity, position and yield stable.

Gathering, camp construction/rest, guardian clears and departure save with inventory, roster and village state. Failed resource/camp/departure saves restore charges and progress. F5 also saves. Saving and quitting during an expedition preserves the floor and inventory; the next session starts safely in the village. It does not restore an unfinished fight or leave village actors at remote coordinates.

## Implementation and next increments

ATowerExpedition exposes module definitions, connections, materials, costs, interactions and status to Blueprints. Generated floor geometry is bounded and reused, with separate entry, resource, camp and encounter roles. It shares the existing world for this slice, avoiding whole-map travel destroying the village session. Companion capsule sweeps follow the player's route, with a lane offset for passing, rather than using town streets inside the floor. The village save retains their original village positions while away.

The floor currently uses simple modular prototype scenery and the approved existing golem outfits/slime. It is not the finished floor art or a full dungeon-management expansion. Next increments are authored region Blueprint art, encounter variants, expedition health/TP persistence, player battle participation, permanent death and inventory soul-stone inheritance, followed by additional floor definitions and streaming. Final boss, crystal revelation, New Game Plus and indefinite lower floors remain future milestones. No existing character geometry or source packs were edited for this slice.

The agreed direction for later floors is in [Tower floor design](TOWER_FLOOR_DESIGN.md).
