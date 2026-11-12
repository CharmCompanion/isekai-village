"""Editable monster model authoring in Blender. Run with Blender --background.

Pack-derived anatomy stays project-local. All new accessories are authored here.
Meshes and animations are versioned; this does not edit existing Unreal maps.
"""
import bpy,math,json,random
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix

ROOT=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters')
OUT=ROOT/'Models_v01';OUT.mkdir(parents=True,exist_ok=True)
FBX=OUT/'FBX';FBX.mkdir(exist_ok=True)
TEX=OUT/'Textures';TEX.mkdir(exist_ok=True)
random.seed(739)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.fps=24

specs=[
 ('Bone',(0.79,.70,.50),.61,0),('Leather',(.18,.075,.033),.72,0),('Wood',(.27,.13,.055),.75,0),('Steel',(.28,.32,.36),.35,.8),('Gold',(.70,.39,.10),.29,.75),
 ('ClothRed',(.38,.065,.055),.84,0),('ClothBlue',(.065,.17,.30),.82,0),('ClothPurple',(.18,.07,.31),.82,0),('ClothTeal',(.045,.22,.23),.8,0),('ClothOlive',(.16,.19,.07),.88,0),
 ('GoblinSkin',(.29,.44,.12),.53,0),('OgreSkin',(.38,.40,.23),.58,0),('EyeDark',(.012,.025,.025),.12,0),('EyeWhite',(.94,.96,.89),.18,0),('EyeAmber',(.84,.44,.03),.20,0),('Rune',(.02,.65,.86),.22,0),
 ('MeadowGel',(.16,.58,.015),.17,0),('WaterGel',(.035,.37,.85),.12,0),('FlameGel',(.95,.14,.018),.18,0),('FrostGel',(.23,.68,.9),.19,0),('PoisonGel',(.33,.025,.62),.18,0),('CrystalGel',(.03,.60,.59),.13,0),
 ('Leaf',(.17,.36,.025),.59,0),('Ice',(.37,.77,.95),.15,.15),('Crystal',(.045,.67,.71),.17,.20),('Flame',(.95,.36,.015),.25,0),('PoisonCore',(.69,.06,.78),.23,0),('WaterCore',(.33,.74,.95),.18,.15),('Mouth',(.18,.018,.018),.48,0),('Hair',(.07,.045,.025),.75,0),('Linen',(.54,.43,.27),.88,0),('Rock',(.26,.25,.23),.74,0)
]
palette={s[0]:i for i,s in enumerate(specs)}
materials={};tex_images={}
width,height=2048,1024
yy,xx=np.mgrid[0:height,0:width];cellx=(xx%256)/255;celly=(yy%256)/255
grain=np.random.default_rng(39).normal(0,.008,(height,width))
rgba=np.ones((height,width,4),np.float32);rough=np.ones((height,width,4),np.float32)
for i,(name,color,r,m) in enumerate(specs):
    mask=(xx//256==i%8)&(yy//256==i//8)
    shade=.84+.16*celly+grain
    if name in ['Wood','Leather','Bone','Rock','Linen']:
        shade+=.024*np.sin(cellx*145+np.sin(celly*31)*2)
    for ch in range(3):rgba[:,:,ch][mask]=np.clip(color[ch]*shade[mask],0,1);rough[:,:,ch][mask]=r
for name,data in [('T_IV_MonsterPalette_v01',rgba),('T_IV_MonsterRoughness_v01',rough)]:
    img=bpy.data.images.new(name,width,height,alpha=True);img.pixels.foreach_set(data.ravel());img.filepath_raw=str(TEX/(name+'.png'));img.file_format='PNG';img.save();tex_images[name]=img
for i,(name,color,r,metal) in enumerate(specs):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=r;bs.inputs['Metallic'].default_value=metal
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=tex_images['T_IV_MonsterPalette_v01'];mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    if 'Gel' in name:
        bs.inputs['Transmission Weight'].default_value=.38;bs.inputs['IOR'].default_value=1.36;bs.inputs['Subsurface Weight'].default_value=.08;bs.inputs['Alpha'].default_value=.78
    if name in ['Rune','Flame','PoisonCore']:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=1.5
    materials[name]=mat

parts=[];current='';rig=None
def finish(o,mat,bone=None):
    global parts
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.clear();o.data.materials.append(materials[mat])
    for p in o.data.polygons:p.use_smooth=True
    if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
    uv=o.data.uv_layers.active.data;box=[o.matrix_world@v.co for v in o.data.vertices]
    i=palette[mat];cx=i%8;cy=i//8
    for p in o.data.polygons:
        for li in p.loop_indices:
            v=box[o.data.loops[li].vertex_index]
            # Repeating painted palette tile, with padding to prevent color bleed.
            u=(v.x*1.73+v.y*.41)%1;w=(v.z*.71)%1
            uv[li].uv=((cx+.10+.80*u)/8,(cy+.10+.80*w)/4)
    if bone:
        vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
    parts.append(o);return o

def ell(name,pos,scale,mat,bone=None,segments=24,rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=pos)
    o=bpy.context.object;o.name=name;o.scale=scale;return finish(o,mat,bone)

def block(name,pos,scale,mat,bone=None,bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Rounded crafted edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,mat,bone)

def tube(name,coords,radii,mat,bone=None,sides=12):
    coords=[Vector(p) for p in coords];verts=[];faces=[]
    if isinstance(radii,(float,int)):radii=[radii]*len(coords)
    for j,p in enumerate(coords):
        tangent=(coords[min(j+1,len(coords)-1)]-coords[max(0,j-1)]).normalized()
        v=tangent.cross(Vector((0,1,0)))
        if v.length<.1:v=tangent.cross(Vector((1,0,0)))
        v.normalize();w=tangent.cross(v).normalized()
        for k in range(sides):verts.append(p+radii[j]*(math.cos(k*2*math.pi/sides)*v+math.sin(k*2*math.pi/sides)*w))
    for j in range(len(coords)-1):
        for k in range(sides):a=j*sides+k;b=j*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(reversed(range(sides))));faces.append(tuple(range((len(coords)-1)*sides,len(coords)*sides)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,mat,bone)

def ribbon(name,rows,mat,bone=None,thickness=.012):
    verts=[v for row in rows for v in row];n=len(rows[0]);faces=[]
    for j in range(len(rows)-1):
        for k in range(n-1):a=j*n+k;faces.append((a,a+1,a+1+n,a+n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    mod=o.modifiers.new('Fabric thickness','SOLIDIFY');mod.thickness=thickness;bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,mat,bone)

def crystal(name,pos,size,mat,bone,lean=0):
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=size*.23,radius2=size*.15,depth=size*.70,location=(pos[0],pos[1],pos[2]+size*.35));o=bpy.context.object;o.rotation_euler[1]=lean;finish(o,mat,bone)
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=size*.15,radius2=0,depth=size*.30,location=(pos[0]+math.sin(lean)*size*.65,pos[1],pos[2]+size*.85));o=bpy.context.object;o.rotation_euler[1]=lean;finish(o,mat,bone)

