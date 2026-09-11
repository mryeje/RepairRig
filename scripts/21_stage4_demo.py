import sys,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 reset(); poses=json.loads((OUT/'poses.json').read_text())
 # Remove test assemblies from this new checkpoint. Stage 3 file is untouched.
 for o in bpy.data.objects:
  if o.animation_data:
   for tr in list(o.animation_data.nla_tracks): o.animation_data.nla_tracks.remove(tr)
 names=['BODY_Idle_Standing','BODY_Bend_Forward','BODY_Crouch_Shallow','BODY_Kneel_L','BODY_Kneel_R','BODY_Stand_From_Kneel_L','REACH_Forward_Low_R','REACH_Forward_Mid_R','REACH_Forward_Low_L','BRACE_Forward_L','TOOL_Screwdriver_CW_R','TOOL_Screwdriver_CCW_R','TOOL_Pliers_Squeeze_R','GESTURE_Talk_OneHand_R','GESTURE_Point_R']
 (OUT/'expected_actions.json').write_text(json.dumps(names,indent=2))
 # This is shot staging, deliberately distinct from body and reach library clips.
 a=new('SHOT4_ArmRest',desc='Demo-only relaxed arm timing follows lowering/standing. Edit alongside body retiming.',scope='both hand IK and elbow poles')
 for label,f in [('stand',1),('stand',65),('mid',87),('kneel',113),('kneel',325),('mid',351),('stand',373),('stand',485)]:
  for n in ['hand_ik.L','hand_ik.R','upper_arm_ik_target.L','upper_arm_ik_target.R']:
   for path in ['location','rotation_quaternion']: key(n,path,f,poses[label][n][path])
 finish(a)
 a=new('SHOT4_Look',desc='Demo-only head attention; native Damped Track influence.',scope='head look constraint')
 c=r.pose.bones['head'].constraints['Look | TARGET_Look']
 for f,v in [(1,0),(65,0),(129,.78),(301,.78),(373,0),(485,0)]: c.influence=v; c.keyframe_insert('influence',frame=f)
 finish(a)
 reset()
 strip(r,'01 BODY | support and transitions',bpy.data.actions['BODY_Idle_Standing'],1)
 strip(r,'01 BODY | support and transitions',bpy.data.actions['BODY_Kneel_L'],65)
 strip(r,'01 BODY | support and transitions',bpy.data.actions['BODY_Stand_From_Kneel_L'],325)
 strip(r,'01 BODY | support and transitions',bpy.data.actions['BODY_Idle_Standing'],373,repeat=1.75)
 strip(r,'02 ARMS | shot rest timing',bpy.data.actions['SHOT4_ArmRest'],1)
 for name,track in [('REACH_Forward_Low_R','03 RIGHT | approach - hold - withdraw'),('BRACE_Forward_L','04 LEFT | brace - hold - withdraw')]:
  strip(r,track,bpy.data.actions[name],129)
  st=strip(r,track,bpy.data.actions[name],269); st.use_reverse=True; st.extrapolation='NOTHING'
 st=strip(r,'05 PRESENTATION | right arm',bpy.data.actions['GESTURE_Talk_OneHand_R'],405); st.extrapolation='NOTHING'
 strip(r,'06 HEAD | independent look',bpy.data.actions['SHOT4_Look'],1)
 # Starting with tool in hand keeps this demo about the action library.
 for f,v in zip(FINGERS,[.58,.58,.58,.58,.70]): r.pose.bones[f+'.01_master.R'].scale=(1,v,1)
 tool=bpy.data.objects['TOOL_Screwdriver']; tool.matrix_basis=bpy.data.objects['TARGET_ToolGrip'].matrix_world.copy(); tool.constraints[0].influence=1
 roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R']; strip(roll,'TOOL | CW quarter-turn x3',bpy.data.actions['TOOL_Screwdriver_CW_R'],161,3).extrapolation='HOLD'
 screw=bpy.data.objects['SCREW_Visible']; a=new('SHOT4_ScrewResult',screw,'Demo-only accumulated quarter turns matching the three CW strokes.',scope='visible screw')
 for f,deg in [(1,-35),(161,-35),(166,-35),(182,55),(197,55),(202,55),(218,145),(233,145),(238,145),(254,235),(485,235)]:
  screw.rotation_euler.z=math.radians(deg); screw.keyframe_insert('rotation_euler',index=2,frame=f)
 finish(a,screw); strip(screw,'SHOT | cumulative screw result',a,1)
 # Park pliers next to the scene, ready for separate tool practice.
 pliers=bpy.data.objects['TOOL_Pliers']; pliers.constraints[0].influence=0; pliers.location=(.62,-.30,.24)
 s.frame_start=1; s.frame_end=485; s.render.fps=24
 for m in list(s.timeline_markers): s.timeline_markers.remove(m)
 for f,label in [(1,'Idle | tool already held'),(65,'Lower to left knee'),(113,'Kneel hold'),(129,'Reach + independent brace'),(161,'Screwdriver | 3 CW cycles'),(269,'Reverse reach + brace'),(301,'Hands clear'),(325,'Stand from left knee'),(373,'Idle reused'),(405,'Explain with tool'),(453,'Rest')]: s.timeline_markers.new(label,frame=f)
 s['Stage 4']='15 reusable motion Actions + 6 native hand Pose Assets. 24 fps. See docs/animation_library.md. SHOT4 Actions are demonstration staging.'
 for a in bpy.data.actions:
  if a.name in names:
   a.asset_mark(); a.asset_data.description=a.get('intended_use',''); a.asset_data.tags.new('Stage 4 Motion')
  elif a.name.startswith('POSE_'): a.asset_data.tags.new('Stage 4 Hand Pose')
 # Useful editable file layout: timeline becomes a native NLA Editor.
 bpy.context.view_layer.objects.active=r; bpy.ops.object.select_all(action='DESELECT'); r.select_set(True)
 for area in bpy.context.screen.areas:
  if area.type=='DOPESHEET_EDITOR': area.type='NLA_EDITOR'
 update(179)
 check_actions(names,'final_library_channels')
 for label,f in [('demo_idle',1),('demo_lower',87),('demo_contact',179),('demo_withdraw',285),('demo_stand',351),('demo_talk',425)]: render(label,f)
 update(179)
 target=ROOT/'blend/RepairRig_04_ActionLibrary.blend'; assert not target.exists(),'Do not silently overwrite a delivered checkpoint'
 bpy.ops.wm.save_as_mainfile(filepath=str(target))
 (OUT/'demo_created.json').write_text(json.dumps({'pass':True,'file':str(target),'actions':names},indent=2))
except: (OUT/'error_demo.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
