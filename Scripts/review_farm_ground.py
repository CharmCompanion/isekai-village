import unreal
eye=unreal.Vector(12800,-11900,2630)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(13000,-9800,2780)))
