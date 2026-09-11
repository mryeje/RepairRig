import bpy,json
from pathlib import Path
r=bpy.data.objects['RepairRig']
out={'bones':{},'objects':{},'ops':[]}
for p in r.pose.bones:
 if not p.name.startswith(('DEF-','MCH-','ORG-')):
  out['bones'][p.name]={'loc':list(p.location),'rot':list(p.rotation_quaternion),'scale':list(p.scale),'props':{k:str(v) for k,v in p.items()},'rest':[list(x) for x in p.bone.matrix_local],'constraints':[(c.name,c.type) for c in p.constraints]}
out['ops']=dir(bpy.ops.poselib)
Path('E:/RepairRig/tests/stage4').mkdir(exist_ok=True)
Path('E:/RepairRig/tests/stage4/probe.json').write_text(json.dumps(out,indent=2))
bpy.ops.wm.quit_blender()
