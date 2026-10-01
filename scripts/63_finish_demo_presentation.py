"""Improve only the new demo's presentation using existing library clips."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'E:/RepairRig/scripts')
from stage6_demo_common import track
LIB=Path('E:/BlenderAssets/RepairRig');p=LIB/'Demo/RepairRig_NewProject_Validated.blend'
report=json.loads((LIB/'Docs/Validation_Report.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==report['demo_sha256']
bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=True);r=bpy.data.objects['RepairRig'];s=bpy.context.scene
bpy.ops.wm.append(directory=str(LIB/'Actions/RepairRig_Motion.blend')+'/Action/',filename='BRACE_Forward_L',do_reuse_local_id=True,clear_asset_data=True)
track(r,bpy.data.actions['BRACE_Forward_L'],65,'05 | Left hand — brace support','HOLD')
cam=s.camera;cam.location=(-3,.3,1.6);cam.rotation_euler=(Vector((0,-.4,.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
bpy.data.objects['TOOL_RestStand'].hide_render=True;bpy.data.objects['TOOL_RestStand'].hide_set(True)
for a in bpy.data.actions:
 if a.asset_data:a.asset_clear()
s.frame_set(117);bpy.context.view_layer.objects.active=r
for o in bpy.context.selected_objects:o.select_set(False)
r.select_set(True);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=True,compress=True)
print('DEMO_PRESENTATION_SAVED',flush=True)