def make_rig(name,bones):
    bpy.ops.object.armature_add();arm=bpy.context.object;arm.name=name;arm.data.name=name
    bpy.ops.object.mode_set(mode='EDIT');arm.data.edit_bones.remove(arm.data.edit_bones[0]);made={}
    for n,h,t,parent in bones:
        b=arm.data.edit_bones.new(n);b.head=h;b.tail=t
        if parent:b.parent=made[parent]
        made[n]=b
    bpy.ops.object.mode_set(mode='OBJECT');return arm

def nearest_weights(o,arm):
    bones=[b for b in arm.data.bones if b.name!='root' and not any(x in b.name.lower() for x in ['ik_','twist','weapon'])]
    groups={b.name:o.vertex_groups.get(b.name) or o.vertex_groups.new(name=b.name) for b in bones}
    for v in o.data.vertices:
        p=o.matrix_world@v.co;dist=[]
        for b in bones:
            a=arm.matrix_world@b.head_local;c=arm.matrix_world@b.tail_local;d=c-a;t=max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-9)));dist.append(((p-(a+d*t)).length,b.name))
        ds=sorted(dist)[:2];ww=[1/(d+.008)**4 for d,_ in ds];total=sum(ww)
        for (_,n),w in zip(ds,ww):groups[n].add([v.index],w/total,'REPLACE')

def merged(name,arm):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        for mod in list(o.modifiers):
            if mod.type=='ARMATURE':o.modifiers.remove(mod)
        if not len(o.vertex_groups):nearest_weights(o,arm)
        o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SK_'+name
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    mod=o.modifiers.new('Deformation rig','ARMATURE');mod.object=arm;o.parent=arm;o.matrix_parent_inverse=Matrix.Identity(4)
    return o

def bonepos(arm,n,tail=False):
    b=arm.data.bones[n];return arm.matrix_world@(b.tail_local if tail else b.head_local)

def material_record(o):
    return [{'slot':i,'name':m.name,'palette_index':palette.get(m.name),'roughness':specs[palette[m.name]][2] if m.name in palette else .25,'metallic':specs[palette[m.name]][3] if m.name in palette else 0} for i,m in enumerate(o.data.materials)]

def set_pose_zero(arm):
    for pb in arm.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)

def animate(arm,name,family):
    actions=[]
    for kind,frames in [('Idle',48),('Move',32),('Attack',32),('Hit',20),('Death',36)]:
        arm.animation_data_create();arm.animation_data.action=bpy.data.actions.new('AN_'+name+'_'+kind)
        action=arm.animation_data.action
        action.use_fake_user=True
        for f in range(1,frames+1):
            set_pose_zero(arm);t=(f-1)/(frames-1);wave=math.sin(t*2*math.pi)
            if family=='Slime':
                b=arm.pose.bones['gel']
                if kind=='Idle':b.scale=(1+.04*wave,1+.04*wave,1-.05*wave)
                elif kind=='Move':b.scale=(1+.12*wave,1+.12*wave,1-.15*wave);b.location.z=.035*max(0,-wave)
                elif kind=='Attack':s=math.sin(t*math.pi);b.scale=(1-.17*s,1+.25*s,1+.35*s);b.location.y=-.12*s
                elif kind=='Hit':s=math.sin(t*math.pi)*(1-t);b.scale=(1+.22*s,1+.22*s,1-.35*s)
                else:b.scale=(1+.48*t,1+.48*t,max(.08,1-.92*t))
                names=['gel']
            else:
                names=[n for n in ['root','pelvis','spine_01','spine_02','spine_03','spine_04','spine_05','head','upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r'] if n in arm.pose.bones]
                def rotate(n,axis,value):
                    if n in arm.pose.bones:
                        pb=arm.pose.bones[n];orient=pb.bone.matrix_local.to_quaternion();ax=Vector((int(axis==0),int(axis==1),int(axis==2)))
                        pb.rotation_euler=(orient.inverted()@Quaternion(ax,value)@orient).to_euler()
                if kind=='Idle':rotate('spine_02',0,.02*wave);rotate('head',2,.04*wave)
                elif kind=='Move':
                    for side,sign in [('l',1),('r',-1)]:rotate('thigh_'+side,0,.36*wave*sign);rotate('calf_'+side,0,-.50*max(0,wave*sign));rotate('upperarm_'+side,0,-.24*wave*sign)
                    if 'pelvis' in arm.pose.bones:
                        pb=arm.pose.bones['pelvis'];pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,.014*(1-math.cos(t*4*math.pi))))
                elif kind=='Attack':s=math.sin(t*math.pi);rotate('upperarm_r',0,-1.15*s);rotate('lowerarm_r',0,-.45*s);rotate('spine_02',2,-.30*s)
                elif kind=='Hit':s=math.sin(t*math.pi)*(1-t);rotate('spine_01',0,-.30*s);rotate('head',0,.20*s)
                else:
                    s=t*t*(3-2*t);rotate('root',0,-1.55*s);rotate('spine_01',0,.10*s)
                    if 'root' in arm.pose.bones:
                        pb=arm.pose.bones['root'];pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,(.30 if family=='Ogre' else .15)*s))
            for n in names:
                pb=arm.pose.bones[n]
                for prop in ['location','rotation_euler','scale']:pb.keyframe_insert(data_path=prop,frame=f,group=n)
        actions.append((kind,action,frames))
    arm.animation_data.action=None;set_pose_zero(arm);scene.frame_set(1);return actions

