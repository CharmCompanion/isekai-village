# Regional civilizations — v29

The mainland now has distinct three-dimensional civilizations following the supplied country map. El Ruhn remains a small neutral floating country. This is an environmental art pass: mainland settlements are scenic assets, not NPC simulations, complete building interiors, or a fully navigable second game world.

## Regional identity

- **Northern religious island:** a cathedral citadel, an inner precinct, outer curtain walls, open gatehouses, gold religious emblems, banners, watchtowers and a coastal defense circuit. The second offshore island has a fortified monastery settlement. These islands retain the source map's Gosain affiliation.
- **Yozuan desert:** caravan camps, canvas shelters, carts, markets and spring-side palms identify the nomads. Two separate, remote dark-stone sanctuary compounds identify the cultists. The canyon and its side ravines remain intact.
- **Kelsin Federation:** arcane manufacturing halls, crystal-powered civic towers and visible energy conduits give the region its magic-technology identity. No extractive industries or raw-resource export facilities were added.
- **Rabaric Republic:** farm villages, granaries, windmills, orchards, hedgerows and irregular crop parcels give the lush plains an agricultural economy. Larger fields continue across the regional map.
- **Vylfod Dominion:** low tidal shelves, branching coastal channels, palm groves and reed banks surround stilt settlements. Raised boardwalks link the homes, with a harbor pier reaching the tidal channel and boats on the water.

## Art and placement

Landmarks use rounded towers, beveled masonry, detailed roof courses, buttresses, window recesses and multiple materials. Existing native village, market, tent, tree and boat assets provide the smaller detail. Ground shading changes with viewing distance, adding lit textured surfaces near a camera while preserving the readable continent from El Ruhn. The atmosphere's ground level is now aligned with the mainland sea level.

All settlement items are placed against the actual exported mainland triangles. Foundations extend into the terrain, retaining walls adapt to the slopes, and the tidal buildings use submerged support piles. The 31 sites contain roughly 4,800 homes and tents, plus civic landmarks, defenses, infrastructure and vegetation. Exact instance counts are in the world metadata.

## Validation

- 56,620 grounded instance checks; no ground-level instance more than two metres above its foundation surface. Banners, attached mill sails and floating boats are checked by their intended placement instead.
- Two expected support-pile placements extend below sea level; no unexpected submerged buildings.
- El Ruhn's inverse cavity still matches within 2.3e-12 metres, with no internal open edges or nonmanifold edges.
- The playable island geometry is retained from v28, whose 768 terrain-join and 96 underside collision checks passed.
- Added mainland scenery has not been gameplay-performance benchmarked. The environmental pass does not add mainland navigation, interiors, population AI, quest or trade systems.

## Project continuation

Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
Source: Saved/AdventureWorldSource/world_design_v29.json
Instance plan: Saved/AdventureWorldSource/civilization_instances_v29.json
Validation: Saved/AdventureWorldSource/civilizations_validation_v29.json
Backup: Saved/WorldBackups/BeforeCivilizations_v29/Map_AnimeAdventure.umap

Build order: prepare_civilized_world_v29.py, build_puzzle_continent_v29.py, build_civilizations_v29.py, then apply_puzzle_continent_v29.py in Unreal. Grounding uses the actual mesh and refreshes its cache when that mesh changes. The paired island foundation remains SM_IV_JoinedMountain_v28. Do not independently reshape the cavity or island boundary.

Final material pass: region-specific native house materials preserve the original textures and improve shadow readability. Cult tents and bastions use separate red/dark-stone variants. Removed 584 trees from mapped lake surfaces and clipped 479 crop triangles from water. Native editor validation confirms the new landmark and gate counts and a saved map. Final request 194 applied the finish; request 195 verified the native scene.
