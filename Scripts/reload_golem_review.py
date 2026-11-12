import unreal as u,time
world=u.EditorLoadingAndSavingUtils.load_map('/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(0,-1120,490),u.Rotator(pitch=-11,yaw=90,roll=0))
started=time.monotonic()
def snap(delta):
 if time.monotonic()-started<5:return
 u.unregister_slate_post_tick_callback(handle);u.AutomationLibrary.take_high_res_screenshot(1600,1000,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs/Elrhun_Golems_LightingFixed.png')
handle=u.register_slate_post_tick_callback(snap)
