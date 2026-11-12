"""Reference-led humanoid refinement. Leaves all v01 and slime assets intact."""
from pathlib import Path
base=Path(__file__).with_name('build_monsters_v01.py').read_text()
base=base.split("for name,gel in [('MeadowSlime'")[0]
base=base.replace("OUT=ROOT/'Models_v01'","OUT=ROOT/'Models_v02'").replace('_v01','_v02')
exec(compile(base,'monster authoring foundation','exec'))
from mathutils.bvhtree import BVHTree
old_humanoid=imported_humanoid
old_skull=skull

# Latest direction: Korean action-fantasy manhwa. Original designs, darker palette.
manhwa_colors={'Bone':(.60,.62,.56),'Leather':(.065,.033,.028),'Wood':(.11,.075,.045),'Steel':(.085,.12,.16),'Gold':(.29,.24,.15),'ClothRed':(.16,.025,.05),'ClothBlue':(.025,.055,.095),'ClothPurple':(.07,.025,.12),'ClothTeal':(.025,.075,.085),'ClothOlive':(.06,.10,.07),'GoblinSkin':(.15,.25,.17),'OgreSkin':(.33,.075,.07),'Linen':(.20,.18,.16),'Hair':(.014,.019,.027),'Rock':(.14,.16,.19),'Rune':(.06,.30,1.0)}
specs=[(n,manhwa_colors.get(n,c),.52 if n=='Steel' else r,m) for n,c,r,m in specs]
for n,c,r,m in specs:
    mat=materials[n];mat.diffuse_color=(*c,1);bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=r
    if n=='Rune':bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=2

# Shared stylized surface atlas: softly painted tonal breakup and restrained relief.
# These are reusable surface textures, not a substitute for a unique sculpt bake.
rng=np.random.default_rng(207);rgba=np.ones((height,width,4),np.float32);normal=np.ones_like(rgba);roughmap=np.ones_like(rgba)
normal[:,:,:3]=(.5,.5,1)
for i,(name,color,roughness,metal) in enumerate(specs):
    mask=(xx//256==i%8)&(yy//256==i//8)
    clouds=(np.sin(cellx*11+np.sin(celly*7)*1.8)+np.sin(celly*19+cellx*5))*.018
    fine=rng.normal(0,.003,(height,width));shade=.95+clouds+fine
    relief=np.zeros((height,width),np.float32)
    if name.startswith('Cloth') or name=='Linen':
        relief=.002*(np.sin(cellx*math.tau*110)+np.sin(celly*math.tau*95));shade+=relief
    elif name in ['Wood','Leather','Hair']:
        relief=.009*np.sin(cellx*85+np.sin(celly*12)*3);shade+=relief*.7
    elif name in ['Steel','Gold']:
        shade+=.018*np.sin(cellx*33+celly*14);relief=.004*np.sin(cellx*63+celly*41)
    elif name in ['Bone','Rock']:
        shade+=clouds;relief=clouds*.3
    for ch in range(3):rgba[:,:,ch][mask]=np.clip(color[ch]*shade[mask],0,1);roughmap[:,:,ch][mask]=np.clip(roughness+clouds[mask],.05,1)
    dy,dx=np.gradient(relief);nx=-dx*25;ny=-dy*25;nz=np.ones_like(nx);length=np.sqrt(nx*nx+ny*ny+nz*nz)
    for ch,data in enumerate([nx,ny,nz]):normal[:,:,ch][mask]=(data[mask]/length[mask]+1)/2
for name,data in [('T_IV_MonsterPalette_v02',rgba),('T_IV_MonsterRoughness_v02',roughmap),('T_IV_MonsterNormal_v02',normal)]:
    img=tex_images.get(name) or bpy.data.images.new(name,width,height,alpha=True)
    if 'Normal' in name or 'Roughness' in name:img.colorspace_settings.name='Non-Color'
    img.pixels.foreach_set(data.ravel());img.filepath_raw=str(TEX/(name+'.png'));img.file_format='PNG';img.save();tex_images[name]=img
for name,mat in materials.items():
    bs=mat.node_tree.nodes.get('Principled BSDF')
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=tex_images['T_IV_MonsterNormal_v02'];nm=mat.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.45;mat.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])

def rawmesh(name,verts,faces,mat,bone,thick=0):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
    if thick:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        m=o.modifiers.new('Crafted shell thickness','SOLIDIFY');m.thickness=thick;bpy.ops.object.modifier_apply(modifier=m.name)
    return finish(o,mat,bone)

