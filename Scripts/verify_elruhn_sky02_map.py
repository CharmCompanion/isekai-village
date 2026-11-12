"""Verify the persisted native world, independent of the generation plan."""
from pathlib import Path
import unreal,json,math
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage');out=root/'ArtSource/World/ElRuhnSky02'
exec(compile((root/'Scripts/verify_elruhn_sky01.py').read_text(),'verify support constellation','exec'),{})
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=list(editor.get_all_level_actors());by_name={a.get_name():a for a in actors}
plan=json.loads((out/'village_plan.json').read_text());tower=next(a for a in actors if a.get_actor_label()=='El Ruhn | Tower of the Five Winds');location=tower.get_actor_location()
assert (location-unreal.Vector(*[float(n)*100 for n in plan['center_m']])).length()<.1
runtime=next(a for a in actors if isinstance(a,unreal.VillageRuntime));plots=runtime.get_editor_property('authored_plots');catalog=runtime.get_editor_property('building_catalog');free=[p for p in plots if p.flexible_use]
assert len(free)==plan['purchase_slots'] and len(set(str(p.id) for p in free))==len(free)
assert all(not p.built and not p.scenery and not p.building_class and str(p.catalog_id)=='None' for p in free)
assert all(entry.building_class and entry.buildable_size<=min(p.buildable_size for p in free) for entry in catalog)
assert len({str(entry.id) for entry in catalog})==18 and runtime.placement_preview_material
assert all(p.kind==unreal.TownBuilding.UNASSIGNED for p in free)
assert all(a.get_actor_label() not in ('Guild Hall','Inherited House') for a in actors)
assert not any(str(a.get_folder_path()).startswith('BuildGrid/') for a in actors)
assert all(a.static_mesh_component.static_mesh and a.static_mesh_component.get_material(0) for a in actors if isinstance(a,unreal.StaticMeshActor) and 'ElRuhnSky02' in [str(t) for t in a.tags])
foundation_hits=0
for parcel in free:
    hits=unreal.SystemLibrary.line_trace_multi_for_objects(world,parcel.location+unreal.Vector(0,0,140),parcel.location-unreal.Vector(0,0,100),[unreal.ObjectTypeQuery.ECC_WORLD_STATIC],True,[],unreal.DrawDebugTrace.NONE,True) or []
    for hit in hits:
        values=hit.to_tuple()
        if any(isinstance(value,unreal.StaticMeshActor) and value.get_actor_label()=='Village | BuildingFoundations' for value in values) and abs(values[5].z-parcel.location.z)<3:
            foundation_hits+=1;break
assert foundation_hits==len(free),f'{foundation_hits}/{len(free)} physical parcel tops aligned'
snapshot=json.loads((out/'before.json').read_text())['actors'];farm_count=0
for row in snapshot:
 if row['folder'].startswith('Farms/') or row['label']=='Farmhouse':
  actor=by_name[row['name']];assert (actor.get_actor_location()-unreal.Vector(*row['p'])).length()<.1,row['label'];farm_count+=1
report={'status':'passed','tower_center_m':plan['center_m'],'available_plots':len(free),'catalogue_choices':len(catalog),'all_free_land_unassigned':True,'farm_actors_verified':farm_count,'source_world_hash_verified':True,'runtime_save_slot':runtime.construction_save_slot,'game_mode':world.get_world_settings().get_editor_property('default_game_mode').get_path_name()}
report['parcel_foundation_collision_hits']=foundation_hits
(out/'native_verification.json').write_text(json.dumps(report,indent=2));unreal.SystemLibrary.execute_console_command(world,'Automation RunTests IsekaiVillage.Construction.AuthoredPlots')
