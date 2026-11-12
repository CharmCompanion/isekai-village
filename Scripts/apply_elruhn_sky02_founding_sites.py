"""Release the two fixed founding sites in the already assembled copy."""
from pathlib import Path
import json, math, unreal

root=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
out=root/'ArtSource/World/ElRuhnSky02'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
plan=json.loads((out/'village_plan.json').read_text())
baseline=json.loads((out/'before.json').read_text())['actors']
actors={actor.get_name():actor for actor in editor.get_all_level_actors()}
released={p['released_starter_actor'] for p in plan['plots'] if p.get('released_starter_actor')}
existing=[r for r in baseline if r['folder']=='Village/Buildings']
settled={p['existing_actor_label']:p for p in plan['plots'] if p['existing_actor_label']}
for row in baseline:
    actor=actors.get(row['name'])
    if not actor:
        continue
    if row['label'] in released or row['folder'].startswith('BuildGrid/'):
        editor.destroy_actor(actor)
    elif row['folder'] in ('Village/Props','Village/Lanterns'):
        x,y=row['p'][:2]
        if row['folder']=='Village/Lanterns' and math.hypot(x,y)<2500:
            continue
        nearest=min(existing,key=lambda b:math.hypot(b['p'][0]-x,b['p'][1]-y))
        if math.hypot(nearest['p'][0]-x,nearest['p'][1]-y)<2600:
            if nearest['label'] in released:
                editor.destroy_actor(actor)
            elif nearest['label'] in settled:
                pitch,yaw,roll=row['r']
                yaw+=settled[nearest['label']]['yaw_deg']-nearest['r'][1]
                actor.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll),False)

runtime=next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.VillageRuntime))
slots=list(runtime.authored_plots)
vacant={p['id'] for p in plan['plots'] if not p['existing_actor_label']}
for slot in slots:
    if str(slot.id) in vacant:
        slot.flexible_use=True;slot.built=False;slot.scenery=False
        slot.kind=unreal.TownBuilding.UNASSIGNED;slot.display_name='Unassigned land';slot.bed_bonus=0
runtime.set_editor_property('authored_plots',slots)
catalog=[entry for entry in runtime.building_catalog if str(entry.id)!='InheritedHouse']
cottage=next(entry for entry in catalog if str(entry.id)=='Cottage')
inherited=unreal.TownPlot()
for prop in ('kind','era','building_class','building_scale','building_offset','buildable_size','bed_bonus'):
    inherited.set_editor_property(prop,cottage.get_editor_property(prop))
inherited.id='InheritedHouse';inherited.display_name='Inherited home';inherited.wood_cost=0;inherited.unique_building=True
for entry in catalog:
    entry.unique_building=str(entry.id)=='Guild'
runtime.set_editor_property('building_catalog',[inherited]+catalog)
assert len(runtime.building_catalog)==18 and len(vacant)==28
assets='/Game/IsekaiVillage/AdventureWorld/ElRuhnSky02'
weights=unreal.load_asset(assets+'/Textures/T_ES02_VillageWeights')
weights.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
weights.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
weights.set_editor_property('filter',unreal.TextureFilter.TF_BILINEAR)
unreal.EditorAssetLibrary.save_loaded_asset(weights)
parent=unreal.load_asset(assets+'/Materials/M_ES02_Landscape')
unreal.MaterialEditingLibrary.recompile_material(parent)
unreal.EditorAssetLibrary.save_loaded_asset(parent)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report=json.loads((out/'assembled.json').read_text())
report.update(existing_buildings_relocated=8,unassigned_purchase_plots=28,founding_sites_player_selected=True)
catalog_report=[row for row in report['catalog'] if row['id']!='InheritedHouse']
deed=dict(next(row for row in catalog_report if row['id']=='Cottage'))
deed.update(id='InheritedHouse',name='Inherited home',cost=[0,0,0],unique=True)
for row in catalog_report:
    row['unique']=row['id']=='Guild'
report['catalog']=[deed]+catalog_report
(out/'assembled.json').write_text(json.dumps(report,indent=2))
