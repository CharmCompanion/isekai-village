from pathlib import Path
P=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts');p=P/'final_continent_material_v30.py';s=p.read_text();s=s.replace("camera=M.create_material_expression", """agriculture=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample)
agriculture.set_editor_property('texture',unreal.load_asset(R+'/Textures/T_IV_Agriculture30'))
agriculture.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
M.connect_material_expressions(faruv,'',agriculture,'UVs')
camera=M.create_material_expression""")
s=s.replace("float depth=saturate", """// Fields share the terrain surface; analytic boundaries keep the survey grid crisp.
float smallField=step(.5,Agriculture.r);
float2 cellSize=lerp(float2(400.,800.),float2(200.,400.),smallField);
float2 fieldCell=frac(p.xy/cellSize)*cellSize;
float2 edge=min(fieldCell-28.,cellSize-28.-fieldCell);
float farm=smoothstep(-2.,3.,min(edge.x,edge.y))*smoothstep(.15,.75,Agriculture.b);
int crop=(int)round(Agriculture.g*5.);
float3 cropColor=crop==0?float3(.17,.26,.075):crop==1?float3(.34,.29,.09):crop==2?float3(.12,.24,.065):crop==3?float3(.27,.33,.11):crop==4?float3(.23,.22,.08):float3(.38,.32,.115);
float rows=.94+.06*smoothstep(-.3,.5,sin(p.x*1.15));
float rowVisibility=1.-smoothstep(400.,1800.,distance(WorldPos,CameraPosition)/100.);
cropColor*=lerp(1.,rows,rowVisibility);
ground=lerp(ground,cropColor,farm);
float depth=saturate""")
s=s.replace("'WorldPos':(pos,''),'SurfaceNormal':", "'Agriculture':(agriculture,'RGB'),'CameraPosition':(camera,''),'WorldPos':(pos,''),'SurfaceNormal':")
p.write_text(s)
