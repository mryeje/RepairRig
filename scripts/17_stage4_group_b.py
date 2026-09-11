import sys,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 poses=json.loads((OUT/'poses.json').read_text()); names=[]
 reset()
 col=bpy.data.collections.new('Stage 4 | Library targets and pliers'); s.collection.children.link(col)
 def target(name,pos,rotation):
  o=bpy.data.objects.new(name,None); col.objects.link(o); o.empty_display_type='ARROWS'; o.empty_display_size=.06; o.location=pos; o.rotation_mode='QUATERNION'; o.rotation_quaternion=rotation; return o
 mid=target('TARGET_Reach_Mid_R',(-.28,-.38,1.08),bpy.data.objects['CONTACT_WorkWrist_R'].matrix_world.to_quaternion())
 low=target('TARGET_Reach_Low_L',(.28,-.44,.57),bpy.data.objects['TARGET_Brace_L'].rotation_quaternion)
 for side,o,cn in [('R',mid,'Reach | Mid_R'),('L',low,'Reach | Low_L')]:
  c=r.pose.bones['hand_ik.'+side].constraints.new('COPY_TRANSFORMS'); c.name=cn; c.target=o; c.owner_space='WORLD'; c.target_space='WORLD'; c.influence=0
 def reach(name,side,cn,base):
  reset(); a=new(name,desc='33-frame approach and settle. Hold last frame; reverse strip for withdrawal. Adjust wrist target and elbow pole for body pose.',scope=side+' arm IK / target-dependent'); names.append(name)
  for f,t in [(1,0),(9,.12),(25,1),(33,1)]:
   for n in ['hand_ik.'+side,'upper_arm_ik_target.'+side]:
    for path in ['location','rotation_quaternion']: key(n,path,f,poses[base][n][path])
   prop('upper_arm_parent.'+side,'IK_FK',f,0)
   for c in r.pose.bones['hand_ik.'+side].constraints:
    if c.type=='COPY_TRANSFORMS': c.influence=t if c.name==cn else 0; c.keyframe_insert('influence',frame=f)
  finish(a)
 reach('REACH_Forward_Low_R','R','Work | TARGET_Screw','kneel')
 reach('REACH_Forward_Mid_R','R','Reach | Mid_R','stand')
 reach('BRACE_Forward_L','L','Brace | TARGET_Brace_L','kneel')
 # Group B validates low right + independent left brace before adding variants.
 reset(); strip(r,'B test body',bpy.data.actions['BODY_Kneel_L'],1)
 strip(r,'B test right',bpy.data.actions['REACH_Forward_Low_R'],49)
 strip(r,'B test left',bpy.data.actions['BRACE_Forward_L'],49)
 errors={}
 for side in ['L','R']:
  errors[side]=0
  for f in range(49,82):
   update(f); p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
   errors[side]=max(errors[side],(p['DEF-hand.'+side].head-p['hand_ik.'+side].head).length)
 assert max(errors.values())<.003,errors
 render('group_b_contacts',81)
 reset(); strip(r,'B test bend',bpy.data.actions['BODY_Bend_Forward'],1); strip(r,'B test mid',bpy.data.actions['REACH_Forward_Mid_R'],33)
 update(65); p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
 errors['mid_R']=(p['DEF-hand.R'].head-p['hand_ik.R'].head).length
 assert errors['mid_R']<.003,errors
 render('group_b_mid',65)
 check_actions(names,'group_b_channels'); (OUT/'group_b_validation.json').write_text(json.dumps({'hand_ik_errors':errors,'pass':True},indent=2)); save('group_b.blend')
except: (OUT/'error_b.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
