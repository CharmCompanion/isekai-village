# Kingdom civilizations — v33

Mainland towns are no longer circle clearings. Each kingdom now has a capital with an impossibly tall magic spire, lesser cities, and smaller settlements whose footprints follow biome, terrain and lore. El Ruhn’s playable village, farm and dungeon path were not moved.

## Hierarchy

One capital per mainland kingdom:

| Kingdom | Capital | Form |
|---|---|---|
| Divine Empire of Gosain | Both northern islands (cathedral citadel + monastery quarter) | Walled religious castle-city, coastal curtain, stone bridges |
| Yozuan Desert | Caravan capital on the canyon rim | Elongated tent souk along the wadi |
| Kelsin Federation | Arcane manufacturing capital | Chamfered workshop blocks, conduits, crystal spire |
| Rabaric Republic | Farming capital on the survey grid | Elongated market town in the crop lattice, mill and granary |
| Vylfod Dominion | Tidal capital | Linear stilt quays along the channel |

Lesser cities: mainland Gosain abbey-city, Vylfod tidal harbor, and two promoted towns in each kingdom. Villages are single lanes or short hamlets, not rings.

## Gosain island city

The citadel and monastery islands are one capital. Outer `SM_Civ33_EmpireWall` follows each coastline (much taller than the old 38 m curtain). A rectangular inner precinct holds the cathedral and the capital spire. Dense street-grid towns sit on both islands (cathedral city + monastery quarter), with mid-block alleys, plazas, shops and street furniture. A stone bridge joins the islands; a second span reaches Gosain mainland.

Vylfod’s capital is a floating pleasure city west of the continent (`SM_Civ34_PleasureIsle`): canals, boardwalks, stalls, lanterns and a spire.

## What stayed

El Ruhn buildings, landscape, lake and foundation. Mainland terrain, farms, oasis palms, tidal reeds and the existing road network.

## Apply

Project: `D:/DEVELOPMENT/Games/IsekaiVillage`  
Map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`  
Build: `Scripts/build_civilization_assets_v33.py`, `Scripts/build_civilizations_v33.py`  
Editor: `Scripts/apply_civilizations_v33.py` (delayed runner)  
Renders: `Docs/WorldDesign/Civ33_*.png`
