import bpy,runpy,traceback
from pathlib import Path
area=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES'); area.type='FILE_BROWSER'; area.ui_type='ASSETS'
def setup():
 try:
  area.spaces.active.params.asset_library_reference='LOCAL'
  bpy.app.timers.register(execute,first_interval=3)
 except Exception: Path('E:/RepairRig/tests/stage4/error_pose_launcher.txt').write_text(traceback.format_exc()); bpy.ops.wm.quit_blender()
def execute():
 try:
  with bpy.context.temp_override(area=area,region=next(reg for reg in area.regions if reg.type=='WINDOW')):
   runpy.run_path('E:/RepairRig/scripts/20_stage4_pose_test.py',run_name='__main__')
 except Exception: Path('E:/RepairRig/tests/stage4/error_pose_launcher.txt').write_text(traceback.format_exc()); bpy.ops.wm.quit_blender()
bpy.app.timers.register(setup,first_interval=2)
