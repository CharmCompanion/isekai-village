from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
for name in ['import_surface_normals_v28.py','final_continent_material_v28.py']:
 exec(compile((B/'Scripts'/name).read_text(),name,'exec'),{'__name__':'__main__'})
