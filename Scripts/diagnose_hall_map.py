from pathlib import Path
import json,unreal as u
e=u.get_editor_subsystem(u.EditorActorSubsystem)
v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime))
rows=[{'id':str(p.id),'built':p.built,'scenery':p.scenery,'kind':str(p.kind),'beds':p.bed_bonus} for p in v.authored_plots]
Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Saved/hall_map_diagnostic.json').write_text(json.dumps(rows,indent=2))
u.EditorPythonScripting.set_keep_python_script_alive(False)
