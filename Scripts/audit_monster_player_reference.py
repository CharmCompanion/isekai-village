"""Read-only player appearance audit; exports reference copies into Saved."""
import unreal, json, traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/MonsterArtReference')
root.mkdir(parents=True,exist_ok=True)
result={'maps':{},'classes':{},'errors':[]}
paths=['/Game/IsekaiVillage/Input/BP_OverworldCharacter','/Game/IsekaiVillage/Input/BP_ThirdPersonCharacter','/Game/SpellCraft/Blueprints/Character/BP_MageCharacter']
for path in paths:
    try:
        cls=unreal.EditorAssetLibrary.load_blueprint_class(path)
        if not cls: continue
        cdo=unreal.get_default_object(cls)
        rows=[]
        for comp in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
            mesh=comp.get_editor_property('skeletal_mesh_asset')
            rows.append({'component':comp.get_name(),'mesh':mesh.get_path_name() if mesh else None,'materials':[m.get_path_name() if m else None for m in comp.get_materials()]})
        result['classes'][path]=rows
    except Exception as e:result['errors'].append(path+': '+str(e))
for path in ['/Game/IsekaiVillage/Maps/Map_Village','/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure']:
    try:
        world=unreal.EditorLoadingAndSavingUtils.load_map(path)
        settings=world.get_world_settings()
        mode=settings.get_editor_property('default_game_mode')
        pawn=unreal.get_default_object(mode).get_editor_property('default_pawn_class') if mode else None
        actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        result['maps'][path]={'game_mode':mode.get_path_name() if mode else None,'default_pawn':pawn.get_path_name() if pawn else None,'characters':[]}
        for actor in actors:
            if isinstance(actor,unreal.Character):
                result['maps'][path]['characters'].append({'label':actor.get_actor_label(),'class':actor.get_class().get_path_name(),'meshes':[{'component':c.get_name(),'mesh':c.get_editor_property('skeletal_mesh_asset').get_path_name() if c.get_editor_property('skeletal_mesh_asset') else None} for c in actor.get_components_by_class(unreal.SkeletalMeshComponent)]})
    except Exception as e:result['errors'].append(path+': '+str(e))
(root/'player_audit.json').write_text(json.dumps(result,indent=2))
# Keep this audit metadata-only. Skeletal FBX export with -nullrhi triggered
# an engine MeshObject assertion; export references in a rendering editor.
unreal.log('MONSTER_PLAYER_AUDIT_COMPLETE '+str(root))
