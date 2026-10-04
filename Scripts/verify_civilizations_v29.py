from pathlib import Path
import sys,json,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from civilization_ground_v29 import ground
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';data=json.loads((S/'civilization_instances_v29.json').read_text());native=json.loads((B/'Saved/civilization_assets_v29.json').read_text());mins={}
for q in json.loads((S/'Civilizations29/assets.json').read_text()):
 if q['name'] not in data['instances']:continue
 z=[float(l.split()[3])/100 for l in (S/'Civilizations29'/(q['name']+'.obj')).open() if l.startswith('v ')];mins[q['name']]=min(z)
checks=0;floating=[];water=[]
for key,rows in data['instances'].items():
 if key in ['Sails','Boat','SM_Civ29_Banner']:continue
 minz=mins[key] if key in mins else native[data['assets'][key]]['min'][2]/100
 for p in rows:
  z=ground(p[0],p[1]);foot=p[2]+minz*p[5];checks+=1
  if foot-z>2.05:floating.append({'asset':key,'xy':p[:2],'gap':foot-z})
  if z<-20600.5:water.append({'asset':key,'xy':p[:2],'height':z})
mesh=json.loads((S/'puzzle_continent_v29_report.json').read_text());assert mesh['inverse_fit_max_error_m']<1e-8 and mesh['internal_open_edges']==0 and mesh['nonmanifold_edges']==0
r={'grounded_instance_checks':checks,'floating_above_2m':floating,'below_sea_placements':water,'paired_inverse_error_m':mesh['inverse_fit_max_error_m'],'internal_open_edges':mesh['internal_open_edges'],'nonmanifold_edges':mesh['nonmanifold_edges'],'sites':len(json.loads((S/'world_design_v29.json').read_text())['settlements'])}
(S/'civilizations_validation_v29.json').write_text(json.dumps(r,indent=2));print({k:(len(v) if isinstance(v,list) else v) for k,v in r.items()},flush=True);assert not floating
