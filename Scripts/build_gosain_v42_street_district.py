"""Street-first masonry district; creates sources only, no editor mutation."""
import gosain37_geometry as g
import json, numpy as np, shapely
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from PIL import Image, ImageDraw, ImageFont
O=g.ROOT/'ArtSource/World/Gosain42';O.mkdir(exist_ok=True)
OUT=g.ROOT/'Docs/WorldDesign/Gosain42';OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(42016);mesh=g.Mesh()
d=json.loads((g.ROOT/'ArtSource/World/Gosain37/Gosain37.json').read_text())
roads=[(LineString(np.array(r['points_m'])-g.CAP),r['width']) for r in d['roads']]
reserve=unary_union([r.buffer(w/2+1.2) for r,w in roads])
cells=list(box(-460,-230,-220,40).difference(reserve).geoms)
# Whole existing street blocks: no rectangular district cut through buildings.
blocks=sorted(cells,key=lambda p:p.area,reverse=True)[:2]
district=unary_union(blocks);origin=np.array([*g.CAP,-20310.0])
def ground(p):return -20600+(g.ground_many(np.array(p)+g.CAP)+20600)*.3-origin[2]
def polygons(p):return [p] if p.geom_type=='Polygon' else [q for q in getattr(p,'geoms',[]) if q.geom_type=='Polygon']
def cap(poly,z,mat,up=True):
    for t in shapely.constrained_delaunay_triangles(poly).geoms:
        v=np.c_[np.array(orient(t,sign=1).exterior.coords)[:3],np.full(3,z)]
        mesh.part(v,[[0,1,2] if up else [2,1,0]],mat)
def solid(poly,z,h,mat):
    if poly.is_empty or poly.area<.02:return
    poly=orient(poly,sign=1)
    for ring in [poly.exterior,*poly.interiors]:
        p=np.array(ring.coords)
        for a,b in zip(p[:-1],p[1:]):
            mesh.part([[*a,z],[*b,z],[*b,z+h],[*a,z+h]],[[0,1,2],[0,2,3]],mat)
    cap(poly,z+h,mat);cap(poly,z,mat,False)
def strip(a,b,z,h,width,mat):
    a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
    if length>.01:mesh.box([*((a+b)/2),z],[length,width,h],mat,float(np.degrees(np.arctan2(*(b-a)[::-1]))))
lanes=[];land=[];bridges=[]
for bi,b in enumerate(blocks):
    xmin,ymin,xmax,ymax=b.bounds;cx,cy=b.centroid.coords[0]
    # Lanes enter the existing streets at both ends, following a bent, inherited route.
    path=LineString([(cx-13,ymin-8),(cx+7,cy-25),(cx-6,cy+12),(cx+14,ymax+8)])
    branch=LineString([(xmin-8,cy-8),(cx-6,cy+12),(xmax+8,cy+29)])
    lanes.extend([path,branch]);cut=unary_union([path.buffer(1.7),branch.buffer(1.45)])
    # Small non-symmetric light wells, not a formal courtyard.
    wells=unary_union([Point(cx+24,cy-15).buffer(4.3,quad_segs=4),Point(cx-25,cy+26).buffer(3.2,quad_segs=3)])
    land.extend(polygons(b.difference(cut.union(wells))))
buildable=unary_union(land)
# Party-wall plots inherit the road-edge silhouette, including wedge/corner buildings.
sites=[]
for y in np.arange(-225,35,17):
    for x in np.arange(-440,-255,19):
        p=[x+rng.uniform(-5,5),y+rng.uniform(-5,5)]
        if district.buffer(25).covers(Point(p)):sites.append(p)
vor=shapely.voronoi_polygons(shapely.MultiPoint(sites),extend_to=district.envelope.buffer(50))
parcels=[]
for cell in vor.geoms:
    for p in polygons(cell.intersection(buildable)):
        if p.area>35:parcels.append(p)
