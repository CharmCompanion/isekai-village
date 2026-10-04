import unreal,time,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');OUT=B/'Docs/WorldDesign';data=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v29.json').read_text());land=data['landmarks'];views=[]
for name,culture in [('SacredIsland','citadel'),('ArcaneCity','arcane'),('NomadCaravans','nomad'),('CultSanctuary','cult'),('FarmingPlains','farming'),('WetlandHarbor','harbor')]:
 q=next(q for q in land if q['culture']==culture);x,y=q['xy_m'];z=q['z'];r=q['radius'];eye=(x+r*1.35,y-r*1.85,z+r*1.05);target=(x,y,z+r*.08);views.append(('Civilizations29_'+name,eye,target))
q=next(q for q in land if q['culture']=='citadel');x,y=q['xy_m'];z=q['z'];views.insert(1,('Civilizations29_FortifiedCoast',(x+5500,y-7700,z+5100),(x,y,z-250)))
q=next(q for q in land if q['culture']=='citadel');x,y=q['xy_m'];z=q['z'];views.append(('Civilizations29_CathedralCourtyard',(x+210,y-340,z+125),(x,y+80,z+105)))
q=next(q for q in land if q['culture']=='arcane');x,y=q['xy_m'];z=q['z'];views.append(('Civilizations29_ArcaneStreet',(x+270,y-360,z+100),(x,y,z+60)))
views.append(('Civilizations29_Island',(850,-1280,440),(0,30,-190)))
state={'index':0,'stage':'camera','next':0,'completed':[]};holder={}
def write():(B/'Saved/civilizations_render_v29.json').write_text(json.dumps(state,indent=2))
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
