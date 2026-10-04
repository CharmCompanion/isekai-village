from pathlib import Path
import numpy as np,json
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');report={}
for source in S.glob('*_source_v28.obj'):
 v=[];uv=[];f=[];ft=[]
 for l in source.open():
  if l.startswith('v '):v.append(list(map(float,l.split()[1:4])))
  elif l.startswith('vt '):uv.append(list(map(float,l.split()[1:3])))
  elif l.startswith('f '):
   corners=[q.split('/') for q in l.split()[1:]];f.append([int(q[0])-1 for q in corners]);ft.append([int(q[1])-1 for q in corners])
 v=np.array(v);v=v[:,[0,2,1]];v[:,1]*=-1 # exporter Y-up -> established importer coordinates
 uv=np.array(uv);f=np.array(f);ft=np.array(ft)
 v,inverse=np.unique(np.round(v,4),axis=0,return_inverse=True);f=inverse[f];oldmin=v.min(axis=0);oldmax=v.max(axis=0)
 neighbor=[set() for _ in v];edges={}
 for a,b,c in f:
  for x,y,z in [(a,b,c),(b,c,a),(c,a,b)]:
   edges.setdefault(tuple(sorted((x,y))),[]).append(z);neighbor[x].add(y);neighbor[y].add(x)
 boundary={i for edge,op in edges.items() if len(op)!=2 for i in edge}
 new=v.copy()
 for i,near in enumerate(neighbor):
  if i in boundary or len(near)<3:continue
  n=len(near);beta=3/(8*n) if n>3 else 3/16;loop=v[i]*(1-n*beta)+beta*v[list(near)].sum(axis=0);new[i]=v[i]*.60+loop*.40
 positions=list(new);edge_ids={}
 for edge,op in edges.items():
  a,b=edge;mid=(v[a]+v[b])*.5
  if len(op)==2:mid=.3*mid+.7*((v[a]+v[b])*.375+(v[op[0]]+v[op[1]])*.125)
  edge_ids[edge]=len(positions);positions.append(mid)
 nf=[];nuv=[]
 for face,texface in zip(f,ft):
  a,b,c=face;ab=edge_ids[tuple(sorted((a,b)))];bc=edge_ids[tuple(sorted((b,c)))];ca=edge_ids[tuple(sorted((c,a)))];ta,tb,tc=uv[texface];tab=(ta+tb)/2;tbc=(tb+tc)/2;tca=(tc+ta)/2
  nf.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]);nuv.extend([(ta,tab,tca),(tab,tb,tbc),(tca,tbc,tc),(tab,tbc,tca)])
 v=np.array(positions);f=np.array(nf);nuv=np.array(nuv).reshape(-1,2)
 # Retain placement envelopes so contacts do not shift when instances are replaced.
 v=(v-v.min(axis=0))/np.maximum(v.max(axis=0)-v.min(axis=0),1e-9)*(oldmax-oldmin)+oldmin
 norm=np.zeros_like(v);cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
 for k in range(3):np.add.at(norm,f[:,k],cross)
 norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-9)
 name=source.stem.replace('_source_v28','_Smooth28')
 with (S/(name+'.obj')).open('w') as out:
  out.write('o '+name+'\n')
  for q in v:out.write('v '+' '.join(f'{x:.6f}' for x in q)+'\n')
  for q in nuv:out.write('vt '+' '.join(f'{x:.7f}' for x in q)+'\n')
  for q in norm:out.write('vn '+' '.join(f'{x:.7f}' for x in q)+'\n')
  for i,face in enumerate(f):out.write('f '+' '.join(f'{vertex+1}/{i*3+k+1}/{vertex+1}' for k,vertex in enumerate(face))+'\n')
 report[name]={'vertices':len(v),'triangles':len(f),'source':source.name,'bounds_preserved':True}
(S/'smooth_rock_assets_v28.json').write_text(json.dumps(report,indent=2));print(report)
