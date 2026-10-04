import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource/T_IV_WorldSurface30.png');t.destination_path=R+'/Textures';t.automated=True;t.replace_existing=True;t.save=True;T.import_asset_tasks([t]);tex=unreal.load_asset(R+'/Textures/T_IV_WorldSurface30')
tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(tex)
