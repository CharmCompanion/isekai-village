"""Prepare coordinated road/foundation sources and regenerate grounded coastal defenses."""
import gosain37_geometry as g
from pathlib import Path
import numpy as np,json
B=g.ROOT;O=B/'ArtSource/World/Gosain40';sea=-20600
old_ground=g.ground_many
def lowered(p):
    z=old_ground(p);return np.where(np.isin(g.component(np.asarray(p)),[1,2])&(z>sea),sea+(z-sea)*.30,z)
def delta(p):return lowered(p)-old_ground(p)
manifest=[]
entries=[]
for q in json.loads((B/'ArtSource/World/Gosain37/Gosain37.json').read_text())['meshes']:
    entries.append((B/'ArtSource/World/Gosain37'/(q['name']+'.obj'),q['origin_m'],q['name']))
entries.extend([(B/'ArtSource/World/Gosain38/SM_Civ36_Roads_OutsideOldGosainBridge38.obj',[0,0,0],'SM_Civ36_Roads_OutsideOldGosainBridge38'),(B/'ArtSource/World/Gosain37/SM_Civ36_Foundations_OutsideGosain37.obj',[0,0,0],'SM_Civ36_Foundations_OutsideGosain37')])
q=json.loads((B/'ArtSource/World/Gosain39/capital_infill.json').read_text())['mesh'];entries.append((B/'ArtSource/World/Gosain39'/(q['name']+'.obj'),q['origin_m'],q['name']))
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
    name=oldname+'_Relief40';idx=0
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
# Regenerate the bridge against the fixed sea level and lowered abutments.
g.ground_many=lowered;g.OUT=O
src=(B/'Scripts/build_gosain_v38_defenses.py').read_text().replace("O=ROOT/'ArtSource/World/Gosain38';g.OUT=O","O=ROOT/'ArtSource/World/Gosain40';g.OUT=O").replace("(O/'whole_island_plan.json')","(ROOT/'ArtSource/World/Gosain38/whole_island_plan.json')").replace('SM_Gosain38_','SM_Gosain40_')
exec(compile(src,'defenses40','exec'))
