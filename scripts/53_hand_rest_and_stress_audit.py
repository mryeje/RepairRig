"""Separate rest-mesh, neutral-control, and extreme-amplitude diagnostics."""
import sys
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
report={}
for label,path in (('before',SRC),('after',DST)):
 r,m=load(path);prep=prepare(m);pose('OpenHand');item={}
 item['neutral_controls']=metrics(r,m,prep)
 r.data.pose_position='REST';update();item['rest_mesh']=metrics(r,m,prep)
 r.data.pose_position='POSE';update()
 for f in F:
  for j,angle in ((1,65),(2,80),(3,45)):r.pose.bones[f+'.%02d.R'%j].rotation_quaternion=Euler((math.radians(angle),0,0)).to_quaternion()
 update();item['synthetic_stress']=metrics(r,m,prep);report[label]=item
 print(label,'REST',item['rest_mesh']['intersection_categories'],'STRESS',item['synthetic_stress']['self_intersection_triangle_pairs'],flush=True)
(OUT/'rest_stress_validation.json').write_text(json.dumps(report,indent=2))
