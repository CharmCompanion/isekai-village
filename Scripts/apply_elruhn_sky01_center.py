"""Concentric levitation rig centered on the visible island footprint, not map zero."""
import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
actors=list(E.get_all_level_actors());surfaces=[a for a in actors if 'matching rock foundation' in a.get_actor_label() or 'rim rock collar' in a.get_actor_label()];assert len(surfaces)==2
bounds=[a.get_actor_bounds(False) for a in surfaces];minx=min(p.x-e.x for p,e in bounds);maxx=max(p.x+e.x for p,e in bounds);miny=min(p.y-e.y for p,e in bounds);maxy=max(p.y+e.y for p,e in bounds);cx=(minx+maxx)/2;cy=(miny+maxy)/2;z=-12000.
root=next((a for a in actors if a.get_actor_label()=='El Ruhn | centered levitation pivot'),None)
if not root:root=E.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(cx,cy,z));root.set_actor_label('El Ruhn | centered levitation pivot');root.set_folder_path('El Ruhn Sky/Levitation');root.tags=['ElRuhnSkyCenter01']
root.set_actor_location(unreal.Vector(cx,cy,z),False,False);report=[]
for i in range(5):
 angle=-math.pi/2+i*math.tau/5;target=unreal.Vector(cx+86800*math.cos(angle),cy+86800*math.sin(angle),z)
 stone=next(a for a in actors if a.get_actor_label().startswith('Levitation Stone %d '%(i+1)))
 seal=next(a for a in actors if a.get_actor_label().startswith('Stone %d |'%(i+1)))
 origin,_=stone.get_actor_bounds(False);p=stone.get_actor_location();stone.set_actor_location(p+(target-origin),False,False);seal.set_actor_location(target,False,False)
 for a in [stone,seal]:a.attach_to_actor(root,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 c,_=stone.get_actor_bounds(False);assert (c-target).length()<.01
 report.append({'stone':stone.get_name(),'center_m':[c.x/100,c.y/100,c.z/100],'seal_center_m':[target.x/100,target.y/100,target.z/100]})
for name,height in [('Island levitation ring | below village',z),('Island covenant | rune band',z+50)]:
 a=next(a for a in actors if a.get_actor_label()==name);a.set_actor_location(unreal.Vector(cx,cy,height),False,False);a.attach_to_actor(root,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'centering_applied.json').write_text(json.dumps({'status':'saved','center_definition':'XY midpoint of union of native visible rim and matching rock foundation bounds; excludes invisible landscape rectangle and props','island_center_m':[cx/100,cy/100],'ring_center_m':[cx/100,cy/100],'stone_orbit_radius_m':868,'equal_angular_spacing_degrees':72,'common_pivot':root.get_name(),'stone_and_seal_centers':report,'top_down_review':'pending'},indent=2))
