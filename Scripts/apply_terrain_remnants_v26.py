import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in E.get_all_level_actors():
 tags=[str(t) for t in a.tags]
 if 'IVRemnant22' in tags or 'IVRemnant23' in tags:E.destroy_actor(a);continue
 if isinstance(a,unreal.Landscape):
  a.set_actor_label('El Ruhn - neutral floating kingdom - playable terrain')
  if 'ElRuhnNeutralCountry' not in tags:a.tags=list(a.tags)+[unreal.Name('ElRuhnNeutralCountry')]
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
  name=a.static_mesh_component.static_mesh.get_name()
  if name=='SM_IV_JoinedMountain_v21':a.set_actor_label('El Ruhn - matching rock foundation')
  if name=='SM_IV_PuzzleContinent_v26':a.set_actor_label('World beneath El Ruhn - mapped biomes and neighboring countries')
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
  m=a.static_mesh_component.static_mesh
  if m.get_name()=='SM_StylizedSkyDome_Clouds' and a.static_mesh_component.is_visible():
   bb=m.get_bounding_box();sc=60000000./max(1.,bb.max.x-bb.min.x);a.set_actor_scale3d(unreal.Vector(sc,sc,sc))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Docs/WorldDesign/El_Ruhn_World.json').write_text((B/'Saved/AdventureWorldSource/world_design_v26.json').read_text())
