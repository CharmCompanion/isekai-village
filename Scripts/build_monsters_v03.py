"""Creature anatomy, silhouette and fitted costume rebuild; preserve earlier versions."""
from pathlib import Path
src=Path(__file__).with_name('build_monsters_v02.py').read_text().split("for role in ['Fighter','Knight','Archer','Mage']:")[0]
src=src.replace('Models_v02','Models_v03').replace('_v02','_v03')
# Extrapolate the cranial warp rather than clamping the top of the source head.
fix="base=base.replace('[0,.54,1.03,1.48,1.56,1.84],[0,.29,.64,.96,1.015,1.27]', '[0,.54,1.03,1.48,1.56,1.84,2.10],[0,.29,.64,.96,1.015,1.27,1.507]')\nbase=base.replace('[0,.54,1.03,1.48,1.56,1.84],[0,.68,1.55,2.26,2.42,2.96]', '[0,.54,1.03,1.48,1.56,1.84,2.10],[0,.68,1.55,2.26,2.42,2.96,3.462]')\n"
src=src.replace("exec(compile(base,'monster authoring foundation','exec'))",fix+"exec(compile(base,'monster authoring foundation','exec'))")
exec(compile(src,'v03 foundation','exec'))
import bmesh
from mathutils.kdtree import KDTree

def remove_part(o):
    if o in parts:parts.remove(o)
    bpy.data.objects.remove(o,do_unlink=True)

def surface_tree(o):
    return BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])

def weighted_strip(o,arm,upper,lower,z_top,z_bottom):
    for vg in list(o.vertex_groups):o.vertex_groups.remove(vg)
    a=o.vertex_groups.new(name=upper);b=o.vertex_groups.new(name=lower)
    for v in o.data.vertices:
        t=float(np.clip((z_top-v.co.z)/max(.01,z_top-z_bottom),0,1))
        a.add([v.index],1-t,'REPLACE');b.add([v.index],t,'REPLACE')

def copy_skin_uv(o,head,family):
    # Newly authored ears sample the source ear's UV area; no dark atlas/skin seam.
    kd=KDTree(len(head.data.vertices))
    for v in head.data.vertices:kd.insert(v.co,v.index)
    kd.balance();byvertex={}
    for p in head.data.polygons:
        if p.material_index==0:
            for li in p.loop_indices:byvertex[head.data.loops[li].vertex_index]=head.data.uv_layers.active.data[li].uv.copy()
    o.data.materials.clear();o.data.materials.append(materials[family+'HeadSkin'])
    hp=bonepos(rig_for_surface,'head')
    for p in o.data.polygons:
        for li in p.loop_indices:
            point=o.data.vertices[o.data.loops[li].vertex_index].co.copy()
            point.x=math.copysign(min(abs(point.x),.21 if family=='Ogre' else .105),point.x)
            nearest=kd.find_n(point,8);uv=next((byvertex[i] for co,i,d in nearest if i in byvertex),Vector((.5,.5)))
            o.data.uv_layers.active.data[li].uv=uv

