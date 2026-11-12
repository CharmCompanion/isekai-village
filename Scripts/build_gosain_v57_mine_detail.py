"""Detailed mine exterior and short adit, with existing pack props."""
import json,math,numpy as np
from pathlib import Path
from scipy.spatial import Delaunay
import gosain57_mine as m
from gosain_surface_sampler import Surface
O=m.O;s=Surface(O/'graded_surface.npz');rng=np.random.default_rng(57025)

def ground(d,l):
 p=m.xy(np.asarray(d),np.asarray(l)).reshape(-1,2);return s.ground(p)

class Mesh:
 def __init__(self):self.v=[];self.uv=[];self.f=[]
 def tri(self,p,uv):
  i=len(self.v);self.v.extend(p);self.uv.extend(uv);self.f.append([i,i+1,i+2])
 def quad(self,p,uv):self.tri([p[i] for i in [0,1,2]],[uv[i] for i in [0,1,2]]);self.tri([p[i] for i in [0,2,3]],[uv[i] for i in [0,2,3]])
 def write(self,name,mat):
  v=np.array(self.v);f=np.array(self.f);n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
  with (O/(name+'.obj')).open('w') as o:
   o.write('o '+name+'\nusemtl '+mat+'\n')
   for p in v:o.write('v %.6f %.6f %.6f\n'%(p[0]*100,-p[1]*100,p[2]*100))
   for q in self.uv:o.write('vt %.6f %.6f\n'%tuple(q))
   for q in np.repeat(n,3,axis=0):o.write('vn %.6f %.6f %.6f\n'%(q[0],-q[1],q[2]))
   for face in f:o.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
  return {'vertices':len(v),'triangles':len(f)}

# Closed rock shell: real interior surfaces, roof and exterior; open walking ends.
inner=np.array([[5,0],[5,3]]+[[5*math.cos(a),3+5.5*math.sin(a)] for a in np.linspace(0,math.pi,13)[1:-1]]+[[-5,3],[-5,0],[-2.5,0],[0,0],[2.5,0]])
outer=inner.copy();outer[:,0]*=1.43;outer[:,1]=np.where(inner[:,1]<.01,-1.2,inner[:,1]+2.5)
depths=np.array([27,33,40,48,56,64,72,80,87,95.]);rings=[]
for d in depths:
 pair=[]
 for j,profile in enumerate([inner,outer]):
  p=np.c_[np.full(len(profile),d),profile[:,0],profile[:,1]+.012*d]
  if j==1:p[:,1]+=np.sin(d/9+np.arange(len(profile))*1.8)*.45;p[:,2]+=np.where(profile[:,1]>0,np.sin(d/11+np.arange(len(profile)))*.55,0)
  pair.append(p)
 rings.append(pair)
mesh=Mesh();n=len(inner)
for i in range(len(depths)-1):
 for layer in [0,1]:
  for j in range(n):
   j2=(j+1)%n;p=[rings[i][layer][j],rings[i+1][layer][j],rings[i+1][layer][j2],rings[i][layer][j2]]
   center=np.mean(p,axis=0);normal=np.cross(p[1]-p[0],p[2]-p[0]);rad=center-np.array([center[0],0,4+.012*center[0]])
   if (np.dot(normal,rad)>0)==(layer==0):p=p[::-1]
   mesh.quad(p,[[depths[i]/4,j*.7],[depths[i+1]/4,j*.7],[depths[i+1]/4,(j+1)*.7],[depths[i]/4,(j+1)*.7]])
for i in [0,len(depths)-1]:
 for j in range(n):
  j2=(j+1)%n;p=[rings[i][0][j],rings[i][0][j2],rings[i][1][j2],rings[i][1][j]];normal=np.cross(p[1]-p[0],p[2]-p[0])
  if np.sign(normal[0]) != (-1 if i==0 else 1):p=p[::-1]
  mesh.quad(p,[[0,0],[1,0],[1,1],[0,1]])
report={'shell':mesh.write('SM_Gosain57_MineShell','mine_rock')}
# Irregular worn earth yard; follows the final graded ground.
pts=[]
for d in np.arange(-42,31,2):
 for l in np.arange(-28,29,2):
  radius=np.sqrt(((d+6)/40)**2+(l/28)**2)
  if radius<1+.045*np.sin(d/8)*np.cos(l/7):pts.append([d,l])
