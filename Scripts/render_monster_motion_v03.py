"""Representative deformation views, not a motion-quality certificate."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/Models_v03');out=root/'Previews';out.mkdir(exist_ok=True)
results=[]
for name,height in [('SkeletonKnight',1.9),('GoblinFighter',1.3),('OgreChampion',3.1)]:
    for kind,frame in [('Move',9),('Attack',17)]:
        bpy.ops.wm.open_mainfile(filepath=str(root/(name+'.blend')))
        arm=next(o for o in bpy.data.objects if o.type=='ARMATURE');arm.animation_data_create();arm.animation_data.action=bpy.data.actions['AN_'+name+'_'+kind];bpy.context.scene.frame_set(frame)
        scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
        scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.32,.36,1)
        target=Vector((0,0,height*.52))
        for pos,power in [((-4,-4,6),1000),((4,-3,4),800),((0,4,5),1000)]:
            bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=4;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        bpy.ops.object.camera_add(location=(height*.65,-height*3,height*1.03));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=height*1.32;scene.camera=cam
        scene.render.filepath=str(out/(name+'_'+kind+'_Deformation_v03.png'));bpy.ops.render.render(write_still=True);results.append(scene.render.filepath)
(out/'motion_render_report.json').write_text(json.dumps(results,indent=2));print('MOTION_VIEWS_COMPLETE',len(results))