v02_imported=imported_humanoid
anatomy_reports=[]
def imported_humanoid(name,family):
    global rig_for_surface
    arm=v02_imported(name,family);rig_for_surface=arm;body,head=parts[:2];og=family=='Ogre';hz=bonepos(arm,'head').z
    # Reverse the extra torso width warp at the shared neck seam, with a soft fade.
    for v in body.data.vertices:
        x,y,z=v.co
        fade=float(np.clip((z-(2.12 if og else .90))/(.16 if og else .07),0,1))
        if og:factor=1+.055*(1-gauss(x,0,.47))
        else:factor=(1+.07*(1-gauss(x,0,.24)))*(1-.07*gauss(x,0,.20))
        v.co.x=x*(1-fade)+x/factor*fade
    # Preserve eye/lid topology while moving the lower face into creature proportions.
    for v in head.data.vertices:
        x,y,z=v.co;az=z-hz
        if not og:
            mask=gauss(az,.035,.045)*gauss(y,-.14,.065)
            v.co.y-=.020*mask;v.co.x*=1+.16*mask
            nose=gauss(x,0,.038)*gauss(az,.057,.025)*gauss(y,-.155,.06)
            v.co.y-=.012*nose;v.co.z-=.005*nose
        else:
            mask=gauss(az,.04,.067)*gauss(y,-.25,.12)
            v.co.x*=1+.30*mask;v.co.y-=.045*mask
            nose=gauss(x,0,.09)*gauss(az,.13,.046)*gauss(y,-.25,.13)
            v.co.x*=1+.20*nose;v.co.y-=.015*nose
    # Match corresponding neck seam positions and skin weights before welding.
    kd=KDTree(len(body.data.vertices))
    for v in body.data.vertices:kd.insert(v.co,v.index)
    kd.balance();snapped=0
    cut=hz-(.20 if og else .09)
    for v in head.data.vertices:
        if v.co.z>cut:continue
        co,i,d=kd.find(v.co)
        if d<(.025 if og else .014):
            v.co=co;snapped+=1
            for g in list(v.groups):head.vertex_groups[g.group].remove([v.index])
            for g in body.data.vertices[i].groups:
                label=body.vertex_groups[g.group].name
                vg=head.vertex_groups.get(label) or head.vertex_groups.new(name=label);vg.add([v.index],g.weight,'REPLACE')
    for o in [body,head]:
        if o.data.has_custom_normals:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
    # Old cap and tube locks are discarded; use actual scalp surfaces and swept cards.
    for o in list(parts[2:]):
        if o.name.startswith(('Fitted hair scalp','Swept hair lock','Clan cheek warpaint','Angular creature brow')):remove_part(o)
        elif o.name.startswith('Curved cartilage ear'):copy_skin_uv(o,head,family)
        elif o.name.startswith('Ear cartilage fold'):
            o.data.materials[0]=materials[family+'HeadSkin'];copy_skin_uv(o,head,family)
    face=surface_tree(head)
    # Tapered brow follows the eyelid, with irregular rather than rectangular ends.
    for s in [-1,1]:
        eye=hz+(.18 if og else .085);rows=[]
        for j in range(13):
            t=j/12;x=s*((.030 if og else .017)+(.100 if og else .062)*t)
            z=eye+(.010 if og else .007)+(.026 if og else .015)*t
            w=(.016 if og else .009)*math.sin(math.pi*(.13+.80*t))
            rows.append([(x,fit_front(face,x,z+q,-.25,.0015),z+q) for q in [-w,0,w]])
        ribbon('Predatory tapered brow',rows,'Hair','head',.0015)
    if og:scalp_hair(head,arm,name)
    anatomy_reports.append({'id':name,'aligned_neck_vertices':snapped,'head_top':max(v.co.z for v in head.data.vertices)})
    return arm

def scalp_hair(head,arm,name):
    hz=bonepos(arm,'head').z;tree=surface_tree(head)
    top=max(v.co.z for v in head.data.vertices);origin=Vector((0,.025,hz+.20))
    # Extract the upper head polygons; hem follows an organic hairline, no helmet band.
    verts=[];faces=[];index={}
    for p in head.data.polygons:
        if p.material_index!=0:continue
        keep=True
        for vi in p.vertices:
            co=head.data.vertices[vi].co
            threshold=hz+.285 if co.y<-.035 else hz+.205
            if co.z<threshold:keep=False;break
        if not keep:continue
        ids=[]
        for vi in p.vertices:
            if vi not in index:
                co=head.data.vertices[vi].co.copy();out=(co-origin).normalized();co+=out*.006
                index[vi]=len(verts);verts.append(co)
            ids.append(index[vi])
        faces.append(ids)
    rawmesh('Scalp following hair foundation',verts,faces,'Hair','head',.004)
    # Broad flattened locks with creased central ridges; tips sweep into the crown.
    for k in range(25):
        a=math.tau*k/25;r=.19+.025*math.sin(k*2.4);rows=[]
        for j in range(17):
            t=j/16;angle=a+.36*t;rad=r*(1-.72*t)
            x=rad*math.cos(angle);y=.022+rad*.77*math.sin(angle)
            hit=tree.ray_cast(Vector((x,y,top+.35)),Vector((0,0,-1)))
            z=hit[0].z if hit[0] is not None else top-.035
            z+=.006+.023*math.sin(math.pi*t)
            tangent=Vector((-math.sin(angle),math.cos(angle),0));width=.034*(1-t)**.65+.001
            row=[]
            for u in [-1,-.5,0,.5,1]:
                point=Vector((x,y,z))+tangent*width*u;point.z+=.010*(1-abs(u))*math.sin(math.pi*(.1+.8*t));row.append(point)
            rows.append(row)
        ribbon('Swept sculpted hair blade',rows,'Hair','head',.003)
    # Temples and nape locks conceal the coarse extracted scalp hem.
    for k in range(19):
        a=.15+(math.pi-.3)*k/18;rows=[]
        for j in range(12):
            t=j/11;z=hz+.36-.19*t;x=.22*math.cos(a)*(1+.02*t);y=.025+.17*math.sin(a)
            hit=tree.ray_cast(Vector((x*2,y*2,z)),Vector((-x,-y,0)).normalized())
            if hit[0] is not None:x,y,_=hit[0]+hit[1]*.006
            w=.036*(1-t)**.5+.001
            rows.append([(x+q*w*math.sin(a),y-q*w*math.cos(a),z+.01*(1-abs(q))) for q in [-1,0,1]])
        ribbon('Tapered nape hair clump',rows,'Hair','head',.003)

