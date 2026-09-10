import bpy,json
from pathlib import Path
rig=bpy.data.objects['RepairRig']
names=['torso','hips','chest','head','hand_ik.R','hand_ik.L','foot_ik.R','foot_ik.L','thigh_ik_target.L','thigh_ik_target.R','upper_arm_ik_target.L','upper_arm_ik_target.R']
names += [b.name for b in rig.pose.bones if b.name.startswith(('DEF-thigh','DEF-shin','DEF-foot','DEF-hand','DEF-forearm','DEF-upper_arm','DEF-f_index','DEF-thumb'))]
Path('E:/RepairRig/tests/stage3_inventory.json').write_text(json.dumps({n:{'head':list(rig.pose.bones[n].head),'tail':list(rig.pose.bones[n].tail),'matrix':[list(r) for r in rig.pose.bones[n].matrix],'props':{k:rig.pose.bones[n][k] for k in rig.pose.bones[n].keys() if isinstance(rig.pose.bones[n][k],(str,int,float,bool))}} for n in names},indent=2))
