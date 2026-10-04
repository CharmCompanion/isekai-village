from pathlib import Path
import shutil
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');P=B/'Scripts';S=B/'Saved/AdventureWorldSource'
backup=B/'Saved/WorldBackups/BeforeNetworks_v30';backup.mkdir(parents=True,exist_ok=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
for stem in ['build_puzzle_continent','world_reference','civilization_ground','refine_scenic_mesh','build_world_surface','import_surface_normals','apply_puzzle_continent','clean_puzzle_details','apply_terrain_remnants','final_continent_material','build_civilization_assets','build_civilizations','apply_civilizations','polish_civilization_palette','render_puzzle_continent','verify_civilizations']:
 t=(P/(stem+'_v29.py')).read_text()
 for a,b in [('_v29','_v30'),('Atlas29','Atlas30'),('Biomes29','Biomes30'),('Surface29','Surface30'),('Final29','Final30'),('Water29','Water30'),('Civ29','Civ30'),('Civilizations29','Civilizations30'),('terrain29','terrain30')]:t=t.replace(a,b)
 if stem=='apply_puzzle_continent':t=t.replace("['SM_IV_PuzzleContinent_v28',name]","['SM_IV_PuzzleContinent_v29',name]")
 (P/(stem+'_v30.py')).write_text(t)
shutil.copy2(B/'Saved/civilization_assets_v29.json',B/'Saved/civilization_assets_v30.json')
