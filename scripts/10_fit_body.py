import bpy,json
from pathlib import Path
from mathutils import Quaternion
r=bpy.data.objects['RepairRig']; s=bpy.context.scene; a=bpy.data.actions['BODY_Kneel_L']; bag=a.layers[0].strips[0].channelbag(a.slots[0]); result=[]
bpy.data.objects['TARGET_Brace_L'].location.z=.75
for angle in (.35,.45,.55):
 for fc in bag.fcurves:
  if fc.data_path in ['pose.bones["torso"].rotation_quaternion','pose.bones["chest"].rotation_quaternion']:
   for k in fc.keyframe_points:
    t={1:0,16:0,38:.3,64:1,288:1}[round(k.co.x)]; k.co.y=Quaternion((1,0,0),(angle if 'torso' in fc.data_path else .25)*t)[fc.array_index]
   fc.update()
 for h in (.43,.48,.50):
  bpy.data.objects['TARGET_Screw'].location.z=h; errors=[]
  for f in (112,146,152,170,174,184,210,246):
   s.frame_set(f); r.update_tag(); bpy.context.view_layer.update(); p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
   errors.append({side:(p['hand_ik.'+side].head-p['DEF-hand.'+side].head).length for side in ('L','R')})
  result.append({'torso_angle':angle,'screw_height':h,'max_R':max(x['R'] for x in errors),'max_L':max(x['L'] for x in errors)})
Path('E:/RepairRig/tests/stage3_reach_fit2.json').write_text(json.dumps(result,indent=2))
