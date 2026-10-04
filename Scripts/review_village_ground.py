import unreal
eye=unreal.Vector(0,-2100,2680)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,1700,3100)))