def fit_ring(tree,center,rx,ry,z,count=49,offset=.01):
    row=[]
    for a in np.linspace(0,math.tau,count):
        direction=Vector((math.cos(a),math.sin(a),0))
        candidate=Vector((center.x+rx*math.cos(a),center.y+ry*math.sin(a),z))
        if tree:
            origin=Vector((center.x,center.y,z))+direction*2
            hit=tree.ray_cast(origin,-direction)
            if hit[0] is not None and (hit[0]-Vector((center.x,center.y,z))).length<max(rx,ry)*2.3:candidate=hit[0]+direction*offset
        row.append(candidate)
    return row

def bootwraps(arm,scale):
    tree=body_tree(arm);og='Ogre' in arm.data.name;sk='Skeleton' in arm.data.name
    for side in ['l','r']:
        foot=bonepos(arm,'foot_'+side);knee=bonepos(arm,'calf_'+side)
        low=foot.z+.035*scale;high=foot.z+.23*scale
        rows=[]
        for j in range(17):
            t=j/16;z=low+(high-low)*t;line=foot.lerp(knee,(z-foot.z)/max(.01,knee.z-foot.z))
            rows.append(fit_ring(tree,line,.082*scale,.081*scale,z,offset=.012*scale))
        o=ribbon('Anatomically fitted calf gaiter',rows,'Leather','calf_'+side,.006*scale)
        for j in [2,12]:tube('Gaiter fitted leather binding',rows[j],.004*scale,'Steel','calf_'+side,8)
        # Laced front panel follows the actual silhouette instead of cutting the calf.
        for j in range(3,14,2):tube('Gaiter cross stitch',[rows[j][34],rows[j+2][38]],.0018*scale,'Linen','calf_'+side,6)

def bracers(arm,scale):
    body=parts[0] if 'Skeleton' not in arm.data.name else None;tree=surface_tree(body) if body else None
    for side in ['l','r']:
        a=bonepos(arm,'lowerarm_'+side);b=bonepos(arm,'hand_'+side);d=(b-a).normalized();v=d.cross(Vector((0,1,0))).normalized();w=d.cross(v);rows=[]
        for j in range(13):
            t=.30+.59*j/12;c=a.lerp(b,t);r=(.050-.010*j/12)*scale;row=[]
            for u in np.linspace(0,math.tau,41):
                n=v*math.cos(u)+w*math.sin(u);p=c+n*r
                if tree:
                    hit=tree.ray_cast(c+n*1.5,-n)
                    if hit[0] is not None and (hit[0]-c).length<r*2:p=hit[0]+n*.008*scale
                row.append(p)
            rows.append(row)
        ribbon('Contoured leather vambrace',rows,'Leather','lowerarm_'+side,.005*scale)
        for j in [1,11]:tube('Vambrace edge binding',rows[j],.003*scale,'Steel','lowerarm_'+side,8)
        for j in range(2,11,2):tube('Vambrace hand sewn lacing',[rows[j][27],rows[j+1][31]],.0015*scale,'Linen','lowerarm_'+side,6)

