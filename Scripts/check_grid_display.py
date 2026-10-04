import unreal,json
from pathlib import Path
out=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if str(a.get_folder_path())=='BuildGrid/Debug':
        c=a.static_mesh_component
        out.append({'name':a.get_actor_label(),'hidden':a.get_editor_property('hidden'),'temporary':a.is_temporarily_hidden_in_editor(),'visible':c.is_visible(),'triangles':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_number_verts(c.static_mesh,0)})
        a.set_actor_hidden_in_game(False)
        a.set_is_temporarily_hidden_in_editor(False)
        c.set_visibility(True)
eye=unreal.Vector(12000,-23000,15000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(5000,-3000,2500)))
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/grid_display_check.json').write_text(json.dumps(out,indent=2))
