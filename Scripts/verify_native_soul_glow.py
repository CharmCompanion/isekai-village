changed=[]
for actor in pair:
 comp=actor.get_editor_property('skeletal_mesh_component')
 for mi in comp.get_materials():
  if mi and mi.get_path_name().startswith('/Game/Elrhun/Golems/PlayerBody/Materials/Classes/') and mi not in changed:changed.append(mi)
try:
 for mi in changed:M.set_material_instance_scalar_parameter_value(mi,'ELR_GlowStrength',12.)
 capture=actor_sys.spawn_actor_from_class(u.SceneCapture2D,eye,u.MathLibrary.find_look_at_rotation(eye,center+u.Vector(0,0,95)));cap=capture.get_component_by_class(u.SceneCaptureComponent2D);rt=u.RenderingLibrary.create_render_target2d(world,1800,1200,u.TextureRenderTargetFormat.RTF_RGBA8);cap.set_editor_property('texture_target',rt);cap.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('fov_angle',38.);cap.capture_scene();u.RenderingLibrary.export_render_target(world,rt,'C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs','Elrhun_Glow_Position_Check.png');actor_sys.destroy_actor(capture)
finally:
 for mi in changed:M.set_material_instance_scalar_parameter_value(mi,'ELR_GlowStrength',.45);A.save_loaded_asset(mi,only_if_is_dirty=False)
