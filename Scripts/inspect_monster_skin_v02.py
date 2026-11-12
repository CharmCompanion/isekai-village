import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');out=B/'ArtSource/Monsters/PlayerReference'
rows={}
for family,path in [('Body','/Game/StylizedCharacters/BodyA/Body'),('Head','/Game/StylizedCharacters/BodyA/Heads/Head_01')]:
    mi=unreal.load_asset(path+'/Materials/MI_'+('BodyA_a' if family=='Body' else 'HeadA_01_a'))
    rows[family]={'vectors':{},'textures':{}}
    for n in unreal.MaterialEditingLibrary.get_vector_parameter_names(mi):
        c=unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(mi,n);rows[family]['vectors'][str(n)]=[c.r,c.g,c.b,c.a]
    for n in unreal.MaterialEditingLibrary.get_texture_parameter_names(mi):
        t=unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi,n);rows[family]['textures'][str(n)]=t.get_path_name() if t else None
    for suffix in ['Grayscale','N','M_R_AO']:
        name='T_'+('BodyA_01' if family=='Body' else 'HeadA_01')+'_'+suffix
        tex=unreal.load_asset(path+'/Textures/'+name)
        task=unreal.AssetExportTask();task.object=tex;task.filename=str(out/(name+'.png'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.TextureExporterPNG();unreal.Exporter.run_asset_export_task(task)
(out/'skin_parameters_v02.json').write_text(json.dumps(rows,indent=2))
