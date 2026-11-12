import bpy,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v05')
manifest=json.loads((root/'model_manifest.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for model in manifest['models']:
    name=model['id'];family=model['family']
    with bpy.data.libraries.load(str(root/(name+'.blend')),link=False) as (src,dst):dst.objects=['SK_'+name]
    mesh=dst.objects[0];bpy.context.collection.objects.link(mesh);mesh.parent=None
    for m in list(mesh.modifiers):mesh.modifiers.remove(m)
    mesh.hide_set(False);mesh.hide_render=False
    ids=[r['id'] for r in manifest['models'] if r['family']==family];i=ids.index(name)
    mesh.location=({'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]*(i-(len(ids)-1)/2),{'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/'IV_Monster_Library_v05.blend'))
print('AUTHORED_GALLERY_COMPLETE')
