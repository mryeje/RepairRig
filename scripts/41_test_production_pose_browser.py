"""Native GUI Asset Browser application test; no scene saves."""
import bpy,sys,json,traceback
from pathlib import Path
sys.path.insert(0,'E:/RepairRig/scripts')
from production_grip_common import CONTROLS,OUT
area=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES');area.type='FILE_BROWSER';area.ui_type='ASSETS'
def finish(result):
 (OUT/'asset_browser_validation.json').write_text(json.dumps(result,indent=2));bpy.ops.wm.quit_blender()
def execute():
 try:
  r=bpy.data.objects['RepairRig'];r.animation_data.action=None;r.animation_data.use_nla=False
  bpy.context.view_layer.objects.active=r
  if bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
  bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.ops.object.mode_set(mode='POSE')
  for p in r.pose.bones:p.select=p.name in CONTROLS
  results={}
  with bpy.context.temp_override(area=area,region=next(reg for reg in area.regions if reg.type=='WINDOW')):
   for a in [a for a in bpy.data.actions if a.name.endswith('_R_Production')]:
    bpy.context.space_data.activate_asset_by_id(a)
    status=bpy.ops.poselib.apply_pose_asset(asset_library_type='LOCAL',relative_asset_identifier='Action/'+a.name,blend_factor=1)
    errors=[]
    for l in a.layers:
     for st in l.strips:
      bag=st.channelbag(a.slots[0])
      for fc in bag.fcurves:errors.append(abs(r.path_resolve(fc.data_path)[fc.array_index]-fc.evaluate(1)))
    results[a.name]={'operator':list(status),'max_channel_error':max(errors)}
    assert 'FINISHED' in status and max(errors)<1e-5,(a.name,status,max(errors))
  assert len(results)==6;finish({'pass':True,'assets':results})
 except:finish({'pass':False,'error':traceback.format_exc()})
def setup():
 try:area.spaces.active.params.asset_library_reference='LOCAL';bpy.app.timers.register(execute,first_interval=3)
 except:finish({'pass':False,'error':traceback.format_exc()})
bpy.app.timers.register(setup,first_interval=2)
