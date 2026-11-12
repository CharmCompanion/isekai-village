"""Save the reviewed camera and record the completed native checkpoint."""
import unreal,json,hashlib,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');D=B/'Docs/WorldDesign/Gosain37'
validation=json.loads((B/'Saved/Gosain37/native_validation.json').read_text())
assert not validation['unexpected_actor_changes'] and validation['outside_foliage_equal']
shots=json.loads((D/'after_renders.json').read_text())
assert len(shots)==7 and all(Path(p).is_file() and not p.startswith('FAILED') for p in shots)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
path=B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap'
report={'status':'saved_and_reviewed_capital_layout_checkpoint','not_final_empire':True,
        'map':str(path),'map_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'saved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'existing_actors_checked':validation['checked_existing_actors'],
        'unexpected_actor_changes':0,'outside_foliage_equal':True,
        'screenshots':shots,'next':'Gosain capital coastal defenses and road/bridge connections; preserve El Ruhn.'}
(D/'checkpoint_result.json').write_text(json.dumps(report,indent=2))
unreal.log('GOSAIN37_CHECKPOINT_SAVED')
