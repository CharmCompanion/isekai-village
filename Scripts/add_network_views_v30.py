from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/render_puzzle_continent_v30.py');s=p.read_text();a=s.index("views.append(('Civilizations30_Island'")
s=s[:a]+'''for name,culture in [('RabaricNetwork','farming'),('KelsinNetwork','arcane'),('DesertRoutes','nomad')]:
 q=next(q for q in land if q['culture']==culture);x,y=q['xy_m'];z=q['z'];views.append(('Civilizations30_'+name,(x+6200,y-8700,z+8200),(x,y,z)))
'''+s[a:];p.write_text(s)
