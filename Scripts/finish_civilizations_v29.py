from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
for name in ['apply_civilizations_v29.py','final_continent_material_v29.py']:
 exec(compile((B/'Scripts'/name).read_text(),name,'exec'),{'__name__':'__main__'})
