import unreal,json
from pathlib import Path
out={}
for name in ['get_used_foliage_types','get_instance_transforms','get_foliage_types','get_instances_for_component','add_instances','remove_all_instances']:
    try:out[name]=str(getattr(unreal.InstancedFoliageActor,name).__doc__)
    except Exception as e:out[name]=str(e)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain40/foliage_api.json').write_text(json.dumps(out,indent=2))
