from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/render_puzzle_continent_v30.py');s=p.read_text();s=s.replace("if meta.get('bridges'):","""farm_sites=[q for q in meta['settlements'] if q['country']=='RabaricRepublic']
pairs=[(sum((a-b)**2 for a,b in zip(q['xy_m'],t['xy_m'])),q,t) for i,q in enumerate(farm_sites) for t in farm_sites[:i] if q['kind']!='city' and t['kind']!='city']
_,q,t=min(pairs,key=lambda v:v[0]);x=(q['xy_m'][0]+t['xy_m'][0])*.5;y=(q['xy_m'][1]+t['xy_m'][1])*.5;z=(q['ground_m']+t['ground_m'])*.5
views.append(('Civilizations30_FarmVillages',(x+1900,y-2700,z+2400),(x,y,z)))
if meta.get('bridges'):""");p.write_text(s)
