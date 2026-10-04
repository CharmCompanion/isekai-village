# Beaches and plausible biome transitions — v24

El Ruhn remains the small neutral floating kingdom. This update refines the surrounding continent while retaining its mapped outline and the detailed island/cavity pair.

## Changes
- Southern Yozuan desert extends into the former light-green western lowlands as a semi-arid sand and grass mosaic. Five spring-fed oasis ponds create greener pockets before the region grades into plains. The existing nine inland lakes remain.
- Broader biome blends replace abrupt color boundaries. A modest interior mountain divide helps shelter the western dry basin from assumed easterly maritime winds.
- Warm low coasts have variable sandy beaches, roughly 160–420 m wide at this scenic scale, wet-sand margins and low coastal shelves rising into coastal plains. Highland coasts retain more exposed rock.
- Northern lowlands use cool scrub/woodland rather than permanent sea-level ice. Snow appears only above about 1,850 m and becomes more extensive higher up. Dense southern/eastern vegetation is humid woodland rather than a claim of equatorial climate.

## Plausibility and limits
This is a compressed fantasy regional geography, not a simulated climate. At roughly 141 by 95 km, the map is too small to explain polar-to-tropical conditions by latitude alone. Elevation, sheltered western terrain and moisture from the east provide a more plausible organizing model. The new oases have authored spring sources represented by ponds; underground aquifers and seasonal flow are world-design assumptions, not simulated systems. Full continental drainage and ocean circulation have not been modeled.

Background references: [National Geographic: rain shadows](https://education.nationalgeographic.org/resource/rain-shadow/), [National Geographic: deserts and oases](https://education.nationalgeographic.org/resource/desert/), [USGS: types of coasts](https://pubs.usgs.gov/circ/c1075/types.html).

## Current project
Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
Current generators/application: Scripts/*_v24.py
World design: Docs/WorldDesign/El_Ruhn_World.json
Sources: Saved/AdventureWorldSource/world_reference_v24.npz and world_design_v24.json
Previous map backup: Saved/WorldBackups/BeforeEcology_v24/Map_AnimeAdventure.umap
Live editor request: 172, apply_puzzle_continent_v24.py
Scenic cities/towns/villages remain distant indications; diplomacy and neighboring settlement gameplay are not implemented.

## Verification
Generated terrain is finite. Five spring lakes and sandy coastal bands are present; no snow-mask cells occur below 1,850 m. The exact island/cavity fit is preserved (maximum error 2.3e-12 m); the mesh has no internal open edges or nonmanifold edges. The nearby river bed was checked at 1,201 exported-mesh positions with zero obstructions and minimum clearance of 2.23 m.
