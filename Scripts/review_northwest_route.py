import unreal,json
from pathlib import Path
e=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out=[]
for a in e.get_all_level_actors():
    if str(a.get_folder_path()).startswith('Adventure/SealedCave'):
        out.append({'name':a.get_actor_label(),'location':str(a.get_actor_location()),'bounds':str(a.get_actor_bounds(False))})
for p in ['/Game/SoStylized/Environment/Water/Waterfalls/SM_Waterfall1','/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1']:
    m=unreal.load_asset(p)
    out.append({'asset':p,'bounds':str(m.get_bounding_box()),'materials':[str(m.get_material(i)) for i in range(m.get_num_sections(0))]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/northwest_review.json').write_text(json.dumps(out,indent=2))
eye=unreal.Vector(-32000,23500,12500)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(-35000,27500,8700)))
