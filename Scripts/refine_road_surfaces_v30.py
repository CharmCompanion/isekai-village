from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/build_civilizations_v30.py');s=p.read_text().replace("h(*q)+.12","h(*q)+.35").replace("h(xx,yy)+.18","h(xx,yy)+.12")
s=s.replace("if z is None:z=h(x,y)","""if key in ['Oak','Pine','Palm','DesertPalm']:
  if field('road_clearance',x,y)<85:return
  if site is not None:
   q=sites[site];u=x-q['xy_m'][0];v=y-q['xy_m'][1];r=q['radius_m']
   if abs(v)<r and abs(u)<26:return
   if abs(u)<r and min(abs(v-r*.27-35*np.sin(u/(r*.38))),abs(v+r*.27-35*np.sin(u/(r*.38))))<22:return
 if z is None:z=h(x,y)""")
s=s.replace("add('Cart',ax+55,ay+30,height=3,yaw=90)","add('Cart',ax+55,ay+30,height=3,yaw=90)\n  ribbon([[ax-28,ay+32],[ax+30,ay+32]],7)")
p.write_text(s)
# This short finishing step runs after plan generation, avoiding an expensive repeat.
