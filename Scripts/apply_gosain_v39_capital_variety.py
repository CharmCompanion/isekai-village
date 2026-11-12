import unreal,json,math,shutil,random
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/Gosain39'
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not (O/'capital_variety_applied.json').exists(),'Already applied'
backup=B/'Saved/WorldBackups/BeforeGosain39_20261015';backup.mkdir(exist_ok=True)
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
data=json.loads((B/'ArtSource/World/Gosain37/Gosain37.json').read_text());kits={k['name']:k for k in json.loads((O/'merged_house_assets.json').read_text())}
selected=['1','2','6','9','10'];groups={k:[] for k in selected};rng=random.Random(3915)
for oldkey in ['HouseA','HouseB']:
    for p in data['instances'][oldkey]:
        k=rng.choices(selected,weights=[3,2,2,2,2])[0];q=kits[k];lo=q['min'];hi=q['max'];fac=min(600/(hi[0]-lo[0]),580/(hi[1]-lo[1]))
        sc=[s*fac for s in p[3:6]];cx=(lo[0]+hi[0])/2*sc[0];cy=(lo[1]+hi[1])/2*sc[1];a=math.radians(p[6])
        pos=[p[0]*100-cx*math.cos(a)+cy*math.sin(a),p[1]*100-cx*math.sin(a)-cy*math.cos(a),p[2]*100-lo[2]*sc[2]]
        groups[k].append(unreal.Transform(location=unreal.Vector(*pos),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*sc)))
fts={};T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary
for k in selected:
    path=D+'/Foliage/FT_Gosain39_House_'+k
    ft=T.create_asset('FT_Gosain39_House_'+k,D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());assert ft
    ft.set_editor_property('mesh',unreal.load_asset(kits[k]['path']));ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));A.save_loaded_asset(ft);fts[k]=ft
for k in ['HouseA','HouseB']:
    ft=unreal.load_asset(R+'/Gosain37/Foliage/FT_Gosain37_'+k);assert ft
    unreal.InstancedFoliageActor.remove_all_instances(W,ft)
for k,rows in groups.items():unreal.InstancedFoliageActor.add_instances(W,fts[k],rows)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'capital_variety_applied.json').write_text(json.dumps({'status':'saved','counts':{k:len(v) for k,v in groups.items()},'total':sum(map(len,groups.values())),'scope':'Existing capital houses only; whole-island expansion remains pending','backup':str(backup)},indent=2))
