"""Close-up creature benchmark and complete humanoid rebuild, with preserved revisions."""
from pathlib import Path
foundation=Path(__file__).with_name('build_monsters_v03.py').read_text().split('# Build all requested humanoids')[0]
foundation=foundation.replace('Models_v03','Models_v04').replace('_v03','_v04')
exec(compile(foundation,'creature foundation v04','exec'))

v03_imported=imported_humanoid
v03_hair=scalp_hair
v03_merge=merged
v03_export=export_model
skin_done=set();grip_records=[]

def paint_skin_texture(o,family,kind,arm):
    key=family+kind
    mat=materials[key+'Skin'];prefix='T_BodyA_01' if kind=='Body' else 'T_HeadA_01'
    file=TEX/('T_IV_'+key+'_Painted_v04.png')
    if key not in skin_done:
        original=bpy.data.images.load(str(ROOT/'PlayerReference'/(prefix+'_Grayscale.png')),check_existing=True)
        W,H=original.size;data=np.array(original.pixels[:],np.float32).reshape(H,W,4).copy()
        color=np.array((.29,.072,.048) if family=='Ogre' else (.115,.215,.085),np.float32)
        data[:,:,:3]*=color
        hz=bonepos(arm,'head').z;uv=o.data.uv_layers.active.data;o.data.calc_loop_triangles()
        # Paint large deliberate forms in surface space, then rasterize to original UVs.
        # This keeps ear/neck joins in the same skin family and avoids screen-space paint.
        for tri in o.data.loop_triangles:
            if tri.material_index!=0:continue
            u=np.array([tuple(uv[li].uv) for li in tri.loops],np.float64);u[:,0]*=W-1;u[:,1]*=H-1
            lo=np.maximum(np.floor(u.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(u.max(axis=0)).astype(int),[W-1,H-1])
            if np.any(hi<lo):continue
            px,py=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
            a,b,c=u;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8:continue
            w0=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
            w1=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den;w2=1-w0-w1
            inside=(w0>=-.002)&(w1>=-.002)&(w2>=-.002)
            xyz=np.array([tuple(o.data.vertices[vi].co) for vi in tri.vertices]);p=w0[:,:,None]*xyz[0]+w1[:,:,None]*xyz[1]+w2[:,:,None]*xyz[2]
            x,y,z=p[:,:,0],p[:,:,1],p[:,:,2];shade=np.zeros(x.shape,np.float32);scar=np.zeros_like(shade)
            if kind=='Head':
                front=np.clip((-y-(.055 if family=='Ogre' else .035))/.075,0,1)
                zz=z-hz
                if family=='Ogre':
                    # Two unequal cheek slashes, with a healed diagonal eyebrow scar.
                    line=np.abs(np.abs(x)-(.17+.11*(zz-.08)))
                    shade=np.clip((.030-line)/.008,0,1)*np.clip((zz-.045)/.025,0,1)*np.clip((.24-zz)/.035,0,1)*front
                    scar=np.exp(-((zz-(.19+.31*x))/.006)**2)*np.clip((x+.19)/.025,0,1)*np.clip((.055-x)/.025,0,1)*front
                else:
                    # Darker nasal plane and angular clan pigment at the outer cheek.
                    shade=np.clip((.016-np.abs(np.abs(x)-(.089+.07*zz)))/.006,0,1)*np.clip((zz-.028)/.012,0,1)*np.clip((.095-zz)/.025,0,1)*front*.8
                    scar=np.exp(-((zz-(.105-.21*x))/.0035)**2)*np.clip((x+.11)/.014,0,1)*np.clip((-.035-x)/.014,0,1)*front*.45
            elif family=='Ogre':
                # Faction paint across deltoids and diagonal upper chest, not random noise.
                outer=np.clip((np.abs(x)-.39)/.10,0,1)*np.clip((.94-np.abs(x))/.15,0,1)
                stripe=np.minimum(np.abs(z-(2.21+.10*np.abs(x))),np.abs(z-(2.08+.10*np.abs(x))))
                shade=np.clip((.023-stripe)/.010,0,1)*outer*.85
                scar=np.exp(-((z-(2.18+.26*x))/.007)**2)*np.clip((.30-np.abs(x))/.06,0,1)*np.clip((-y-.12)/.12,0,1)*.55
            block=data[lo[1]:hi[1]+1,lo[0]:hi[0]+1,:3]
            pigment=np.array((.060,.016,.015) if family=='Ogre' else (.020,.060,.030),np.float32)
            healed=np.array((.42,.16,.115) if family=='Ogre' else (.20,.30,.13),np.float32)
            painted=block*(1-shade[:,:,None]*.8)+pigment*shade[:,:,None]*.8
            painted=painted*(1-scar[:,:,None]*.50)+healed*scar[:,:,None]*.50
            block[inside]=painted[inside]
        image=bpy.data.images.new('T_IV_'+key+'_Painted_v04',W,H,alpha=True);image.pixels.foreach_set(data.ravel());image.filepath_raw=str(file);image.file_format='PNG';image.save();skin_done.add(key)
    image=bpy.data.images.load(str(file),check_existing=True)
    bs=mat.node_tree.nodes.get('Principled BSDF');tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=image;mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    normal=bpy.data.images.load(str(ROOT/'PlayerReference'/(prefix+'_N.png')),check_existing=True);normal.colorspace_settings.name='Non-Color'
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=normal;nm=mat.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.60;mat.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])

