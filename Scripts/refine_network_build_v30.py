from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/prepare_civilized_world_v30.py');s=p.read_text();s=s.replace("p=route(nodes[i],nodes[j])", """approach=[]
 for a,b in [(i,j),(j,i)]:
  q=sites[a];x,y=q['xy_m'];sgn=1 if sites[b]['xy_m'][1]>y else -1
  temp={'pixel':[cx-x/M,cy-(y+sgn*q['radius_m']*1.35)/M]};approach.append(nearest(temp))
 p=route(*approach)""")
s=s.replace("sign=1 if near[1]>y else -1","sign=1 if near[1]>y else -1").replace("ends.append([[x,y+sign*r*.55],[x,y+sign*r*.97]])","ends.append([[x,y+sign*r*.55],[x,y+sign*r*.97],[x,y+sign*r*1.35]])")
p.write_text(s)