reports=[];lineup=[]
def export_model(name,family,mesh,arm,actions,folder):
    folder.mkdir(exist_ok=True);bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm
    scene.frame_set(1);arm.animation_data.action=None;set_pose_zero(arm)
    common=dict(use_selection=True,add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,use_armature_deform_only=False,mesh_smooth_type='FACE')
    bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),bake_anim=False,**common)
    for kind,action,frames in actions:
        arm.animation_data.action=action;scene.frame_start=1;scene.frame_end=frames
        bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
        bpy.ops.export_scene.fbx(filepath=str(folder/('AN_'+name+'_'+kind+'.fbx')),bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,**common)
    arm.animation_data.action=None;set_pose_zero(arm);scene.frame_set(1)
    for image in list(bpy.data.images):
        if image.source=='FILE' and image.filepath and not Path(bpy.path.abspath(image.filepath)).exists() and not image.packed_file:bpy.data.images.remove(image)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    triangles=sum(len(p.vertices)-2 for p in mesh.data.polygons)
    unweighted=sum(not v.groups or sum(g.weight for g in v.groups)<.999 for v in mesh.data.vertices)
    report={'id':name,'family':family,'mesh':mesh.name,'vertices':len(mesh.data.vertices),'triangles':triangles,'bones':len(arm.data.bones),'unweighted_vertices':unweighted,'materials':material_record(mesh),'animations':[x[0] for x in actions],'fbx':str(folder/(name+'.fbx')),'blend':str(OUT/(name+'.blend'))}
    assert unweighted==0,report
    reports.append(report);(OUT/'model_manifest.json').write_text(json.dumps({'status':'building','models':reports},indent=2))
    # Keep a duplicate posed at rest for the final comparison gallery.
    copy=mesh.copy();copy.data=mesh.data.copy();bpy.context.collection.objects.link(copy);copy.parent=None
    for m in list(copy.modifiers):copy.modifiers.remove(m)
    copy.hide_render=True;copy.hide_set(True);lineup.append((name,family,copy))
    bpy.data.objects.remove(mesh,do_unlink=True);bpy.data.objects.remove(arm,do_unlink=True)

def make_slime(name,gel):
    global parts
    parts=[];h=.58 if name!='CrystalSlime' else .63
    verts=[(0,0,.008)];faces=[];nr,ns=32,64
    for j in range(1,nr):
        th=math.pi*j/nr;z=h*(1-math.cos(th))/2;rad=.36*math.sin(th)**.80*(1.15+.22*math.cos(th))
        for k in range(ns):
            a=k*math.tau/ns;r=rad*(1+.025*math.sin(3*a+j*.15));verts.append((r*math.cos(a)+.035*(z/h)**3,r*math.sin(a),z))
    top=len(verts);verts.append((.035,0,h))
    for k in range(ns):faces.append((0,1+(k+1)%ns,1+k))
    for j in range(nr-2):
        for k in range(ns):a=1+j*ns+k;b=1+j*ns+(k+1)%ns;faces.append((a,b,b+ns,a+ns))
    for k in range(ns):faces.append((top,1+(nr-2)*ns+k,1+(nr-2)*ns+(k+1)%ns))
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();body=bpy.data.objects.new('Gel body',data);bpy.context.collection.objects.link(body);finish(body,gel,'gel')
    for x in [-.13,.13]:
        ell('Expressive eye',(x,-.422,.31),(.045,.023,.060),'EyeDark','gel')
        ell('Eye catchlight',(x-.012,-.447,.333),(.010,.005,.014),'EyeWhite','gel',16,12)
    tube('Smile',[(-.054,-.433,.215),(0,-.440,.192),(.054,-.433,.215)],.010,'Mouth','gel')
    core={'MeadowSlime':'Leaf','WaterSlime':'WaterCore','FlameSlime':'Flame','FrostSlime':'Ice','PoisonSlime':'PoisonCore','CrystalSlime':'Crystal'}[name]
    ell('Inner core',(0,-.02,.20),(.095,.095,.095),core,'gel')
    if name=='MeadowSlime':
        tube('Bud stem',[(.035,0,h-.02),(.03,0,h+.13)],.012,'Leaf','gel')
        for sign in [-1,1]:
            rows=[]
            for j in range(9):t=j/8;w=.065*math.sin(t*math.pi);rows.append([(sign*(.03+.14*t),-w,h+.09+.15*t), (sign*(.03+.14*t),0,h+.09+.15*t+.018),(sign*(.03+.14*t),w,h+.09+.15*t)])
            ribbon('Leaf blade',rows,'Leaf','gel',.004)
    elif name in ['FrostSlime','CrystalSlime']:
        for i in range(7):a=i*math.tau/7;crystal('Crown crystal',(.16*math.cos(a),.13*math.sin(a),h*.82),.12+(.16 if i==3 else .03),core,'gel',.10*math.cos(a))
    elif name in ['WaterSlime','FlameSlime','PoisonSlime']:
        coords=[(.035,0,h-.02),(.06,0,h+.09),(.13,0,h+.18),(.21,0,h+.17),(.24,0,h+.12)]
        points=[Vector(v) for v in coords];radii=[.065,.055,.036,.022,.007];smooth=[];rs=[]
        for j in range(4):
            p0=points[max(0,j-1)];p1=points[j];p2=points[j+1];p3=points[min(4,j+2)]
            for step in range(6):
                t=step/6;smooth.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t));rs.append(radii[j]*(1-t)+radii[j+1]*t)
        smooth.append(points[-1]);rs.append(radii[-1]);tube('Element crest',smooth,rs,gel,'gel',24)
        if name=='FlameSlime':
            tube('Secondary flame',[(-.14,0,h*.75),(-.18,0,h+.01),(-.12,0,h+.10)],[.045,.02,.002],'Flame','gel')
        if name=='PoisonSlime':ell('Hanging drop',(.24,0,h+.10),(.023,.025,.038),gel,'gel')
    arm=make_rig('Armature',[('root',(0,0,0),(0,.1,0),None),('gel',(0,0,0),(0,.75,0),'root')])
    mesh=merged(name,arm);actions=animate(arm,name,'Slime');export_model(name,'Slime',mesh,arm,actions,FBX/name)

