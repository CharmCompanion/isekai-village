import unreal, json, traceback
from pathlib import Path
out = {'maps':{}, 'assets':[], 'api':{}}
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lev = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
try:
    for name in ['Landscape','InstancedFoliageActor','FoliageType_InstancedStaticMesh','EditorLevelLibrary']:
        cls=getattr(unreal,name)
        out['api'][name]=[x for x in dir(cls) if any(k in x for k in ['import','instance','component','level','layer'])]
    for path in ['/Game/IsekaiVillage/Maps/Map_Village','/Game/IsekaiVillage/Maps/Map_Overworld','/Game/SpellCraft/Maps/Height_DemoCopy']:
        lev.load_level(path)
        actors=[]
        for a in sub.get_all_level_actors():
            item={'name':a.get_actor_label(),'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'scale':str(a.get_actor_scale3d())}
            if isinstance(a,unreal.LandscapeProxy):
                item['bounds']=str(a.get_actor_bounds(False))
                for p in ['component_size_quads','subsection_size_quads','num_subsections','landscape_material','landscape_section_offset','landscape_components']:
                    try:item[p]=str(a.get_editor_property(p))
                    except:pass
            actors.append(item)
        out['maps'][path]=actors
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    for root in ['/Game/AdvancedVillagePack','/Game/Fantastic_Village_Pack','/Game/StylizedIsland','/Game/SoStylized','/Game/StylizedBarrierShader','/Game/AdvancedPortalsSystemVFX']:
        for data in reg.get_assets_by_path(root,recursive=True):
            path=str(data.package_name); typ=str(data.asset_class_path.asset_name)
            if typ in ['StaticMesh','Blueprint','Texture2D','MaterialInstanceConstant']:
                out['assets'].append({'path':path,'type':typ})
    out['api']['add_instances_doc']=unreal.InstancedFoliageActor.add_instances.__doc__
    out['samples']=[]
    wanted=['SM_OakTree1','SM_Pine01','SM_Bush1','SM_Grass1','SM_Stylized_Fountain','SM_Dock_Straight','SM_CliffClassic1','SM_PROP_bench_01','SM_PROP_streetlamp_v01_01']
    for item in out['assets']:
        if item['type']=='StaticMesh' and item['path'].rsplit('/',1)[-1] in wanted:
            asset=unreal.load_asset(item['path'])
            out['samples'].append({'path':item['path'],'bounds':str(asset.get_bounding_box())})
    out['status']='complete'
except:out['error']=traceback.format_exc()
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/adventure_audit.json').write_text(json.dumps(out,indent=2))
unreal.log('Adventure world audit complete; editor left open.')
