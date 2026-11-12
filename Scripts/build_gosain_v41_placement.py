import gosain37_geometry as g
import numpy as np,json
B=g.ROOT;O=B/'ArtSource/World/Gosain41';g.OUT=O
center=g.CAP+[-82,115];scale=.8
p=np.array([center+[x,y] for x in np.linspace(-37,37,17) for y in np.linspace(-32,32,17)])
z=-20600+(g.ground_many(p)+20600)*.3;base=float(z.max()+.16);low=float(z.min()-.5)
m=g.Mesh();m.box([*center,low],[73.6,64,base-low-.22],'foundation')
# Link the south passage to the precinct entrance while skirting the cathedral.
line=np.array([center+[0,-35],g.CAP+[-100,60],g.CAP+[-110,-110],g.CAP+[-55,-155],g.CAP+[0,-165]])
pts=[]
for a,b in zip(line[:-1],line[1:]):pts.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/2)),endpoint=False))
pts=np.array(pts+[line[-1]]);tan=np.gradient(pts,axis=0);tan/=np.linalg.norm(tan,axis=1,keepdims=True);side=np.c_[-tan[:,1],tan[:,0]];vv=[]
for offset in [-.5,0,.5]:
    q=pts+side*5*offset;h=-20600+(g.ground_many(q)+20600)*.3+.08;h[:8]=np.linspace(base,h[7],8);vv.append(np.c_[q,h])
v=np.stack(vv,axis=1).reshape(-1,3);faces=[]
for i in range(len(pts)-1):
    for j in range(2):a=i*3+j;b=(i+1)*3+j;faces.extend([[a,b,b+1],[a,b+1,a+1]])
m.part(v,faces,'paving');mesh=m.write('SM_Gosain41_BlockApproach',[center[0],center[1],base])
report={'status':'source_only','center_m':[float(center[0]),float(center[1]),base],'scale':[scale,scale,1],'terrain_min_m':float(z.min()),'terrain_max_m':float(z.max()),'foundation_mesh':mesh,'path_m':line.tolist(),'placement':'northwest precinct courtyard, clear of cathedral footprint; one architectural pilot block'}
(O/'placement.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
