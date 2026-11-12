"""Remove local height spikes and shading seams without moving established sites."""
import json,time,numpy as np,shapely
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter,median_filter,map_coordinates
import gosain51_kingdom as k
from gosain_surface_sampler import Surface
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';O.mkdir(exist_ok=True)
b=np.load(B/'ArtSource/World/Gosain57/graded_surface.npz');v=b['vertices'].copy();old=v.copy();f=b['triangles'];uv=b['uv'];norm=b['normals'].copy();step=8.
routes=[]
for line in (B/'ArtSource/World/Gosain57/SM_Gosain57_KingdomRoutesRefined.obj').read_text().splitlines():
 if line.startswith('v '):routes.append(np.array([float(x) for x in line.split()[1:4]])*[.01,-.01,.01])
routes=np.array(routes);rt=cKDTree(routes[:,:2]);mine=np.array([15950.,41900.]);changed_region=np.zeros(len(v),bool);fields=[]
for i,poly in enumerate(k.POLYS):
 bounds=np.array(poly.bounds);lo=np.floor((bounds[:2]-500)/step)*step;hi=np.ceil((bounds[2:]+500)/step)*step
 near=np.all((old[:,:2]>=lo-150)&(old[:,:2]<=hi+150),axis=1);points=old[near];tree=cKDTree(points[:,:2]);xs=np.arange(lo[0],hi[0]+step,step);ys=np.arange(lo[1],hi[1]+step,step);xx,yy=np.meshgrid(xs,ys);q=np.c_[xx.ravel(),yy.ravel()]
 _,ids=tree.query(q,workers=2);raw=points[ids,2].reshape(xx.shape);field=gaussian_filter(median_filter(raw,size=3),sigma=3.0,mode='nearest')
 np.savez_compressed(O/('island_field_'+str(i)+'.npz'),height=field,xs=xs,ys=ys)
 ix=np.flatnonzero(near);ps=shapely.points(old[ix,:2]);coast=shapely.distance(ps,poly);inside=shapely.contains(poly,ps);blend=1-k.old.ease((coast-30)/150)
 town=shapely.distance(ps,k.TOWNS[i]);blend*=k.old.ease((town-35)/110)
 lake=shapely.distance(ps,k.LAKE);blend*=k.old.ease((lake-160)/160)
 dm=np.linalg.norm(old[ix,:2]-mine,axis=1);blend*=k.old.ease((dm-185)/110)
 for end in k.old.PLAN['bridge_endpoints_m']:
  blend*=k.old.ease((np.linalg.norm(old[ix,:2]-np.array(end),axis=1)-180)/140)
 road_distance,_=rt.query(old[ix,:2],workers=2);blend*=k.old.ease((road_distance-12)/65)
 target=map_coordinates(field,[(old[ix,1]-lo[1])/step,(old[ix,0]-lo[0])/step],order=1,mode='nearest')
 v[ix,2]=old[ix,2]+(target-old[ix,2])*blend;changed_region[ix]|=blend>0
 fields.append({'island':i,'grid_spacing_m':step,'smoothing_radius_m':24,'raster_shape':list(field.shape),'candidate_vertices':len(ix)})
 print('smoothed island',i,flush=True)
changed=abs(v[:,2]-old[:,2])>1e-8;v[~changed]=old[~changed]
face_region=changed[f].any(axis=1);ff=f[face_region];delta=v[:,2]-old[:,2]
def steepness(p):
 cross=np.cross(p[ff[:,1]]-p[ff[:,0]],p[ff[:,2]]-p[ff[:,0]]);area=np.linalg.norm(cross,axis=1);slope=np.degrees(np.arctan2(np.linalg.norm(cross[:,:2],axis=1),abs(cross[:,2])));return {'faces_over_60deg':int((slope>60).sum()),'faces_over_75deg':int((slope>75).sum()),'p95_slope_degrees':float(np.quantile(slope,.95)),'area_over_60deg_m2':float((area[slope>60]/2).sum())}
before=steepness(old);after=steepness(v)
# Accumulate all neighboring faces, avoiding the discontinuous partial normals in prior passes.
cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,f[:,j],cross)
normal_region=np.zeros(len(v),bool);normal_region[np.unique(ff)]=True;length=np.linalg.norm(acc,axis=1);valid=normal_region&(length>1e-12);norm[valid]=acc[valid]/length[valid,None]
protected=~shapely.dwithin(shapely.points(old[:,:2]),shapely.union_all(k.POLYS),180)
townmask=shapely.contains(shapely.union_all(k.TOWNS),shapely.points(old[:,:2]));mine_mask=np.linalg.norm(old[:,:2]-mine,axis=1)<185
report={'changed_vertices':int(changed.sum()),'max_abs_height_change_m':float(abs(delta).max()),'p95_abs_height_change_m':float(np.quantile(abs(delta[changed]),.95)),'outside_gosain_unchanged':bool(np.array_equal(v[protected],old[protected])),'town_ground_unchanged':bool(np.array_equal(v[townmask],old[townmask])),'mine_ground_unchanged':bool(np.array_equal(v[mine_mask],old[mine_mask])),'xy_and_topology_unchanged':bool(np.array_equal(v[:,:2],old[:,:2])),'finite':bool(np.isfinite(v).all() and np.isfinite(norm).all()),'before':before,'after':after,'fields':fields,'native_review':'required'}
assert report['outside_gosain_unchanged'] and report['town_ground_unchanged'] and report['mine_ground_unchanged'] and report['finite'];assert after['faces_over_75deg']<before['faces_over_75deg'],report
(O/'terrain_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,uv=uv,normals=norm,region=changed)
name='SM_IV_Continent_GosainRefined58'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in norm:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
print('terrain source exported',flush=True)
surface=Surface(O/'graded_surface.npz');trees={}
for side,src in [('left',B/'ArtSource/World/Gosain56/left_forest_instances.json'),('right',B/'ArtSource/World/Gosain56/forest_instances.json')]:
 a=np.array(json.loads(src.read_text()));previous=a.copy();a[:,2]=surface.ground(a[:,:2]);assert np.isfinite(a).all();(O/(side+'_forest_instances.json')).write_text(json.dumps(a.tolist()));trees[side]={'count':len(a),'max_height_adjustment_m':float(abs(a[:,2]-previous[:,2]).max()),'xy_variants_scales_unchanged':bool(np.array_equal(a[:,[0,1,3,4,5]],previous[:,[0,1,3,4,5]]))};print(side,'forest aligned',flush=True)
(O/'forest_validation.json').write_text(json.dumps(trees,indent=2));(O/'source_complete.json').write_text(json.dumps({'status':'ready_for_native_import','time':time.strftime('%Y-%m-%d %H:%M:%S')}))
