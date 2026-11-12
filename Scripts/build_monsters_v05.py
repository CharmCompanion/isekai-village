"""Anatomical skeleton and pointed hair/costume refinement; all earlier assets retained."""
from pathlib import Path
source=Path(__file__).with_name('build_monsters_v04.py').read_text().split("for role in ['Fighter','Knight','Archer','Mage']:")[0]
source=source.replace('Models_v04','Models_v05').replace('_v04','_v05')
exec(compile(source,'creature foundation v05','exec'))

def cutter(verts,faces,target,label):
    data=bpy.data.meshes.new(label);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(label,data);bpy.context.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(o,do_unlink=True)

def socket_cut(target,outline,label):
    verts=[(x,y,z) for y in [-.24,-.018] for x,z in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
    cutter(verts,faces,target,label)

def skull():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=40,location=(0,.021,1.694));o=bpy.context.object;o.name='Anatomical cranial vault';o.scale=(.128,.117,.148)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        face=gauss(p.y,-.080,.060)*gauss(p.z,1.695,.09)
        p.y=p.y*(1-face*.30)+(-.077)*face*.30
        p.x*=1+.05*gauss(p.z,1.66,.04)-.045*gauss(p.z,1.78,.045);v.co=o.matrix_world.inverted()@p
    for s in [-1,1]:
        outline=[(s*.018,1.724),(s*.089,1.743),(s*.112,1.722),(s*.098,1.666),(s*.039,1.660),(s*.017,1.681)]
        if s<0:outline.reverse()
        socket_cut(o,outline,'Angular anatomical orbit')
    socket_cut(o,[(0,1.682),(.020,1.646),(.026,1.622),(0,1.617),(-.026,1.622),(-.020,1.646)],'Pear shaped nasal aperture')
    # Expose the dental arcade below the maxilla; no lower spherical face mass.
    socket_cut(o,[(-.16,1.610),(.16,1.610),(.16,1.49),(-.16,1.49)],'Open lower maxilla')
    finish(o,'Bone','head')
    for s in [-1,1]:
        rawmesh('Recessed dark orbital bed',[(s*.020,-.016,1.718),(s*.090,-.015,1.735),(s*.104,-.015,1.718),(s*.089,-.015,1.672),(s*.033,-.015,1.670)],[(0,1,2,3,4)],'EyeDark','head',.001)
        ell('Restrained spectral iris',(s*.060,-.064,1.693),(.0065,.004,.008),'Rune','head',20,12)
        tube('Supraorbital bone keel',[(s*.013,-.077,1.731),(s*.043,-.093,1.740),(s*.080,-.089,1.752),(s*.110,-.070,1.738)],[.006,.008,.010,.008],'Bone','head',12)
        tube('Zygomatic anatomical arch',[(s*.105,-.035,1.696),(s*.134,-.047,1.661),(s*.115,-.071,1.630),(s*.079,-.096,1.615)],[.011,.016,.012,.010],'Bone','head',16)
        tube('Mandibular ramus',[(s*.103,.018,1.639),(s*.112,-.009,1.605),(s*.100,-.052,1.564),(s*.068,-.095,1.548),(0,-.112,1.542)],[.012,.014,.018,.016,.014],'Bone','head',18)
    upper=[];lower=[]
    for k in range(25):
        t=(k-12)/12;upper.append((t*.077,-.106+.044*t*t,1.610+.005*t*t));lower.append((t*.075,-.105+.044*t*t,1.553+.009*t*t))
    tube('Upper dental arcade',upper,.007,'Bone','head',12);tube('Lower dental arcade',lower,.006,'Bone','head',12)
    for top,z in [(True,1.597),(False,1.566)]:
        for k in range(12):
            t=(k-5.5)/5.5;h=.014 if top else .011
            if k in [2,9]:h*=1.25
            tooth=block('Tapered dental tooth',(t*.069,-.107+.040*t*t,z),(.010,.012,h),'Bone','head',.002)
            for v in tooth.data.vertices:
                tip=(v.co.z<0) if top else (v.co.z>0)
                if tip:v.co.x*=.78;v.co.y*=.85
    for s in [-1,1]:
        tube('Cranial temporal suture',[(s*.072,-.030,1.824),(s*.081,-.051,1.801),(s*.074,-.068,1.784),(s*.089,-.076,1.763)],.0009,'Leather','head',6)

v04_tube=tube
def tube(name,coords,radii,mat,bone=None,sides=12):
    o=v04_tube(name,coords,radii,mat,bone,sides)
    if name=='Curved rib':
        # Flatten the rib cross-section and vary the costal crest; stop reading as tubing.
        points=[Vector(p) for p in coords];kd=KDTree(len(points))
        for i,p in enumerate(points):kd.insert(p,i)
        kd.balance()
        for v in o.data.vertices:
            near,i,d=kd.find(v.co);delta=v.co-near;delta.z*=.58;v.co=near+delta
    return o

