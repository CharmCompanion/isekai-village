"""Dress only the new AdventureWorld map. Original project maps/assets are untouched."""
import unreal, json, math, random, struct, traceback
from pathlib import Path

ROOT='/Game/IsekaiVillage/AdventureWorld'
MAP=ROOT+'/Maps/Map_AnimeAdventure'
SOURCE=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
REPORT=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/adventure_build.json')
DATA=json.loads((SOURCE/'world.json').read_text())
RAW=struct.unpack('<'+'H'*(1009*1009),(SOURCE/'IV_Adventure_1009.r16').read_bytes())
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.EditorAssetLibrary
M=unreal.MaterialEditingLibrary
T=unreal.AssetToolsHelpers.get_asset_tools()
R=random.Random(260926)
counts={};warnings=[]
def log(s):
    unreal.log('IV WORLD: '+str(s))
    REPORT.write_text(json.dumps({'stage':str(s),'counts':counts,'warnings':warnings},indent=2))
def h(x,y):
    u=max(0,min(1007.999,(x+600)/1200*1008));v=max(0,min(1007.999,(y+600)/1200*1008))
    i=int(u);j=int(v);a=u-i;b=v-j
    z=(RAW[j*1009+i]*(1-a)+RAW[j*1009+i+1]*a)*(1-b)+(RAW[(j+1)*1009+i]*(1-a)+RAW[(j+1)*1009+i+1]*a)*b
    return (z-32768)/64
def asset(path):
    a=unreal.load_asset(path)
    if not a:raise RuntimeError('Required asset missing: '+path)
    return a
def mark(a,name,folder):
    a.set_actor_label(name);a.set_folder_path(folder)
    a.set_editor_property('tags',[unreal.Name('IVAdventureGenerated')])
    counts[folder]=counts.get(folder,0)+1
    return a
def mesh(path,x,y,scale=1,yaw=0,z=None,name=None,folder='Nature/Rocks',ground=True):
    m=asset(path);s=scale if isinstance(scale,tuple) else (scale,scale,scale)
    base=h(x,y)*100 if z is None else z*100
    if ground:base-=m.get_bounding_box().min.z*s[2]
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,base),unreal.Rotator(yaw=yaw))
    a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*s))
    mark(a,name or m.get_name(),folder)
    return a
def bp(path,x,y,width,yaw,name,folder='Village/Buildings',z=None):
    cls=unreal.load_class(None,path+'.'+path.rsplit('/',1)[-1]+'_C')
    if not cls:raise RuntimeError('Missing Blueprint '+path)
    a=E.spawn_actor_from_class(cls,unreal.Vector(x*100,y*100,0),unreal.Rotator(yaw=yaw))
    o,e=a.get_actor_bounds(False)
    s=width*100/max(e.x*2,e.y*2,100)
    a.set_actor_scale3d(unreal.Vector(s,s,s));o,e=a.get_actor_bounds(False)
    base=h(x,y)*100 if z is None else z*100
    a.set_actor_location(unreal.Vector(x*100,y*100,base-(o.z-e.z)),False,False)
    mark(a,name,folder)
    return a
def texture(file):
    name=Path(file).stem;path=ROOT+'/Textures/'+name
    if not A.does_asset_exist(path):
        t=unreal.AssetImportTask();t.filename=str(SOURCE/file);t.destination_path=ROOT+'/Textures';t.destination_name=name;t.automated=True;t.save=True
        T.import_asset_tasks([t])
    tex=asset(path)
    tex.set_editor_property('srgb',False)
    tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
    tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP)
    A.save_loaded_asset(tex)
    return tex