def gauss(x,c,r):return math.exp(-((x-c)/r)**2)

def body_tree(arm):
    if not any(n in arm.data.name for n in ['Goblin','Ogre']):return None
    body=parts[0]
    return BVHTree.FromPolygons([v.co for v in body.data.vertices],[tuple(p.vertices) for p in body.data.polygons])

def fit_front(tree,x,z,fallback,offset=.014):
    if tree:
        hit=tree.ray_cast(Vector((x,-5,z)),Vector((0,1,0)))
        if hit[0] is not None:return hit[0].y-offset
    return fallback

def skin_material(name,kind,color):
    if name in materials:return materials[name]
    mat=bpy.data.materials.new(name);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.72
    prefix='T_BodyA_01' if kind=='Body' else 'T_HeadA_01'
    f=ROOT/'PlayerReference'/(prefix+'_Grayscale.png')
    if f.exists():
        tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(f),check_existing=True)
        mul=mat.node_tree.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*color,1);mat.node_tree.links.new(tx.outputs['Color'],mul.inputs[1]);mat.node_tree.links.new(mul.outputs[0],bs.inputs['Base Color'])
    materials[name]=mat;return mat

def imported_humanoid(name,family):
    arm=old_humanoid(name,family);og=family=='Ogre';body,head=parts[:2]
    # Remove the old disconnected triangular ears, polygon spikes and neck tusks.
    for o in list(parts[2:]):parts.remove(o);bpy.data.objects.remove(o,do_unlink=True)
    hp=bonepos(arm,'head');hz=hp.z
    # Sculpt the shared head topology into creature anatomy; retain its skin weights.
    for v in head.data.vertices:
        x,y,z=v.co;az=z-hz;front=gauss(y,-.15 if og else -.10,.12 if og else .08)
        jaw=gauss(az,.00 if og else -.015,.12 if og else .055)
        neckblend=float(np.clip((az+(.16 if og else .055))/(.15 if og else .055),0,1))
        v.co.x=x*(1+((.35 if og else -.025)+(.12 if og else -.13)*jaw)*neckblend)
        v.co.y=y*(1+(.24 if og else .12)*neckblend)
        v.co.y-=front*(.045 if og else .021)*gauss(x,0,.10 if og else .045)*gauss(az,.115 if og else .055,.065 if og else .032)
        # Heavy brow slopes down toward the nose, cheek ridges and square lower jaw.
        brow=gauss(abs(x),.105 if og else .062,.065 if og else .031)*gauss(az,.23 if og else .125,.035 if og else .018)*front
        v.co.y-=brow*(.032 if og else .018);v.co.z-=brow*(.022 if og else .014)
        v.co.z=hz+az*(1+(.08 if og else .03)*neckblend)
        if og:v.co.y-=.027*jaw*front
    # Broad ogre torso, enlarged forearms/hands, and lankier goblin arms.
    for v in body.data.vertices:
        x,y,z=v.co
        if og:
            central=gauss(x,0,.47);belly=gauss(z,1.77,.34)*central
            v.co.y-=.08*belly*max(0,-y/.35)
            outer=1-gauss(x,0,.47);v.co.x*=1+.055*outer
        else:
            v.co.x*=(1+.07*(1-gauss(x,0,.24)))*(1-.07*gauss(x,0,.20))
    color=(.15,.25,.17) if not og else (.33,.075,.07)
    for o,kind in [(body,'Body'),(head,'Head')]:
        skin='GoblinSkin' if not og else 'OgreSkin';pi=palette[skin];uv=o.data.uv_layers.active.data
        matname=family+kind+'Skin';mat=skin_material(matname,kind,color)
        o.data.materials[0]=mat
        for p in o.data.polygons:
            if p.material_index==0:
                for li in p.loop_indices:
                    u,w=uv[li].uv;uv[li].uv=((u*8-pi%8-.1)/.8,(w*4-pi//8-.1)/.8)
    face=BVHTree.FromPolygons([v.co for v in head.data.vertices],[tuple(p.vertices) for p in head.data.polygons])
    for s in [-1,1]:
        # A sharp angular brow reads at gameplay distance without changing the eyes.
        eyez=hz+(.18 if og else .085);xs=[.035,.070,.115] if og else [.018,.043,.075];zs=[eyez-.008,eyez+.009,eyez+.018]
        verts=[]
        for x,z in zip(xs,zs):
            for dz in [0,.013 if og else .008]:
                yy=fit_front(face,s*x,z+dz,-.2 if og else -.13,.002)
                verts.append((s*x,yy,z+dz))
        rawmesh('Angular creature brow',verts,[(0,1,3,2),(2,3,5,4)],'Hair','head',.002)
        # Original angular cheek mark, fitted against the deformed face surface.
        if og:
            verts=[]
            for x,z in [(s*.14,hz+.17),(s*.185,hz+.20),(s*.185,hz+.10),(s*.14,hz+.13)]:verts.append((x,fit_front(face,x,z,-.22,.002),z))
            rawmesh('Clan cheek warpaint',verts,[(0,1,2,3)],'Hair','head',.0008)
    # Curved, fleshy pointed ears with an inset inner fold, attached inside the head.
    sx=.19 if og else .095;length=.18 if og else .15;zc=hz+(.19 if og else .10)
    for s in [-1,1]:
        rows=[]
        for j in range(17):
            t=j/16;w=(.062 if og else .036)*math.sin((.18+.82*t)*math.pi)**.65
            x=s*(sx+length*t);z=zc+(.066 if og else .035)*t
            rows.append([(x,.036,z-w),(x,-.040-.02*math.sin(t*math.pi),z),(x,.027,z+w)])
        ribbon('Curved cartilage ear',rows,'OgreSkin' if og else 'GoblinSkin','head',.012)
        tube('Ear cartilage fold',[(s*sx,-.046,zc),(s*(sx+length*.5),-.055,zc+.027),(s*(sx+length*.9),-.006,zc+.05)],[.007,.009,.002],'Leather','head',10)
        if og:
            tube('Integrated upward tusk',[(s*.125,-.240,hz-.03),(s*.160,-.310,hz+.005),(s*.185,-.300,hz+.09),(s*.176,-.270,hz+.15)],[.035,.027,.014,.0015],'Bone','head',16)
        else:
            tube('Small lower fang',[(s*.039,-.156,hz-.01),(s*.047,-.169,hz+.016),(s*.045,-.165,hz+.038)],[.008,.007,.001],'Bone','head',10)
    if og:
        # Swept hair locks with a curved taper, rather than crystal spikes.
        rows=[]
        for j in range(13):
            th=.001+1.37*j/12;rows.append([( .275*math.sin(th)*math.cos(a),.04+.22*math.sin(th)*math.sin(a),hz+.225+.235*math.cos(th)) for a in np.linspace(0,math.tau,49)])
        ribbon('Fitted hair scalp',rows,'Hair','head',.007)
        for i in range(19):
            a=math.tau*i/19;x=.20*math.cos(a);y=.045+.14*math.sin(a)
            tube('Swept hair lock',[(x,y,hz+.35),(x*.75,y+.02,hz+.435),(x*.38,y+.075,hz+.46),(x*.18,y+.12,hz+.41)],[.041,.038,.019,.002],'Hair','head',10)
    return arm

def collar(arm,color,og=False):
    p=bonepos(arm,'neck_01');rx=.225 if og else .14;ry=.175 if og else .125
    for j in range(3):
        coords=[(rx*math.cos(a),p.y+ry*math.sin(a),p.z-.05-j*.018+.018*math.sin(a*2+j)) for a in np.linspace(0,math.tau,65)]
        tube('Folded cowl collar',coords,.024 if og else .017,color,'spine_05',10)

def waist(arm,family,color):
    p=bonepos(arm,'pelvis');og=family=='Ogre';sk=family=='Skeleton'
    rx=.51 if og else .15 if sk else .195;ry=.33 if og else .12 if sk else .145
    rows=[[(rx*math.cos(a),ry*math.sin(a),p.z+z) for a in np.linspace(0,math.tau,65)] for z in [-.07,.015]]
    ribbon('Fitted broad belt',rows,'Leather','pelvis',.014)
    # Open buckle frame, punched holes and a separate strap tongue.
    w=.11 if og else .064;h=.065 if og else .04
    coords=[(-w,-ry-.018,p.z-h),(w,-ry-.018,p.z-h),(w,-ry-.018,p.z+h),(-w,-ry-.018,p.z+h),(-w,-ry-.018,p.z-h)]
    tube('Forged buckle frame',coords,.009 if og else .005,'Steel','pelvis',8)
    tube('Buckle tongue',[(0,-ry-.022,p.z-h),(0,-ry-.024,p.z+h*.6)],.004,'Steel','pelvis',8)
    # Individually layered tassets break the silhouette rather than a skirt cylinder.
    for k in range(10):
        a=k*math.tau/10;rows=[];length=(.37 if og else .23)*(1+.17*math.sin(k*2.3))
        for j in range(8):
            t=j/7;row=[]
            for n in range(7):
                u=n/6;aa=a+(u-.5)*.59;flare=1+.19*t
                row.append((rx*flare*math.cos(aa),ry*flare*math.sin(aa),p.z-.07-length*t+.014*math.cos(u*math.tau)*t))
            rows.append(row)
        o=ribbon('Overlapping leather tasset',rows,'Leather' if k%3 else color,'pelvis',.009)
        for n in [1,5]:ell('Tasset fastener',rows[0][n],(.005,.005,.005),'Steel','pelvis',10,6)
    tabard(arm,color,.55 if og else .35,rx*.68,front=-ry-.035,z=p.z-.035,bone='pelvis')
    for s in [-1,1]:
        c=Vector((s*rx*.82,-ry*.65,p.z-.025));size=.10 if og else .055
        block('Tailored satchel',c,(size,.045,size*1.15),'Leather','pelvis',.008)
        block('Satchel flap',c+Vector((0,-.026,size*.25)),(size*.93,.015,size*.58),'Wood','pelvis',.007)
        ell('Satchel clasp',c+Vector((0,-.04,0)),(.007,.004,.007),'Gold','pelvis',12,8)

def tabard(arm,color,length,width,front,z,bone):
    rows=[]
    for j in range(15):
        t=j/14;row=[]
        for k in range(17):
            u=k/16;x=(u-.5)*2*width*(1-.12*t);y=front-.027*math.cos(u*math.pi*6)*t-.12*t
            zz=z-length*t+.04*abs(u-.5)*2*t+.006*math.sin(k*3)*t
            row.append((x,y,zz))
        rows.append(row)
    ribbon('Long split heraldic tabard',rows,color,bone,.008)
    for edge in [0,16]:tube('Tabard woven piping',[r[edge] for r in rows],.003,'Gold',bone,6)
    center=Vector((0,front-.12,z-length*.62));scale=width*.47
    tube('Embroidered diamond',[center+Vector((0,0,scale)),center+Vector((scale,0,0)),center+Vector((0,0,-scale)),center+Vector((-scale,0,0)),center+Vector((0,0,scale))],.004,'Gold',bone,6)

def plate(arm,og=False):
    c=bonepos(arm,'spine_04');w=.47 if og else .165;h=.27 if og else .13;depth=.36 if og else .125
    tree=body_tree(arm)
    rows=[]
    for j in range(17):
        t=j/16;row=[]
        for k in range(25):
            u=k/24;ww=w*(.84+.16*math.sin(t*math.pi));x=(u-.5)*2*ww
            y=-depth*math.sqrt(max(.08,1-(x/(w*1.12))**2))-.02
            z=c.z+.08+h*(1-2*t)+.025*abs(u-.5)*2*(1-t)
            y=fit_front(tree,x,z,y,.065 if og else .013)
            row.append((x,y,z))
        rows.append(row)
    # Forge a smooth plate envelope rather than reproducing abdominal muscle dents.
    for iteration in range(8):
        old=[[tuple(p) for p in row] for row in rows]
        for j in range(1,16):
            for k in range(1,24):
                p=list(rows[j][k]);p[1]=.40*old[j][k][1]+.15*(old[j-1][k][1]+old[j+1][k][1]+old[j][k-1][1]+old[j][k+1][1]);rows[j][k]=tuple(p)
    ribbon('Contoured forged cuirass',rows,'Steel','spine_04',.014)
    for j in [0,16]:tube('Cuirass rolled border',rows[j],.009 if og else .005,'Gold','spine_04',8)
    tube('Forged central keel',[r[12] for r in rows],.007 if og else .004,'Steel','spine_04',8)

def pauldron(arm,side='r',scale=1):
    p=bonepos(arm,'upperarm_'+side);rx=.09*scale;ry=.10*scale;rz=.08*scale
    for layer in range(3):
        rows=[]
        for j in range(7):
            th=.001+(1.50+layer*.10-.001)*j/6;row=[]
            for k in range(33):
                a=k*math.tau/32;row.append(p+Vector((rx*(1+layer*.08)*math.sin(th)*math.cos(a),ry*(1+layer*.08)*math.sin(th)*math.sin(a),rz*math.cos(th)-layer*.026*scale+.032*scale)))
            rows.append(row)
        ribbon('Articulated shoulder lame',rows,'Steel','upperarm_'+side,.009*scale)
        tube('Shoulder rolled edge',rows[-1],.004*scale,'Gold','upperarm_'+side,8)
        for k in [18,22,26,30]:ell('Hammered shoulder rivet',rows[-1][k],(.005*scale,)*3,'Gold','upperarm_'+side,10,6)

def bandolier(arm,og=False):
    p=bonepos(arm,'spine_04');w=.37 if og else .145;h=.52 if og else .29;depth=.27 if og else .105
    tree=body_tree(arm)
    rows=[]
    for j in range(25):
        t=j/24;x=-w+w*2*t;z=p.z-h*.42+h*t;y=-depth*math.sqrt(max(.2,1-(x/(w*1.3))**2))-.035
        rows.append([(x-.025,fit_front(tree,x-.025,z+.015,y,.11 if 'OgreChampion' in arm.data.name else .018),z+.015),(x+.025,fit_front(tree,x+.025,z-.015,y,.11 if 'OgreChampion' in arm.data.name else .018),z-.015)])
    ribbon('Diagonal leather harness',rows,'Leather','spine_04',.011)
    for k in [5,11,17,22]:ell('Harness rivet',Vector(rows[k][0]).lerp(Vector(rows[k][1]),.5)+Vector((0,-.008,0)),(.005,.004,.005),'Gold','spine_04',10,6)

def bracers(arm,scale):
    for side in ['l','r']:
        a=bonepos(arm,'lowerarm_'+side);b=bonepos(arm,'hand_'+side);d=(b-a).normalized();v=d.cross(Vector((0,1,0))).normalized();w=d.cross(v)
        rows=[]
        for j in range(7):
            t=.36+.55*j/6;p=a.lerp(b,t);r=(.047-.009*j/6)*scale
            rows.append([p+r*(v*math.cos(u)+w*math.sin(u)) for u in np.linspace(0,math.tau,33)])
        ribbon('Fitted stitched bracer',rows,'Leather','lowerarm_'+side,.005)
        for j in [0,6]:tube('Bracer metal binding',rows[j],.0028*scale,'Steel','lowerarm_'+side,6)
        for j in range(6):tube('Bracer cross lacing',[rows[j][23],rows[j+1][27]],.0018*scale,'Linen','lowerarm_'+side,6)

def bootwraps(arm,scale):
    for side in ['l','r']:
        p=bonepos(arm,'foot_'+side);r=.078*scale;z=p.z
        rows=[]
        for j in range(9):
            t=j/8;rows.append([(p.x+r*(1+.1*t)*math.cos(a),p.y+r*.88*math.sin(a),z+.025*scale+t*.17*scale) for a in np.linspace(0,math.tau,33)])
        ribbon('Fitted open-toe gaiter',rows,'Leather','calf_'+side,.007)
        for i in range(2):
            coords=[(p.x+r*1.08*math.cos(a),p.y+r*.96*math.sin(a),z+(.05+i*.08)*scale+.004*math.sin(a*2)) for a in np.linspace(0,math.tau,49)]
            tube('Gaiter crossed binding',coords,.0038*scale,'Linen','calf_'+side,6)

def sword(arm,side='r',heavy=False):
    p=bonepos(arm,'hand_'+side)+Vector((0,-.02,0));bone='hand_'+side
    tube('Bound sword handle',[p+Vector((0,0,.04)),p-Vector((0,0,.09))],.014,'Leather',bone,12)
    for i in range(8):tube('Grip leather stitch',[(p.x-.014,p.y-.009,p.z-.085+i*.016),(p.x+.014,p.y-.009,p.z-.076+i*.016)],.002,'Linen',bone,6)
    ell('Faceted pommel',p+Vector((0,0,.062)),(.022,.015,.026),'Gold',bone,12,8)
    tube('Swept steel crossguard',[p+Vector((-.105,0,-.10)),p+Vector((-.065,0,-.13)),p+Vector((0,0,-.12)),p+Vector((.065,0,-.13)),p+Vector((.105,0,-.10))],[.005,.009,.012,.009,.005],'Steel',bone,10)
    length=min(.73,p.z-.22);verts=[];faces=[]
    for t,width in [(0,.039),(.12,.046),(.85,.029),(1,.001)]:
        z=p.z-.14-length*t;verts.extend([(p.x-width,p.y,z),(p.x,p.y-.013,z),(p.x+width,p.y,z),(p.x,p.y+.013,z)])
    for j in range(3):
        for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
    rawmesh('Diamond section forged blade',verts,faces,'Steel',bone)

def shield(arm):
    c=bonepos(arm,'lowerarm_l').lerp(bonepos(arm,'hand_l'),.48)+Vector((0,-.10,0));w=.19 if c.z<1 else .24;h=w*1.5
    outline=[(-w,-h*.4),(-w,h*.72),(-w*.7,h),(w*.7,h),(w,h*.72),(w,-h*.4),(0,-h)]
    verts=[c+Vector((0,-.035,0))]+[c+Vector((x,0,z)) for x,z in outline]
    rawmesh('Curved kite shield',verts,[(0,i+1,(i+1)%7+1) for i in range(7)],'ClothBlue','lowerarm_l',.019)
    tube('Kite shield rolled rim',verts[1:]+[verts[1]],.009,'Steel','lowerarm_l',8)
    for p in verts[1:]:ell('Shield corner fastener',p+Vector((0,-.012,0)),(.006,.004,.006),'Gold','lowerarm_l',10,6)
    tube('Shield crest diamond',[c+Vector((0,-.045,h*.5)),c+Vector((w*.4,-.046,0)),c+Vector((0,-.045,-h*.4)),c+Vector((-w*.4,-.046,0)),c+Vector((0,-.045,h*.5))],.007,'Gold','lowerarm_l',8)

def skull():
    start=len(parts);old_skull()
    for o in list(parts[start:]):
        if o.name.startswith('Soul light'):parts.remove(o);bpy.data.objects.remove(o,do_unlink=True)
    vault=next(o for o in parts[start:] if o.name.startswith('Sculpted skull vault'))
    # Wider zygomatic silhouette, narrower temple and flatter facial plane.
    for v in vault.data.vertices:
        z=v.co.z+vault.location.z
        v.co.x*=1+.10*gauss(z,1.62,.04)-.06*gauss(z,1.72,.05)
    for s in [-1,1]:
        ell('Deep orbital shadow',(s*.058,-.076,1.689),(.039,.021,.028),'EyeDark','head',24,16)
        ell('Small spectral pupil',(s*.058,-.103,1.689),(.008,.006,.011),'Rune','head',16,10)
        tube('Angular supraorbital ridge',[(s*.020,-.107,1.718),(s*.055,-.119,1.731),(s*.097,-.094,1.717)],[.007,.009,.006],'Bone','head',10)
    for i in range(3):
        x=-.07+i*.06
        tube('Cranium fracture inlay',[(x,-.072,1.796),(x+.016,-.087,1.783),(x+.007,-.095,1.766),(x+.024,-.10,1.748)],.0014,'Leather','head',6)

def material_record(o):
    return [{'slot':i,'name':m.name,'palette_index':palette.get(m.name),'roughness':specs[palette[m.name]][2] if m.name in palette else .72,'metallic':specs[palette[m.name]][3] if m.name in palette else 0} for i,m in enumerate(o.data.materials)]

original_tube=tube
def tube(name,coords,radii,mat,bone=None,sides=12):
    if name in ['Curved rib','Mandible','Cheek arch','Pelvic wing'] and len(coords)>3:
        pts=[Vector(p) for p in coords];rr=[radii]*len(pts) if isinstance(radii,(float,int)) else radii;new=[];rs=[]
        for j in range(len(pts)-1):
            a=pts[max(0,j-1)];b=pts[j];c=pts[j+1];d=pts[min(len(pts)-1,j+2)]
            for k in range(5):
                t=k/5;new.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));rs.append(rr[j]*(1-t)+rr[j+1]*t)
        new.append(pts[-1]);rs.append(rr[-1]);coords=new;radii=rs
    return original_tube(name,coords,radii,mat,bone,sides)

