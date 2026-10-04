import unreal,struct,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Layered_v05.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
out=[]
for a in E.get_all_level_actors():
    if a.get_actor_label()=='Entrance shoulder rock':
        p=a.get_actor_location();box=a.static_mesh_component.static_mesh.get_bounding_box();size=4.4 if 'Mine' in str(a.get_folder_path()) else 5.5
        scale=size*100/max(box.max.x-box.min.x,box.max.y-box.min.y);a.set_actor_scale3d(unreal.Vector(scale,scale,scale*1.2))
        a.set_actor_location(unreal.Vector(p.x,p.y,h(p.x/100,p.y/100)*100-box.min.z*scale*1.2),False,False)
    if a.get_actor_label()=='Tunnel lantern glow':a.get_component_by_class(unreal.PointLightComponent).set_editor_property('intensity',95)
    if isinstance(a,unreal.StaticMeshActor) and 'continuous walkable tunnel' in a.get_actor_label():out.append({'name':a.get_actor_label(),'bounds':str(a.get_actor_bounds(False)),'verts':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_number_verts(a.static_mesh_component.static_mesh,0)})
    if a.get_actor_label()=='Southern Sea - Coastal Ocean':a.set_actor_scale3d(unreal.Vector(200000,200000,1))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/tunnel_mesh_check.json').write_text(json.dumps(out,indent=2))
unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(B/'Docs/WorldDesign/Trade_Pass_Review.png'),delay=1.)
