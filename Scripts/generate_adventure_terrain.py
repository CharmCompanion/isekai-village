"""Deterministic native-Landscape source; +X east, +Y north, metres."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
OUT.mkdir(parents=True,exist_ok=True)
N=1009
AX=np.linspace(-600,600,N)
X,Y=np.meshgrid(AX,AX)
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1)
    return t*t*(3-2*t)
def g(x,y,sx,sy):return np.exp(-((X-x)/sx)**2-((Y-y)/sy)**2)
# A warm sheltered basin, an irregular beach, and a genuinely seaward cliff.
shore=-420+22*np.sin(X/125)+12*np.sin(X/53)
H=-15+39*smooth(shore-50,shore+155,Y)
H+=2*np.sin(X/73)*np.sin(Y/81)+1.3*np.cos(X/42+Y/69)
H+=45*g(-370,100,155,310)+32*g(80,310,310,140)
for x,y,sx,sy,h in [(-495,405,105,200,190),(-295,530,140,105,230),(-55,560,130,115,194),(190,548,145,110,216),(-565,45,90,155,180),(-520,-175,85,130,115)]:
    ridge=g(x,y,sx,sy)
    H+=h*ridge*(1+.10*np.sin(X/26+Y/31)+.055*np.sin(X/12-Y/24))
headland=smooth(235,410,X)*(42+45*smooth(-340,340,Y))
H+=headland
edge=480+18*np.sin(Y/105)+8*np.sin(Y/39)
H=H*(1-smooth(edge-15,edge+15,X))-20*smooth(edge-15,edge+15,X)
# Central town terrace and reserve meadows remain generous and buildable.
town=1-smooth(115,215,np.sqrt((X*.92)**2+((Y+5)*1.05)**2))
H=H*(1-town)+(25+.007*Y+.003*X)*town

ROUTES=[
 {'name':'Harbor Road','width':4.5,'points':[(0,-12),(0,-75),(30,-145),(15,-215),(-20,-295),(-35,-390)]},
 {'name':'Guild Walk','width':4,'points':[(-85,-30),(-55,-15),(-22,0),(0,0),(30,15),(60,38),(70,85)]},
 {'name':'Market Crescent','width':3.5,'points':[(-60,55),(-35,35),(0,27),(38,22),(67,-12),(65,-50),(32,-68),(0,-75),(-43,-64),(-72,-37),(-60,0),(-60,55)]},
 {'name':'Whisperwood Trail','width':3,'points':[(-60,55),(-95,100),(-145,133),(-196,139),(-240,170),(-270,226),(-304,259),(-350,274)]},
 {'name':'North Pass','width':3.2,'points':[(70,85),(95,145),(80,215),(110,270),(163,310),(195,385),(230,445)]},
 {'name':'East Meadow','width':3,'points':[(65,-50),(123,-66),(184,-45),(240,-4),(280,48),(302,122)]},
 {'name':'Farm Lane','width':2.8,'points':[(15,-215),(90,-200),(135,-220),(187,-260)]},
 {'name':'West Ridge','width':2.7,'points':[(-72,-37),(-142,-47),(-212,-15),(-274,6),(-310,-45),(-362,-84)]}
]
def curved(points):
    p=np.asarray([points[0]]+points+[points[-1]],dtype=float);res=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for t in np.linspace(0,1,6,endpoint=False):
            res.append((.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)).tolist())
    return res+[list(points[-1])]
for route in ROUTES:route['points']=curved(route['points'])
def route_distance(points):
    d=np.full_like(H,1e9); target=H.copy()
    for (a,b),(c,e) in zip(points,points[1:]):
        t=np.clip(((X-a)*(c-a)+(Y-b)*(e-b))/((c-a)**2+(e-b)**2),0,1)
        dist=np.hypot(X-a-t*(c-a),Y-b-t*(e-b))
        za=float(H[round((b+600)/1200*(N-1)),round((a+600)/1200*(N-1))])
        zb=float(H[round((e+600)/1200*(N-1)),round((c+600)/1200*(N-1))])
        target=np.where(dist<d,za+(zb-za)*t,target);d=np.minimum(d,dist)
    return d,target
ROAD=np.zeros_like(H)
for r in ROUTES:
    d,z=route_distance(r['points']);w=r['width']
    blend=(1-smooth(w+1,w+7,d))*.88
    H=H*(1-blend)+z*blend
    ROAD=np.maximum(ROAD,1-smooth(w*.7,w+1,d))
PLAZA=1-smooth(12,14,np.hypot(X,Y))
H=H*(1-PLAZA)+25*PLAZA
ROAD=np.maximum(ROAD,PLAZA)
# Curated building sites; values are metres and final footprint radius.
BUILDINGS=[
 ('Guild Hall',39,51,15,6,225),('Inherited House',-35,57,10,2,275),
 ('Seabreeze Inn',-38,-26,13,8,20),('Bakery',26,-27,9,1,160),
 ('General Store',43,-43,10,4,160),('Smithy',-81,-18,11,3,10),
 ('Cottage A',-28,-84,9,5,60),('Cottage B',-53,-76,9,7,80),
 ('Cottage C',85,17,10,9,180),('Cottage D',12,58,9,10,270),
 ('Farmhouse',115,-181,10,11,220),('Harbormaster',-64,-366,10,1,5)]
for name,x,y,r,variant,yaw in BUILDINGS:
    z=float(H[round((y+600)/1200*(N-1)),round((x+600)/1200*(N-1))])
    t=1-smooth(r,r+7,np.hypot(X-x,Y-y));H=H*(1-t)+z*t
    ROAD=np.maximum(ROAD,(1-smooth(r-1,r+1,np.hypot(X-x,Y-y)))*.3)
# Small cultivated terraces are part of the ground, not floating cubes.
for x,y in [(100,-230),(133,-244),(162,-222)]:
    d=np.maximum(abs(X-x)/12,abs(Y-y)/20)
    z=float(H[round((y+600)/1200*(N-1)),round((x+600)/1200*(N-1))])
    t=1-smooth(.9,1.3,d);H=H*(1-t)+z*t
    ROAD=np.maximum(ROAD,(1-smooth(.9,1,d))*.95)
DY,DX=np.gradient(H,1200/(N-1)); slope=np.hypot(DX,DY)
SAND=1-smooth(3,9,H)
ROCK=np.maximum(smooth(.4,.95,slope),smooth(115,220,H)*.8)
SNOW=smooth(200,270,H)*(1-smooth(.8,1.8,slope))
RAW=np.clip(np.rint(32768+H*64),0,65535).astype('<u2') # Zscale 200
RAW.tofile(OUT/'IV_Adventure_1009.r16')
Image.fromarray(RAW).save(OUT/'IV_Adventure_1009.png')
RG=np.stack([RAW>>8,RAW&255,np.zeros_like(RAW),np.full_like(RAW,255)],-1).astype('uint8')
Image.fromarray(RG).save(OUT/'T_IV_Height_RG.png')
Image.fromarray(np.rint(np.stack([ROAD,SAND,ROCK,SNOW],-1)*255).astype('uint8')).save(OUT/'T_IV_Biome.png')
np.save(OUT/'height.npy',H)
meta={'size':N,'span_m':1200,'origin_cm':[-60000,-60000,0],'xy_scale':120000/(N-1),'z_scale':200,'height_range':[float(H.min()),float(H.max())],'routes':ROUTES,'buildings':BUILDINGS}
(OUT/'world.json').write_text(json.dumps(meta,indent=2))
# A plan rendered directly from the real height source, with north at top.
color=np.zeros((*H.shape,3));color[:]=[91,132,70]
for mask,col in [(ROAD,[169,138,90]),(SAND,[212,193,143]),(ROCK,[113,128,133]),(SNOW,[224,234,235])]:color=color*(1-mask[...,None])+np.array(col)*mask[...,None]
shade=np.clip((1-.38*DX+.55*DY)/np.sqrt(1+DX*DX+DY*DY),.35,1.3)
color*=shade[...,None];color[H<0]=[50,121,155]
im=Image.fromarray(np.clip(color[::-1],0,255).astype('uint8')).resize((1100,1100))
d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
for name,x,y in [('Fountain / Village',0,0),('Whisperwood',-225,225),('Sealed Cave',-350,285),('Crown Peaks',20,490),('Eastern Cliffs',380,80),('South Harbor',-40,-410),('Farm Terraces',135,-220),('Expansion Meadows',190,140)]:
    px=(x+600)/1200*1100;py=(600-y)/1200*1100
    d.ellipse((px-4,py-4,px+4,py+4),fill='white')
    d.text((px+9,py-10),name,font=font,fill='white',stroke_width=2,stroke_fill='#23323a')
d.text((22,20),'ISEKAI VILLAGE  /  TERRAIN & DISTRICTS',font=font,fill='white')
d.text((22,49),'NORTH UP  •  1.2 km × 1.2 km  •  Native Unreal Landscape',font=font,fill='white')
im.save(OUT/'World_Layout.png')
print(json.dumps({'height':meta['height_range'],'files':str(OUT)}))