original_hood=hood
def hood(arm,color):
    start=len(parts);original_hood(arm,color)
    o=parts[-1];center=bonepos(arm,'head')+Vector((0,.015,.035))
    # Shape cloth into a peaked, asymmetric drape instead of a helmet sphere.
    if color!='Steel':
        for v in o.data.vertices:
            z=v.co.z
            v.co.z+=.047*gauss(z,center.z+.18,.06)
            v.co.y+=.013*math.sin(v.co.x*24)*gauss(z,center.z-.07,.15)
        collar(arm,color)
        for s in [-1,1]:tube('Hood opening bound edge',[(s*.14,-.11,1.56),(s*.148,-.14,1.66),(s*.104,-.125,1.79),(0,-.06,1.875)],.004,'Gold' if color=='ClothPurple' else 'Linen','head',8)
    else:
        tube('Helmet central crest',[(0,.11,1.69),(0,.07,1.84),(0,-.05,1.875),(0,-.144,1.75)],.010,'Steel','head',8)
        for s in [-1,1]:
            rawmesh('Forged helmet cheek guard',[(s*.15,-.045,1.70),(s*.158,-.08,1.59),(s*.10,-.13,1.555),(s*.10,-.14,1.69)],[(0,1,2,3)],'Steel','head',.008)
            tube('Helmet cheek trim',[(s*.15,-.06,1.70),(s*.15,-.095,1.60),(s*.10,-.14,1.555)],.004,'Gold','head',8)

