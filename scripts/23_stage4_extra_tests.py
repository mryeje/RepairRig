import sys,traceback,runpy,importlib
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 out={}; update(179); roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R']
 def bm(n): return r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones[n].matrix.copy()
 body=bm('torso'); brace=bm('DEF-hand.L'); before=roll.matrix_world.copy(); tr=roll.animation_data.nla_tracks[0]; tr.mute=True; roll.rotation_euler.z=0; roll.location.z=0; update(185)
 err=lambda a,b:max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
 out['layer_isolation']={'body_error':err(body,bm('torso')),'brace_error':err(brace,bm('DEF-hand.L')),'tool_changed':err(before,roll.matrix_world)}
 assert out['layer_isolation']['body_error']<1e-6 and out['layer_isolation']['brace_error']<1e-6 and out['layer_isolation']['tool_changed']>.01
 out['loops']={}
 for name in ['BODY_Idle_Standing','TOOL_Screwdriver_CW_R','TOOL_Screwdriver_CCW_R','TOOL_Pliers_Squeeze_R']:
  reset(); a=bpy.data.actions[name]; owner=bpy.data.objects[a['owner']]; st=strip(owner,'Test '+name,a,1,3); period=int(a.frame_range[1]-a.frame_range[0]); values={}
  for f in range(1,period*3+1):
   update(f); row=[]
   for fc in curves(a):
    v=owner.path_resolve(fc.data_path)
    try: row.append(float(v[fc.array_index]))
    except TypeError: row.append(float(v))
   values[f]=row
  e=max(abs(x-y) for f in range(1,period*2+1) for x,y in zip(values[f],values[f+period])); assert e<1e-6
  out['loops'][name]={'period':period,'repeat':3,'max_channel_error':e}
 # Body variants: actual stationary feet and staged support through complete clip.
 out['body_variants']={}
 for name in ['BODY_Bend_Forward','BODY_Crouch_Shallow','BODY_Kneel_L','BODY_Kneel_R','BODY_Stand_From_Kneel_L']:
  reset(); a=bpy.data.actions[name]; assign(a); leg=0; nearest=0; end=int(a.frame_range[1]); feet={}
  for f in range(1,end+17):
   update(f); p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
   for side in ['L','R']: leg=max(leg,(p['DEF-foot.'+side].head-p['foot_ik.'+side].head).length)
   nearest=max(nearest,min(abs(p['foot_ik.'+side].head.z-.0852) for side in ['L','R']))
   if f>=end: feet[f]=[p['DEF-foot.'+side].head.copy() for side in ['L','R']]
  drift=max((feet[f][i]-feet[end][i]).length for f in feet for i in [0,1]); assert leg<.003 and nearest<.0001 and drift<.0001
  out['body_variants'][name]={'leg_error':leg,'support_height_error':nearest,'hold_foot_drift':drift}
 out['pass']=True; (OUT/'additional_validation.json').write_text(json.dumps(out,indent=2))
 # Restore final shot for close visual review, never save test mutations.
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_04_ActionLibrary.blend'),use_scripts=True)
 import stage4_common; importlib.reload(stage4_common)
 r=bpy.data.objects['RepairRig']; s=bpy.context.scene; s.frame_set(179); bpy.context.view_layer.update()
 cam=bpy.data.objects['CAM_Grip_Detail']; s.camera=cam; center=r.pose.bones['hand_ik.R'].head+Vector((0,0,.065))
 cam.location=center+Vector((-.38,.42,.25)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=.42
 tool=bpy.data.objects['TOOL_Screwdriver']; tool.constraints[0].influence=0; tool.location=(2,2,2)
 s.render.resolution_x=480; s.render.resolution_y=480
 for name in json.loads((OUT/'pose_values.json').read_text()):
  a=bpy.data.actions[name]; r.animation_data.action=a; r.animation_data.action_slot=a.slots[0]; s.frame_set(179); r.update_tag(); bpy.context.view_layer.update()
  s.render.filepath=str(OUT/(name+'.png')); bpy.ops.render.render(write_still=True)
except: (OUT/'error_extra.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
