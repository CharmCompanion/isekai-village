"""Pose benchmark: resolve the open hand / floating weapon defect before propagation."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');root=B/'ArtSource/Monsters/Models_v03';out=B/'ArtSource/Monsters/Models_v05/Previews';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'OgreChampion.blend'))
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='SK_OgreChampion');arm=next(o for o in bpy.data.objects if o.type=='ARMATURE');arm.animation_data_clear()
for p in arm.pose.bones:p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
def world_rotation(n,axis,angle):
    p=arm.pose.bones[n];q=p.bone.matrix_local.to_quaternion();p.rotation_euler=(q.inverted()@Quaternion(Vector(axis),angle)@q).to_euler()
hand=arm.data.bones['hand_r'].head_local.copy();center=Vector((-1.12,-.30,1.405));rot=Quaternion(Vector((1,0,0)),math.pi/2)
gi=mesh.vertex_groups['hand_r'].index
gear={vi for p in mesh.data.polygons if not mesh.data.materials[p.material_index].name.endswith('Skin') for vi in p.vertices}
for v in mesh.data.vertices:
    if v.index in gear and any(g.group==gi and g.weight>.99 for g in v.groups):
        # Source hand skin is weighted to individual digits; hand-rigid pieces are gear.
        v.co=center+rot@(v.co-hand)
for digit in ['index','middle','ring','pinky']:
    for j,angle in [(1,-.55),(2,-1.02),(3,-.65)]:world_rotation(f'{digit}_{j:02}_r',(0,1,0),angle)
for j,angle in [(1,.15),(2,.35),(3,.25)]:world_rotation(f'thumb_{j:02}_r',(0,1,0),angle)
world_rotation('hand_r',(1,0,0),-math.pi/2)
bpy.context.view_layer.update()
# Anatomical contact solve, with bounded angular changes per CCD step.
from mathutils import Matrix
bpy.context.view_layer.update()
goal=center+Vector((-.025,-.035,.063))
for iteration in range(32):
    for joint in [3,2,1]:
        pb=arm.pose.bones[f'thumb_{joint:02}_r'];tip=arm.pose.bones['thumb_03_r'].tail.copy();pivot=pb.head.copy()
        delta=(tip-pivot).rotation_difference(goal-pivot)
        if delta.angle>.18:delta=Quaternion(delta.axis,.18)
        mat=pb.matrix.copy();pb.matrix=Matrix.LocRotScale(pivot,delta@mat.to_quaternion(),mat.to_scale())
        bpy.context.view_layer.update()
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.32,.36,1)
target=Vector((-1.11,-.10,1.69))
for pos,power in [((-4,-4,6),1000),((4,-3,4),800),((0,4,5),1000)]:
    bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=4;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-2.3,-2.1,2.5));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.85;scene.camera=cam
scene.render.filepath=str(out/'Ogre_Grip_Benchmark_v05.png');bpy.ops.render.render(write_still=True)
print('GRIP_BENCHMARK_COMPLETE')
