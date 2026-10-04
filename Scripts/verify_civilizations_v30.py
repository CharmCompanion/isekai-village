"""Validate water footprints, road continuity and exact island/cavity fit."""
from pathlib import Path
import json,numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
from civilization_ground_v30 import ground
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';D=dict(np.load(S/'world_reference_v30.npz'));meta=json.loads((S/'world_design_v30.json').read_text());data=json.loads((S/'civilization_instances_v30.json').read_text());native=json.loads((B/'Saved/civilization_assets_v30.json').read_text());cx=float(D['cx']);cy=float(D['cy']);m=float(D['mpp']);bb={}
for q in json.loads((S/'Civilizations30/assets.json').read_text()):
 if not data['instances'].get(q['name']):continue
 v=np.array([[float(a)/100 for a in l.split()[1:]] for l in (S/'Civilizations30'/(q['name']+'.obj')).open() if l.startswith('v ')]);v[:,1]*=-1;bb[q['name']]=(v.min(0),v.max(0))
for k,path in data['assets'].items():
 if k not in bb and path in native:bb[k]=(np.array(native[path]['min'])/100,np.array(native[path]['max'])/100)
def clearance(p):return map_coordinates(D['water_clearance'],[cy-p[:,1]/m,cx-p[:,0]/m],order=1,mode='constant',cval=0)
wetbuild=[];floating=[];checked=0;buildings=0
for key,rows in data['instances'].items():
 if key not in bb or key in ['Sails','Boat','SM_Civ30_Banner']:continue
 lo,hi=bb[key]
 for p in rows:
  xy=np.array(p[:2]);foot=p[2]+lo[2]*p[5];gap=foot-ground(*xy);checked+=1
  if gap>2.05:floating.append({'asset':key,'xy':p[:2],'gap_m':gap})
  if key in ['SM_Civ30_Boardwalk','Oak','Pine','Palm','DesertPalm','SM_Civ30_Reeds']:continue
  corners=np.array([[x,y] for x in [lo[0],(lo[0]+hi[0])*.5,hi[0]] for y in [lo[1],(lo[1]+hi[1])*.5,hi[1]]])*p[3:5];a=np.radians(p[6]);rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);corners=corners@rot.T+xy;buildings+=1
  if np.min(clearance(corners))<40:wetbuild.append({'asset':key,'xy':p[:2],'clearance':float(np.min(clearance(corners)))})
bridgepoints=np.vstack([q['points_m'] for q in meta.get('bridges',[])]);bridgetree=cKDTree(bridgepoints)
wetroad=[];pointschecked=0
for i,q in enumerate(meta['routes']+meta['farm_lanes']):
 points=np.array(q['points_m']);dense=np.vstack([a+(b-a)*t for a,b in zip(points[:-1],points[1:]) for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/20)+1))]);pointschecked+=len(dense)
 danger=clearance(dense)<q['width_m']/2+40
 if danger.any() and (bridgetree.query(dense[danger])[0]>45).any():wetroad.append(i)
wetfarms=[]
for i,q in enumerate(meta['agricultural_parcels']):
 a=np.array(q['corners'][0]);b=np.array(q['corners'][2]);x,y=np.meshgrid(np.linspace(a[0],b[0],9),np.linspace(a[1],b[1],17));p=np.column_stack([x.ravel(),y.ravel()])
 if np.min(clearance(p))<80:wetfarms.append(i)
adj={q['id']:set() for q in meta['settlements']}
for q in meta['routes']:adj[q['from']].add(q['to']);adj[q['to']].add(q['from'])
isolated=[q for q in adj if not adj[q]];seen=set();groups=[]
for n in adj:
 if n in seen:continue
 todo=[n];component=[]
 while todo:
  node=todo.pop()
  if node in seen:continue
  seen.add(node);component.append(node);todo.extend(adj[node]-seen)
 groups.append(component)
mesh=json.loads((S/'puzzle_continent_v30_report.json').read_text())
r={'ground_checks':checked,'building_footprints_checked':buildings,'buildings_on_water':wetbuild,'floating_above_2m':floating,'road_samples_checked':pointschecked,'roads_crossing_water':wetroad,'farms_on_water':wetfarms,'isolated_sites':isolated,'road_component_sizes':sorted(map(len,groups),reverse=True),'network_summary':meta['network_summary'],'paired_inverse_error_m':mesh['inverse_fit_max_error_m'],'internal_open_edges':mesh['internal_open_edges'],'nonmanifold_edges':mesh['nonmanifold_edges']}
(S/'civilizations_validation_v30.json').write_text(json.dumps(r,indent=2));print({k:len(v) if isinstance(v,list) and k not in ['road_component_sizes'] else v for k,v in r.items()},flush=True)
assert not wetbuild and not floating and not wetroad and not wetfarms
# Offshore island components have ports; all mainland sites must share a road network.
assert sorted(map(len,groups),reverse=True)==[135,2,2]
assert mesh['inverse_fit_max_error_m']<1e-8 and mesh['internal_open_edges']==0 and mesh['nonmanifold_edges']==0

