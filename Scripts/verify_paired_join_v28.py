import unreal,json,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=E.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mountain=next(a for a in actors if 'IVJoined13' in [str(t) for t in a.tags]);land=next(a for a in actors if isinstance(a,unreal.Landscape))
raw=struct.unpack('<'+'H'*1009**2,(B/'Saved/AdventureWorldSource/IV_DishPeak_v11.r16').read_bytes())
def h(x,y):
 u=max(0,min(1007.999,(x+600)*.84));v=max(0,min(1007.999,(y+600)*.84));i=int(u);j=int(v);a=u-i;b=v-j
 value=(raw[j*1009+i]*(1-a)+raw[j*1009+i+1]*a)*(1-b)+(raw[(j+1)*1009+i]*(1-a)+raw[(j+1)*1009+i+1]*a)*b
 return (value-32768)/64
ignore=[a for a in actors if a not in [land,mountain]]
checks=[]
for i in range(256):
 angle=math.tau*i/256;o=(1+.012*math.sin(7*angle)+.008*math.sin(13*angle))/(abs(math.cos(angle))**4+abs(math.sin(angle))**4)**.25
 for r in [.995,.999,1.0015]:
  x=580*math.cos(angle)*o*r;y=20+570*math.sin(angle)*o*r;z=h(x,y)
  hit=unreal.SystemLibrary.line_trace_single_for_objects(w,unreal.Vector(x*100,y*100,(z+5)*100),unreal.Vector(x*100,y*100,(z-5)*100),[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],True,ignore,unreal.DrawDebugTrace.NONE,True);result=hit.to_tuple() if hit else None
  checks.append({'angle_degrees':i*360/256,'radius':r,'hit':bool(result and result[0]),'height_difference':(result[4].z/100-z) if result and result[0] else None})
ignore=[a for a in actors if a!=mountain];radial=[]
for z in [-150,-400,-700]:
 for i in range(32):
  a=math.tau*i/32;hit=unreal.SystemLibrary.line_trace_single_for_objects(w,unreal.Vector((-82+1600*math.cos(a))*100,(58+1600*math.sin(a))*100,z*100),unreal.Vector(-8200,5800,z*100),[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],True,ignore,unreal.DrawDebugTrace.NONE,True);result=hit.to_tuple() if hit else None;radial.append({'angle':i*11.25,'height':z,'hit':bool(result and result[0])})
report={'join_checks':checks,'all_768_join_checks_pass':all(c['hit'] for c in checks),'join_failures':[c for c in checks if not c['hit']],'all_96_underside_checks_pass':all(c['hit'] for c in radial),'underside_checks':radial,'geometry':json.loads((B/'Saved/AdventureWorldSource/joined_mountain_v13.json').read_text())}
(B/'Saved/paired_join_validation_v28.json').write_text(json.dumps(report,indent=2));assert report['all_768_join_checks_pass'];assert report['all_96_underside_checks_pass']
