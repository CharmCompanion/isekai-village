import unreal,json
from pathlib import Path
root='/Game/IsekaiVillage/AdventureWorld'
mat=unreal.load_asset(root+'/Materials/M_IV_Landscape')
m=unreal.MaterialEditingLibrary
for n in m.get_material_expressions(mat):
    if isinstance(n,unreal.MaterialExpressionCustom) and 'float macro=' in n.get_editor_property('code') and 'farmSoil' not in n.get_editor_property('code'):
        code=n.get_editor_property('code')
        # Only cultivated beds receive rich soil color; access lanes stay pale.
        rects=[]
        for x,y in [(110,-145),(146,-145),(110,-181),(146,-181)]:
            rects.append(f'(1-smoothstep(11.3,12.0,abs(P.x/100.0-{x})))*(1-smoothstep(12.3,13.0,abs(P.y/100.0-({y}))))')
        soil='float farmSoil=saturate('+ '+'.join(rects)+'); c=lerp(c,c*float3(0.40,0.25,0.13),farmSoil); '
        n.set_editor_property('code',code.replace('return lerp(c,float3(0.73',soil+'return lerp(c,float3(0.73'))
m.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
tex=unreal.load_asset(root+'/Textures/T_IV_Biome');tex.set_editor_property('filter',unreal.TextureFilter.TF_BILINEAR);unreal.EditorAssetLibrary.save_loaded_asset(tex)
out={}
for path in ['/Game/StylizedIsland/Mesh/Foliage/SM_Wheat','/Game/SoStylized/Environment/Water/Waterfalls/SM_Waterfall1']:
    asset=unreal.load_asset(path);out[path]=str(asset.get_bounding_box()) if asset else None
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/farm_visual_assets.json').write_text(json.dumps(out,indent=2))
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if str(a.get_folder_path())=='BuildGrid/Debug':a.static_mesh_component.set_visibility(True)
eye=unreal.Vector(41000,-42000,56000);target=unreal.Vector(4000,4000,3000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
