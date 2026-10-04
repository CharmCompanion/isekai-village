"""Tools > Execute Python Script: show/hide saved editor-only construction overlay."""
import unreal
e=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=[a for a in e.get_all_level_actors() if str(a.get_folder_path())=='BuildGrid/Debug']
assert actors,'Open Map_AnimeAdventure first.'
show=not any(a.static_mesh_component.is_visible() for a in actors)
for a in actors:
    a.static_mesh_component.set_visibility(show)
    a.set_actor_hidden_in_game(not show)
    a.set_is_temporarily_hidden_in_editor(False)
unreal.log('Construction grid '+('ON: green = open, amber = reserved, red = protected' if show else 'OFF'))
