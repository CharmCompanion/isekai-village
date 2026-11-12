import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v02')
bpy.ops.wm.open_mainfile(filepath=str(root/'IV_Monster_Library_v02.blend'))
out=root/'Previews';out.mkdir(exist_ok=True)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=2000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.24,.26,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
scene.view_settings.view_transform='AgX'
models=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SK_')]
groundmat=bpy.data.materials.new('Review stage');groundmat.diffuse_color=(.32,.35,.39,1);groundmat.use_nodes=True;groundmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.32,.35,.39,1);groundmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.83
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));ground=bpy.context.object;ground.data.materials.append(groundmat)
def light(pos,power,size):
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;return o
lights=[light((-4,-4,6),900,5),light((4,-2,4),650,4),light((0,4,6),1000,4)]
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO'
captures=[]
for family,center,span,targetz in [('Skeleton',0,8.3,.95),('Goblin',4,5.7,.80),('Ogre',9,9.0,1.5)]:
    for o in models:o.hide_render=family not in o.name
    cam.location=(.8,center-9,3.7 if family!='Ogre' else 5.0);target=Vector((0,center,targetz));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span
    for i,o in enumerate(lights):
        o.location=[(-4,center-4,6),(4,center-2,4),(0,center+4,6)][i];o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(family+'_Models_v02.png'));bpy.ops.render.render(write_still=True);captures.append(scene.render.filepath)
(out/'render_report.json').write_text(json.dumps(captures,indent=2));print('MONSTER_PREVIEWS_COMPLETE')