def material():
    path=ROOT+'/Materials/M_IV_Landscape'
    if A.does_asset_exist(path):
        mat=asset(path);M.delete_all_material_expressions(mat)
    else:mat=T.create_asset('M_IV_Landscape',ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    def node(cls,**props):
        n=M.create_material_expression(mat,cls)
        for k,v in props.items():n.set_editor_property(k,v)
        return n
    def wire(a,out,b,inp):assert M.connect_material_expressions(a,out,b,inp)
    pos=node(unreal.MaterialExpressionWorldPosition)
    def custom(code,typ,inputs):
        pins=[]
        for k in inputs:
            pin=unreal.CustomInput();pin.set_editor_property('input_name',k);pins.append(pin)
        n=node(unreal.MaterialExpressionCustom,code=code,output_type=typ,inputs=pins)
        for k,(a,out) in inputs.items():wire(a,out,n,k)
        return n
    uv=custom('return P.xy / 550.0;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'P':(pos,'')})
    mapuv=custom('return (P.xy + 60000.0 + 59.52381) / 120119.04762;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'P':(pos,'')})
    def sample(tex,coord):
        n=node(unreal.MaterialExpressionTextureSample,texture=tex,sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        wire(coord,'',n,'UVs');return n
    mask=sample(texture('T_IV_Biome.png'),mapuv)
    mask.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    base='/Game/SoStylized/Environment/Landscape/Textures/'
    grass=sample(asset(base+'T_Grass1_BC'),uv)
    dirt=sample(asset(base+'T_Dirt1_BC'),uv)
    sand=sample(asset(base+'T_Sand_BC'),uv)
    rock=sample(asset('/Game/SoStylized/Environment/Rocks/Textures/Classic/T_RockClassic_Rocks_BC'),uv)
    color=custom('float macro=0.94+0.06*sin(P.x/2700.0)*sin(P.y/1900.0); float3 c=G*float3(0.82,1.02,0.74)*macro; c=lerp(c,D*float3(1.16,1.07,0.88),Mask.r); c=lerp(c,S,Mask.g); c=lerp(c,K*float3(0.87,0.94,1.02),Mask.b); return lerp(c,float3(0.73,0.82,0.86),Mask.a);',unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'G':(grass,'RGB'),'D':(dirt,'RGB'),'S':(sand,'RGB'),'K':(rock,'RGB'),'Mask':(mask,'RGBA'),'P':(pos,'')})
    M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=node(unreal.MaterialExpressionConstant,r=.86);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    M.recompile_material(mat);A.save_loaded_asset(mat)
    return mat
def pathdistance(x,y):
    best=1e9
    for r in DATA['routes']:
        for (ax,ay),(bx,by) in zip(r['points'],r['points'][1:]):
            vx=bx-ax;vy=by-ay;d=vx*vx+vy*vy
            t=max(0,min(1,((x-ax)*vx+(y-ay)*vy)/max(d,.001)))
            best=min(best,math.hypot(x-ax-t*vx,y-ay-t*vy)-r['width'])
    return best
def clear(x,y,margin=0):
    if math.hypot(x,y)<17+margin:return False
    for _,a,b,r,_,_ in DATA['buildings']:
        if math.hypot(x-a,y-b)<r+margin:return False
    return pathdistance(x,y)>margin
def foliage(meshpath,positions,name,cull=0,collision=False):
    path=ROOT+'/Foliage/FT_'+name
    if A.does_asset_exist(path):ft=asset(path)
    else:ft=T.create_asset('FT_'+name,ROOT+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',asset(meshpath))
    if cull:ft.set_editor_property('cull_distance',unreal.Int32Interval(min=cull-3000,max=cull))
    A.save_loaded_asset(ft)
    transforms=[unreal.Transform(location=unreal.Vector(x*100,y*100,h(x,y)*100-12),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)) for x,y,s,yaw in positions]
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    counts[name]=len(positions)

def main():
    global world
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert world.get_path_name().startswith(MAP+'.'), 'Open the new AdventureWorld map first.'
    landscapes=[a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape)]
    assert len(landscapes)==1,'Import the 1009 Landscape through Landscape mode first.'
    land=landscapes[0]
    # Refuse to stack another build on top of a completed world.
    assert not any('IVAdventureGenerated' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Generated set already exists; use a targeted refinement script.'
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    land.set_actor_scale3d(unreal.Vector(DATA['xy_scale'],DATA['xy_scale'],200))
    # Center using actual component extents, independent of the import tool origin convention.
    o,e=land.get_actor_bounds(False);loc=land.get_actor_location()
    land.set_actor_location(unreal.Vector(loc.x-o.x,loc.y-o.y,0),False,False)
    land.set_actor_label('Isekai Coast - Native Sculptable Landscape');land.set_folder_path('Landscape')
    log('Creating textured grass, path, sand and mountain material')
    land.set_editor_property('landscape_material',material())
    # This world has one sun; fixed exposure keeps the pastel palette stable.
    pp=E.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector())
    pp.set_editor_property('unbound',True)
    settings=pp.get_editor_property('settings')
    for k,v in [('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),('auto_exposure_min_brightness',0.0),('auto_exposure_max_brightness',0.0),('override_bloom_intensity',True),('bloom_intensity',.2),('override_vignette_intensity',True),('vignette_intensity',.12)]:
        settings.set_editor_property(k,v)
    pp.set_editor_property('settings',settings);mark(pp,'Coastal Color & Exposure','Atmosphere')
    ocean=mesh('/Engine/BasicShapes/Plane',0,0,(2500,2500,1),z=0,name='Southern Sea',folder='Coast',ground=False)
    ocean.static_mesh_component.set_material(0,asset('/Game/SoStylized/Environment/Water/Materials/MI_WaterWaves'))
    ocean.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    log('Building village streets and furnished civic center')
    for name,x,y,r,variant,yaw in DATA['buildings']:
        bp('/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_'+str(variant),x,y,r*1.45,yaw,name)
    f=mesh('/Game/StylizedIsland/Mesh/Props/SM_Fountain/SM_Stylized_Fountain_Mesh/SM_Stylized_Fountain',0,0,1.25,name='Permanent Civic Fountain',folder='Village/Civic')
    bench='/Game/Fantastic_Village_Pack/meshes/props/furniture/SM_PROP_bench_01'
    lamp='/Game/Fantastic_Village_Pack/meshes/props/light/SM_PROP_streetlamp_v01_01'
    for a in [35,125,215,305]:
        rad=math.radians(a);x=9.5*math.cos(rad);y=9.5*math.sin(rad)
        mesh(bench,x,y,1.2,a-90,folder='Village/Civic')
        mesh(lamp,x*1.35,y*1.35,1,a,folder='Village/Lanterns')
    for x,y in [(-21,-6),(21,6),(-53,15),(51,20),(-42,-54),(35,-66),(6,-105),(58,64)]:mesh(lamp,x,y,1,90,folder='Village/Lanterns')
    for i,(name,x,y,r,variant,yaw) in enumerate(DATA['buildings']):
        for dx,dy,prop in [(r*.8,0,'SM_Barrel'),(r*.8,1.7,'SM_Crate_Closed')]:
            mesh('/Game/AdvancedVillagePack/Meshes/'+prop,x+dx,y+dy,.85,R.uniform(0,360),folder='Village/Props')
    for x,y in [(-17,-28),(48,-55),(-72,-11)]:
        bp('/Game/Fantastic_Village_Pack/blueprints/props/BP_PROP_cart_01',x,y,3,30,'Supply Cart','Village/Props')
    log('Dressing the harbor and farm terraces')
    dock='/Game/StylizedIsland/Mesh/Props/SM_Docks/SM_Stylized_Docks/SM_Dock_Straight'
    for i in range(5):mesh(dock,-35,-395-i*7.55,1,180,z=1.7,ground=False,folder='Coast/Harbor',name='Timber Pier '+str(i+1))
    bp('/Game/Fantastic_Village_Pack/blueprints/props/BP_PROP_rowboat',-29,-419,5,15,'Fishing Skiff','Coast/Harbor',z=.3)
    for x,y in [(-42,-394),(-43,-391),(-40,-393)]:mesh('/Game/AdvancedVillagePack/Meshes/SM_Barrel',x,y,1,0,folder='Coast/Harbor')
    for x,y in [(100,-230),(133,-244),(162,-222)]:
        for dx in [-12,12]:
            for j in range(7):mesh('/Game/AdvancedVillagePack/Meshes/SM_Fence_Var01',x+dx,y-18+j*6,.9,90,folder='Farms/Fences')
    log('Planting layered forest and wildflower meadows')
    trees=[[],[],[]];bushes=[];grass=[];flowers=[]
    # Jittered cells avoid both random overlaps and mechanical planting rows.
    for ix in range(66):
        for iy in range(62):
            x=-520+ix*15+R.uniform(-5,5);y=-345+iy*15+R.uniform(-5,5)
            z=h(x,y)
            density=.85 if (y>140+35*math.sin(x/85) or x<-185+20*math.sin(y/73)) else .055
            if x>275:density=.13
            if z<8 or z>170 or R.random()>density or not clear(x,y,8):continue
            # Keep district meadows open.
            if 95<x<245 and 35<y<230:continue
            if math.hypot(h(x+2,y)-z,h(x,y+2)-z)>3:continue
            k=2 if z>95 else R.randrange(2)
            trees[k].append((x,y,R.uniform(.72,1.18),R.uniform(0,360)))
    for k,path in enumerate(['Trees/Oak/SM_OakTree1','Trees/Oak/SM_OakTree3','Trees/Pine/SM_Pine01']):foliage('/Game/SoStylized/Environment/'+path,trees[k],['OakCanopy','OakVariation','MountainPine'][k])
    for _ in range(1800):
        x=R.uniform(-430,360);y=R.uniform(-360,440);z=h(x,y)
        if 7<z<135 and clear(x,y,3) and (y>120 or x<-150 or R.random()<.2):bushes.append((x,y,R.uniform(.6,1.25),R.uniform(0,360)))
    for _ in range(28000):
        x=R.uniform(-410,350);y=R.uniform(-340,370);z=h(x,y)
        if 9<z<125 and clear(x,y,1.5):
            grass.append((x,y,R.uniform(.55,1.05),R.uniform(0,360)))
    for _ in range(1100):
        x=R.uniform(-115,140);y=R.uniform(-110,125)
        if clear(x,y,2):flowers.append((x,y,R.uniform(.7,1.1),R.uniform(0,360)))
    foliage('/Game/SoStylized/Environment/Foliage/SM_Bush1',bushes,'Understory',45000)
    foliage('/Game/SoStylized/Environment/Foliage/SM_Grass1',grass,'MeadowGrass',16000)
    foliage('/Game/SoStylized/Environment/Foliage/SM_Flower_Allium',flowers,'VillageFlowers',18000)
    # Rock outcrops add close-range silhouette detail without replacing terrain.
    for i in range(60):
        x=R.uniform(-450,440);y=R.uniform(-375,410)
        if h(x,y)>10 and clear(x,y,10) and (x<-160 or y>180 or x>330):
            mesh('/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1',x,y,R.uniform(.22,.6),R.uniform(0,360),folder='Nature/Outcrops')
    log('Building the concealed northwest seal and exploration landmarks')
    # An outcrop arches around the seal; the approach bends behind the forest ridge.
    for dx,dy,s in [(-10,2,.35),(10,2,.35),(0,9,.42)]:
        mesh('/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1',-350+dx,274+dy,s,90,folder='Adventure/SealedCave')
    bp('/Game/AdvancedPortalsSystemVFX/Blueprints/BP_Portal_3',-350,272,7,90,'Ancient Magical Seal','Adventure/SealedCave',z=h(-350,272)+1)
    sign='/Game/Fantastic_Village_Pack/meshes/props/deco/SM_PROP_signpost_01'
    for x,y,name in [(-87,94,'Whisperwood Trail'),(87,139,'Crown Pass'),(26,-142,'South Harbor'),(120,-63,'East Meadows')]:mesh(sign,x,y,1.2,30,name=name,folder='Adventure/Wayfinding')
    player=E.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,-1900,h(0,-19)*100+110),unreal.Rotator(yaw=90));mark(player,'Start - Fountain Approach','Gameplay')
    # Named empty actors define expansion choices without placeholder houses.
    for x,y,tier in [(105,92,'Town'),(155,145,'Barony'),(205,215,'Kingdom'),(-109,-90,'Homestead'),(91,-99,'Village')]:
        a=E.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(x*100,y*100,h(x,y)*100));mark(a,tier+' Expansion Reserve','Design/Expansion')
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(21000,-26000,19000),unreal.Rotator(pitch=-31,yaw=130))
    L.save_current_level()
    log('Built and saved; viewport review required')
    REPORT.write_text(json.dumps({'status':'saved','map':MAP,'counts':counts,'warnings':warnings,'landscape_bounds':str(land.get_actor_bounds(False))},indent=2))

try:main()
except Exception:
    REPORT.write_text(json.dumps({'status':'error','error':traceback.format_exc(),'counts':counts,'warnings':warnings},indent=2))
    unreal.log_error(traceback.format_exc())
