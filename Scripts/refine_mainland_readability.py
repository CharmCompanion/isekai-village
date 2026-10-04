import unreal,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
mat=unreal.load_asset(R+'/Materials/M_IV_DistantMainland');n=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in E.get_all_level_actors():
 if isinstance(a,unreal.ExponentialHeightFog):a.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_max_opacity',.22)
 if a.get_actor_label()=='SoStylized illustrated cloud horizon':a.static_mesh_component.set_visibility(True,True);a.set_actor_hidden_in_game(False)
raw=struct.unpack('<'+'H'*1009**2,(B/'Saved/AdventureWorldSource/IV_Refined_v08.r16').read_bytes())
for a in E.get_all_level_actors():
 if a.get_actor_label()!='Upheaved cliff strata':continue
 o,e=a.get_actor_bounds(False);x=o.x/100;y=o.y/100
 radial=(abs(x/580)**4+abs((y-20)/570)**4)**.25
 if radial>.945:
  i=max(0,min(1008,round((x+600)*.84)));j=max(0,min(1008,round((y+600)*.84)));z=(raw[j*1009+i]-32768)/64
  p=a.get_actor_location();a.set_actor_location(unreal.Vector(p.x,p.y,p.z+(z*100-160-e.z-o.z)),False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
eye=unreal.Vector(200000,-1200000,-350000);target=unreal.Vector(0,0,-650000);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target));unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(B/'Saved/continent_diagnostic.png'),delay=3.)