old_skeleton=skeleton_variant
def skeleton_variant(name,role):
    # Keep the anatomical base but replace the former accessory implementations.
    old_skeleton(name,role)

# Disable the round cuirass created by the old class routine; plate is fitted below.
original_ell=ell
def ell(name,pos,scale,mat,bone=None,segments=24,rings=16):
    if name=='Knight cuirass':return None
    return original_ell(name,pos,scale,mat,bone,segments,rings)

old_merge=merged
def merged(name,arm):
    family='Ogre' if name.startswith('Ogre') else 'Goblin' if name.startswith('Goblin') else 'Skeleton'
    if family=='Skeleton':
        # Remove the old waist cylinder and simplistic boot/bracer accessories.
        for o in list(parts):
            if any(o.name.startswith(n) for n in ['Layered waist belt','Layered ragged waistcloth','Belt buckle','Supply pouch']):parts.remove(o);bpy.data.objects.remove(o,do_unlink=True)
        role=name.removeprefix('Skeleton');col={'Fighter':'ClothRed','Knight':'ClothBlue','Archer':'ClothOlive','Mage':'ClothPurple'}[role]
        waist(arm,family,col);bandolier(arm);bootwraps(arm,.7)
        if role=='Knight':plate(arm);tabard(arm,col,.61,.10,-.145,1.02,'pelvis')
        if role in ['Mage','Archer']:collar(arm,col)
    return old_merge(name,arm)

