import bpy,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v05')
manifest=json.loads((root/'model_manifest.json').read_text())
for model in manifest['models']:
    if model['family']=='Skeleton':continue
    name=model['id'];bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
    mesh=bpy.data.objects['SK_'+name]
    for mat in mesh.data.materials:
        if not mat.name.endswith('Skin'):continue
        for node in mat.node_tree.nodes:
            if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.22 if 'HeadSkin' in mat.name else .48
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/(name+'.blend')))
print('SKIN_RESPONSE_SYNC_COMPLETE')
