import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');m=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Meshes/Refinement/SM_IV_FractureBedrock_v10');ss=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);d={}
try:
 b=ss.get_lod_build_settings(m,0);d['before']=str(b);b.set_editor_property('recompute_normals',False);b.set_editor_property('recompute_tangents',True);ss.set_lod_build_settings(m,0,b);unreal.EditorAssetLibrary.save_loaded_asset(m);d['after']=str(ss.get_lod_build_settings(m,0))
except Exception as e:d['error']=str(e)
(B/'Saved/rockrim_normals.json').write_text(json.dumps(d,indent=2));exec(compile((B/'Scripts/render_rockrim_v10.py').read_text(),'rockrim_render','exec'),{'__name__':'__main__'})
