# Mapped world and neutral El Ruhn — v23

The playable floating island is the Kingdom of El Ruhn, a small neutral sovereign country. Its current playable size, terrain, town and matching rock foundation are preserved. This establishes world geography and scenery; diplomacy and playable neighboring cities are not implemented here.

## Reference geography
The supplied map.png, Biomes.png and kingdom masks in GuildFounder-DesktopCopy/BaseProject/assets/map guide the continent. Original reference assets remain untouched. West is Yozuan desert; north is Gosain with connected mountains and snow; east is Kelsin; southwest is Rabaric; southeast is Vylfod. Plains, forest and jungle follow the supplied biome layers. North is +Y and map east is -X in the Unreal scene.

The mainland atlas spans approximately 141 by 95 km. The reference is geographic guidance, not a literal survey of the existing 1.2 km playable island. El Ruhn retains its existing dimensions and matching hollow, with the mainland translated 20 km below it.

## Scenery changes
- Continuous terrain mountain ranges replace the scattered mainland rock and cliff instances.
- Wooded remnant slopes, hills and mountain branches remain around the opening.
- Nine mapped inland lake basins supplement the local river and lake system.
- Five city, ten town and twenty-five village areas suggest settlement at distance, with thirty-five connecting routes. These are proposed scenic locations, not named settlements supplied by the reference.
- Distant settlement areas use subtle surface patterns, without individual house meshes or rectangular farm grids.
- The enlarged sky dome accommodates the wider continent.

## Validation
The v21 island foundation remains paired with its exact inverse cavity: maximum reported fit error 2.3e-12 metres, zero internal open edges and zero nonmanifold edges. The exported river bed was sampled at 1,201 positions: zero obstructions and minimum water clearance 2.23 m. Playable island landscape is unchanged.

## Continue work
Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
World data: Docs/WorldDesign/El_Ruhn_World.json
Source data: Saved/AdventureWorldSource/world_design_v23.json
Scripts: prepare_world_reference_v23.py, build_puzzle_continent_v23.py, apply_puzzle_continent_v23.py, final_continent_material_v23.py, render_puzzle_continent_v23.py.
The live editor uses Scripts/adventure_editor_session.py and Saved/adventure_request.json. The latest application request is 170; final cleanup and render request is 171.
