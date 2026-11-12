"""Mine revision after native inspection: continuous landform and broken rock exposure."""
import numpy as np,json,math
from collections import defaultdict,deque
from pathlib import Path
import gosain57_mine as m
from gosain_surface_sampler import Surface
O=m.O;s=Surface(m.O/'graded_surface.npz')
def ground(d,l):return s.ground(m.xy(np.asarray(d),np.asarray(l)).reshape(-1,2))-m.Z
class Mesh:
 def __init__(self):self.v=[];self.f=[]
 def face(self,p):
  i=len(self.v);self.v.extend(p);self.f.extend([[i,i+j,i+j+1] for j in range(1,len(p)-1)])
 def write(self,name):
  v=np.array(self.v);f=np.array(self.f);v,ids=np.unique(np.round(v,7),axis=0,return_inverse=True);f=ids[f]
  adjacency=defaultdict(list)
  for i,face in enumerate(f):
   for a,b in zip(face,np.roll(face,-1)):adjacency[tuple(sorted((a,b)))].append((i,1 if a<b else -1))
  flips={0:1};queue=deque([0])
  while queue:
   i=queue.popleft()
   for a,b in zip(f[i],np.roll(f[i],-1)):
    edge=adjacency[tuple(sorted((a,b)))];assert len(edge)==2
    own=1 if a<b else -1
    for j,sign in edge:
     if j==i:continue
     wanted=-own*flips[i]*sign
     if j not in flips:flips[j]=wanted;queue.append(j)
     else:assert flips[j]==wanted
  assert len(flips)==len(f)
  for i,sign in flips.items():
   if sign<0:f[i]=f[i,::-1]
  if np.einsum('ij,ij->',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]]))<0:f=f[:,::-1]
  cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);norm=np.zeros_like(v)
  for j in range(3):np.add.at(norm,f[:,j],cross)
  norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-12)
  edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
  assert np.all(counts==2);assert np.all(np.linalg.norm(cross,axis=1)>1e-7)
  with (O/(name+'.obj')).open('w') as o:
   o.write('o '+name+'\nusemtl mine_rock\n')
   for p in v:o.write('v %.6f %.6f %.6f\n'%(p[0]*100,-p[1]*100,p[2]*100))
   for p in v:o.write('vt %.6f %.6f\n'%(p[0]/4,p[1]/4))
   for p in norm:o.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
   for face in f:o.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
  return {'vertices':len(v),'faces':len(f),'nonmanifold_edges':int((counts!=2).sum()),'degenerate_faces':0}
angles=np.linspace(0,math.pi,25)
profile=np.array([[5,0],[5,3]]+[[5*math.cos(a),3+5.5*math.sin(a)] for a in angles[1:-1]]+[[-5,3],[-5,0],[-2.5,0],[0,0],[2.5,0]])
n=len(profile);inner=[];outer=[];depths=np.r_[np.arange(27,95,4),95.]
for d in depths:
 p=np.c_[np.full(n,d),profile[:,0],profile[:,1]+.012*d]
 # Restrained irregular cut-rock surface, keeping a wide continuous corridor.
 for j in range(1,n-4):
  p[j,1]+=.11*math.sin(d*.29+j*1.7);p[j,2]+=.10*math.sin(d*.39+j*.8)
 inner.append(p)
outerdepth=np.r_[depths,105.,117.,130.,145.]
def width(d):return float(np.interp(d,[27,45,70,95,117,145],[23,31,34,31,23,10]))
def roof(d,l):
 base=ground(d,l);w=width(d);u=np.clip(np.asarray(l)/w,-1,1);arch=np.sqrt(np.maximum(0,1-u*u));fade=1-m.ease((d-95)/50)
 center=float(ground(d,0)[0]);raiseby=max(0,13.0+.012*d-center)+1.4*math.sin(d/21)
 return base+raiseby*arch**2.2*fade-.9*(1-arch*fade)
