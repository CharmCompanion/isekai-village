from pathlib import Path
P=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts');p=P/'prepare_civilized_world_v30.py';s=p.read_text()
s=s.replace("&(np.hypot(X,Y)>19000)&~urban","&(np.hypot(X,Y)>12000)&~urban")
s=s.replace("roadlabels,_=label(walk,np.ones((3,3)))","roadlabels,_=label(walk)")
s=s.replace("def nearest(q):\n px,py=q['pixel'];d=(wx-px/stride)**2+(wy-py/stride)**2;j=np.argmin(d);return (int(wy[j]),int(wx[j]))", """def nearest(q,component=None):
 px,py=q['pixel'];d=(wx-px/stride)**2+(wy-py/stride)**2
 if component is not None:d=np.where(roadlabels[wy,wx]==component,d,np.inf)
 j=np.argmin(d);return (int(wy[j]),int(wx[j]))""")
s=s.replace("approach.append(nearest(temp))","approach.append(nearest(temp,int(roadlabels[nodes[a]])))")
s=s.replace("if len(p)<2:raise ValueError(('unroutable sites',i,j))","if len(p)==0:raise ValueError(('unroutable sites',i,j))\n if len(p)==1:p=np.vstack([p,p])")
s=s.replace("# A* on a conservative", """# Persist the terrain/population stage separately so routing can be refined independently.
np.savez_compressed(S/'networks30_checkpoint.npz',h=h,color=color,clear=clear,slope=slope,X=X,Y=Y,channel=channel,wetblend=wetblend,urban=urban,farmcover=farmcover,dry=dry,water=water)
(S/'networks30_checkpoint.json').write_text(json.dumps({'sites':sites,'meta':meta,'farms':farms,'gridroutes':gridroutes,'relocated':relocated}))
# A* on a conservative""")
s=s.replace("D.update(height=h.astype", """mainmask=Image.new('L',(W,H));md=ImageDraw.Draw(mainmask)
for q in routes:md.line([(round(cx-x/M),round(cy-y/M)) for x,y in q['points_m']],fill=255,width=1)
D['road_clearance']=(distance_transform_edt(np.asarray(mainmask)==0)*M).astype('float32')
D.update(height=h.astype""")
p.write_text(s)
