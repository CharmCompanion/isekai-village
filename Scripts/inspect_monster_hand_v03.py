import bpy,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v03')
bpy.ops.wm.open_mainfile(filepath=str(root/'OgreChampion.blend'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rows=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local)} for b in arm.data.bones if any(w in b.name for w in ['hand_r','index','middle','ring','pinky','thumb'])]
(root/'hand_anatomy.json').write_text(json.dumps(rows,indent=2));print(json.dumps([r for r in rows if r['name'].endswith('_r')]))
