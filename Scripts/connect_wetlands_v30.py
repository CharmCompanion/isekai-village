"""Join wetland land pockets with explicit, supported timber crossings."""
from pathlib import Path
import numpy as np,json,heapq
from scipy.ndimage import distance_transform_edt,map_coordinates
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';D=dict(np.load(S/'world_reference_v30.npz'));meta=json.loads((S/'world_design_v30.json').read_text());sites=meta['settlements'];h=D['height'];M=float(D['mpp']);cx=float(D['cx']);cy=float(D['cy']);H,W=h.shape
permanent=D['water']&(D['channel']<.025);shore=distance_transform_edt(~permanent)*M;slope=np.hypot(*np.gradient(h,M));stride=1;walk=(shore>110)&(slope<1.2);walk=walk[::stride,::stride];cost=(1+slope*25+(D['channel']>.015)*35)[::stride,::stride];gh,gw=walk.shape
parent=list(range(len(sites)));ids={q['id']:i for i,q in enumerate(sites)}
def root(a):
 while parent[a]!=a:a=parent[a]
 return a
for q in meta['routes']:parent[root(ids[q['from']])]=root(ids[q['to']])
wy,wx=np.where(walk)
def nearest(q):
 px,py=q['pixel'];j=np.argmin((wx-px/stride)**2+(wy-py/stride)**2);return (int(wy[j]),int(wx[j]))
def route(start,goal):
 sy,sx=start;gy,gx=goal;heap=[(0,0,sy,sx)];dist={start:0.};prev={}
 while heap:
  _,current,y,x=heapq.heappop(heap)
  if current!=dist.get((y,x)):continue
  if (y,x)==goal:break
  for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   ny,nx=y+dy,x+dx
   if not(0<=ny<gh and 0<=nx<gw) or not walk[ny,nx] or not walk[y,nx] or not walk[ny,x]:continue
   nd=current+float(cost[ny,nx])*(1.41421356 if dx*dy else 1)
   if nd<dist.get((ny,nx),1e30):dist[(ny,nx)]=nd;prev[(ny,nx)]=(y,x);heapq.heappush(heap,(nd+np.hypot(ny-gy,nx-gx),nd,ny,nx))
 else:return []
 p=[goal]
 while p[-1]!=start:p.append(prev[p[-1]])
 return np.array([[(cx-x*stride)*M,(cy-y*stride)*M] for y,x in p[::-1]])
def values(key,p):return map_coordinates(D[key],[cy-p[:,1]/M,cx-p[:,0]/M],order=1,mode='constant')
links=[];bridges=meta.get('bridges',[]);candidates=[]
for i,a in enumerate(sites):
 if a['country']!='VylfodDominion':continue
 for j,b in enumerate(sites[:i]):
  if b['country']=='VylfodDominion' and root(i)!=root(j):candidates.append((np.linalg.norm(np.array(a['xy_m'])-b['xy_m']),i,j))
for _,i,j in sorted(candidates):
 if root(i)==root(j):continue
 p=route(nearest(sites[i]),nearest(sites[j]))
 if len(p)<2:continue
 p=np.vstack([sites[i]['xy_m'],p,sites[j]['xy_m']]);dense=np.vstack([a+(b-a)*t for a,b in zip(p[:-1],p[1:]) for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/20)+1))]);wet=values('water_clearance',dense)<155
 starts=np.where(np.diff(np.r_[False,wet,False].astype(int))==1)[0];ends=np.where(np.diff(np.r_[False,wet,False].astype(int))==-1)[0];new=[]
 for a,b in zip(starts,ends):
  a=max(0,a-3);b=min(len(dense)-1,b+3);segment=dense[a:b+1]
  if np.linalg.norm(np.diff(segment,axis=0),axis=1).sum()>1300:break
  # A crossing must touch authored tidal water, never an inland lake or the sea.
  w=values('water',segment)>.5
  if not w.any():continue
  if not (values('channel',segment)[w]>.01).all():break
  new.append({'points_m':segment.tolist(),'width_m':12,'type':'supported timber bridge','from':sites[i]['id'],'to':sites[j]['id']})
 else:
  parent[root(i)]=root(j);links.append({'from':sites[i]['id'],'to':sites[j]['id'],'country':'VylfodDominion','kind':'wetland_bridge_route','width_m':12,'points_m':p.tolist()});bridges+=new;print({'wetland_link':[sites[i]['name'],sites[j]['name']],'bridges':len(new)},flush=True)
meta['routes']+=links;meta['bridges']=bridges;meta['network_summary']['regional_links']=len(meta['routes']);meta['network_summary']['tidal_bridges']=len(bridges);meta['network_summary']['regional_road_km']=sum(np.linalg.norm(np.diff(q['points_m'],axis=0),axis=1).sum() for q in meta['routes'])/1000
(S/'world_design_v30.json').write_text(json.dumps(meta,indent=2));print(meta['network_summary'],flush=True)
