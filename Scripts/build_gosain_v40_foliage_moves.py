import gosain37_geometry as g
from pathlib import Path
import numpy as np,json
B=g.ROOT;O=B/'ArtSource/World/Gosain40';R='/Game/IsekaiVillage/AdventureWorld'
rows=json.loads((B/'Saved/Gosain40/baseline_foliage.json').read_text());d37=json.loads((B/'ArtSource/World/Gosain37/Gosain37.json').read_text());d36=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v36.json').read_text());kits={k['name']:k for k in json.loads((B/'ArtSource/World/Gosain39/merged_house_assets.json').read_text())}
mapping={}
for key,inst in d37['instances'].items():
    if key in ('HouseA','HouseB'):continue
    path=d37['assets'][key]
    if key.startswith('SM_Civ'):path=R+'/Gosain37/Meshes/'+key+'_Gosain37'
    matches=[r for r in rows if r['mesh'].split('.')[0]==path and r['count']==len(inst)]
    assert len(matches)==1,(key,len(matches));mapping[matches[0]['name']]=R+'/Gosain37/Foliage/FT_Gosain37_'+key
for prefix,report in [('House','capital_variety_applied.json'),('Infill','capital_infill_applied.json')]:
    counts=json.loads((B/'ArtSource/World/Gosain39'/report).read_text())['counts']
    for k,n in counts.items():
        matches=[r for r in rows if r['mesh']==kits[k]['path'] and r['count']==n];assert len(matches)==1,(k,n)
        mapping[matches[0]['name']]=R+'/Gosain39/Foliage/FT_Gosain39_'+prefix+'_'+k
moves=[]
for r in rows:
    tr=np.array(r['transforms'])
    if not len(tr):continue
    p=tr[:,:2]/100;mask=np.isin(g.component(p),[1,2])&(tr[:,2]<-1800000);ix=np.flatnonzero(mask)
    if not len(ix):continue
    if r['name'] not in mapping:
        keys=[k for k,path in d36['assets'].items() if path==r['mesh'].split('.')[0]];assert len(keys)==1,(r['name'],keys)
        mapping[r['name']]=R+'/Foliage/Civilizations/FT_Civ36_'+keys[0]
    z=g.ground_many(p[ix]);delta=-.70*np.maximum(z+20600,0)*100
    moves.append({'component':r['name'],'mesh':r['mesh'],'count':r['count'],'foliage_type':mapping[r['name']],'indices':ix.tolist(),'delta_cm':delta.tolist()})
(O/'foliage_moves.json').write_text(json.dumps(moves));print('types',len(moves),'instances',sum(len(m['indices']) for m in moves),flush=True)