def imported_humanoid(name,family):
    arm=v03_imported(name,family);body,head=parts[:2];hz=bonepos(arm,'head').z;og=family=='Ogre'
    # A pronounced underbite and flattened heavy nasal plane distinguish the ogre.
    for v in head.data.vertices:
        x,y,z=v.co;az=z-hz;front=gauss(y,-.24 if og else -.15,.10 if og else .06)
        if og:
            jaw=gauss(az,.035,.050)*front;v.co.y-=.028*jaw;v.co.x*=1+.10*jaw
            nose=gauss(az,.135,.037)*gauss(x,0,.074)*front;v.co.x*=1+.25*nose
        else:
            jaw=gauss(az,.022,.025)*front;v.co.y-=.008*jaw
    paint_skin_texture(body,family,'Body',arm);paint_skin_texture(head,family,'Head',arm)
    return arm

def scalp_hair(head,arm,name):
    start=len(parts);v03_hair(head,arm,name)
    for o in list(parts[start:]):
        if o.name.startswith(('Swept sculpted hair blade','Tapered nape hair clump')):remove_part(o)
    tree=surface_tree(head);top=max(v.co.z for v in head.data.vertices);hz=bonepos(arm,'head').z
    # Attached broad locks sweep back into a crest, with tapered ends at the nape.
    for layer in range(3):
        count=11 if layer==0 else 9
        for k in range(count):
            x=-.20+.40*k/(count-1);y=-.115+layer*.087
            hit=tree.ray_cast(Vector((x,y,top+.3)),Vector((0,0,-1)))
            if hit[0] is None:continue
            root=hit[0]+hit[1]*.004;rows=[];width=.035+.010*math.sin(k*1.7+layer)**2
            for j in range(21):
                t=j/20;c=root+Vector((x*.18*t,.26*t,.10*math.sin(math.pi*t)-.10*t*t))
                w=width*math.sin(math.pi*(.08+.90*t))**.65+.001;d=.014*math.sin(math.pi*(.10+.89*t))+.001
                rows.append([c+Vector((w*math.cos(a),0,d*math.sin(a))) for a in np.linspace(0,math.tau,13)])
            ribbon('Swept back crested hair lock',rows,'Hair','head',.002)
    # Short pointed temple tufts soften the hairline without a continuous helmet rim.
    for s in [-1,1]:
        for j in range(4):
            x=s*(.20-.013*j);z=hz+.30+.018*j;rows=[]
            for k in range(13):
                t=k/12;w=.024*(1-t)+.001;rows.append([(x+s*.012*t+q*w,-.025+.15*t,z-.12*t+.007*(1-abs(q))) for q in [-1,0,1]])
            ribbon('Tapered temple hair lock',rows,'Hair','head',.002)

