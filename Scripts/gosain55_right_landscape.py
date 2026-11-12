"""Gosain right island relief, preserving town, coast and bridge abutments."""
import numpy as np,shapely
import gosain51_kingdom as k
PEAKS=[(17000,43200,650,520,900),(17100,44300,490,450,700),(16800,42150,470,650,750),(15700,41400,280,650,600),(18100,41700,220,500,650)]
MINE=np.array([15950.,41900.])
def height(p,old):
 p=np.asarray(p,float).reshape(-1,2);out=np.asarray(old,float).copy();ps=shapely.points(p);inside=shapely.contains(k.POLYS[1],ps);ix=np.flatnonzero(inside)
 if not len(ix):return out
 q=p[ix];pts=ps[ix];mass=[]
 for x,y,h,sx,sy in PEAKS:mass.append(h*np.exp(-(((q[:,0]-x)/sx)**2+((q[:,1]-y)/sy)**2)*.65))
 mountain=np.power(np.sum(np.power(mass,6),axis=0),1/6)
 detail=1+.065*np.sin(q[:,0]/170+q[:,1]/290)+.045*np.cos(q[:,0]/95-q[:,1]/210)
 country=68+20*np.sin(q[:,0]/1000)*np.cos(q[:,1]/1300)+12*np.sin((q[:,0]+q[:,1])/640)
 foothill=80*np.exp(-(((q[:,0]-17000)/1900)**2+((q[:,1]-42500)/2600)**2))
 natural=k.SEA+country+mountain*detail+foothill
 coast=shapely.distance(pts,k.POLYS[1].boundary);town=shapely.distance(pts,k.TOWNS[1]);blend=k.old.ease(coast/350)*k.old.ease(town/550)
 for end in k.old.PLAN['bridge_endpoints_m']:blend*=k.old.ease((np.linalg.norm(q-np.array(end),axis=1)-180)/250)
 out[ix]=out[ix]*(1-blend)+natural*blend
 return out
