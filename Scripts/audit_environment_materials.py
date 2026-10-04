import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;out={}
for p in ['/Game/SoStylized/Environment/Water/Materials/MI_Ocean','/Game/SoStylized/Environment/Water/Materials/MI_WaterWaves','/Game/IsekaiVillage/AdventureWorld/Materials/M_IV_Landscape']:
    a=unreal.load_asset(p);data={}
    if isinstance(a,unreal.MaterialInstanceConstant):
        data['scalars']={str(n):M.get_material_instance_scalar_parameter_value(a,n) for n in M.get_scalar_parameter_names(a)}
        data['vectors']={str(n):str(M.get_material_instance_vector_parameter_value(a,n)) for n in M.get_vector_parameter_names(a)}
    else:
        data['custom']=[{'code':n.get_editor_property('code'),'inputs':[str(i.get_editor_property('input_name')) for i in n.get_editor_property('inputs')]} for n in M.get_material_expressions(a) if isinstance(n,unreal.MaterialExpressionCustom)]
    out[p]=data
out['collision_api']=[x for x in dir(unreal.StaticMeshEditorSubsystem) if 'collision' in x.lower()]
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/environment_material_audit.json').write_text(json.dumps(out,indent=2))
