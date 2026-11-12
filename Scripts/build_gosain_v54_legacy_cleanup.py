import sys,json,numpy as np,shapely
from pathlib import Path
sys.path.insert(0,'Scripts');import gosain51_kingdom as k
O=Path('ArtSource/World/Gosain54');O.mkdir(exist_ok=True);reports=[]
for kind in ['RoadsOutsideCity','FoundationsOutsideCity']:
 src=Path('ArtSource/World/Gosain47')/('SM_Gosain47_'+kind+'.obj');lines=src.read_text().splitlines(True)
 vertices=np.array([[float(q) for q in l.split()[1:4]] for l in lines if l.startswith('v ')]);vertices[:,1]*=-1;vertices/=100
 face_lines=[i for i,l in enumerate(lines) if l.startswith('f ')];faces=[[int(p.split('/')[0])-1 for p in lines[i].split()[1:]] for i in face_lines]
 centroids=np.array([vertices[f].mean(axis=0) for f in faces]);points=shapely.points(centroids[:,:2]);inside=shapely.contains(shapely.union_all(k.POLYS),points)
 reject=set(np.array(face_lines)[inside]);name='SM_Gosain54_'+kind
 with (O/(name+'.obj')).open('w') as out:
  for i,l in enumerate(lines):
   if i not in reject:out.write('o '+name+'\n' if l.startswith('o ') else l)
 reports.append({'name':name,'removed_Gosain_triangles':int(inside.sum()),'retained_other_triangles':int((~inside).sum()),'retained_vertex_and_face_records_unchanged':True})
(O/'legacy_cleanup.json').write_text(json.dumps(reports,indent=2));print(reports)
