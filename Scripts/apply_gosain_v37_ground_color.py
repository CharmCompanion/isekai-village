"""Refine only Gosain's private regional meadow color after native visual review."""
import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain37/Materials/M_Gosain37_RegionalTerrain')
changed=[]
for n in M.get_material_expressions(mat):
    if not isinstance(n,unreal.MaterialExpressionCustom):continue
    code=n.get_editor_property('code')
    if 'float3 meadow=' in code:
        n.set_editor_property('code', '''float3 q=P/100.;
float macro=saturate(.5+.26*sin(q.x/123.+sin(q.y/183.))+.22*cos(q.y/91.+q.x/267.));
float3 meadow=lerp(float3(.012,.043,.013),float3(.044,.105,.024),macro);
float lum=clamp(dot(G,float3(.3,.5,.2))*4.2,.45,1.35);
meadow*=lum;
float worn=.06+.08*(1.-macro);
meadow=lerp(meadow,D*.16,worn);
float slope=1.-smoothstep(.66,.95,abs(N.z));
float3 stone=R*float3(.40,.46,.49);
return lerp(meadow,stone,slope);''')
        changed.append(n.get_name())
assert len(changed)==1,changed
M.recompile_material(mat)
assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/Gosain37/ground_color_result.json').write_text(json.dumps({'stage':'saved','changed':changed}))
