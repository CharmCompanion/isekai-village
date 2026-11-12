import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for k in json.loads((O/'merged_house_assets.json').read_text()):
    if k['name'] not in ['1','2','6','9','10']:continue
    m=unreal.load_asset(k['path']);n=m.get_editor_property('nanite_settings');n.enabled=True;SS.set_nanite_settings(m,n,True);unreal.EditorAssetLibrary.save_loaded_asset(m)
(O/'nanite_enabled.json').write_text(json.dumps({'enabled':['1','2','6','9','10'],'performance_benchmarked':False}))