parcels.sort(key=lambda p:(p.centroid.y,p.centroid.x))
records=[];window_count=0
def facade(poly,base,levels,storey,mat,upper=False):
    global window_count
    p=np.array(orient(poly,sign=1).exterior.coords)
    for ei,(a,b) in enumerate(zip(p[:-1],p[1:])):
        t=b-a;length=np.linalg.norm(t)
        if length<2.8:continue
        t/=length;n=np.array([t[1],-t[0]])
        # No expensive or nonsensical windows on shared, buried party walls.
        if not upper and buildable.covers(Point((a+b)/2+n*.45)):continue
        count=max(1,int(length/3.25));spacing=length/count
        for floor in range(levels):
            z=base+floor*storey
            for j in range(count):
                c=a+t*(j+.5)*spacing;w=min(1.25,spacing*.47);h=1.85 if floor else 2.3
                zz=z+(.72 if floor else .2)
                strip(c-t*w/2+n*.035,c+t*w/2+n*.035,zz,h,.07,'recess')
                for sign in [-1,1]:
                    cc=c+t*sign*(w/2+.095)+n*.10;strip(cc-t*.075,cc+t*.075,zz-.12,h+.24,.24,'trim')
                strip(c-t*(w/2+.22)+n*.15,c+t*(w/2+.22)+n*.15,zz-.18,.18,.38,'trim')
                strip(c-t*(w/2+.18)+n*.09,c+t*(w/2+.18)+n*.09,zz+h,.20,.24,'trim')
                strip(c-t*.035+n*.12,c+t*.035+n*.12,zz,h,.10,'mullion')
                window_count+=1
                if floor==1 and j%3==0:
                    # Masonry window pediments: triangular stone, no timber rafters.
                    v=[[*(c-t*(w/2+.3)+n*.18),zz+h+.22],[*(c+t*(w/2+.3)+n*.18),zz+h+.22],[*(c+n*.18),zz+h+.65]]
                    mesh.part(v,[[0,1,2],[2,1,0]],'trim')
        # Rusticated ground-floor courses and heavier institutional stone plinth.
        for z in np.arange(base+.35,base+storey,.55):strip(a+n*.06,b+n*.06,z,.045,.13,'joint')
        for j in range(1,int(length/1.7)):
            c=a+t*(j*1.7);strip(c-t*.023+n*.065,c+t*.023+n*.065,base,.5,.14,'joint')
        strip(a+n*.09,b+n*.09,base+storey-.1,.24,.3,'trim')
for i,p in enumerate(parcels):
    xy=np.array(p.exterior.coords)[:-1];zs=ground(xy);base=float(zs.max()+.06)
    levels=int(rng.choice([4,5,6,7,8],p=[.12,.25,.30,.23,.10]));storey=3.25
    mat=['limestone','ivory','aged','warmstone'][i%4]
    solid(p,float(zs.min()-1),base-float(zs.min())+1,'foundation')
    # The lower occupied mass connects neighboring plots; upper accretions step back.
    low=levels-2;solid(p,base,low*storey,mat);facade(p,base,low,storey,mat)
    upper=p.buffer(-float(rng.choice([.35,.6,1.2])),join_style=2)
    if upper.geom_type!='Polygon' or upper.area<20:upper=p
    z=base+low*storey
    solid(p.buffer(.13,join_style=2),z-.22,.27,'trim')
    cap(p,z+.06,'roofstone')
    solid(upper,z,2*storey,mat);facade(upper,z,2,storey,mat,True)
    top=z+2*storey;solid(upper.buffer(.16,join_style=2),top-.18,.24,'trim')
    cap(upper,top+.07,'roofstone')
    # Closed masonry parapet rings, subdued roof terraces and irregular service additions.
    ring=upper.difference(upper.buffer(-.27,join_style=2));solid(ring,top,.85,mat)
    core=upper.buffer(-2.1,join_style=2)
    if i%3==0 and core.geom_type=='Polygon' and core.area>20:
        cut=box(core.bounds[0]-1,core.bounds[1]-1,core.centroid.x+1,core.bounds[3]+1).intersection(core)
        for part in polygons(cut):
            if part.area>8:solid(part,top,2.9,'aged');solid(part.buffer(.12,join_style=2),top+2.9,.20,'roofstone')
    records.append({'footprint':list(p.exterior.coords),'base_local_m':base,'storeys':levels,'height_m':levels*storey,'area_m2':p.area})
# Secondary service lanes and tiny courts have terrain-following paving.
free=district.difference(buildable)
for p in polygons(free):
    for t in shapely.constrained_delaunay_triangles(p).geoms:
        xy=np.array(orient(t).exterior.coords)[:3];mesh.part(np.c_[xy,ground(xy)+.055],[[0,1,2]],'paving')