def modeled_bone(name,a,b,r,group):
    a=Vector(a);b=Vector(b);d=b-a;coords=[a+d*t for t in [0,.07,.22,.50,.78,.94,1]]
    for i,p in enumerate(coords):p.y+=.007*math.sin(i*math.pi/6)*min(1,d.length/.3)
    o=tube(name,coords,[r*1.30,r*1.22,r*.86,r*.68,r*.86,r*1.28,r*1.32],'Bone',group,14)
    if d.length>.20:
        axis=d.normalized();lateral=axis.cross(Vector((0,1,0))).normalized()
        for s in [-1,1]:ell('Anatomical distal condyle',b+lateral*r*.54,(r*.75,r*.83,r*.67),'Bone',group,18,12)
    return o

def scalp_hair(head,arm,name):
    hz=bonepos(arm,'head').z;tree=surface_tree(head);top=max(v.co.z for v in head.data.vertices)
    verts=[];faces=[];ids={}
    for p in head.data.polygons:
        if p.material_index!=0:continue
        if any(head.data.vertices[vi].co.z<hz+(.295 if head.data.vertices[vi].co.y<-.04 else .225) for vi in p.vertices):continue
        face=[]
        for vi in p.vertices:
            if vi not in ids:
                co=head.data.vertices[vi].co.copy();co+=(co-Vector((0,.025,hz+.19))).normalized()*.004;ids[vi]=len(verts);verts.append(co)
            face.append(ids[vi])
        faces.append(face)
    rawmesh('Organic scalp hair foundation',verts,faces,'Hair','head',.002)
    for layer,count in [(0,9),(1,8),(2,7)]:
        for k in range(count):
            x=-.205+.410*k/(count-1)+.003*math.sin(k*4.7);y=-.105+layer*.077+.008*math.sin(k*1.9)
            hit=tree.ray_cast(Vector((x,y,top+.3)),Vector((0,0,-1)))
            if hit[0] is None:continue
            root=hit[0]+hit[1]*.003;verts=[];faces=[];length=.16+.065*math.sin(k*2.3+layer)**2;width=.027+.012*math.sin(k*1.2)**2
            for j in range(25):
                t=j/24;c=root+Vector((x*.35*t+.012*math.sin(k*3.1)*t,length*t,.035*math.sin(math.pi*t)+(.073-layer*.016)*t))
                taper=math.sin(math.pi*t)**.62 if j not in [0,24] else .018
                w=width*taper;dep=.008*taper
                for a in np.linspace(0,math.tau,13)[:-1]:verts.append(c+Vector((w*math.cos(a),0,dep*math.sin(a))))
            for j in range(24):
                for k2 in range(12):a=j*12+k2;b=j*12+(k2+1)%12;faces.append((a,b,b+12,a+12))
            faces.append(tuple(reversed(range(12))));faces.append(tuple(range(24*12,25*12)))
            rawmesh('Pointed swept hair blade',verts,faces,'Hair','head')
    for s in [-1,1]:
        for j in range(5):
            rows=[]
            for k in range(17):
                t=k/16;w=.015*math.sin(math.pi*t)**.6+.0002
                rows.append([(s*(.204-.008*j)+q*w,-.011+.115*t,hz+.305+j*.012-.10*t+.008*(1-abs(q))*math.sin(math.pi*t)) for q in [-1,0,1]])
            ribbon('Pointed temple wisps',rows,'Hair','head',.001)

v04_bow=bow
def bow(arm):
    start=len(parts);v04_bow(arm)
    for o in parts[start:]:
        if o.name.startswith(('Recurve bow','Bow string')):
            for v in o.data.vertices:v.co.x-=.07 if bonepos(arm,'hand_l').z>=1 else .07

v05_waist=waist
def waist(arm,family,color):
    start=len(parts);v05_waist(arm,family,color)
    scale=2.2 if family=='Ogre' else 1
    for o in list(parts[start:]):
        if not o.name.startswith('Overlapping leather tasset'):continue
        coords=[o.data.vertices[j*7+1].co.copy() for j in range(1,8)]
        coords.extend(o.data.vertices[7*7+k].co.copy() for k in range(2,6))
        coords.extend(o.data.vertices[j*7+5].co.copy() for j in reversed(range(1,7)))
        tube('Inset hand sewn tasset hem',coords,.001*scale,'Linen','pelvis',6)
    p=bonepos(arm,'pelvis');ry=.33 if family=='Ogre' else .12 if family=='Skeleton' else .145
    for j in range(5):
        ell('Belt punched recess',(.06*scale+j*.022*scale,-ry-.012,p.z-.025),(.003*scale,.0015*scale,.003*scale),'EyeDark','pelvis',10,6)