pts=np.array(pts);z=ground(pts[:,0],pts[:,1])-m.Z+.05;yard=Mesh()
for face in Delaunay(pts).simplices:
 p=np.c_[pts[face],z[face]]
 if np.cross(p[1]-p[0],p[2]-p[0])[2]<0:p=p[::-1]
 yard.tri(p,p[:,:2]/4)
report['yard']=yard.write('SM_Gosain57_MineYard','mine_soil')
# A short approach surface joins the existing road end and portal.
path=Mesh()
for d in np.arange(-7,29,2):
 p=np.array([[d,-4.4],[d+2,-4.4],[d+2,4.4],[d,4.4]]);z=ground(p[:,0],p[:,1])-m.Z+.08;path.quad(np.c_[p,z],p/4)
report['approach']=path.write('SM_Gosain57_MineApproach','mine_soil')
# Existing kingdom route vertices near the yard are reseated; all others kept verbatim.
source=m.B/'ArtSource/World/Gosain56/SM_Gosain56_KingdomRoutes.obj';lines=source.read_text().splitlines();vertices=[];vid=[]
for i,line in enumerate(lines):
 if line.startswith('v '):vertices.append(np.array([float(x) for x in line.split()[1:4]])*[.01,-.01,.01]);vid.append(i)
v=np.array(vertices);sel=np.linalg.norm(v[:,:2]-m.C,axis=1)<100;v[sel,2]=s.ground(v[sel,:2])+.12
for j in np.flatnonzero(sel):p=v[j];lines[vid[j]]='v %.6f %.6f %.6f'%(p[0]*100,-p[1]*100,p[2]*100)
(O/'SM_Gosain57_KingdomRoutes.obj').write_text('\n'.join(lines)+'\n');report['route_vertices_reseated']=int(sel.sum())
P='/Game/Fantastic_Village_Pack/meshes/';R='/Game/SoStylized/Environment/Rocks/';rows=[]
def prop(label,path,d,l,size=None,scale=1,yaw=0,z=None,override=None):
 p=m.xy(d,l);h=float(ground(d,l)[0]) if z is None else m.Z+z
 rows.append({'label':label,'path':path,'xy':p.tolist(),'z':h,'size':size,'scale':scale,'yaw':math.degrees(math.atan2(m.F[1],m.F[0]))+yaw,'override':override})
# Native timber framing; clear 8 m opening, repeated inside the adit.
for j,d in enumerate([28,39,51,63,75,87]):prop('Mine timber support '+str(j),P+'props/construction/SM_PROP_wall_wood_gate_frame_01',d,0,[1.7,12.1,9.0],z=.012*d-.12)
# Large geological shoulders. No rock blocks the central opening.
for j,(d,l,size,yaw) in enumerate([(36,-12,[23,11,18],7),(38,13,[25,12,21],-12),(55,-14,[28,14,22],15),(63,15,[25,16,20],-8),(82,-14,[22,14,18],5),(85,14,[20,16,17],-15)]):
 prop('Mine bedrock shoulder '+str(j),R+'Cubic/SM_CubicCliff04',d,l,size,yaw=yaw,z=.012*d-2,override='rock')
for j,(d,l,size) in enumerate([(27,-8,[10,8,12]),(29,8.3,[10,9,13]),(22,-12,[10,10,7]),(21,14,[12,9,8]),(45,-20,[16,12,13]),(55,22,[16,14,11]),(69,-23,[18,14,12]),(92,19,[15,14,11])]):
 prop('Mine weathered outcrop '+str(j),R+'Spire/SM_RockSpire_RockClumpB0'+str(2+j%2),d,l,size,yaw=float(rng.uniform(-35,35)),z=float(ground(d,l)[0]-m.Z)-size[2]*.25,override='rock')
