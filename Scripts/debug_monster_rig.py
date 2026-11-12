import bpy,json
from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v01')
bpy.ops.wm.open_mainfile(filepath=str(p/'GoblinFighter.blend'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
obj=bpy.data.objects.get('SK_GoblinFighter')
r={'rig':arm.name,'matrix':[[v for v in row] for row in arm.matrix_world],'bones':[{'name':n,'local':list(arm.data.bones[n].head_local),'world':list(arm.matrix_world@arm.data.bones[n].head_local)} for n in ['pelvis','head','upperarm_l','hand_l','foot_l']], 'matrices':[[v for v in row] for row in obj.matrix_world], 'slots':[m.name for m in obj.data.materials]}
by={}
for poly in obj.data.polygons:
    name=obj.data.materials[poly.material_index].name
    for i in poly.vertices:by.setdefault(name,[]).append(obj.data.vertices[i].co.z)
r['ranges']={k:[min(v),max(v)] for k,v in by.items()}
(p/'rig_debug.json').write_text(json.dumps(r,indent=2))
