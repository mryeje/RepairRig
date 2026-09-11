import sys,traceback,copy,runpy
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 poses=json.loads((OUT/'poses.json').read_text()); seq=[]
 for f,t in [(1,0),(11,.08),(21,.24),(35,.66),(49,1)]:
  pose=copy.deepcopy(poses['stand'])
  pose['torso']['location']=[-.04*math.sin(math.pi*t),.06*t,-.50*t]; pose['torso']['rotation_quaternion']=list(Quaternion((1,0,0),.55*t)); pose['chest']['rotation_quaternion']=list(Quaternion((1,0,0),.25*t))
  for side in ['L','R']:
   u=max(0,(f-21)/28) if side=='L' else min(1,(f-1)/20)
   p0=Vector(poses['stand']['foot_ik.'+side]['location']); p1=Vector(poses['kneel']['foot_ik.'+side]['location']); v=p0.lerp(p1,u); v.z+=(.055 if side=='L' else .07)*math.sin(math.pi*u)
   pose['foot_ik.'+side]['location']=list(v); pose['foot_ik.'+side]['rotation_quaternion']=list(Quaternion(poses['stand']['foot_ik.'+side]['rotation_quaternion']).slerp(Quaternion(poses['kneel']['foot_ik.'+side]['rotation_quaternion']),u))
   pose['thigh_ik_target.'+side]=copy.deepcopy(poses['kneel']['thigh_ik_target.'+side])
  seq.append((f,pose))
 for name,reverse,mirror in [('BODY_Kneel_L',False,False),('BODY_Stand_From_Kneel_L',True,False),('BODY_Kneel_R',False,True)]:
  a=bpy.data.actions[name]
  for fc in curves(a): fc.keyframe_points.clear()
  assign(a)
  for f,src in seq:
   pose=copy.deepcopy(src)
   if mirror:
    pose['torso']['location'][0]*=-1
    for side,other in [('L','R'),('R','L')]:
     for prefix in ['foot_ik.','thigh_ik_target.']:
      vals=copy.deepcopy(src[prefix+other]); vals['location'][0]*=-1; vals['rotation_quaternion'][2]*=-1; vals['rotation_quaternion'][3]*=-1; pose[prefix+side]=vals
   pose_keys(pose,50-f if reverse else f)
  finish(a)
 # Bend the resting left elbow slightly more during support transfer.
 poses['mid']['hand_ik.L']['location']=list(Vector(poses['mid']['hand_ik.L']['location']) + r.data.bones['hand_ik.L'].matrix_local.to_3x3().inverted() @ Vector((0,0,.035)))
 # The limb staging remains separate, but its timing follows the refined body.
 a=bpy.data.actions['SHOT4_ArmRest']; assign(a)
 for fc in curves(a): fc.keyframe_points.clear()
 for label,f in [('stand',1),('stand',65),('stand',75),('mid',85),('mid',99),('kneel',113),('kneel',325),('mid',339),('mid',353),('stand',363),('stand',373),('stand',485)]:
  for n in ['hand_ik.L','hand_ik.R','upper_arm_ik_target.L','upper_arm_ik_target.R']:
   for path in ['location','rotation_quaternion']: key(n,path,f,poses[label][n][path])
 finish(a)
 pliers=bpy.data.objects['TOOL_Pliers']; pliers.location=(.62,-.30,0); pliers.rotation_euler.x=math.pi/2
 for o in bpy.data.objects:
  if o.animation_data:
   for tr in o.animation_data.nla_tracks: tr.mute=False
 r.animation_data.action=None
 validate=runpy.run_path(str(OUT/'validate_library.py'))['validate']; validate('presave_validation')
 for name,f in [('demo_lower_refined',85),('demo_stand_refined',353),('demo_final_contact',179)]: render(name,f)
 update(179); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blend/RepairRig_04_ActionLibrary.blend'))
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_04_ActionLibrary.blend'),use_scripts=True)
 # Reload helper bindings to the reopened scene.
 import importlib,stage4_common
 importlib.reload(stage4_common)
 runpy.run_path(str(OUT/'validate_library.py'))['validate']('reopen_validation')
except: (OUT/'error_final.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
