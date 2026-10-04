import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');OUT=B/'Docs/WorldDesign';data=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v30.json').read_text());land=data['landmarks'];views=[]
for name,culture in [('SacredIsland','citadel'),('ArcaneCity','arcane'),('NomadCaravans','nomad'),('CultSanctuary','cult'),('FarmingPlains','farming'),('WetlandHarbor','harbor')]:
 q=next(q for q in land if q['culture']==culture);x,y=q['xy_m'];z=q['z'];r=q['radius'];eye=(x+r*1.35,y-r*1.85,z+r*1.05);target=(x,y,z+r*.08);views.append(('Civilizations30_'+name,eye,target))
q=next(q for q in land if q['culture']=='citadel');x,y=q['xy_m'];z=q['z'];views.insert(1,('Civilizations30_FortifiedCoast',(x+5500,y-7700,z+5100),(x,y,z-250)))
q=next(q for q in land if q['culture']=='citadel');x,y=q['xy_m'];z=q['z'];views.append(('Civilizations30_CathedralCourtyard',(x+210,y-340,z+125),(x,y+80,z+105)))
q=next(q for q in land if q['culture']=='arcane');x,y=q['xy_m'];z=q['z'];views.append(('Civilizations30_ArcaneStreet',(x+270,y-360,z+100),(x,y,z+60)))
for name,culture in [('RabaricNetwork','farming'),('KelsinNetwork','arcane'),('DesertRoutes','nomad')]:
 q=next(q for q in land if q['culture']==culture);x,y=q['xy_m'];z=q['z'];views.append(('Civilizations30_'+name,(x-6200,y+8700,z+8200) if culture=='farming' else (x+6200,y-8700,z+8200),(x+2000,y-3500,z) if culture=='farming' else (x,y,z)))
meta=json.loads((B/'Saved/AdventureWorldSource/world_design_v30.json').read_text())
farm_sites=[q for q in meta['settlements'] if q['country']=='RabaricRepublic']
pairs=[(sum((a-b)**2 for a,b in zip(q['xy_m'],t['xy_m'])),q,t) for i,q in enumerate(farm_sites) for t in farm_sites[:i] if q['kind']!='city' and t['kind']!='city']
_,q,t=min(pairs,key=lambda v:v[0]);x=(q['xy_m'][0]+t['xy_m'][0])*.5;y=(q['xy_m'][1]+t['xy_m'][1])*.5;z=(q['ground_m']+t['ground_m'])*.5
views.append(('Civilizations30_FarmVillages',(x+1900,y-2700,z+2400),(x,y,z)))
if meta.get('bridges'):
 p=meta['bridges'][0]['points_m'];x=(p[0][0]+p[-1][0])*.5;y=(p[0][1]+p[-1][1])*.5
 views.append(('Civilizations30_TidalBridge',(x+750,y-1100,-20020),(x,y,-20590)))
views.append(('Civilizations30_Island',(850,-1280,440),(0,30,-190)))
state={'index':0,'stage':'camera','next':0,'completed':[]};holder={}
def write():(B/'Saved/civilizations_render_v30.json').write_text(json.dumps(state,indent=2))
def tick(delta):
 if time.monotonic()<state['next']:return
 if state['index']>=len(views):
  state['stage']='complete';write();unreal.unregister_slate_post_tick_callback(holder['handle']);return
 name,eye,target=views[state['index']];path=OUT/(name+'.png')
 if state['stage']=='camera':
  a=unreal.Vector(*(v*100 for v in eye));b=unreal.Vector(*(v*100 for v in target));unreal.EditorLevelLibrary.set_level_viewport_camera_info(a,unreal.MathLibrary.find_look_at_rotation(a,b));state['next']=time.monotonic()+6;state['stage']='capture'
 elif state['stage']=='capture':
  state['mtime']=path.stat().st_mtime if path.exists() else 0;unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(path),delay=.5);state['stage']='waiting';state['next']=time.monotonic()+2
 elif path.exists() and path.stat().st_mtime>state['mtime']:state['completed'].append(str(path));state['index']+=1;state['stage']='camera'
 else:state['next']=time.monotonic()+1
 write()
holder['handle']=unreal.register_slate_post_tick_callback(tick)