def rotate_pose_world(arm,n,axis,angle):
    p=arm.pose.bones[n];q=p.bone.matrix_local.to_quaternion();p.rotation_mode='XYZ';p.rotation_euler=(q.inverted()@Quaternion(Vector(axis),angle)@q).to_euler()

def close_grip(mesh,arm,name):
    if name.startswith('Skeleton'):return
    og=name.startswith('Ogre');scale=1 if og else .49
    gear={vi for p in mesh.data.polygons if 'Skin' not in mesh.data.materials[p.material_index].name and 'Eye' not in mesh.data.materials[p.material_index].name for vi in p.vertices}
    # Both hands have a consistent bind grip, so family skeleton sharing stays valid.
    for side,s in [('r',1),('l',-1)]:
        hand=bonepos(arm,'hand_'+side);center=hand+Vector((-s*.056*scale,-.159*scale,-.221*scale))
        rot=Quaternion(Vector((1,0,0)),s*math.pi/2);gi=mesh.vertex_groups['hand_'+side].index
        for v in mesh.data.vertices:
            if v.index in gear and any(g.group==gi and g.weight>.99 for g in v.groups):v.co=center+rot@(v.co-hand)
        for digit in ['index','middle','ring','pinky']:
            for j,angle in [(1,-.55),(2,-.65),(3,-.45)]:rotate_pose_world(arm,f'{digit}_{j:02}_{side}',(0,1,0),s*angle)
        for j,angle in [(1,.15),(2,.35),(3,.25)]:rotate_pose_world(arm,f'thumb_{j:02}_{side}',(0,1,0),s*angle)
        rotate_pose_world(arm,'hand_'+side,(1,0,0),-s*math.pi/2)
    bpy.context.view_layer.update()
    # Bake the closed grip into the bind state, retaining all deform groups and UVs.
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
    mod=next(m for m in mesh.modifiers if m.type=='ARMATURE');mod.use_deform_preserve_volume=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm;bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
    mod=mesh.modifiers.new('Closed-grip deformation rig','ARMATURE');mod.object=arm
    grip_records.append({'id':name,'bind_hands':'closed around authored handles','rig_bones':len(arm.data.bones)})

def subdivide_skin(mesh,arm):
    if not any('BodySkin' in m.name for m in mesh.data.materials):return
    # Keep armor/hair sharp while adding usable deformation density to creature skin.
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bpy.ops.object.mode_set(mode='OBJECT')
    for p in mesh.data.polygons:p.select='Skin' in mesh.data.materials[p.material_index].name
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
    skin=next(o for o in bpy.context.selected_objects if o.type=='MESH' and o!=mesh)
    for m in list(skin.modifiers):skin.modifiers.remove(m)
    bpy.context.view_layer.objects.active=skin
    m=skin.modifiers.new('Creature skin deformation density','SUBSURF');m.levels=1;m.render_levels=1;bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join()
    return mesh

def merged(name,arm):
    mesh=v03_merge(name,arm);close_grip(mesh,arm,name);subdivide_skin(mesh,arm);return mesh

def export_model(name,family,mesh,arm,actions,folder):
    v03_export(name,family,mesh,arm,actions,folder)

for role in ['Fighter','Knight','Archer','Mage']:skeleton_variant('Skeleton'+role,role)
for role in ['Scout','Fighter','Shaman']:humanoid_variant('Goblin'+role,'Goblin',role)
for role in ['Brute','Champion']:humanoid_variant('Ogre'+role,'Ogre',role)
for _,_,o in lineup:o.hide_render=False;o.hide_set(False)
for family in ['Skeleton','Goblin','Ogre']:
    objects=[o for _,f,o in lineup if f==family];spacing={'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]
    for i,o in enumerate(objects):o.location=(spacing*(i-(len(objects)-1)/2),{'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IV_Monster_Library_v04.blend'))
(OUT/'model_manifest.json').write_text(json.dumps({'status':'geometry_and_exports_complete','models':reports,'unreal_import':'pending','slimes':'unchanged v01','grips':grip_records,'anatomy':anatomy_reports},indent=2))
print('MONSTER_REBUILD_V04_COMPLETE',len(reports))