v05_plate=plate
def plate(arm,og=False):
    start=len(parts);v05_plate(arm,og)
    target=next(o for o in parts if o.name.startswith('Contoured forged cuirass'))
    c=bonepos(arm,'spine_04')
    for o in parts[start:]:
        if o!=target and not o.name.startswith(('Cuirass rolled border','Forged central keel','Forged breastplate clan sigil')):continue
        for v in o.data.vertices:
            t=max(0,min(1,(v.co.z-(c.z-.20))/(.54 if og else .30)))
            v.co.x*=.80+.20*t
            v.co.y-=((.026 if og else .010)*max(0,1-abs(v.co.x)/(.42 if og else .15)))
    tree=surface_tree(target);s=2.6 if og else 1.;cz=c.z+(.12 if og else .04)
    def at(x,z):
        hit=tree.ray_cast(Vector((x,-5,z)),Vector((0,1,0)));return Vector((x,hit[0].y-.004 if hit[0] else -.16,z))
    for side in [-1,1]:
        for j in range(3):
            x0=side*(.012+j*.019)*s;z0=cz+(.035-j*.017)*s
            path=[at(x0,z0),at(side*(.052+j*.016)*s,z0+.018*s),at(side*(.093+j*.010)*s,z0+.050*s)]
            tube('Etched wing heraldry',path,.0012*s,'Gold','spine_04',6)
    tube('Chest crest blade',[at(0,cz+.047*s),at(0,cz-.077*s)],.002*s,'Gold','spine_04',8)

v05_shield=shield
def shield(arm):
    start=len(parts);v05_shield(arm)
    surface=next(o for o in parts[start:] if o.name.startswith('Curved kite shield'))
    tree=surface_tree(surface);c=bonepos(arm,'lowerarm_l').lerp(bonepos(arm,'hand_l'),.48)+Vector((0,-.10,0));w=.19 if c.z<1 else .24;h=w*1.5
    def at(x,z):
        hit=tree.ray_cast(Vector((x,-5,z)),Vector((0,1,0)));return Vector((x,hit[0].y-.004 if hit[0] else c.y-.04,z))
    for s in [-1,1]:
        for j in range(3):
            z=c.z+h*(.25-j*.12);path=[at(c.x+s*w*.07,z),at(c.x+s*w*.32,z+h*.04),at(c.x+s*w*(.61+j*.025),z+h*.19)]
            tube('Shield chased wing inlay',path,.002,'Gold','lowerarm_l',6)
    tube('Shield heraldic spear',[at(c.x,c.z+h*.59),at(c.x,c.z-h*.60)],.003,'Gold','lowerarm_l',8)

v04_merge=merged
def merged(name,arm):
    if name.startswith('Skeleton'):
        for o in list(parts):
            if o.name.startswith(('Metacarpal','Finger phalanx')):remove_part(o)
        for side in ['r','l']:
            p=bonepos(arm,'hand_'+side);bone='hand_'+side
            for digit in range(4):
                z=p.z-.013-digit*.017;path=[]
                for j in range(7):
                    a=-.35+3.5*j/6;path.append(p+Vector((.023*math.cos(a),-.020+.023*math.sin(a),z-p.z)))
                tube('Gripping skeletal metacarpal',[p+Vector((0,.008,-.002)),path[0]],.006,'Bone',bone,12)
                for j in range(3):modeled_bone('Curved gripping phalanx',path[j*2],path[j*2+2],.0045,bone)
            tube('Opposed skeletal thumb',[p+Vector((-.012,.008,.003)),p+Vector((-.028,-.019,-.013)),p+Vector((-.023,-.041,-.022)),p+Vector((-.005,-.047,-.025))],[.007,.006,.005,.003],'Bone',bone,12)
    return v04_merge(name,arm)

v05_imported_humanoid=imported_humanoid
def imported_humanoid(name,family):
    arm=v05_imported_humanoid(name,family)
    for o in parts[:2]:
        for mat in o.data.materials:
            if not mat.name.endswith('Skin'):continue
            for node in mat.node_tree.nodes:
                if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.22 if 'HeadSkin' in mat.name else .48
    return arm

for role in ['Fighter','Knight','Archer','Mage']:skeleton_variant('Skeleton'+role,role)
for role in ['Scout','Fighter','Shaman']:humanoid_variant('Goblin'+role,'Goblin',role)
for role in ['Brute','Champion']:humanoid_variant('Ogre'+role,'Ogre',role)
for _,_,o in lineup:o.hide_render=False;o.hide_set(False)
for family in ['Skeleton','Goblin','Ogre']:
    objects=[o for _,f,o in lineup if f==family];spacing={'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]
    for i,o in enumerate(objects):o.location=(spacing*(i-(len(objects)-1)/2),{'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IV_Monster_Library_v05.blend'))
(OUT/'model_manifest.json').write_text(json.dumps({'status':'geometry_and_exports_complete','models':reports,'unreal_import':'pending','slimes':'unchanged v01','grips':grip_records,'anatomy':anatomy_reports},indent=2))
print('MONSTER_REBUILD_V05_COMPLETE',len(reports))
