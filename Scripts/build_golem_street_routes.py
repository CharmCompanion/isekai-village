from pathlib import Path
import json,math,array,collections
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');folder=r/'ArtSource/World/ElRuhnSky02';plan=json.loads((folder/'village_plan.json').read_text());nodes=[];buckets=collections.defaultdict(list);edges=set();cell=1.2
def add(p):
 key=(math.floor(p[0]/cell),math.floor(p[1]/cell))
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:
   for i in buckets[(key[0]+dx,key[1]+dy)]:
    if math.dist(nodes[i],p)<.65:return i
 i=len(nodes);nodes.append(p);buckets[key].append(i);return i
# The circuit crosses the fountain footprint; the authored plaza bypass is
# the walkable route. Connect its northern 3 m gap and exclude the base.
fx,fy=plan['fountain_m'][:2]
roads=list(plan['roads'])+[{'name':'Fountain bypass approach','points':[[fx,fy+21],[fx,fy+18]]}]
for road in roads:
 last=None
 for a,b in zip(road['points'],road['points'][1:]):
  count=max(1,math.ceil(math.dist(a,b)/1.6))
  for j in range(count+1):
   point=[a[k]+(b[k]-a[k])*j/count for k in [0,1]]
   if math.dist(point,[fx,fy]) < 9.0:
    last=None;continue
   i=add(point)
   if last is not None and last!=i:edges.add(tuple(sorted((last,i))))
   last=i
# Join overlapping road centerlines where the source polylines cross.
for i,p in enumerate(nodes):
 key=(math.floor(p[0]/cell),math.floor(p[1]/cell))
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:
   for j in buckets[(key[0]+dx,key[1]+dy)]:
    if j>i and math.dist(p,nodes[j])<1.25:edges.add((i,j))
adj=[set() for _ in nodes]
for a,b in edges:adj[a].add(b);adj[b].add(a)
components=[];remaining=set(range(len(nodes)))
while remaining:
 todo=[remaining.pop()];group=set(todo)
 while todo:
  for v in adj[todo.pop()]:
   if v in remaining:remaining.remove(v);group.add(v);todo.append(v)
 components.append(group)
components.sort(key=len,reverse=True);largest=components[0];parcels={}
for p in plan['plots']:
 i=min(range(len(nodes)),key=lambda i:math.dist(p['stake_m'][:2],nodes[i]));parcels[p['id']]={'node':i,'distance_m':math.dist(p['stake_m'][:2],nodes[i]),'connected':i in largest}
assert all(p['connected'] for p in parcels.values()),[k for k,v in parcels.items() if not v['connected']]
heights=array.array('f');heights.frombytes((folder/'terrain_height_f32.bin').read_bytes())
def height(x,y):
 u=max(0,min(1007.999,(x+600)*.84));v=max(0,min(1007.999,(y+600)*.84));ix=int(u);iy=int(v);fx=u-ix;fy=v-iy
 return (heights[iy*1009+ix]*(1-fx)+heights[iy*1009+ix+1]*fx)*(1-fy)+(heights[(iy+1)*1009+ix]*(1-fx)+heights[(iy+1)*1009+ix+1]*fx)*fy
data={'success':True,'nodes_cm':[[x*100,y*100,height(x,y)*100] for x,y in nodes],'edges':[list(e) for e in sorted(edges)],'component_sizes':[len(c) for c in components],'parcels':parcels,'scope':'Authored street centerlines and frontage access paths; worker capsules still sweep and stop at physical obstacles.'};(folder/'golem_street_routes.json').write_text(json.dumps(data,separators=(',',':')))
print(json.dumps({'nodes':len(nodes),'edges':len(edges),'components':data['component_sizes'],'parcels':len(parcels),'all_parcels_connected':True},indent=2))
