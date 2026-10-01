import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/grip_refined';OUT.mkdir(exist_ok=True)
F=['f_index','f_middle','f_ring','f_pinky','thumb'];result={}
for label,file in [('canonical','RepairRig_04_ActionLibrary.blend'),('production','RepairRig_05B_ProductionCharacter_ReachFixed.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend'/file),use_scripts=False);r=bpy.data.objects['RepairRig'];h=r.data.bones['DEF-hand.R'].matrix_local.inverted();d={'bones':{},'tools':{},'poses':{}}
 for p in r.pose.bones:
  if p.name.endswith('.R') and any(f in p.name for f in F) and not p.name.startswith(('MCH','ORG')):
   d['bones'][p.name]={'head':list(h@p.bone.head_local),'tail':list(h@p.bone.tail_local),'length':p.bone.length,'rotation_mode':p.rotation_mode,'lock_rotation':list(p.lock_rotation),'parent':p.parent.name if p.parent else None,'constraints':[{'name':c.name,'type':c.type} for c in p.constraints]}
 for name in ['Screwdriver_Handle','Pliers_Handle_-1','Pliers_Handle_1','ATTACH_Screwdriver_R','ATTACH_Pliers_R','TOOL_Pliers']:
  o=bpy.data.objects[name];d['tools'][name]={'matrix_in_hand':[list(row) for row in (r.matrix_world@r.pose.bones['DEF-hand.R'].matrix).inverted()@o.matrix_world],'dimensions':list(o.dimensions),'bounds':[list(v) for v in o.bound_box],'constraints':[{'name':c.name,'type':c.type,'influence':c.influence} for c in o.constraints]}
 for a in bpy.data.actions:
  if not a.name.startswith('POSE_'):continue
  d['poses'][a.name]=[(fc.data_path,fc.array_index,fc.evaluate(1)) for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
 result[label]=d
(OUT/'inspection.json').write_text(json.dumps(result,indent=2));print('PYTHON',sys.version);print('OUTPUT',OUT/'inspection.json');bpy.ops.wm.quit_blender()
