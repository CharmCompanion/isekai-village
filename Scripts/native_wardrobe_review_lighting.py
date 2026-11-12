# Called with the wardrobe review world, center and actor_sys already available.
assert world.get_name()=='Map_GolemPlayerBody'
for label,offset,power in [('Native wardrobe key',u.Vector(-220,350,300),250),('Native wardrobe fill',u.Vector(260,180,220),170)]:
 light=next((a for a in actor_sys.get_all_level_actors() if a.get_actor_label()==label),None)
 pos=center+offset;rot=u.MathLibrary.find_look_at_rotation(pos,center+u.Vector(0,0,100))
 if not light:light=actor_sys.spawn_actor_from_class(u.RectLight,pos,rot)
 light.set_actor_label(label);light.set_actor_location(pos,False,False);light.set_actor_rotation(rot,False)
 c=light.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(power);c.set_editor_property('attenuation_radius',1800);c.set_editor_property('source_width',300);c.set_editor_property('source_height',300)
pp=next((a for a in actor_sys.get_all_level_actors() if a.get_actor_label()=='Native wardrobe exposure'),None)
if not pp:pp=actor_sys.spawn_actor_from_class(u.PostProcessVolume,center,u.Rotator())
pp.set_actor_label('Native wardrobe exposure');pp.set_editor_property('unbound',True);pp.set_editor_property('priority',10.)
settings=pp.get_editor_property('settings')
for key,value in {'override_auto_exposure_method':True,'auto_exposure_method':u.AutoExposureMethod.AEM_MANUAL,'override_auto_exposure_apply_physical_camera_exposure':True,'auto_exposure_apply_physical_camera_exposure':False,'override_auto_exposure_bias':True,'auto_exposure_bias':-.5}.items():settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings)
u.EditorLoadingAndSavingUtils.save_map(world,base+'/Maps/Map_GolemPlayerBody')
