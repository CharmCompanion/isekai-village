import unreal as u,json,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
mesh=u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem')
report={'mesh_materials':[str(m.material_interface) for m in mesh.get_editor_property('materials')]}
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  c=a.get_editor_property('skeletal_mesh_component')
  report[a.get_actor_label()]=[str(c.get_material(i)) for i in range(4)]
for name in ('M_ClayBody','M_SoulGem'):
 mat=u.load_asset('/Game/Elrhun/Golems/Materials/'+name)
 u.MaterialEditingLibrary.set_material_usage(mat,u.MaterialUsage.MATUSAGE_SKELETAL_MESH)
 u.MaterialEditingLibrary.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat)
(root/'Saved/golem_actual_materials.json').write_text(json.dumps(report,indent=2))