def humanoid_variant(name,family,role):
    arm=imported_humanoid(name,family);og=family=='Ogre';scale=2.35 if og else .95
    color='ClothRed' if role in ['Fighter','Champion'] else 'ClothTeal' if role=='Shaman' else 'Linen'
    waist(arm,family,color);bracers(arm,scale);bootwraps(arm,scale);bandolier(arm,og)
    if family=='Goblin':
        if role=='Scout':bow(arm);sword(arm);collar(arm,'ClothRed');cape(arm,'ClothOlive',.42)
        elif role=='Fighter':sword(arm);shield(arm);pauldron(arm,'r',1.15)
        else:
            staff(arm,scale=.75);collar(arm,color);cape(arm,color,.65)
            p=bonepos(arm,'pelvis');tabard(arm,color,.46,.12,-.175,p.z+.08,'pelvis')
            for s in [-1,1]:tube('Shaman bone pendant',[(s*.036,-.13,.98),(s*.046,-.16,.88)],[.008,.003],'Bone','spine_04',10)
    else:
        ogre_club(arm,role=='Champion')
        if role=='Champion':plate(arm,True);pauldron(arm,'r',scale);pauldron(arm,'l',scale*.9);cape(arm,color,.95)
    mesh=merged(name,arm);actions=animate(arm,name,family);export_model(name,family,mesh,arm,actions,FBX/name)

