from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
for script in ['apply_civilizations_v30.py','polish_civilization_palette_v30.py','final_continent_material_v30.py']:
 exec(compile((B/'Scripts'/script).read_text(),script,'exec'),{'__name__':'__main__'})
