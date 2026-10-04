import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource/T_IV_ContinentAtlas17.png');t.destination_path=R+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
tex=unreal.load_asset(R+'/Textures/T_IV_ContinentAtlas17')
for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('never_stream',True),('virtual_texture_streaming',False),('address_x',unreal.TextureAddress.TA_CLAMP),('address_y',unreal.TextureAddress.TA_CLAMP)]:tex.set_editor_property(k,v)
A.save_loaded_asset(tex)
mat=unreal.load_asset(R+'/Materials/M_IV_LivingContinent_v17')
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionTextureSample):n.set_editor_property('texture',tex)
M.recompile_material(mat);A.save_loaded_asset(mat)
exec(compile((B/'Scripts/render_living_continent_v17.py').read_text(),'atlas review','exec'),{'__name__':'__main__'})