def pauldron(arm,side='r',scale=1):
    p=bonepos(arm,'upperarm_'+side);s=1 if side=='l' else -1
    # Forged faceted shoulder silhouette: broad ridge with downturned front/rear wings.
    for layer in range(3):
        rows=[];length=.175*scale;width=.105*scale
        for j in range(7):
            t=j/6;x=p.x+s*(-.045*scale+length*t+layer*.042*scale)
            z=p.z+(.070-.060*t-layer*.045)*scale
            row=[]
            for k in range(13):
                u=k/12;yy=(u-.5)*2*width*(1-.20*t)
                zz=z-(.045*abs(2*u-1)**1.35+.014*t*t)*scale
                row.append(Vector((x,p.y+yy,zz)))
            rows.append(row)
        o=ribbon('Ridged forged shoulder plate',rows,'Steel','upperarm_'+side,.007*scale)
        for pface in o.data.polygons:pface.use_smooth=True
        for edge in [0,12]:tube('Shoulder bevel edge',[r[edge] for r in rows],.0025*scale,'Gold','upperarm_'+side,6)
        tube('Shoulder outer bevel',rows[-1],.003*scale,'Steel','upperarm_'+side,8)
        for k in [2,10]:ell('Inset shoulder rivet',rows[1][k]+Vector((0,0,.003*scale)),(.0038*scale,)*3,'Gold','upperarm_'+side,10,6)

def cape(arm,color,length=.6):
    shoulder=bonepos(arm,'spine_05');og='Ogre' in arm.data.name;tree=body_tree(arm)
    w=.46 if og else .19;rows=[];n=25
    for j in range(25):
        t=j/24;row=[]
        for k in range(n):
            u=k/(n-1);x=(u-.5)*2*w*(.86+.32*t)
            z=shoulder.z+.025-length*t+.035*(2*u-1)**2*t
            y=(.31 if og else .145)+(.085 if og else .035)*math.sin(u*math.pi*8+.50*t)*math.sin(math.pi*(.15+.80*t))+.10*t
            if tree:
                hit=tree.ray_cast(Vector((x,3,z)),Vector((0,-1,0)))
                if hit[0] is not None:y=max(y,hit[0].y+.025)
            row.append((x,y,z))
        rows.append(row)
    o=ribbon('Weighted tailored folded mantle',rows,color,'spine_04',.006)
    weighted_strip(o,arm,'spine_05','pelvis',shoulder.z,shoulder.z-length)
    for edge in [0,n-1]:
        o=tube('Mantle sewn edge',[r[edge] for r in rows],.0025,'Gold','spine_04',6);weighted_strip(o,arm,'spine_05','pelvis',shoulder.z,shoulder.z-length)

v02_waist=waist
def waist(arm,family,color):
    start=len(parts);v02_waist(arm,family,color)
    # Skin-test the belt and tassets so there are no exposed hip intersections.
    tree=body_tree(arm)
    if not tree:return
    for o in parts[start:]:
        if not o.name.startswith(('Fitted broad belt','Overlapping leather tasset')):continue
        for v in o.data.vertices:
            p=v.co;direction=Vector((p.x,p.y,0)).normalized();origin=Vector((0,0,p.z))+direction*3
            hit=tree.ray_cast(origin,-direction)
            if hit[0] is not None:
                desired=hit[0]+direction*.018
                old_radius=Vector((p.x,p.y,0)).length;new_radius=Vector((desired.x,desired.y,0)).length
                # A radial ray can hit a hand beside the hip; that is not the torso.
                if old_radius<new_radius<old_radius*1.24:v.co=desired

v02_plate=plate
def plate(arm,og=False):
    start=len(parts);v02_plate(arm,og)
    # Add abdomen lames, sculpted recessed collar and readable chest heraldry.
    p=bonepos(arm,'spine_04');tree=body_tree(arm);w=.35 if og else .12
    for j in range(3):
        z=p.z-(.22 if og else .08)-j*(.085 if og else .035);rows=[]
        for dz in [0,-.04 if og else -.017]:
            rows.append([(x,fit_front(tree,x,z+dz,-.11,.076 if og else .025),z+dz+.015*abs(x/w)) for x in np.linspace(-w,w,19)])
        ribbon('Overlapping abdomen armor lame',rows,'Steel','spine_03',.008)
    centerz=p.z+(.12 if og else .05);a=.075 if og else .032
    pts=[]
    for x,z in [(0,centerz+a),(a,centerz),(0,centerz-a),(-a,centerz),(0,centerz+a)]:pts.append((x,fit_front(tree,x,z,-.14,.087 if og else .030),z))
    tube('Forged breastplate clan sigil',pts,.004 if og else .0025,'Gold','spine_04',8)