# Family builders are below; helper functions intentionally remain reusable.

def imported_humanoid(name,family):
    global parts
    parts=[];before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'PlayerReference/SKM_BodyA.fbx'))
    bodyobjs=[o for o in bpy.data.objects if o not in before];arm=next(o for o in bodyobjs if o.type=='ARMATURE');body=next(o for o in bodyobjs if o.type=='MESH')
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/'PlayerReference/SKM_HeadA_01.fbx'))
    headobjs=[o for o in bpy.data.objects if o not in before];head=next(o for o in headobjs if o.type=='MESH')
    for o in headobjs:
        if o.type=='ARMATURE':
            head.parent=None
            for m in list(head.modifiers):
                if m.type=='ARMATURE':head.modifiers.remove(m)
            bpy.data.objects.remove(o,do_unlink=True)
    # Unreal FBX stores the rig's axis conversion on the armature object.
    # Bake that basis before applying any world-space anatomical warp.
    for o in [body,head]:
        mw=o.matrix_world.copy();o.parent=None;o.matrix_world=mw
        for mod in list(o.modifiers):
            if mod.type=='ARMATURE':o.modifiers.remove(mod)
    bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
    source_rig_matrix=arm.matrix_world.copy()
    arm.delta_scale=(1,1,1);arm.delta_location=(0,0,0);arm.delta_rotation_euler=(0,0,0);arm.matrix_world=Matrix.Identity(4)
    def warp(p):
        x,y,z=p
        if family=='Goblin':
            nz=float(np.interp(z,[0,.54,1.03,1.48,1.56,1.84],[0,.29,.64,.96,1.015,1.27]))
            t=float(np.clip((z-1.50)/.08,0,1));t=t*t*(3-2*t)
            factor=.85+.43*t
            return Vector((x*factor,y*(.88+.32*t),nz))
        nz=float(np.interp(z,[0,.54,1.03,1.48,1.56,1.84],[0,.68,1.55,2.26,2.42,2.96]))
        t=float(np.clip((z-1.50)/.10,0,1));t=t*t*(3-2*t)
        factor=2.25-.25*t
        return Vector((x*factor,y*(1.85-.20*t),nz))
    skin='GoblinSkin' if family=='Goblin' else 'OgreSkin'
    # Preserve the actual player's anatomical topology and skin weights.
    for o in [body,head]:
        mw=o.matrix_world.copy();o.parent=None
        for v in o.data.vertices:v.co=warp(mw@v.co)
        o.delta_scale=(1,1,1);o.delta_location=(0,0,0);o.delta_rotation_euler=(0,0,0);o.matrix_world=Matrix.Identity(4)
        old_indices=[p.material_index for p in o.data.polygons]
        o.data.materials.clear();o.data.materials.append(materials[skin])
        eye=bpy.data.materials.get('EyeExisting')
        if not eye:
            eye=bpy.data.materials.new('EyeExisting');eye.diffuse_color=(.85,.78,.43,1);eye.use_nodes=True
            texfile=ROOT/'PlayerReference/T_Eye_01_Grayscale.png'
            if texfile.exists():
                tx=eye.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(texfile));eye.node_tree.links.new(tx.outputs['Color'],eye.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
        if o==head:o.data.materials.append(eye)
        active_uv=o.data.uv_layers.active
        for layer in list(o.data.uv_layers):
            if layer!=active_uv:o.data.uv_layers.remove(layer)
        active_uv.name='UVMap'
        uv=active_uv.data;idx=palette[skin]
        for p,old in zip(o.data.polygons,old_indices):
            iseye=o==head and old==0;p.material_index=1 if iseye else 0;p.use_smooth=True
            if not iseye:
                for li in p.loop_indices:
                    u,v=uv[li].uv;uv[li].uv=((idx%8+.1+.8*(u%1))/8,(idx//8+.1+.8*(v%1))/4)
        parts.append(o)
    arm.name='Armature';arm.data.name='RIG_'+name
    bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for b in arm.data.edit_bones:
        h=source_rig_matrix@b.head;t=source_rig_matrix@b.tail
        b.head=warp(h);b.tail=warp(t)
    if 'root' not in arm.data.edit_bones:
        root=arm.data.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.05)
        for b in arm.data.edit_bones:
            if b!=root and b.parent is None:b.parent=root
    bpy.ops.object.mode_set(mode='OBJECT')
    # Extend the ears with shaped tapered skin forms, keeping the head attachment.
    hp=bonepos(arm,'head');scale=.095 if family=='Goblin' else .15
    for s in [-1,1]:
        x=s*(.090 if family=='Goblin' else .180);z=hp.z+.06
        rows=[]
        for t,w in [(0,.46),(.23,.66),(.65,.30),(1,.012)]:
            ex=x+s*scale*1.75*t;ez=z+.06*t
            rows.append([(ex,.008,ez-scale*w),(ex,-.020,ez),(ex,.008,ez+scale*w)])
        ribbon('Pointed ear membrane',rows,skin,'head',.009)
        tube('Ear inner fold',[(x,-.018,z+.008),(x+s*scale*.9,-.005,z+.023),(x+s*scale*1.45,.010,z+.04)],[scale*.08,scale*.055,.001],skin,'head',10)
        if family=='Ogre':
            tube('Lower tusk',[(s*.090,-.190,hp.z-.09),(s*.098,-.205,hp.z-.015),(s*.083,-.212,hp.z+.02)],[.025,.014,.001],'Bone','head')
    if family=='Ogre':
        for i in range(11):
            a=i*math.tau/11;crystal('Rough hair',(.15*math.cos(a),.025+.12*math.sin(a),hp.z+.39),.14,'Hair','head',math.cos(a)*.4)
    return arm

def belt_and_skirt(arm,family,color):
    pelvis=bonepos(arm,'pelvis');ogre=family=='Ogre';sx=.48 if ogre else .18;sy=.285 if ogre else .13
    rows=[]
    for j in range(2):
        row=[]
        for k in range(33):a=k*math.tau/32;row.append((sx*math.cos(a),sy*math.sin(a),pelvis.z+(.04 if j else -.075)))
        rows.append(row)
    ribbon('Layered waist belt',rows,'Leather','pelvis',.018)
    block('Belt buckle',(0,-sy-.016,pelvis.z-.015),(.085 if ogre else .055,.022,.058 if ogre else .040),'Steel','pelvis')
    rows=[]
    for j in range(4):
        row=[];t=j/3
        for k in range(33):
            a=k*math.tau/32;radius=1+.22*t;z=pelvis.z-.07-(.38 if ogre else .25)*t+.024*math.sin(k*2.1)*t
            row.append((sx*radius*math.cos(a),sy*radius*math.sin(a),z))
        rows.append(row)
    ribbon('Layered ragged waistcloth',rows,color,'pelvis',.009)
    for s in [-1,1]:block('Supply pouch',(s*sx*.82,-sy*.80,pelvis.z-.03),(.10 if ogre else .055,.055,.09 if ogre else .06),'Leather','pelvis')

def sword(arm,side='r',heavy=False):
    p=bonepos(arm,'hand_'+side);p.y-=.015;L=min(.60,p.z-.28) if not heavy else 1.0;w=.045 if p.z<1 else .06
    tube('Sword grip',[p,p+Vector((0,0,-.14))],.018 if not heavy else .038,'Leather','hand_'+side)
    block('Sword guard',p+Vector((0,0,-.16)),(.19 if not heavy else .33,.025,.025),'Steel','hand_'+side)
    rows=[]
    for t in [0,.90,1]:
        width=w*(1 if t<1 else .03);z=p.z-.18-L*t
        rows.append([(p.x-width,p.y,z),(p.x,p.y-.022,z),(p.x+width,p.y,z)])
    ribbon('Forged sword blade',rows,'Steel','hand_'+side,.008)

def bow(arm):
    p=bonepos(arm,'hand_l');h=.48 if p.z<1 else .65
    coords=[p+Vector((.07*math.sin(i*math.pi/16),0,h*(i/16-.5))) for i in range(17)]
    tube('Recurve bow',coords,[.010+.010*math.sin(i*math.pi/16) for i in range(17)],'Wood','hand_l')
    tube('Bow string',[coords[0],p+Vector((-.045,0,0)),coords[-1]],.0025,'Linen','hand_l',6)
    chest=bonepos(arm,'spine_04')
    tube('Leather quiver',[chest+Vector((.09,.15,-.14)),chest+Vector((.09,.18,.17))],.052,'Leather','spine_04')
    for i in range(5):
        end=chest+Vector((.06+i*.013,.18,.25));tube('Arrow shaft',[end-Vector((0,0,.28)),end],.004,'Wood','spine_04',6)
        block('Arrow fletching',end,(.018,.008,.037),'Linen','spine_04',.002)

def staff(arm,side='l',scale=1):
    p=bonepos(arm,'hand_'+side);h=max(1.5,p.z+scale*.65)
    tube('Carved staff',[(p.x,p.y,.08),(p.x-.018,p.y,p.z),(p.x+.025,p.y,h)],[.025*scale,.022*scale,.018*scale],'Wood','hand_'+side)
    crystal('Runic stone',(p.x+.025,p.y,h-.03),.15*scale,'Rune','hand_'+side)
    for s in [-1,1]:tube('Staff crown',[(p.x,p.y,h-.12),(p.x+s*.085*scale,p.y,h),(p.x+s*.07*scale,p.y,h+.12)],[.025,.020,.002],'Wood','hand_'+side)

def shield(arm):
    p=bonepos(arm,'lowerarm_l');q=bonepos(arm,'hand_l');c=(p+q)/2;c.y-=.095
    sz=.20 if c.z<1 else .30
    o=ell('Wooden shield',c,(sz,.045,sz*1.30),'Wood','lowerarm_l',32,16)
    coords=[c+Vector((sz*math.cos(a),-.044,sz*1.3*math.sin(a))) for a in np.linspace(0,math.tau,65)]
    tube('Shield iron rim',coords,.012,'Steel','lowerarm_l')
    ell('Shield boss',c+Vector((0,-.047,0)),(.065,.035,.065),'Steel','lowerarm_l')
    for a in np.linspace(0,math.tau,12,endpoint=False):ell('Shield rivet',c+Vector((sz*.89*math.cos(a),-.043,sz*1.16*math.sin(a))),(.007,.005,.007),'Steel','lowerarm_l',12,8)

def cape(arm,color,length=.6):
    shoulder=bonepos(arm,'spine_05');w=.46 if shoulder.z>1.5 else .18
    rows=[]
    for j in range(12):
        t=j/11;row=[]
        for k in range(17):
            u=k/16;x=(u-.5)*2*w*(1+.2*t);y=.12+.03*math.cos(u*8*math.pi)+.08*t;z=shoulder.z+.015-length*t+.022*math.sin(k*1.8)*t
            row.append((x,y,z))
        rows.append(row)
    ribbon('Draped cape',rows,color,'spine_04',.012)

def pauldron(arm,side='r',scale=1):
    p=bonepos(arm,'upperarm_'+side)
    o=ell('Forged shoulder armor',p+Vector((0,0,.028*scale)),(.105*scale,.115*scale,.067*scale),'Steel','upperarm_'+side)
    for j in [-1,0,1]:ell('Armor rivet',p+Vector((j*.054*scale,-.108*scale,.018*scale)),(.007*scale,.005*scale,.007*scale),'Gold','upperarm_'+side,12,8)

def bracers(arm,scale):
    for side in ['l','r']:
        a=bonepos(arm,'lowerarm_'+side);b=bonepos(arm,'hand_'+side);p=a.lerp(b,.65)
        tube('Leather bracer',[a.lerp(b,.42),a.lerp(b,.90)],[.047*scale,.038*scale],'Leather','lowerarm_'+side,16)
        for t in [.44,.83]:
            v=a.lerp(b,t);ell('Bracer binding',v,(.047*scale,.045*scale,.017*scale),'Linen','lowerarm_'+side)

def bootwraps(arm,scale):
    for side in ['l','r']:
        p=bonepos(arm,'foot_'+side);z=p.z
        tube('Wrapped boot',[(p.x,p.y,z+.025*scale),(p.x,p.y,z+.15*scale)],[.063*scale,.069*scale],'Leather','calf_'+side,20)
        for i in range(3):
            coords=[(p.x+.072*scale*math.cos(a),p.y+.067*scale*math.sin(a),z+(.05+i*.038)*scale+.009*scale*math.sin(a)) for a in np.linspace(0,math.tau,33)]
            tube('Boot tie',coords,.007*scale,'Linen','calf_'+side,8)

def ogre_club(arm,champion):
    p=bonepos(arm,'hand_r');tip=p+Vector((0,-.07,-1.1))
    tube('Heavy weapon handle',[p+Vector((0,0,.15)),tip],[.045,.04],'Wood','hand_r')
    if champion:
        block('Stone maul head',tip,(.66,.35,.37),'Rock','hand_r',.065)
        for x in [-.20,.20]:block('Maul binding',tip+Vector((x,0,0)),(.055,.37,.39),'Steel','hand_r',.01)
    else:
        tube('Tree-trunk club',[tip-Vector((0,0,.15)),tip+Vector((.07,0,.30))],[.20,.14],'Wood','hand_r',16)
        for k in range(7):a=k*math.tau/7;tube('Bark ridge',[tip+Vector((.19*math.cos(a),.19*math.sin(a),-.10)),tip+Vector((.13*math.cos(a)+.06,.13*math.sin(a),.25))],.012,'Leather','hand_r',8)

def humanoid_variant(name,family,role):
    arm=imported_humanoid(name,family);ogre=family=='Ogre';scale=2.4 if ogre else .95
    belt_and_skirt(arm,family,'ClothRed' if role in ['Fighter','Champion'] else 'Linen');bracers(arm,scale);bootwraps(arm,scale)
    if role in ['Fighter','Champion']:pauldron(arm,'r',scale*1.2)
    if family=='Goblin':
        if role=='Scout':bow(arm);sword(arm);cape(arm,'ClothOlive',.40)
        elif role=='Fighter':sword(arm);shield(arm)
        else:staff(arm,scale=.75);cape(arm,'ClothTeal',.63)
    else:
        ogre_club(arm,role=='Champion')
        if role=='Champion':
            chest=bonepos(arm,'spine_04');ell('Iron breastplate',chest+Vector((0,-.22,.12)),(.42,.075,.33),'Steel','spine_04');pauldron(arm,'l',scale*1.2);cape(arm,'ClothRed',.92)
    mesh=merged(name,arm);actions=animate(arm,name,family);export_model(name,family,mesh,arm,actions,FBX/name)

def skeleton_rig(name):
    bones=[('root',(0,0,0),(0,0,.08),None),('pelvis',(0,0,.98),(0,0,1.06),'root'),('spine_01',(0,0,1.06),(0,0,1.15),'pelvis'),('spine_02',(0,0,1.15),(0,0,1.24),'spine_01'),('spine_03',(0,0,1.24),(0,0,1.34),'spine_02'),('spine_04',(0,0,1.34),(0,0,1.44),'spine_03'),('spine_05',(0,0,1.44),(0,0,1.52),'spine_04'),('neck_01',(0,0,1.52),(0,0,1.63),'spine_05'),('head',(0,0,1.63),(0,0,1.80),'neck_01')]
    for side,s in [('l',1),('r',-1)]:
        bones.extend([('upperarm_'+side,(s*.21,.02,1.46),(s*.36,.055,1.23),'spine_05'),('lowerarm_'+side,(s*.36,.055,1.23),(s*.49,-.06,1.07),'upperarm_'+side),('hand_'+side,(s*.49,-.06,1.07),(s*.53,-.08,.98),'lowerarm_'+side),('thigh_'+side,(s*.11,0,.96),(s*.13,0,.50),'pelvis'),('calf_'+side,(s*.13,0,.50),(s*.14,.02,.10),'thigh_'+side),('foot_'+side,(s*.14,.02,.10),(s*.14,-.15,.04),'calf_'+side)])
    return make_rig('Armature',bones)

def modeled_bone(name,a,b,r,group):
    a=Vector(a);b=Vector(b);d=b-a
    small=d.length<.065
    tube(name,[a,a+d*.12,a+d*.35,a+d*.65,a+d*.88,b],[r*1.28,r,r*.70,r*.68,r,r*1.25],'Bone',group,8 if small else 12)
    for p in [a,b]:ell('Joint condyle',p,(r*1.34,r*1.05,r*1.15),'Bone',group,10 if small else 16,6 if small else 10)

def skull():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=28,location=(0,.018,1.675));o=bpy.context.object;o.name='Sculpted skull vault';o.scale=(.132,.122,.162)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for x in [-.058,.058,0]:
        pos=(x,-.094,1.690 if x else 1.632);sc=(.048,.065,.045) if x else (.022,.06,.027)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=pos);cut=bpy.context.object;cut.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Carved orbital cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    finish(o,'Bone','head')
    for s in [-1,1]:
        ell('Soul light',(s*.058,-.099,1.685),(.018,.018,.018),'Rune','head',20,12)
        modeled_bone('Cheek arch',(s*.092,-.041,1.625),(s*.065,-.112,1.601),.015,'head')
    coords=[(-.10,.025,1.61),(-.096,-.055,1.548),(-.06,-.108,1.523),(0,-.116,1.515),(.06,-.108,1.523),(.096,-.055,1.548),(.10,.025,1.61)]
    tube('Mandible',coords,[.016,.016,.018,.021,.018,.016,.016],'Bone','head',16)
    for upper,z in [(True,1.578),(False,1.546)]:
        for k in range(10):
            t=(k-4.5)/4.5;x=t*.070;y=-.113+.045*t*t
            block('Individual tooth',(x,y,z),(.011,.014,.017),'Bone','head',.003)

