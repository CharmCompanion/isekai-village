import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';world=u.EditorLoadingAndSavingUtils.load_map(base+'/Maps/Map_GolemPlayerBody');E=u.get_editor_subsystem(u.EditorActorSubsystem)
pair=sorted([a for a in E.get_all_level_actors() if a.get_actor_label() in ['Golem - Original Player Body','Golem - Original Female Player Body']],key=lambda a:a.get_actor_label());center=(pair[0].get_actor_location()+pair[1].get_actor_location())*.5
for i,a in enumerate(pair):a.set_actor_location(center+u.Vector(0,(i*2-1)*95,0),False,False)
for a in E.get_all_level_actors():
 if isinstance(a,u.RectLight):a.get_component_by_class(u.RectLightComponent).set_visibility(False)
light=E.spawn_actor_from_class(u.PointLight,center+u.Vector(300,0,250),u.Rotator());c=light.get_component_by_class(u.PointLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(500);c.set_attenuation_radius(2000);c.set_editor_property('cast_shadows',False)
out='C:/Users/RY0M/Documents/Codex/2026-11-03/referenced-chatgpt-conversation-this-is-an/outputs'
for sign in [1,-1]:
 eye=center+u.Vector(sign*520,50,135);rot=u.MathLibrary.find_look_at_rotation(eye,center+u.Vector(0,0,95));light.set_actor_location(center+u.Vector(sign*300,0,250),False,False);a=E.spawn_actor_from_class(u.SceneCapture2D,eye,rot);cap=a.get_component_by_class(u.SceneCaptureComponent2D);rt=u.RenderingLibrary.create_render_target2d(world,1600,1100,u.TextureRenderTargetFormat.RTF_RGBA8);cap.set_editor_property('texture_target',rt);cap.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR);cap.set_editor_property('capture_every_frame',False);cap.set_editor_property('fov_angle',40.);cap.capture_scene();u.RenderingLibrary.export_render_target(world,rt,out,'Elrhun_Native_Facing_'+str(sign)+'.png');E.destroy_actor(a)
