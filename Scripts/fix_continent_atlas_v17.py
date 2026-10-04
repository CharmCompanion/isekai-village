import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
t=unreal.load_asset(R+'/Textures/T_IV_LivingContinent_v17')
report={}
for k in ['srgb','compression_settings','virtual_texture_streaming','mip_gen_settings','never_stream','lod_bias']:
 try:report[k]=str(t.get_editor_property(k))
 except Exception as e:report[k]=str(e)
t.set_editor_property('virtual_texture_streaming',False);t.set_editor_property('never_stream',True);t.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);A.save_loaded_asset(t)
m=unreal.load_asset(R+'/Materials/M_IV_LivingContinent_v17');M.recompile_material(m);A.save_loaded_asset(m)
(B/'Saved/continent_atlas_diagnostic.json').write_text(json.dumps(report,indent=2))
exec(compile((B/'Scripts/render_living_continent_v17.py').read_text(),'render fixed atlas','exec'),{'__name__':'__main__'})
