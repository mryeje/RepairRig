import bpy,json
from pathlib import Path
r=bpy.data.objects['RepairRig']; bpy.context.scene.frame_set(170); bpy.context.view_layer.update()
p=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
Path('E:/RepairRig/tests/stage3_pose_diagnostic.json').write_text(json.dumps({n:{'head':list(p[n].head),'scale':list(p[n].scale),'loc':list(p[n].location),'props':{k:p[n][k] for k in p[n].keys() if isinstance(p[n][k],(int,float,bool))}} for n in ['torso','chest','DEF-spine.003','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L','DEF-hand.L','hand_ik.L','DEF-hand.R','hand_ik.R','upper_arm_parent.L','upper_arm_parent.R']},indent=2))
