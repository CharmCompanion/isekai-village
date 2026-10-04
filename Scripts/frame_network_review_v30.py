from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/render_puzzle_continent_v30.py');s=p.read_text();s=s.replace("views.append(('Civilizations30_'+name,(x+6200,y-8700,z+8200),(x,y,z)))", "views.append(('Civilizations30_'+name,(x-6200,y+8700,z+8200) if culture=='farming' else (x+6200,y-8700,z+8200),(x+2000,y-3500,z) if culture=='farming' else (x,y,z)))")
# A close review of the new dry-bank crossing, with both bridge approaches visible.
s=s.replace("views.append(('Civilizations30_Island'", """meta=json.loads((B/'Saved/AdventureWorldSource/world_design_v30.json').read_text())
if meta.get('bridges'):
 p=meta['bridges'][0]['points_m'];x=(p[0][0]+p[-1][0])*.5;y=(p[0][1]+p[-1][1])*.5
 views.append(('Civilizations30_TidalBridge',(x+750,y-1100,-20020),(x,y,-20590)))
views.append(('Civilizations30_Island'""");p.write_text(s)
