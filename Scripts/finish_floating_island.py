import unreal,math,random,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
# UE 5.8's internal visibility target name is not the UI label "Visibility".
assert '__LANDSCAPE_VISIBILITY__' in [str(k) for k in land.get_editor_property('target_layers')]
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(unreal.load_asset(R+'/Textures/T_IV_FloatingVisibility'),unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
ok=land.landscape_import_weightmap_from_render_target(rt,'__LANDSCAPE_VISIBILITY__',0);assert ok
mask=next(n for n in M.get_material_expressions(mat) if isinstance(n,unreal.MaterialExpressionLandscapeVisibilityMask));M.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK);M.recompile_material(mat);A.save_loaded_asset(mat);land.force_layers_full_update()
mesh=unreal.load_asset('/Game/StylizedSkymap/meshes/sky/SM_cloud');rng=random.Random(277)
for i in range(48):
 t=i*2*math.pi/48;radius=rng.uniform(750,1650);z=rng.uniform(-570,-240)
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(math.cos(t)*radius*100,math.sin(t)*radius*100,z*100),unreal.Rotator(yaw=rng.uniform(0,360)));a.static_mesh_component.set_static_mesh(mesh)
 s=rng.uniform(22,48);a.set_actor_scale3d(unreal.Vector(s,s*.8,s*.55));a.set_actor_label('Cloud sea - drifting cumulus');a.set_folder_path('Floating Island/Cloud Sea');a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);a.set_editor_property('tags',[unreal.Name('IVFloatingClouds')])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
p=B/'Saved/floating_island_result.json';d=json.loads(p.read_text());d.update(native_visibility_collision_holes=True,cloud_clusters=48);p.write_text(json.dumps(d,indent=2))
