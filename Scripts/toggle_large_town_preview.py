"""Execute in Unreal to inspect future defenses; run again to return to Village."""
import unreal
actors=[a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if 'IVFutureLargeTown' in [str(t) for t in a.tags]]
assert actors,'Open the AdventureWorld map first.'
show=not any(a.static_mesh_component.is_visible() for a in actors)
for a in actors:
    a.static_mesh_component.set_visibility(show);a.set_actor_hidden_in_game(not show)
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if show else unreal.CollisionEnabled.NO_COLLISION)
unreal.log('Large Town defense preview '+('ON' if show else 'OFF'))
