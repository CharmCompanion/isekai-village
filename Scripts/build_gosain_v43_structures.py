import gosain37_geometry as g
from gosain43_terraces import planned
from pathlib import Path
import numpy as np,json
B=g.ROOT;O=B/'ArtSource/World/Gosain43'
def delta(p):
    old=-20600+(g.ground_many(p)+20600)*.3
    return planned(p,old)-old
manifest=[]
entries=[(B/'ArtSource/World/Gosain40'/(q['name']+'.obj'),q['origin_m'],q['name']) for q in json.loads((B/'ArtSource/World/Gosain40/structure_sources.json').read_text())]
for path,origin,oldname in entries:
    vv=[]
    for line in path.open():
        if line.startswith('v '):
            x,y,z=map(float,line.split()[1:]);vv.append([x/100+origin[0],-y/100+origin[1],z/100+origin[2]])
    v=np.array(vv);mask=np.isin(g.component(v[:,:2]),[1,2])&(v[:,2]<-18000);dz=np.zeros(len(v))
    if 'HouseFootings' in oldname or 'InfillFootings' in oldname:
        assert len(v)%8==0
        centers=v.reshape(-1,8,3).mean(axis=1);dz=np.repeat(delta(centers[:,:2]),8)
    else:
        for ids in np.array_split(np.flatnonzero(mask),max(1,int(mask.sum()/12000))):
            if len(ids):dz[ids]=delta(v[ids,:2])
    name=oldname+'_Terraces43';idx=0
    with (O/(name+'.obj')).open('w') as out:
        for line in path.open():
            if line.startswith('v '):
                if abs(dz[idx])>1e-8:
                    p=v[idx]-origin;p[2]+=dz[idx];line='v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100)
                idx+=1
            out.write(line)
    assert np.all(dz[~mask]==0)
    manifest.append({'old_name':oldname,'name':name,'origin_m':origin,'changed_vertices':int((np.abs(dz)>1e-8).sum()),'unchanged_vertices':int((np.abs(dz)<=1e-8).sum())});print(name,flush=True)
(O/'structure_sources.json').write_text(json.dumps(manifest,indent=2))
