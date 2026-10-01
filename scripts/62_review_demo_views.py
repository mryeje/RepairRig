"""Read-only visual framing review of independent demo."""
import bpy,json
from pathlib import Path
from mathutils import Vector
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library')
bpy.ops.wm.open_mainfile(filepath=str(LIB/'Demo/RepairRig_NewProject_Validated.blend'),use_scripts=True)
s=bpy.context.scene;s.frame_set(117);cam=s.camera
for name,pos in [('right_front',(-2.8,-3.8,2.1)),('right_side',(-3,.3,1.6)),('right_rear',(-2.8,2.8,2.1))]:
 cam.location=pos;cam.rotation_euler=(Vector((0,-.4,.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5;s.render.resolution_x=960;s.render.resolution_y=720;s.render.filepath=str(OUT/('demo_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('WORLDS',[(n,list(bpy.data.objects[n].matrix_world.translation),list(bpy.data.objects[n].dimensions)) for n in ['APPLIANCE_Washer_Proxy','TARGET_Screw','RepairRig']],flush=True)
