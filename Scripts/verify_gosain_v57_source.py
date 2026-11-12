"""Source-level locality and mesh closure verification; not runtime certification."""
import json,numpy as np
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57'
a=np.load(B/'ArtSource/World/Gosain56/graded_surface.npz');b=np.load(O/'graded_surface.npz')
v=a['vertices'];w=b['vertices'];f=b['triangles'];n=len(v);C=np.array([15950.,41900.])
outside=np.linalg.norm(v[:,:2]-C,axis=1)>170
changed=np.any(v!=w[:n],axis=1)
faces=f[np.any(f>=n,axis=1)];edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1);edges=edges[np.any(edges>=n,axis=1)]
unique,counts=np.unique(edges,axis=0,return_counts=True)
out={'original_vertices':n,'added_vertices':len(w)-n,'outside_170m_unchanged':bool(np.array_equal(v[outside],w[:n][outside])),'changed_original_vertices':int(changed.sum()),'finite_vertices':bool(np.isfinite(w).all()),'new_edges':len(unique),'new_edge_incidence_not_two':int((counts!=2).sum())}
sv=[];sf=[]
for line in (O/'SM_Gosain57_MineShell.obj').read_text().splitlines():
 if line.startswith('v '):sv.append([float(x) for x in line.split()[1:]])
 elif line.startswith('f '):sf.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
sv=np.array(sv);sf=np.array(sf);wv,idx=np.unique(np.round(sv,5),axis=0,return_inverse=True);wf=idx[sf]
se=np.sort(np.concatenate([wf[:,[0,1]],wf[:,[1,2]],wf[:,[2,0]]]),axis=1);_,sc=np.unique(se,axis=0,return_counts=True)
out['shell_welded_vertices']=len(wv);out['shell_faces']=len(wf);out['shell_nonmanifold_edges']=int((sc!=2).sum());out['shell_degenerate_faces']=int((np.linalg.norm(np.cross(sv[sf[:,1]]-sv[sf[:,0]],sv[sf[:,2]]-sv[sf[:,0]]),axis=1)<1e-7).sum())
(O/'source_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
assert out['outside_170m_unchanged'] and out['finite_vertices'] and out['new_edge_incidence_not_two']==0 and out['shell_nonmanifold_edges']==0 and out['shell_degenerate_faces']==0
