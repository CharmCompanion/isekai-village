"""Author spell sentences with the project's actual SpellRunes font; no model changes."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ArtSource/Magic/SlimeRunes'; OUT.mkdir(parents=True,exist_ok=True)
font_path=ROOT/'ReferenceAssets/Magic Spell/SpellRunes-Regular.otf'
font=ImageFont.truetype(str(font_path),170)
coverage=TTFont(font_path).getBestCmap()
specs=[
 ('Meadow','Verdant Bind','Bind','Terra - Nema - Viridia','EARTH','BIND',(0.2,1,.28),12,1.4,4,12,800,2,0,'Nature'),
 ('Water','Azure Pulse','Repel','Aqua - Vela - Unda','WATER','PUSH',(.06,.48,1),14,1.1,3.6,12,950,0,280,'Water'),
 ('Flame','Cinder Bloom','Ignite','Ignis - Nema - Cindra','FIRE','BURN',(1,.19,.035),16,1.4,4.5,16,850,3,3,'Fire'),
 ('Frost','Winter Needle','Chill','Aqua - Nema - Glacia','WATER','CHILL',(.38,.9,1),12,1.5,4.2,14,1000,3,0,'Ice'),
 ('Poison','Violet Miasma','Poison','Terra - Nema - Venen','EARTH','POISON',(.7,.12,1),8,1.6,5,16,700,5,4,'Poison'),
 ('Crystal','Prism Lance','Strike','Terra - Aegis - Prisma','EARTH','WARD',(.12,1,.83),18,1.8,6,20,1100,4,25,'Crystal'),
]
rows=[]
def point(r,a):return (512+r*math.cos(a),512+r*math.sin(a))
for prefix,name,effect,chant,element,kind,color,damage,cast,cooldown,cost,speed,duration,power,fx in specs:
 sentence=f'{effect} - Enemy - {name}'
 assert all(ord(c) in coverage for c in sentence),sentence
 img=Image.new('RGBA',(1024,1024)); d=ImageDraw.Draw(img)
 for radius,width in [(474,3),(464,1),(382,2),(368,1),(275,2)]:d.ellipse((512-radius,512-radius,512+radius,512+radius),outline='white',width=width)
 text=(sentence+' - ').upper()*2
 for i,char in enumerate(text):
  a=-math.pi/2+(i+.5)*math.tau/len(text)
  tile=Image.new('RGBA',(90,90))
  glyph=Image.new('RGBA',(400,400));ImageDraw.Draw(glyph).text((200,200),char,font=font,anchor='mm',fill='white')
  if glyph.getbbox():
   glyph=glyph.crop(glyph.getbbox());glyph.thumbnail((24,38),Image.Resampling.LANCZOS);tile.alpha_composite(glyph,((90-glyph.width)//2,(90-glyph.height)//2))
  tile=tile.rotate(-math.degrees(a)-90,resample=Image.Resampling.BICUBIC)
  x,y=point(422,a);img.alpha_composite(tile,(round(x-45),round(y-45)))
 for i in range(24):
  a=i*math.tau/24; d.line([point(368,a),point(275,a)],fill='white',width=2)
 # The inner geometric glyph remains fixed relative to the semantic sentence.
 n={'FIRE':3,'WATER':6,'EARTH':4}[element]
 pts=[point(255,-math.pi/2+i*math.tau/n) for i in range(n)];d.line(pts+[pts[0]],fill='white',width=3)
 # User-directed revision: effect seal replaces the central target cross.
 cx,cy=512,512
 if kind in ('BURN','POISON'):
  for dx in (-20,0,20):d.polygon([(cx+dx,cy-25),(cx+dx-9,cy+8),(cx+dx,cy+20),(cx+dx+9,cy+8)],outline='white',width=2)
 elif kind=='WARD':
  d.polygon([(cx,cy-34),(cx+15,cy),(cx,cy+34),(cx-15,cy)],outline='white',width=3)
  d.line([(cx,cy-27),(cx,cy+27)],fill='white',width=2)
 elif kind=='CHILL':
  p=[(cx+27*math.cos(i*math.tau/6),cy+27*math.sin(i*math.tau/6)) for i in range(6)];d.line(p+[p[0]],fill='white',width=3)
  if kind=='CHILL':
   for p0 in p:d.line([(cx,cy),p0],fill='white',width=2)
 elif kind=='BIND':
  p=[(cx+(.9*i)*math.cos(i*.3),cy+(.9*i)*math.sin(i*.3)) for i in range(35)];d.line(p,fill='white',width=3)
 else:
  for r in (12,22,32):d.arc((cx-r,cy-r,cx+r,cy+r),200,340,fill='white',width=3)
 img.save(OUT/f'T_Runes_{prefix}.png')
 rows.append(dict(id=prefix+'Slime',prefix=prefix,name=name,effect_word=effect,incantation=chant,element=element,effect=kind,color=color,damage=damage,cast_time=cast,cooldown=cooldown,tp_cost=cost,speed=speed,duration=duration,power=power,fx=fx,sentence=sentence))
(OUT/'spells.json').write_text(json.dumps(rows,indent=2))
sheet=Image.new('RGB',(1800,1280),(11,16,30));label=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
for i,r in enumerate(rows):
 x=(i%3)*600;y=(i//3)*640;im=Image.open(OUT/f'T_Runes_{r["prefix"]}.png').resize((530,530))
 tint=Image.new('RGBA',im.size,tuple(round(c*255) for c in r['color'])+(255,));tint.putalpha(im.getchannel('A'));sheet.paste(tint,(x+35,y+20),tint)
 dd=ImageDraw.Draw(sheet);dd.text((x+30,y+552),r['id']+' / '+r['name'],font=label,fill='white');dd.text((x+30,y+587),r['sentence'],font=label,fill=(170,187,210))
sheet.save(OUT/'Slime_Spell_Language.png')
print('Created six encoded rune circles and spell manifest:',OUT)