v02_ribbon=ribbon
def ribbon(name,rows,mat,bone=None,thickness=.012):
    if name=='Mage robe':
        # Actual overlapping coat panels and deep folds, with an open front split.
        rows=[]
        for j in range(25):
            t=j/24;row=[]
            for k in range(65):
                a=-math.pi*.36+math.tau*.86*k/64;r=.15+.125*t+.014*math.sin(a*10)*math.sin(math.pi*(.15+.75*t))
                row.append((r*math.cos(a),r*.72*math.sin(a),1.16-.90*t+.020*math.cos(a*2)*t))
            rows.append(row)
        o=v02_ribbon('Split tailored mage coat',rows,mat,bone,.006)
        for edge in [0,64]:tube('Mage coat embroidered border',[row[edge] for row in rows],.003,'Gold','pelvis',8)
        return o
    return v02_ribbon(name,rows,mat,bone,thickness)

# Shape the skeletal shafts rather than attaching identical sphere joints everywhere.
def modeled_bone(name,a,b,r,group):
    a=Vector(a);b=Vector(b);d=b-a;small=d.length<.065
    o=tube(name,[a,a+d*.08,a+d*.22,a+d*.52,a+d*.79,a+d*.93,b],[r*1.26,r*1.15,r*.83,r*.62,r*.84,r*1.22,r*1.30],'Bone',group,10 if small else 18)
    for v in o.data.vertices:
        v.co.x+=.0015*math.sin(v.co.z*11)*min(1,d.length/.2)
    return o

v02_merge=merged
def merged(name,arm):
    mesh=v02_merge(name,arm)
    # Weld coincident source seams while preserving per-loop UV islands/materials.
    bm=bmesh.new();bm.from_mesh(mesh.data)
    before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000015)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh.data);bm.free();mesh.data.update()
    for p in mesh.data.polygons:p.use_smooth=True
    if mesh.data.has_custom_normals:mesh.data.normals_split_custom_set([(0,0,0)]*len(mesh.data.loops))
    print('SEAM_WELD',name,before-len(mesh.data.vertices))
    return mesh

v02_skull=skull
def skull():
    start=len(parts);v02_skull()
    # Compress the round orbital openings into a more hostile sloping eye shape.
    for o in parts[start:]:
        if o.name.startswith(('Sculpted skull vault','Deep orbital shadow','Small spectral pupil')):
            for v in o.data.vertices:
                p=o.matrix_world@v.co
                mask=gauss(abs(p.x),.058,.055)*gauss(p.z,1.689,.044)*gauss(p.y,-.105,.06)
                p.z=1.689+(p.z-1.689)*(1-.27*mask)-.004*mask*(1-abs(p.x)/.13)
                v.co=o.matrix_world.inverted()@p
        if o.name.startswith('Individual tooth'):
            for v in o.data.vertices:v.co.z*=.76
    # Tapered canine forms make the exposed bite less like a uniform toy grin.
    for s in [-1,1]:
        tube('Skeletal canine',[(s*.057,-.097,1.582),(s*.059,-.104,1.570),(s*.060,-.105,1.554)],[.0065,.005,.0015],'Bone','head',10)

# Build all requested humanoids with the replacement anatomy/costume functions.
for role in ['Fighter','Knight','Archer','Mage']:skeleton_variant('Skeleton'+role,role)
for role in ['Scout','Fighter','Shaman']:humanoid_variant('Goblin'+role,'Goblin',role)
for role in ['Brute','Champion']:humanoid_variant('Ogre'+role,'Ogre',role)
for _,_,o in lineup:o.hide_render=False;o.hide_set(False)
for family in ['Skeleton','Goblin','Ogre']:
    objects=[o for _,f,o in lineup if f==family];spacing={'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]
    for i,o in enumerate(objects):o.location=(spacing*(i-(len(objects)-1)/2),{'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IV_Monster_Library_v03.blend'))
(OUT/'model_manifest.json').write_text(json.dumps({'status':'geometry_and_exports_complete','models':reports,'unreal_import':'pending','slimes':'unchanged v01','anatomy':anatomy_reports},indent=2))
print('MONSTER_REBUILD_V03_COMPLETE',len(reports))
