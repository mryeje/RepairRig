import sys, traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 (OUT/'architecture.json').write_text(json.dumps(structure(),indent=2))
 (OUT/'source_hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'blend').glob('*.blend')},indent=2))
 poses={}
 for label,f in [('stand',1),('mid',38),('kneel',64)]: update(f); poses[label]=capture()
 (OUT/'poses.json').write_text(json.dumps(poses,indent=2))
 for a in list(bpy.data.actions):
  if a.name!='POSE_Grip_Screwdriver_R': a.name='STAGE3_'+a.name; a.use_fake_user=True
 for o in bpy.data.objects:
  if o.animation_data:
   for t in o.animation_data.nla_tracks: t.name='STAGE3 archive | '+t.name
 reset()
 names=[]
 a=new('BODY_Kneel_L',desc='Stand to left-knee support; fit feet and knee pad. Arms independent.',scope='body / leg IK'); names.append(a.name)
 for label,f in [('stand',1),('mid',23),('kneel',49)]: pose_keys(poses[label],f)
 finish(a)
 a=new('BODY_Stand_From_Kneel_L',desc='Reverse support transfer from matching left kneel to stand.',scope='body / leg IK'); names.append(a.name)
 for label,f in [('kneel',1),('mid',27),('stand',49)]: pose_keys(poses[label],f)
 finish(a)
 a=new('BODY_Idle_Standing',desc='Standing support and restrained breathing. Add arms separately.',loop=True,scope='body / leg IK'); names.append(a.name)
 for f,t in [(1,0),(17,.7),(33,1),(49,.4),(65,0)]:
  pose_keys(poses['stand'],f)
  v=Vector(poses['stand']['torso']['location']); v.z+=.003*t; key('torso','location',f,v)
  key('chest','rotation_quaternion',f,Quaternion((1,0,0),.008*t))
 finish(a)
 a=new('BODY_Bend_Forward',desc='Standing to mild service-panel bend; feet planted. Hold final pose with NLA extrapolation.',scope='body / leg IK'); names.append(a.name)
 for f,t in [(1,0),(13,.35),(33,1)]:
  pose_keys(poses['stand'],f)
  key('torso','location',f,(0,.07*t,-.075*t)); key('torso','rotation_quaternion',f,Quaternion((1,0,0),.35*t)); key('chest','rotation_quaternion',f,Quaternion((1,0,0),.12*t))
 finish(a)
 check_actions(names,'group_a_channels')
 reset(); assign(bpy.data.actions['BODY_Kneel_L']); update(49)
 for n in ['hand_ik.L','hand_ik.R','upper_arm_ik_target.L','upper_arm_ik_target.R']:
  for k,v in poses['kneel'][n].items(): setattr(r.pose.bones[n],k,v)
 render('group_a_kneel',49)
 # Stationary hold evaluates the actual deform feet, not only IK controls.
 feet={}
 for f in [49,57,65]:
  update(f); ep=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
  feet[f]={n:list(ep[n].head) for n in ['DEF-foot.L','DEF-foot.R','DEF-shin.L','DEF-shin.R']}
 drift=max((Vector(feet[49][n])-Vector(feet[f][n])).length for f in feet for n in feet[f]); assert drift<1e-5
 (OUT/'group_a_validation.json').write_text(json.dumps({'stationary_foot_drift':drift,'positions':feet,'pass':True},indent=2))
 save('group_a.blend')
except: (OUT/'error_a.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
