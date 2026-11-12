import bpy,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/PlayerReference')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for file in ['SKM_BodyA.fbx','SKM_HeadA_01.fbx']:
    bpy.ops.import_scene.fbx(filepath=str(root/file))
rows=[]
for o in bpy.data.objects:
    r={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale)}
    if o.type=='MESH':
        vv=[o.matrix_world@v.co for v in o.data.vertices]
        r.update(vertices=len(vv),bounds=[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]],groups=[g.name for g in o.vertex_groups],materials=[m.name for m in o.data.materials])
    if o.type=='ARMATURE':r['bones']=[{'name':b.name,'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones]
    rows.append(r)
(root/'blender_inspection.json').write_text(json.dumps(rows,indent=2))
print('REFERENCE_INSPECTION_COMPLETE')