# Later enclosed masonry links across internal lanes only; leave the original roads untouched.
for bi,b in enumerate(blocks):
    lane=lanes[bi*2];p=np.array(lane.interpolate(lane.length*.53).coords[0]);t=np.array(lane.interpolate(lane.length*.53+.5).coords[0])-p;t/=np.linalg.norm(t);n=np.array([-t[1],t[0]])
    bridge=Polygon([p+n*5-t*2,p-n*5-t*2,p-n*5+t*2,p+n*5+t*2])
    if b.contains(bridge) and not bridge.intersects(reserve):
        z=float(ground([p])[0]+6.2);solid(bridge,z,3.4,'aged');solid(bridge.buffer(.13,join_style=2),z+3.4,.25,'trim');facade(bridge,z,1,3.4,'aged',True);bridges.append({'polygon':list(bridge.exterior.coords),'floor_local_m':z,'minimum_ground_clearance_m':float(z-max(ground(np.array(bridge.exterior.coords))))})
def write(mesh,name):
    v=np.array(mesh.v);f=np.array(mesh.f);n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);ll=np.linalg.norm(n,axis=1);ok=ll>1e-8;f=f[ok];n=n[ok]/ll[ok,None];mats=np.array(mesh.mat)[ok]
    with (O/(name+'.obj')).open('w') as out:
        out.write('o '+name+'\n')
        for x,y,z in v:out.write('v %.5f %.5f %.5f\n'%(x*100,-y*100,z*100))
        for face,normal in zip(f,n):
            axis=np.argmax(np.abs(normal))
            for u,w in v[face][:,[j for j in range(3) if j!=axis]]/4:out.write('vt %.5f %.5f\n'%(u,w))
        for x,y,z in n:out.write('vn %.6f %.6f %.6f\n'%(x,-y,z))
        last=None
        for i,(face,mat) in enumerate(zip(f,mats)):
            if mat!=last:out.write('usemtl '+mat+'\n');last=mat
            out.write('f '+' '.join('%d/%d/%d'%(face[j]+1,i*3+j+1,i+1) for j in [2,1,0])+'\n')
    return {'name':name,'vertices':len(v),'triangles':len(f),'materials':sorted(set(mats.tolist())),'origin_m':origin.tolist()}
q=write(mesh,'SM_Gosain42_StreetGrownDistrict')
occupied=unary_union([Polygon(r['footprint']) for r in records])
report={'status':'source_only','mesh':q,'blocks':[list(p.exterior.coords) for p in blocks],'buildings':records,'bridges':bridges,'district_area_m2':district.area,'occupied_area_m2':occupied.area,'street_intersection_m2':occupied.intersection(reserve).area,'window_count':window_count,'limitations':['Exterior district architecture; no upper-floor interiors or gameplay navigation certification.','Two existing street blocks only, not the whole capital.']}
assert report['street_intersection_m2']<.01
assert all(b['minimum_ground_clearance_m']>5 for b in bridges)
(O/'district.json').write_text(json.dumps(report,indent=2))
im=Image.new('RGB',(1400,1100),'#263237');draw=ImageDraw.Draw(im)
def uv(p):return (700+(p[0]+350)*3.5,550-(p[1]+110)*3.5)
for r,w in roads:draw.line([uv(p) for p in r.coords],fill='#b7a486',width=max(1,int(w*3.5)))
for i,r in enumerate(records):draw.polygon([uv(p) for p in r['footprint']],fill=['#c5b795','#d7c9aa','#a29b86','#bcaa89'][i%4],outline='#57584d')
for b in bridges:draw.polygon([uv(p) for p in b['polygon']],fill='#795f50')
draw.rectangle([0,0,1400,80],fill='#263237');draw.text((30,20),'GOSAIN | Street-grown masonry district',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',34),fill='white')
draw.rectangle([0,1010,1400,1100],fill='#263237');draw.text((30,1030),'Existing roads preserved | shared walls | narrow lanes | stepped additions',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24),fill='white')
im.save(OUT/'Street_District_Plan.png')
print(json.dumps({k:report[k] for k in ['mesh','district_area_m2','occupied_area_m2','street_intersection_m2','window_count']}));print('Buildings',len(records),'links',len(bridges))