def hood(arm,color):
    center=bonepos(arm,'head')+Vector((0,.015,.035));verts=[];faces=[];N,K=32,16
    for j in range(K+1):
        th=.025+(math.pi*.77-.025)*j/K
        for k in range(N):a=k*math.tau/N;verts.append(center+Vector((.178*math.sin(th)*math.cos(a),.158*math.sin(th)*math.sin(a),.20*math.cos(th))))
    for j in range(K):
        for k in range(N):
            a=k*math.tau/N
            if j>5 and math.sin(a)<-.48:continue
            v=j*N+k;w=j*N+(k+1)%N;faces.append((v,w,w+N,v+N))
    data=bpy.data.meshes.new('Open hood');data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new('Open-faced hood',data);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
    mod=o.modifiers.new('Rolled hood thickness','SOLIDIFY');mod.thickness=.012;bpy.ops.object.modifier_apply(modifier=mod.name);finish(o,color,'head')

def skeleton_variant(name,role):
    global parts
    parts=[];arm=skeleton_rig(name);skull()
    # Paired anatomical ribs sweep from the spine into the sternum.
    for i in range(7):
        z=1.425-i*.040;width=.13+.035*math.sin(i*math.pi/7)
        for s in [-1,1]:
            points=[(0,.068,z),(s*width*.65,.05,z+.006),(s*width,-.018,z-.018),(s*width*.83,-.09,z-.035),(s*.027,-.115,z-.038)]
            tube('Curved rib',points,.0105,'Bone','spine_04',12)
    modeled_bone('Sternum',(0,-.12,1.405),(0,-.115,1.17),.013,'spine_04')
    for i in range(17):
        z=.98+i*.038;g='neck_01' if z>1.50 else 'spine_04' if z>1.27 else 'spine_02' if z>1.12 else 'spine_01'
        ell('Vertebra',(0,.064,z),(.026,.025,.021),'Bone',g,16,10)
        tube('Vertebral process',[(0,.075,z),(0,.106,z-.010)],[.014,.005],'Bone',g,8)
    for s in [-1,1]:
        side='l' if s>0 else 'r'
        modeled_bone('Clavicle',(s*.018,-.020,1.465),(s*.205,.020,1.460),.014,'spine_05')
        ell('Scapula',(s*.10,.09,1.36),(.055,.016,.090),'Bone','spine_04')
        # Pelvic wings and pubic arch stay open and anatomically readable.
        tube('Pelvic wing',[(s*.025,.030,1.02),(s*.110,.010,1.055),(s*.15,-.025,1.00),(s*.115,-.050,.935),(s*.032,-.060,.928)],[.018,.035,.032,.018,.013],'Bone','pelvis',16)
        coords=[(s*.07+.048*math.cos(a),-.026,.915+.057*math.sin(a)) for a in np.linspace(0,math.tau,33)]
        tube('Pelvic opening',coords,.012,'Bone','pelvis')
        modeled_bone('Humerus',bonepos(arm,'upperarm_'+side),bonepos(arm,'lowerarm_'+side),.022,'upperarm_'+side)
        a=bonepos(arm,'lowerarm_'+side);b=bonepos(arm,'hand_'+side)
        for shift in [-.012,.012]:modeled_bone('Radius or ulna',a+Vector((shift,0,0)),b+Vector((shift,0,0)),.010,'lowerarm_'+side)
        hand=b
        for k in range(5):
            x=s*(.49+(k-2)*.014);base=Vector((x,-.060,1.058));end=base+Vector((s*.010,-.015,-.069 if k else -.043))
            modeled_bone('Metacarpal',base,end,.0055,'hand_'+side)
            for j in range(3):
                a=end+Vector((s*.005*j,-.004*j,-.018*j));b=a+Vector((s*.004,-.004,-.017));modeled_bone('Finger phalanx',a,b,.0048,'hand_'+side)
        modeled_bone('Femur',bonepos(arm,'thigh_'+side),bonepos(arm,'calf_'+side),.027,'thigh_'+side)
        ell('Patella',(s*.13,-.03,.50),(.026,.020,.031),'Bone','calf_'+side,16,10)
        a=bonepos(arm,'calf_'+side);b=bonepos(arm,'foot_'+side)
        modeled_bone('Tibia',a,b,.021,'calf_'+side);modeled_bone('Fibula',a+Vector((s*.025,0,-.015)),b+Vector((s*.021,0,0)),.009,'calf_'+side)
        ell('Heel',(s*.14,.027,.060),(.035,.044,.036),'Bone','foot_'+side,16,10)
        for k in range(5):
            x=s*.14+(k-2)*.017;start=(x,.005,.055);end=(x,-.13-(.015 if k<2 else 0),.030)
            modeled_bone('Metatarsal',start,end,.0065,'foot_'+side);modeled_bone('Toe',end,(x,end[1]-.036,.025),.006,'foot_'+side)
    belt_and_skirt(arm,'Skeleton','ClothRed' if role=='Fighter' else 'ClothBlue' if role=='Knight' else 'ClothPurple' if role=='Mage' else 'ClothOlive')
    bracers(arm,.70)
    if role=='Fighter':sword(arm);pauldron(arm,'r',1)
    elif role=='Knight':
        sword(arm);shield(arm);pauldron(arm,'l',1.1);pauldron(arm,'r',1.1);hood(arm,'Steel');ell('Knight cuirass',(0,-.083,1.31),(.195,.070,.15),'Steel','spine_04');cape(arm,'ClothBlue',.60)
    elif role=='Archer':bow(arm);hood(arm,'ClothOlive');cape(arm,'ClothOlive',.65)
    else:
        staff(arm,scale=1);hood(arm,'ClothPurple');cape(arm,'ClothPurple',1.07)
        rows=[]
        for j in range(5):
            t=j/4;row=[]
            for k in range(33):a=k*math.tau/32;r=.13+.13*t;row.append((r*math.cos(a),r*.63*math.sin(a),1.16-.91*t+.012*math.sin(k*1.8)*t))
            rows.append(row)
        ribbon('Mage robe',rows,'ClothPurple','pelvis',.012)
    mesh=merged(name,arm);actions=animate(arm,name,'Skeleton');export_model(name,'Skeleton',mesh,arm,actions,FBX/name)

