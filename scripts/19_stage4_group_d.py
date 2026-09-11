import sys,traceback,copy
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 poses=json.loads((OUT/'poses.json').read_text()); names=[]; reset()
 a=new('BODY_Crouch_Shallow',desc='Lower centre of mass over planted feet; arm motions independent.',scope='body / leg IK'); names.append(a.name)
 for f,t in [(1,0),(13,.35),(33,1)]:
  pose_keys(poses['stand'],f); key('torso','location',f,(0,.045*t,-.20*t)); key('torso','rotation_quaternion',f,Quaternion((1,0,0),.17*t)); key('chest','rotation_quaternion',f,Quaternion((1,0,0),.06*t))
 finish(a)
 a=new('BODY_Kneel_R',desc='Mirrored support transfer to right knee. Move knee pad and fit separate arm targets.',scope='body / leg IK'); names.append(a.name)
 for label,f in [('stand',1),('mid',23),('kneel',49)]:
  pose=copy.deepcopy(poses[label])
  for side,other in [('L','R'),('R','L')]:
   for prefix in ['foot_ik.','thigh_ik_target.']:
    vals=copy.deepcopy(poses[label][prefix+other]); vals['location'][0]*=-1; vals['rotation_quaternion'][2]*=-1; vals['rotation_quaternion'][3]*=-1; pose[prefix+side]=vals
  pose_keys(pose,f)
 finish(a)
 reset(); a=new('REACH_Forward_Low_L',desc='Left wrist approach to TARGET_Reach_Low_L; independent from right reach. Fit elbow pole.',scope='left arm IK / target-dependent'); names.append(a.name)
 for f,t in [(1,0),(9,.12),(25,1),(33,1)]:
  for n in ['hand_ik.L','upper_arm_ik_target.L']:
   for path in ['location','rotation_quaternion']: key(n,path,f,poses['kneel'][n][path])
  prop('upper_arm_parent.L','IK_FK',f,0)
  for c in r.pose.bones['hand_ik.L'].constraints: c.influence=t if c.name=='Reach | Low_L' else 0; c.keyframe_insert('influence',frame=f)
 finish(a)
 for name,point in [('GESTURE_Talk_OneHand_R',False),('GESTURE_Point_R',True)]:
  reset(); a=new(name,desc=('Short pointing arm arc; apply POSE_Point_R separately. Aim manually.' if point else 'Restrained explanatory arm arc; apply open-hand pose separately.')+' Uses normal IK throughout to blend with the existing IK workflow; no mode switch.',scope='right arm IK / free gesture'); names.append(a.name)
  p=r.pose.bones['hand_ik.R']; m0=p.matrix.copy(); q0=m0.to_quaternion()
  frames=[(1,0),(13,.6),(21,1),(29,.75),(37,.35),(49,0)] if not point else [(1,0),(9,.45),(17,1),(29,1),(41,0)]
  end=Vector((-.28,-.42,1.28)) if point else Vector((-.37,-.28,1.22))
  qend=Vector((0,-1,.08)).to_track_quat('Y','Z') if point else Vector((-.25,-.8,.45)).to_track_quat('Y','Z')
  for f,t in frames:
   m=q0.slerp(qend,t).to_matrix().to_4x4(); m.translation=m0.translation.lerp(end,t); m.translation.z+=.035*math.sin(math.pi*t)
   p.matrix=m; update()
   p.keyframe_insert('location',frame=f,group=p.name); p.keyframe_insert('rotation_quaternion',frame=f,group=p.name)
   for path in ['location','rotation_quaternion']: key('upper_arm_ik_target.R',path,f,poses['stand']['upper_arm_ik_target.R'][path])
   prop('upper_arm_parent.R','IK_FK',f,0)
   for c in p.constraints: c.influence=0; c.keyframe_insert('influence',frame=f)
  finish(a)
 check_actions(names,'group_d_channels')
 result={}
 for name,frame in [('BODY_Crouch_Shallow',33),('BODY_Kneel_R',49),('GESTURE_Talk_OneHand_R',21),('GESTURE_Point_R',21),('REACH_Forward_Low_L',33)]:
  reset()
  if name=='REACH_Forward_Low_L':
   for n in BODY:
    for k,v in poses['kneel'][n].items(): setattr(r.pose.bones[n],k,v)
  assign(bpy.data.actions[name]); update(frame)
  if name.startswith('BODY_'):
   base='kneel' if name.endswith('_R') else 'stand'
   for n in ['hand_ik.R','hand_ik.L','upper_arm_ik_target.R','upper_arm_ik_target.L']:
    for k,v in poses[base][n].items(): setattr(r.pose.bones[n],k,v)
  if name=='GESTURE_Point_R':
   for f,v in zip(FINGERS,[1,.48,.48,.48,.72]): r.pose.bones[f+'.01_master.R'].scale.y=v
  update(); p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
  side='L' if name=='REACH_Forward_Low_L' else 'R'
  result[name]={'hand_error':(p['DEF-hand.'+side].head-p['hand_ik.'+side].head).length,'feet':{n:list(p[n].head) for n in ['DEF-foot.L','DEF-foot.R']}}
  if not name.startswith('BODY_'): assert result[name]['hand_error']<.003,result[name]
  render('group_d_'+name,frame)
 (OUT/'group_d_validation.json').write_text(json.dumps({'measurements':result,'pass':True},indent=2)); save('group_d.blend')
except: (OUT/'error_d.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
