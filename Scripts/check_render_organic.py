from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');s=(B/'Scripts/verify_refinement_v08.py').read_text().replace('refinement_validation.json','organic_collision_validation.json');exec(compile(s,'organic_validation','exec'),{'__name__':'__main__'});exec(compile((B/'Scripts/render_organic_underside.py').read_text(),'organic_render','exec'),{'__name__':'__main__'})