for d in outerdepth:
 w=width(d);p=[]
 for j,(l,z) in enumerate(profile):
  ll=l/5*w
  if j==0 or j>=n-4:
   dd=d-8 if d==27 and (j==0 or j==n-4) else d
   zz=min(float(ground(dd,ll)[0]),.012*d)-3.0
  else:
   if j==1 or j==n-5:ll*=.997
   dd=d+((20*(1-(abs(ll)/w)**1.3)-8*(abs(ll)/w)**1.6) if d==27 else 0)
   # Ease the entrance cut back into the slope; no vertical slab facade.
   if 27<d<55:dd+=20*(1-(abs(ll)/w)**1.3)*(55-d)/28
   zz=float(roof(float(d),float(ll))[0]);ll+=.6*math.sin(d/19+j*.45)*math.sin(math.pi*(d-27)/118)
   if j==1 or j==n-5:zz=float(ground(dd,ll)[0])-1.2
  p.append([dd,ll,zz])
 outer.append(np.array(p))
mesh=Mesh()
for rings,inside in [(inner,True),(outer,False)]:
 for i in range(len(rings)-1):
  for j in range(n):
   j2=(j+1)%n;p=np.array([rings[i][j],rings[i+1][j],rings[i+1][j2],rings[i][j2]]);center=p.mean(axis=0);normal=np.cross(p[1]-p[0],p[2]-p[0]);rad=center-np.array([center[0],0,3+.012*center[0]])
   if (np.dot(normal,rad)>0)==inside:p=p[::-1]
   mesh.face(p)
for j in range(n):
 j2=(j+1)%n;p=np.array([inner[0][j],inner[0][j2],outer[0][j2],outer[0][j]])
 if np.cross(p[1]-p[0],p[2]-p[0])[0]>0:p=p[::-1]
 mesh.face(p)
# Solid rock beyond the timber barrier; end of the outer volume is buried in the hill.
for ring,sign in [(inner[-1],-1),(outer[-1],1)]:
 center=ring.mean(axis=0)
 for j in range(n):
  p=np.array([center,ring[j],ring[(j+1)%n]])
  if np.sign(np.cross(p[1]-p[0],p[2]-p[0])[0])!=sign:p=p[::-1]
  mesh.face(p)
report=mesh.write('SM_Gosain57_MineLandformFinal')
# Remove paving covered by the loading court, preserving every unrelated face.
source=(O/'SM_Gosain57_KingdomRoutes.obj').read_text().splitlines();v=[]
for line in source:
 if line.startswith('v '):v.append(np.array([float(x) for x in line.split()[1:]])*[.01,-.01,.01])
v=np.array(v);out=[];removed=0
for line in source:
 if line.startswith('f '):
  face=[int(x.split('/')[0])-1 for x in line.split()[1:]];center=v[face,:2].mean(axis=0)
  if np.linalg.norm(center-m.C)<44:removed+=1;continue
 out.append(line)
(O/'SM_Gosain57_KingdomRoutesRefined.obj').write_text('\n'.join(out)+'\n');report['covered_route_faces_removed']=removed
rows=json.loads((O/'props.json').read_text());rng=np.random.default_rng(57126)
for q in rows:
 d,l=m.local(np.array(q['xy']))
 if q['label'].startswith('Mine bedrock shoulder'):
  j=int(q['label'].split()[-1]);q['path']='/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB0'+str(2+j%2);q['size']=[float(rng.uniform(11,17)),float(rng.uniform(10,15)),float(rng.uniform(8,12))];q['z']=m.Z+float(roof(float(d),float(l))[0])-q['size'][2]*.67
 elif q['label'].startswith('Mine roof strata'):
  q['size']=[float(rng.uniform(9,14)),float(rng.uniform(8,12)),float(rng.uniform(5,8))];q['z']=m.Z+float(roof(float(d),float(l))[0])-q['size'][2]*.73
 elif q['label'].startswith('Mine weathered outcrop'):
  q['size']=[q['size'][0],q['size'][1],q['size'][2]*.72];q['z']=m.Z+(float(ground(d,l)[0])-2 if int(q['label'].split()[-1])<4 else float(roof(float(d),float(l))[0])-q['size'][2]*.72)
(O/'props_refined.json').write_text(json.dumps(rows,indent=2));(O/'refinement_source.json').write_text(json.dumps(report,indent=2));print(report)
