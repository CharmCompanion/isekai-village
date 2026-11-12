"""Prepare lower Gosain relief, keeping exact topology and every outside vertex."""
from pathlib import Path
import numpy as np,json,time
from scipy.ndimage import label
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain50';O.mkdir(exist_ok=True)
t=time.time();base=np.load(B/'ArtSource/World/Gosain37/terrace_base.npz');surface=np.load(B/'ArtSource/World/Gosain44/graded_surface.npz');v=surface['vertices'].copy();old=v.copy();f=np.vstack([base['fixed'],base['work']]);uv=base['uv'];normals=base['normals'].copy()
d=np.load(B/'Saved/AdventureWorldSource/world_reference_v30.npz');components,_=label(~d['water']);px=np.rint(float(d['cx'])-v[:,0]/float(d['mpp'])).astype(int);py=np.rint(float(d['cy'])-v[:,1]/float(d['mpp'])).astype(int);ids=components[np.clip(py,0,components.shape[0]-1),np.clip(px,0,components.shape[1]-1)]
from gosain50_kingdom import heights
reference=np.load(B/'ArtSource/World/Gosain40/graded_surface.npz')['vertices']
v[:,2]=heights(v[:,:2],old[:,2]);region=np.abs(v[:,2]-old[:,2])>1e-8
v[~region]=old[~region]
assert np.array_equal(v[~region],old[~region]);assert np.array_equal(v[:,:2],old[:,:2])
normal_region=region|surface['region']|np.load(B/'ArtSource/World/Gosain43/graded_surface.npz')['region'];local=normal_region[f].any(axis=1);ff=f[local];cross=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);acc=np.zeros_like(v)
for i in range(3):np.add.at(acc,ff[:,i],cross)
l=np.linalg.norm(acc,axis=1);use=normal_region&(l>1e-12);normals[use]=acc[use]/l[use,None]
assert np.isfinite(v).all();assert np.all(np.linalg.norm(cross,axis=1)>1e-10)
np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,region=region)
name='SM_IV_Continent_GosainKingdom50'
with (O/(name+'.obj')).open('w') as out:
    out.write('o '+name+'\n')
    for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
    for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
    for p in normals:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
    for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
report={'status':'source_only_not_applied','name':name,'sea_m':-20600,'terrace_heights_above_sea_m':[48,80,112,144,224], 'castle_is_highest':False,'modified_vertices':int(region.sum()),'unchanged_vertices':int((~region).sum()),'horizontal_coordinates_unchanged':True,'topology_unchanged':True,'old_height_range_above_sea_m':[float(old[region,2].min()+20600),float(old[region,2].max()+20600)],'new_height_range_above_sea_m':[float(v[region,2].min()+20600),float(v[region,2].max()+20600)],'max_lowering_m':float((old[:,2]-v[:,2]).max()),'elapsed_s':time.time()-t,'required_before_application':'Apply with reduced city meshes, countryside, lake and forest; hide obsolete island-wide defenses.'}
(O/'terrain_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
