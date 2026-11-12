"""Original connected Gosain urban block: courtyard, passages and arcaded front."""
import gosain37_geometry as g
import numpy as np,json
O=g.ROOT/'ArtSource/World/Gosain41';O.mkdir(exist_ok=True);g.OUT=O
m=g.Mesh();rng=np.random.default_rng(41016)
# All dimensions metres. Central court opens through axial 6m passages.
def box(p,s,mat='stone',yaw=0):m.box(p,s,mat,yaw)
def roof(x,y,w,d,z,h=3):
    v=np.array([[x-w/2-.5,y-d/2-.5,z],[x+w/2+.5,y-d/2-.5,z],[x+w/2+.5,y+d/2+.5,z],[x-w/2-.5,y+d/2+.5,z],[x-w/2-.5,y,z+h],[x+w/2+.5,y,z+h]])
    m.part(v,[[0,1,5],[0,5,4],[4,5,2],[4,2,3]],'roof');m.part(v,[[0,4,3],[1,2,5]],'plaster')
def facade(x,y,w,z,levels,side=1):
    # Stone sill courses and inset dark windows retain a readable multi-storey scale.
    for level in range(levels):
        zz=z+level*3.4
        box([x,y,zz],[w,.16,.18],'trim')
        for xx in np.arange(x-w/2+1.5,x+w/2-1,3):
            box([xx,y+side*.13,zz+.85],[1.25,.14,1.7],'window')
            for dx in [-.72,.72]:box([xx+dx,y+side*.24,zz+.72],[.16,.24,1.95],'trim')
            box([xx,y+side*.24,zz+.68],[1.6,.30,.18],'trim');box([xx,y+side*.24,zz+2.58],[1.6,.25,.18],'trim')
            box([xx,y+side*.3,zz+.85],[.08,.12,1.7],'wood')
            if (int(abs(xx*2))+level)%5==0:box([xx,y+side*.33,zz+.85],[1.15,.12,1.7],'wood')
def house(x,y,w,d,levels,base=0,arcade=False):
    z=base+(4.2 if arcade else 0);height=levels*3.4
    box([x,y,base-1],[w,d,1],'foundation')
    if arcade:
        # Covered pedestrian gallery under occupied upper floors, open to courtyard/street.
        for xx in np.linspace(x-w/2+.4,x+w/2-.4,max(2,int(w/3.5)+1)):
            for yy in [y-d/2+.4,y+d/2-.4]:
                box([xx,yy,base],[.65,.65,4.2],'stone');box([xx,yy,base+3.7],[1,.9,.5],'trim')
        # Inhabited shop rooms occupy the back of the ground floor.
        back=y+d/2;front=y-d/2+5
        box([x,back-.2,base],[w,.4,4.2],'stone')
        for sx in [-1,1]:box([x+sx*(w/2-.2),(front+back)/2,base],[.4,back-front,4.2],'stone')
        box([x,front,base+3],[w,.4,1.2],'stone')
        for cx,ww in [(x-w/2+1,2),(x,4),(x+w/2-1,2)]:box([cx,front,base],[ww,.4,3],'stone')
        cols=np.linspace(x-w/2+.4,x+w/2-.4,max(2,int(w/3.5)+1))
        for ca,cb in zip(cols[:-1],cols[1:]):
            mid=(ca+cb)/2;rad=(cb-ca-.65)/2;theta=np.linspace(np.pi,0,13)
            for t0,t1 in zip(theta[:-1],theta[1:]):
                xa,xb=mid+rad*np.cos(t0),mid+rad*np.cos(t1);za,zb=base+2+rad*np.sin(t0),base+2+rad*np.sin(t1)
                vv=[[xa,y-d/2+.05,za],[xb,y-d/2+.05,zb],[xb,y-d/2+.05,base+4.2],[xa,y-d/2+.05,base+4.2],[xa,y-d/2+.7,za],[xb,y-d/2+.7,zb],[xb,y-d/2+.7,base+4.2],[xa,y-d/2+.7,base+4.2]]
                m.part(vv,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2]],'stone')
        box([x,y,z-.35],[w,d,.35],'stone')
    plaster=['plaster','plaster_cream','plaster_ochre'][int(abs(x)/12+abs(y)/10)%3]
    box([x,y,z],[w,d,height],plaster)
    for yy,sg in [(y-d/2,-1),(y+d/2,1)]:facade(x,yy,w,z,levels,sg)
    for xx,sg in [(x-w/2,1),(x+w/2,-1)]:
        begin=len(m.v);facade(0,0,d,z,levels,sg)
        for ii in range(begin,len(m.v)):
            vx,vy,vz=m.v[ii];m.v[ii]=[xx-vy,y+vx,vz]
    box([x,y,z+height-.2],[w+.5,d+.5,.32],'trim');roof(x,y,w,d,z+height,2.8+w*.06)
    if levels>=4:box([x+w*.28,y,z+height],[1.1,1.1,5],'stone')
