import sys,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 reset(); bpy.context.view_layer.objects.active=r; bpy.ops.object.select_all(action='DESELECT'); r.select_set(True); bpy.ops.object.mode_set(mode='POSE')
 out={}; vals=json.loads((OUT/'pose_values.json').read_text())
 def apply(name,factor=1):
  bpy.context.space_data.activate_asset_by_id(bpy.data.actions[name])
  return bpy.ops.poselib.apply_pose_asset(asset_library_type='LOCAL',relative_asset_identifier='Action/'+name,blend_factor=factor)
 def select(fingers):
  for p in r.pose.bones: p.select=p.name in [f+'.01_master.R' for f in fingers]
 def read(): return [r.pose.bones[f+'.01_master.R'].scale.y for f in FINGERS]
 select(FINGERS)
 for name,v in vals.items():
  for f in FINGERS: r.pose.bones[f+'.01_master.R'].scale=(1,1,1)
  status=apply(name); actual=read(); err=max(abs(x-y) for x,y in zip(actual,v)); assert err<1e-5,(name,status,actual)
  out[name]=actual
 apply('POSE_OpenHand_R'); select(['f_index']); apply('POSE_Grip_Screwdriver_R'); actual=read(); assert abs(actual[0]-.58)<1e-5 and all(abs(v-1)<1e-5 for v in actual[1:]); out['selected_only']=actual
 select(FINGERS); apply('POSE_OpenHand_R'); apply('POSE_Grip_Screwdriver_R',.5); actual=read(); assert max(abs(x-(1+y)/2) for x,y in zip(actual,vals['POSE_Grip_Screwdriver_R']))<1e-5; out['half_blend']=actual
 apply('POSE_Grip_Screwdriver_R'); apply('POSE_OpenHand_R'); assert all(abs(v-1)<1e-5 for v in read()); out['switch_to_open']=read()
 bpy.ops.object.mode_set(mode='OBJECT')
 reset(); assign(bpy.data.actions['TOOL_Pliers_Squeeze_R']); tool=bpy.data.objects['TOOL_Pliers']; c=tool.constraints[0]; c.influence=1
 # Inverse cancels the parked object's own transform; attachment matches socket.
 angles={}
 for f in [1,11,25]:
  update(f); angles[f]=[bpy.data.objects['Pliers_JawPivot_'+str(sign)].rotation_euler.y for sign in [-1,1]]
 assert abs(angles[1][1]-.18)<1e-5 and abs(angles[11][1]-.035)<1e-5 and angles[1]==angles[25],angles
 out['pliers_jaw_angles']=angles; out['pass']=True; out['source_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
 (OUT/'pose_application_validation.json').write_text(json.dumps(out,indent=2))
 render('pliers_squeeze',11)
except: (OUT/'error_pose.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
