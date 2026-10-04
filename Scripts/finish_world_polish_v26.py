import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
exec(compile((B/'Scripts/polish_clouds_v26.py').read_text(),'cloud polish','exec'),{'__name__':'__main__'})
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();matches=[]
for a in actors:
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_PuzzleContinent_v26' and a.static_mesh_component.is_visible():
  matches.append({'label':a.get_actor_label(),'material':a.static_mesh_component.get_material(0).get_name()})
assert len(matches)==1 and matches[0]['material']=='M_IV_LivingContinent_Final26',matches
assert any('ElRuhnNeutralCountry' in [str(t) for t in a.tags] for a in actors)
(B/'Saved/world_polish_v26_native_check.json').write_text(json.dumps({'visible_mainland':matches,'el_ruhn_tag':True,'map_saved':True},indent=2))
exec(compile((B/'Scripts/render_puzzle_continent_v26.py').read_text(),'final polish views','exec'),{'__name__':'__main__'})