# Continuous perimeter wings with deliberately open middle passageways.
for y,levels in [(-30,3),(30,4)]:
    for side in [-1,1]:
        for j in range(3):
            x=side*(9+12*j);house(x,y,12,14,levels+(j%2),arcade=(y==-30))
for x in [-39,39]:
    for side in [-1,1]:
        for j in range(2):
            y=side*(8+10*j)
            # Side wings adjoin the perimeter ends; short inner passages remain usable.
            house(x,y,12,10,3+(j%2))
# Upper-floor links span the north/south passages, leaving 4.5m head clearance.
for y in [-30,30]:house(0,y,6,14,2,base=5.5)
# Court paving, sheltered gallery floor and alley exits.
box([0,0,-.22],[66,46,.22],'paving')
for y in [-30,30]:box([0,y,-.15],[6,28,.15],'paving')
for x in [-39,39]:box([x,0,-.15],[24,6,.15],'paving')
box([0,-30,-.15],[90,14,.15],'paving')
# One raised public terrace with broad stair, leaving the north/south route clear.
box([-18,9,0],[16,14,1.8],'stone');box([-18,9,1.8],[16,14,.15],'paving')
for j in range(10):box([-18,-1.42+j*.38,0],[5,.4,(j+1)*.18],'stone')
for x in [-25.5,-10.5]:box([x,9,1.95],[.5,14,.9],'stone')
# Shop awnings create an occupied street edge without blocking the arcade.
for x in [-30,-18,-6,6,18,30]:
    box([x,-38,3.4],[5,3,.12],'awning')
    for dx in [-2.3,2.3]:box([x+dx,-39.3,0],[.14,.14,3.4],'wood')
def write_block(mesh,name):
    v=np.array(mesh.v);f=np.array(mesh.f);norm=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);length=np.linalg.norm(norm,axis=1);valid=length>1e-8;f=f[valid];norm=norm[valid]/length[valid,None];mats=np.array(mesh.mat)[valid]
    with (O/(name+'.obj')).open('w') as out:
        out.write('o '+name+'\n')
        for x,y,z in v:out.write('v %.5f %.5f %.5f\n'%(x*100,-y*100,z*100))
        for face,n in zip(f,norm):
            axis=int(np.argmax(np.abs(n)));uv=v[face][:,[j for j in range(3) if j!=axis]]/4
            for u,w in uv:out.write('vt %.6f %.6f\n'%(u,w))
        for x,y,z in norm:out.write('vn %.6f %.6f %.6f\n'%(x,-y,z))
        last=None
        for i,(face,mat) in enumerate(zip(f,mats)):
            if mat!=last:out.write('usemtl '+mat+'\n');last=mat
            out.write('f '+' '.join('%d/%d/%d'%(face[j]+1,i*3+j+1,i+1) for j in [2,1,0])+'\n')
    return {'name':name,'vertices':len(v),'triangles':len(f),'materials':sorted(set(mats.tolist())),'origin_m':[0,0,0],'uv_mapping':'per-face dominant-axis projection; no collapsed vertical-face UVs'}
q=write_block(m,'SM_Gosain41_ConnectedUrbanBlock');(O/'urban_block.json').write_text(json.dumps({'status':'source_prototype_not_applied','mesh':q,'dimensions_m':[90,80],'building_language':'continuous multi-storey courtyard block with covered passages and front arcade','passage_width_m':6,'upper_link_clearance_m':4.5,'limitations':['External architectural prototype; occupied upper floors have no authored interiors.','Must inspect wing junctions and passage clearance in native Unreal before placement.','Not yet a replacement for the entire capital.']},indent=2));print(q,flush=True)


