import gosain37_geometry as g
from gosain43_terraces import planned
import numpy as np,json
B=g.ROOT;O=B/'ArtSource/World/Gosain43'
rows=json.loads((B/'Saved/Gosain43/baseline_foliage.json').read_text());moves=[]
for oldq in json.loads((B/'ArtSource/World/Gosain40/foliage_moves.json').read_text()):
    match=[r for r in rows if r['mesh']==oldq['mesh'] and r['count']==oldq['count']]
    assert len(match)==1,(oldq['foliage_type'],len(match))
    r=match[0];tr=np.array(r['transforms']);p=tr[:,:2]/100;ix=np.flatnonzero(np.isin(g.component(p),[1,2])&(tr[:,2]<-1800000))
    old=-20600+(g.ground_many(p[ix])+20600)*.3;dz=(planned(p[ix],old)-old)*100
    moves.append({'component':r['name'],'mesh':r['mesh'],'count':r['count'],'foliage_type':oldq['foliage_type'],'indices':ix.tolist(),'delta_cm':dz.tolist()})
(O/'foliage_moves.json').write_text(json.dumps(moves));print('moves ready',sum(len(q['indices']) for q in moves),flush=True)