# Sparse overlapping crest rocks break up the shell roof without sealing the entrance.
for j,d in enumerate([34,45,58,70,83,94]):prop('Mine roof strata '+str(j),R+'Spire/SM_RockSpire_RockClumpB0'+str(2+j%2),d,float(rng.uniform(-1.5,1.5)),[16,14,9],yaw=float(rng.uniform(-22,22)),z=.012*d+8.8,override='rock')
# Covered ore-sorting line and repair bench flank the cart turning court.
for j,d in enumerate([-12,-5,2]):
 prop('Ore sorting canopy '+str(j),P+'props/construction/SM_PROP_market_v03_01',d,-18,scale=1.55,yaw=90)
 prop('Sorting table '+str(j),P+'props/furniture/SM_PROP_table_01',d,-18,scale=1.5,yaw=90)
prop('Tool repair shelter',P+'props/construction/SM_PROP_market_v01_01',7,19,scale=1.6,yaw=-90)
prop('Tool repair bench',P+'props/furniture/SM_PROP_table_01',7,19,scale=1.5,yaw=-90)
for j,(d,l,yaw) in enumerate([(-18,8,15),(4,9,-20),(15,-8,20)]):prop('Ore cart '+str(j),P+'props/vehicles/SM_PROP_cart_01',d,l,scale=1.25,yaw=yaw)
for j,(d,l) in enumerate([(-20,-22),(-25,-21),(-25,-24),(17,22),(19,23),(20,19)]):prop('Mine supplies '+str(j),P+'props/container/'+('SM_PROP_crate_01' if j%2==0 else 'SM_PROP_barrel_01'),d,l,scale=1.4,yaw=float(rng.uniform(-15,15)))
for j,(d,l) in enumerate([(-15,22),(-8,23),(-19,21)]):prop('Support timber stock '+str(j),'/Game/AdvancedVillagePack/Meshes/SM_Logs_Var01',d,l,scale=1.5,yaw=90)
# Spoil piles are kept away from the traffic lane.
for j in range(32):
 d,l=rng.normal(-20,4),rng.normal(-12,2.8);size=float(rng.uniform(.45,1.5));prop('Sorted ore '+str(j),'/Game/AdvancedVillagePack/Meshes/SM_Stone_Medium_Var01',float(d),float(l),[size*1.4,size,size*.65],yaw=float(rng.uniform(0,360)),override='ore')
for j in range(54):
 d,l=float(rng.uniform(-38,38)),float(rng.choice([-1,1])*rng.uniform(27,37));size=float(rng.uniform(.6,2.0));prop('Mine verge rubble '+str(j),R+'Spire/SM_RockSpire_RockClumpB0'+str(2+j%2),d,l,[size*1.3,size,size*.7],yaw=float(rng.uniform(0,360)),override='rock')
for j in range(45):
 d,l=float(rng.uniform(-43,40)),float(rng.choice([-1,1])*rng.uniform(29,39));prop('Mine verge grass '+str(j),'/Game/AdvancedVillagePack/Meshes/SM_GrassPatch_Var01',d,l,scale=float(rng.uniform(1,2)),yaw=float(rng.uniform(0,360)))
# A closed timber barrier marks the unfinished workings beyond the short adit.
for j,l in enumerate([-2.5,2.5]):prop('Mine deeper workings gate '+str(j),P+'props/construction/SM_PROP_wall_wood_gate_door_'+('L' if j==0 else 'R')+'_01',91,l,[.5,5.2,7.4],z=.012*91+.05)
for j,(d,l) in enumerate([(26,-4.6),(26,4.6),(43,-4.4),(60,4.4),(79,-4.4)]):prop('Mine lantern '+str(j),P+'props/light/SM_PROP_lantern_01',d,l,scale=1.6,z=.012*d+4.2)
(O/'props.json').write_text(json.dumps(rows,indent=2));lights=[{'d':d,'l':l,'z':.012*d+3.8} for d,l in [(27,-4.2),(27,4.2),(44,-4.2),(61,4.2),(80,-4.2)]];(O/'lights.json').write_text(json.dumps(lights,indent=2))
forest=np.load(m.B/'ArtSource/World/Gosain56/forest_instances.npy');dd,ll=m.local(forest[:,:2]);conf=(dd>-50)&(dd<115)&(abs(ll)<40);report.update(props=len(rows),lights=len(lights),forest_instances_in_site=int(conf.sum()),adit_length_m=68);(O/'build_report.json').write_text(json.dumps(report,indent=2));print(report)