for name,gel in [('MeadowSlime','MeadowGel'),('WaterSlime','WaterGel'),('FlameSlime','FlameGel'),('FrostSlime','FrostGel'),('PoisonSlime','PoisonGel'),('CrystalSlime','CrystalGel')]:make_slime(name,gel)
for role in ['Fighter','Knight','Archer','Mage']:skeleton_variant('Skeleton'+role,role)
for role in ['Scout','Fighter','Shaman']:humanoid_variant('Goblin'+role,'Goblin',role)
for role in ['Brute','Champion']:humanoid_variant('Ogre'+role,'Ogre',role)

# Save all rest-pose display meshes together, with packed image sources.
for _,_,o in lineup:o.hide_render=False;o.hide_set(False)
for family in ['Slime','Skeleton','Goblin','Ogre']:
    objects=[o for _,f,o in lineup if f==family];spacing={'Slime':1.2,'Skeleton':1.8,'Goblin':1.4,'Ogre':3.5}[family]
    for i,o in enumerate(objects):o.location=(spacing*(i-(len(objects)-1)/2),{'Slime':-4,'Skeleton':0,'Goblin':4,'Ogre':9}[family],0)
scene.frame_start=1;scene.frame_end=48;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'IV_Monster_Library_v01.blend'))
(OUT/'model_manifest.json').write_text(json.dumps({'status':'geometry_and_exports_complete','models':reports,'unreal_import':'pending','animations':'authored starter clips; gameplay polish pending'},indent=2))
print('MONSTER_MODEL_BUILD_COMPLETE',len(reports))

