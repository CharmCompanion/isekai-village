"""Add actual open tunnel shells and local Landscape cuts; retain all farm/town samples."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource'
H=np.load(S/'height_waterfall_v03.npy').copy();old=H.copy();N=1009
X,Y=np.meshgrid(np.linspace(-600,600,N),np.linspace(-600,600,N))
mask=np.asarray(Image.open(S/'T_IV_Biome_Farm_v02.png')).copy().astype(float)/255
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(x,y):return float(old[round((y+600)*.84),round((x+600)*.84)])
def curve(points,steps=8):
    out=[]
    for i in range(len(points)-1):
        p0=np.array(points[max(0,i-1)]);p1=np.array(points[i]);p2=np.array(points[i+1]);p3=np.array(points[min(len(points)-1,i+2)])
        for t in np.linspace(0,1,steps,endpoint=False):out.append((.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)).tolist())
    return out+[points[-1]]
def paint(points,width):
    d=np.full_like(X,1e6)
    for a,b in zip(points,points[1:]):
        ax,ay=a[:2];bx,by=b[:2];t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/max((bx-ax)**2+(by-ay)**2,.001),0,1)
        d=np.minimum(d,np.hypot(X-ax-t*(bx-ax),Y-ay-t*(by-ay)))
    mask[:,:,0]=np.maximum(mask[:,:,0],1-smooth(width*.7,width+1,d))
def cut(points,halfwidth):
    global H
    best=np.full_like(X,1e6);floor=np.zeros_like(X)
    for a,b in zip(points,points[1:]):
        ax,ay,az=a;bx,by,bz=b;t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/max((bx-ax)**2+(by-ay)**2,.001),0,1)
        d=np.hypot(X-ax-t*(bx-ax),Y-ay-t*(by-ay));sel=d<best;floor=np.where(sel,az+t*(bz-az),floor);best=np.minimum(best,d)
    w=1-smooth(halfwidth,halfwidth+2.4,best);H=H*(1-w)+floor*w
    paint(points,halfwidth*.85)
def obj(name,points,halfwidth,height,closed=False):
    verts=[];faces=[];uv=[]
    # Profile follows the floor, straight walls, then an elliptical ceiling.
    profile=[(-halfwidth,0),(-halfwidth,2.5)]+[(halfwidth*math.cos(t),2.5+(height-2.5)*math.sin(t)) for t in np.linspace(math.pi,0,17)[1:]]+[(halfwidth,0)]
    L=len(profile);count=len(points);length=0
    for i,p in enumerate(points):
        prev=np.array(points[max(0,i-1)]);nxt=np.array(points[min(count-1,i+1)]);f=nxt[:2]-prev[:2];f/=np.linalg.norm(f);right=np.array([f[1],-f[0]])
        if i:length+=np.linalg.norm(np.array(p)-np.array(points[i-1]))
        for outer in (False,True):
            for j,(x,z) in enumerate(profile):
                if outer:
                    x*=1.55;z=z+2.8 if z>0 else -.8
                v=np.array(p)+np.array([right[0]*x,right[1]*x,z])
                verts.append(v);uv.append((length/4,j/3))
    for i in range(count-1):
        for layer in (0,1):
            for j in range(L-1):
                a=i*L*2+layer*L+j;b=a+1;c=b+L*2;d=a+L*2
                faces.extend([(a,b,c),(a,c,d)] if layer==0 else [(a,c,b),(a,d,c)])
    for i in (0,count-1):
        for j in range(L-1):
            a=i*L*2+j;b=a+1;c=b+L;d=a+L
            faces.extend([(a,c,b),(a,d,c)])
    # Floor joins the sidewalls; the collision shell has an open entrance.
    for i in range(count-1):
        a=i*L*2;b=a+L-1;c=b+L*2;d=a+L*2;faces.extend([(a,c,b),(a,d,c)])
    if closed:
        i=(count-1)*L*2
        for j in range(1,L-1):faces.append((i,i+j,i+j+1))
    lines=['# Isekai route tunnel; centimetres, Unreal orientation after OBJ import']
    lines += [f'v {v[0]*100:.4f} {-v[1]*100:.4f} {v[2]*100:.4f}' for v in verts]
    lines += [f'vt {u:.5f} {v:.5f}' for u,v in uv]
    lines += ['f '+' '.join(f'{i+1}/{i+1}' for i in reversed(face)) for face in faces]
    (S/(name+'.obj')).write_text('\n'.join(lines)+'\n')
trade=curve([[-362,-84,55.6],[-391,-105,55.8],[-410,-145,56.1],[-412,-181,55.8],[-395,-205,54.8]])
mine=curve([[-328,294,68.0],[-345,302,68.4],[-361,313,68.8],[-369,325,69.1]])
dungeon=curve([[230,445,114.7],[238,460,115.1],[237,477,115.5],[245,489,115.8]])
routes=[]
for name,points,w,h,closed in [('TradePass',trade,4.6,7.8,False),('Mine',mine,3.1,5.4,True),('Dungeon',dungeon,4.7,8.0,True)]:
    cut(points,w+.35);obj('SM_'+name+'_Tunnel',points,w,h,closed)
    routes.append({'name':name,'points':points,'halfwidth':w,'height':h,'mesh':'SM_'+name+'_Tunnel','closed':closed})
mine_apron=[[-320,266,sample(-320,266)],[-320,281,67],[-328,294,68.0]]
cut(curve(mine_apron),3.3)
trade_exit=curve([[-395,-205,54.8],[-383,-220,52],[-393,-257,49],[-433,-306,45],[-486,-335,sample(-486,-335)],[-550,-350,sample(-550,-350)]])
cut(trade_exit,3.8)
for route in routes:route['entrance']=route['points'][0]
# A second waterfall screens the new right-hand dungeon entrance, alongside the walking line.
fx,fy=222,447;poolx,pooly=219,438;waterz=113.8
r=np.sqrt(((X-poolx)/5.5)**2+((Y-pooly)/8)**2);weight=1-smooth(1.05,1.6,r)
bed=112.7+1.6*smooth(.55,1.05,r);H=H*(1-weight)+bed*weight
# The fountain plaza becomes a paved civic heart, leaving future gardens reserved.
mask[:,:,0]=np.maximum(mask[:,:,0],1-smooth(17,18,np.hypot(X,Y)))
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Adventure_Routes_v04.r16')
np.save(S/'height_routes_v04.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_RouteHeight_RG.png')
Image.fromarray(np.rint(mask*255).astype('uint8')).save(S/'T_IV_Biome_Routes_v04.png')
town=(X>-220)&(X<300)&(Y>-230)&(Y<300)
assert np.array_equal(raw[town],np.rint(32768+old[town]*64).astype('<u2'))
plan={'version':4,'routes':routes,'trade_exit':trade_exit,'mine_apron':mine_apron,'dungeon_falls':{'fall':[fx,fy,waterz],'pool':[poolx,pooly,waterz]},'changed_height_samples':int(np.count_nonzero(np.rint(32768+old*64).astype('<u2')!=raw))}
(S/'mountain_routes_v04.json').write_text(json.dumps(plan,indent=2))
print(json.dumps({'tunnels':[(r['name'],len(r['points'])) for r in routes],'changed_samples':plan['changed_height_samples'],'town_and_farm_unchanged':True}))