def ogre_club(arm,champion):
    p=bonepos(arm,'hand_r');tip=p+Vector((0,-.065,-1.05));bone='hand_r'
    tube('Heavy carved weapon haft',[p+Vector((0,0,.12)),p+Vector((.02,0,-.55)),tip],[.045,.043,.052],'Wood',bone,16)
    for j in range(13):
        z=p.z+.09-j*.028
        tube('Haft spiral leather wrap',[(p.x+.046*math.cos(a),p.y+.046*math.sin(a),z-.025*a/math.tau) for a in np.linspace(0,math.tau,25)],.006,'Leather',bone,6)
    if champion:
        o=block('Asymmetric carved stone maul',tip,(.69,.36,.38),'Rock',bone,.048)
        for v in o.data.vertices:
            v.co.x+=.016*math.sin(v.co.z*31+v.co.y*22);v.co.z+=.009*math.sin(v.co.x*33+v.co.y*17)
        for x in [-.22,.22]:
            rows=[]
            for q in [-.024,.024]:rows.append([(tip.x+x+q,tip.y+y,tip.z+z) for y,z in [(-.194,-.16),(-.194,.16),(-.15,.202),(.15,.202),(.194,.16),(.194,-.16),(.15,-.202),(-.15,-.202),(-.194,-.16)]])
            ribbon('Maul forged binding',rows,'Steel',bone,.008)
            for z in [-.095,.095]:ell('Maul binding rivet',(tip.x+x,tip.y-.20,tip.z+z),(.009,.008,.009),'Gold',bone,12,8)
    else:
        coords=[tip+Vector((.02*math.sin(j*.8),0,-.18+j*.073)) for j in range(9)]
        o=tube('Knotted tree heartwood club',coords,[.16,.185,.21,.205,.19,.17,.14,.105,.065],'Wood',bone,20)
        for v in o.data.vertices:v.co+=v.normal*.005*math.sin(v.co.z*41+v.co.x*23)
        for j in [1,4]:
            c=coords[j];r=[.16,.185,.21,.205,.19,.17,.14,.105,.065][j]
            for h in [-.014,.014]:tube('Club iron reinforcement',[(c.x+(r+.008)*math.cos(a),c.y+(r+.008)*math.sin(a),c.z+h) for a in np.linspace(0,math.tau,33)],.012,'Steel',bone,8)
        for k in range(8):
            a=k*math.tau/8;path=[p+Vector((.006*math.sin(j+k),0,0))+Vector((r*.99*math.cos(a),r*.99*math.sin(a),0)) for j,(p,r) in enumerate(zip(coords,[.16,.185,.21,.205,.19,.17,.14,.105,.065]))]
            tube('Organic bark split',path,.003,'Leather',bone,6)

