from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
p=json.loads((B/'Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json').read_text())
out=B/'Docs/WorldDesign';out.mkdir(exist_ok=True)
im=Image.new('RGB',(1500,1100),'#14292d');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',29)
def xy(x,y):return (65+(x+250)*1.65,98+(330-y)*1.65)
d.text((50,24),'ISEKAI VILLAGE  /  SETTLEMENT MASTER PLAN',font=bold,fill='#f4efd8')
d.text((51,62),'10 m logical cells · 520 × 530 m grid coverage · North up',font=font,fill='#a6c9bf')
palette={'available':'#406e58','reserved':'#bd954e','road':'#b5ae83','occupied':'#6589a1','rampart':'#665368','grand_square':'#a8bfc1','slope':'#293e42','gate_approach':'#c67d58','farm':'#798347'}
for c in p['cells']:
    if c['status']=='outside':continue
    x,y,z=c['center'];a=xy(x-5,y+5);b=xy(x+5,y-5)
    d.rectangle((*a,*b),fill=palette.get(c['status'],'#384f45'),outline='#1a3432',width=1)
d.line([xy(x,y) for x,y in p['boundary']+[p['boundary'][0]]],fill='#d1bcd2',width=3)
for r in p['future_roads']:d.line([xy(x,y) for x,y in r['points']],fill='#e8d8a8',width=3)
for f in p['farm']['fields']:
    x,y=f['center'];sx,sy=f['size'];a=xy(x-sx/2,y+sy/2);b=xy(x+sx/2,y-sy/2)
    d.rectangle((*a,*b),fill='#9a704b',outline='#d3d994',width=2)
    for row in range(8):
        yy=y-sy/2+2+row*3;d.line([xy(x-sx/2+1,yy),xy(x+sx/2-1,yy)],fill='#d9c982',width=1)
for r in p['farm']['roads']:d.line([xy(x,y) for x,y in r['points']],fill='#f6df9b',width=3)
x,y=p['farm']['farmhouse'];cx,cy=xy(x,y);d.rectangle((cx-9,cy-9,cx+9,cy+9),fill='#ec9979');d.text((cx+12,cy-12),'Farmhouse',font=small,fill='white')
for g in p['gates']:
    x,y=xy(*g['center']);d.ellipse((x-7,y-7,x+7,y+7),fill='#f0ba85')
for i,r in enumerate(p['reservations'],1):
    x,y,_=r['center'];cx,cy=xy(x,y);text=str(i);d.text((cx-5,cy-10),text,font=small,fill='#101f26')
d.text((1020,105),'RESERVED BUILDING PLOTS',font=font,fill='#f4efd8')
for i,r in enumerate(p['reservations'],1):d.text((1020,140+(i-1)*25),f'{i:02}  {r["type"]}  {r["size_cells"][0]*10}m',font=small,fill='#dbded0')
d.text((1020,890),'ERAS',font=font,fill='#f4efd8')
d.text((1020,920),'Village / timber\nLarge Town / stone\nKingdom / Architect expansion',font=font,fill='#a6c9bf',spacing=7)
d.text((50,1010),'Green: open construction cells   •   Gold: reserved plots   •   Blue: existing village',font=font,fill='#d9e0cc')
d.text((50,1040),'Roads, grand square, farmland, steep ground and defense corridors are protected.',font=font,fill='#a6c9bf')
im.save(out/'Settlement_Master_Plan.png')
print(out/'Settlement_Master_Plan.png')
