import unreal,json,math,random,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.IslandLandscapeAuthoring.apply_island_visibility(land,str(B/'Saved/AdventureWorldSource/IV_FloatingVisibility.raw'))
mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape');mask=next(n for n in M.get_material_expressions(mat) if isinstance(n,unreal.MaterialExpressionLandscapeVisibilityMask));M.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK);M.recompile_material(mat);A.save_loaded_asset(mat)
land.set_editor_property('landscape_material',mat);land.set_editor_property('landscape_hole_material',mat);land.force_layers_full_update()
# A fuller woodland canopy meets the mountain foothills; central plots stay open.
for name in ['FT_OakCanopy','FT_OakVariation','FT_MountainPine']:
 ft=unreal.load_asset(R+'/Foliage/'+name);kept=[]
 for a in E.get_all_level_actors():
  if not isinstance(a,unreal.InstancedFoliageActor):continue
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh!=ft.get_editor_property('mesh'):continue
   for i in range(c.get_instance_count()):
    tf=c.get_instance_transform(i,world_space=True);p=tf.translation
    if (p.y>16000 or p.x<-26000) and p.z<15500:tf.scale3d=tf.scale3d*1.6
    kept.append(tf)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/native_island_finished.json').write_text(json.dumps({'applied':True,'native_visibility':True,'forest_canopy_refined':True},indent=2))