original_staff=staff
def staff(arm,side='l',scale=1):
    original_staff(arm,side,scale);p=bonepos(arm,'hand_'+side);h=max(1.5,p.z+scale*.65);bone='hand_'+side
    for j in range(7):
        z=p.z-.08+j*.025
        tube('Staff woven grip',[(p.x+.026*scale*math.cos(a),p.y+.026*scale*math.sin(a),z+.01*a/math.tau) for a in np.linspace(0,math.tau,25)],.0035,'Leather',bone,6)
    for s in [-1,1]:
        tube('Staff curved guardian branch',[(p.x,p.y,h-.16),(p.x+s*.10*scale,p.y+.015,h-.07),(p.x+s*.13*scale,p.y,h+.12),(p.x+s*.07*scale,p.y-.006,h+.20)],[.016,.014,.009,.002],'Wood',bone,12)
    for z in [.35,h-.19]:
        tube('Staff brass binding',[(p.x+.03*scale*math.cos(a),p.y+.03*scale*math.sin(a),z) for a in np.linspace(0,math.tau,33)],.006,'Gold',bone,8)
    tube('Hanging talisman cord',[(p.x+.06*scale,p.y,h-.07),(p.x+.11*scale,p.y-.01,h-.24)],.0025,'Leather',bone,6)
    crystal('Hanging ward crystal',(p.x+.11*scale,p.y-.01,h-.30),.08,'Rune',bone)

for role in ['Fighter','Knight','Archer','Mage']:skeleton_variant('Skeleton'+role,role)
for role in ['Scout','Fighter','Shaman']:humanoid_variant('Goblin'+role,'Goblin',role)
for role in ['Brute','Champion']:humanoid_variant('Ogre'+role,'Ogre',role)
for _,_,o in lineup:o.hide_render=False;o.hide_set(False)
for family in ['Skeleton','Goblin','Ogre']:
    objects=[o for _,f,o in lineup if f==family];spacing={'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]
    for i,o in enumerate(objects):o.location=(spacing*(i-(len(objects)-1)/2),{'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IV_Monster_Library_v02.blend'))
(OUT/'model_manifest.json').write_text(json.dumps({'status':'geometry_and_exports_complete','models':reports,'unreal_import':'pending','slimes':'unchanged v01'},indent=2))
print('MONSTER_REFINEMENT_BUILD_COMPLETE',len(reports))

