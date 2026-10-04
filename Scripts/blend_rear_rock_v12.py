import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape');nodes=M.get_material_expressions(mat)
for n in nodes:
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  if 'farmSoil' in code:
   code=code.replace('c=lerp(c,stone,Mask.b);','c=lerp(c,stone,max(Mask.b,Mask.a));')
   code=code.replace('c=lerp(c,float3(.73,.82,.86)*(0.94+0.06*macro),Mask.a);','c=lerp(c,float3(.73,.82,.86)*(0.94+0.06*macro),Mask.a*smoothstep(23500.,28500.,P.z)*smoothstep(.62,.90,N.z));')
   code=code.replace('stone*=lerp(float3(.40,.47,.46),float3(.58,.62,.64),saturate(P.z/26000.0))*strata;','stone*=float3(.54,.59,.60)*(.94+.06*sin(P.x/17000.+P.y/19000.));')
   n.set_editor_property('code',code)
pos=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionWorldPosition))
rocks=[n for n in nodes if isinstance(n,unreal.MaterialExpressionTextureSample) and n.get_editor_property('texture') and 'T_RockClassic_Rocks_BC' in n.get_editor_property('texture').get_name()]
assert len(rocks)==3
for plane,sample in zip(['xy','xz','yz'],rocks):
 pin=unreal.CustomInput();pin.set_editor_property('input_name','P');uv=M.create_material_expression(mat,unreal.MaterialExpressionCustom);uv.set_editor_property('code','return P.'+plane+'/9500.;');uv.set_editor_property('inputs',[pin]);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);M.connect_material_expressions(pos,'',uv,'P');M.connect_material_expressions(uv,'',sample,'UVs')
M.recompile_material(mat);A.save_loaded_asset(mat)
for kind in ['Grass','Flowers']:
 ft=unreal.load_asset(R+'/Foliage/FT_R12_Rim'+kind);ft.set_editor_property('cast_shadow',False);A.save_loaded_asset(ft)
exec(compile((B/'Scripts/apply_rim_ecology_v12.py').read_text(),'rim ecology','exec'),{'__name__':'__main__'})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/rear_rock_blend_result.json').write_text(json.dumps({'saved':True,'terrain_heights_unchanged':True,'snow_limited_to_high_upward_facing_caps':True,'shared_rock_texture_scale_m':95},indent=2))
exec(compile((B/'Scripts/render_orbit_after.py').read_text(),'final review','exec'),{'__name__':'__main__'})
