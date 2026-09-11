import sys,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 reset(); names=[]; roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R']
 for suffix,sign in [('CW',1),('CCW',-1)]:
  a=new('TOOL_Screwdriver_'+suffix+'_R',roll,'Quarter turn, withdraw 22 mm, return wrist, reseat. 36-frame period; view from handle toward tip.',True,'tool-axis Empty; requires right Work constraint and attached grip'); names.append(a.name)
  for f,deg,z in [(1,-35,0),(6,-35,0),(22,55,0),(25,55,-.022),(33,-35,-.022),(37,-35,0)]:
   roll.rotation_euler.z=math.radians(deg*sign); roll.location.z=z
   roll.keyframe_insert('rotation_euler',index=2,frame=f); roll.keyframe_insert('location',index=2,frame=f)
  finish(a,roll)
 # Pliers use the same right-hand reference and a fitted local grip offset.
 col=bpy.data.collections['Stage 4 | Library targets and pliers']
 tool=bpy.data.objects.new('TOOL_Pliers',None); col.objects.link(tool); tool.empty_display_type='ARROWS'; tool.empty_display_size=.04
 tool.location=(.48,-.22,.45)
 socket=bpy.data.objects.new('ATTACH_Pliers_R',None); col.objects.link(socket); socket.parent=bpy.data.objects['REF_Hand_R']; socket.matrix_basis=bpy.data.objects['ATTACH_Screwdriver_R'].matrix_basis.copy()
 c=tool.constraints.new('CHILD_OF'); c.name='Attach / release | pliers right socket'; c.target=socket; c.inverse_matrix=tool.matrix_basis.inverted(); c.influence=0
 tool['Workflow']='Fit Child Of inverse at pickup. Jaw drivers read right index master scale Y; no custom runtime.'
 for sign in [-1,1]:
  pivot=bpy.data.objects.new('Pliers_JawPivot_'+str(sign),None); col.objects.link(pivot); pivot.parent=tool; pivot.location=(0,0,.09)
  drv=pivot.driver_add('rotation_euler',1).driver; drv.type='SCRIPTED'; v=drv.variables.new(); v.name='grip'; v.type='SINGLE_PROP'; v.targets[0].id=r; v.targets[0].data_path='pose.bones["f_index.01_master.R"].scale[1]'
  drv.expression=str(sign)+'*(0.035+0.145*min(1,max(0,(grip-0.52)/0.26)))'
  for part,z,length,width,mat in [('Handle',-.078,.156,.018,'Tool | amber grip'),('Jaw',.032,.064,.012,'Tool | steel')]:
   bpy.ops.mesh.primitive_cube_add(size=1); o=bpy.context.object; o.name='Pliers_'+part+'_'+str(sign)
   for co in list(o.users_collection): co.objects.unlink(o)
   col.objects.link(o); o.parent=pivot; o.location=(sign*.006,0,z); o.scale=(width,.016,length); o.data.materials.append(bpy.data.materials[mat])
 a=new('TOOL_Pliers_Squeeze_R',desc='Squeeze and release finger masters; native jaw drivers follow index curl. Apply pliers pose and fit attachment first.',loop=True,scope='five right finger masters only'); names.append(a.name)
 for f,t in [(1,0),(7,.5),(11,1),(15,1),(21,.25),(25,0)]:
  for finger in FINGERS: key(finger+'.01_master.R','scale',f,(1,(.78-.26*t) if finger!='thumb' else (.76-.10*t),1),1)
 finish(a)
 # Native single-frame Action assets, no duplicate static motion Actions.
 values={'POSE_Grip_Screwdriver_R':[.58,.58,.58,.58,.70],'POSE_Grip_Pliers_R':[.78,.78,.78,.78,.76],'POSE_HoldSmallPart_R':[.80,.90,.96,.96,.64],'POSE_OpenHand_R':[1,1,1,1,1],'POSE_Fist_R':[.48,.48,.48,.48,.64],'POSE_Point_R':[1,.48,.48,.48,.72]}
 bpy.context.view_layer.objects.active=r; bpy.ops.object.select_all(action='DESELECT'); r.select_set(True); bpy.ops.object.mode_set(mode='POSE')
 for name,vals in values.items():
  for p in r.pose.bones: p.select=p.name in [f+'.01_master.R' for f in FINGERS]
  for finger,val in zip(FINGERS,vals): r.pose.bones[finger+'.01_master.R'].scale=(1,val,1)
  r.data.bones.active=r.data.bones['f_index.01_master.R']; update()
  if name not in bpy.data.actions: bpy.ops.poselib.create_pose_asset(pose_name=name,asset_library_reference='LOCAL')
  a=bpy.data.actions[name]; a.use_fake_user=True; a['Stage']='4'; a.asset_data.description='Right finger masters only. Apply to all five or selected fingers; fit thumb and individual phalanges to actual prop.'
  r.animation_data.action=None
 (OUT/'pose_values.json').write_text(json.dumps(values,indent=2))
 (OUT/'pose_api.json').write_text(json.dumps({'method':[(p.identifier,p.type) for p in r.pose.bl_rna.functions['apply_pose_from_action'].parameters], 'apply':[(p.identifier,p.type) for p in bpy.ops.poselib.apply_pose_asset.get_rna_type().properties],'blend':[(p.identifier,p.type) for p in bpy.ops.poselib.blend_pose_asset.get_rna_type().properties]},indent=2))
 bpy.ops.object.mode_set(mode='OBJECT')
 reset(); strip(r,'C body',bpy.data.actions['BODY_Kneel_L'],1); strip(r,'C reach',bpy.data.actions['REACH_Forward_Low_R'],49); strip(r,'C brace',bpy.data.actions['BRACE_Forward_L'],49)
 tool_sd=bpy.data.objects['TOOL_Screwdriver']; tool_sd.constraints[0].influence=1
 # Restore the Stage 3 pickup-space basis required by its existing inverse.
 tool_sd.matrix_basis=bpy.data.objects['TARGET_ToolGrip'].matrix_world.copy()
 for finger,val in zip(FINGERS,values['POSE_Grip_Screwdriver_R']): r.pose.bones[finger+'.01_master.R'].scale.y=val
 result={}
 for suffix in ['CW','CCW']:
  for tr in roll.animation_data.nla_tracks: tr.mute=True
  strip(roll,'C '+suffix,bpy.data.actions['TOOL_Screwdriver_'+suffix+'_R'],81,3)
  samples={}; tiperr=handerr=0
  for f in range(81,189):
   update(f); dg=bpy.context.evaluated_depsgraph_get(); p=r.evaluated_get(dg).pose.bones
   samples[f]=[list(row) for row in roll.matrix_world]
   handerr=max(handerr,(p['DEF-hand.R'].head-p['hand_ik.R'].head).length)
   if (f-81)%36<=21: tiperr=max(tiperr,(bpy.data.objects['REF_ScrewdriverTip'].evaluated_get(dg).matrix_world.translation-bpy.data.objects['TARGET_Screw'].matrix_world.translation).length)
  repeaterr=max(abs(samples[f][i][j]-samples[f+36][i][j]) for f in range(81,153) for i in range(4) for j in range(4))
  result[suffix]={'tip_error':tiperr,'hand_error':handerr,'repeat_error':repeaterr}; assert tiperr<.0001 and handerr<.003 and repeaterr<1e-5,result
 render('group_c_screwdriver',99)
 check_actions(names,'group_c_channels'); (OUT/'group_c_validation.json').write_text(json.dumps({'screwdriver':result,'pass':True},indent=2)); save('group_c.blend')
except: (OUT/'error_c.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
