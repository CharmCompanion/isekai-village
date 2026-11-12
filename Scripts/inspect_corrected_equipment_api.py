import unreal as u,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
S=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem);static=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
mesh=u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem')
report={'cloth_tools':dir(u.GolemClothTools),'actor':dir(u.GolemEquipmentActor),'skel_api':[x for x in dir(S) if any(v in x for v in ['section','physics','cloth'])],'static_api':[x for x in dir(static) if 'collision' in x],'clothing':json.loads(u.GolemClothTools.inspect_clothing(mesh)),'physics_doc':S.create_physics_asset.__doc__,'static_collision_enum':str(dir(u.ScriptCollisionShapeType))}
(root/'Saved/corrected_equipment_api.json').write_text(json.dumps(report,indent=2))
