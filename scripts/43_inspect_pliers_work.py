"""Read-only Stage 5D work-point and socket inspection."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/pliers_aligned';OUT.mkdir(exist_ok=True);SRC=ROOT/'blend/RepairRig_05D_ProductionCharacter_PliersAttach.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False);bpy.context.view_layer.update()
def mat(m):return [list(r) for r in m]
d={'file':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'frame':bpy.context.scene.frame_current,'objects':{}}
names=['RepairRig','REF_Hand_R','TOOL_Screwdriver','TOOL_Pliers','ATTACH_Screwdriver_R','ATTACH_Pliers_R','REF_ScrewdriverTip','TARGET_Screw','CONTACT_ScrewdriverRoll_R','CONTACT_WorkGrip_R','CONTACT_WorkWrist_R','SCREW_Visible','Pliers_Jaw_-1','Pliers_Jaw_1','Pliers_JawPivot_-1','Pliers_JawPivot_1']
for n in names:
 o=bpy.data.objects[n];d['objects'][n]={'parent':o.parent.name if o.parent else None,'matrix_basis':mat(o.matrix_basis),'matrix_world':mat(o.matrix_world),'dimensions':list(o.dimensions),'rotation_euler':list(o.rotation_euler)}
tips=[bpy.data.objects['Pliers_Jaw_'+str(i)].matrix_world@Vector((0,0,.5)) for i in [-1,1]]
mid=(tips[0]+tips[1])*.5;target=bpy.data.objects['TARGET_Screw'].matrix_world.translation
d['pliers_distal_midpoint_world']=list(mid);d['pliers_distal_midpoint_local']=list(bpy.data.objects['TOOL_Pliers'].matrix_world.inverted()@mid);d['distance_to_screw']=(mid-target).length;d['jaw_tip_points_world']=[list(p) for p in tips]
d['tool_related_objects']=[o.name for o in bpy.data.objects if any(s in o.name.lower() for s in ['plier','tip','contact','screw','attach'])]
r=bpy.data.objects['RepairRig'];d['hand_work_constraint']=[{'name':c.name,'target':c.target.name if getattr(c,'target',None) else None,'type':c.type,'influence':c.influence} for c in r.pose.bones['hand_ik.R'].constraints]
d['active_action']=r.animation_data.action.name if r.animation_data.action else None
(OUT/'inspection.json').write_text(json.dumps(d,indent=2))
print(json.dumps({'frame':d['frame'],'active_action':d['active_action'],'pliers_contact_world':d['pliers_distal_midpoint_world'],'pliers_contact_local':d['pliers_distal_midpoint_local'],'target_world':list(target),'distance':d['distance_to_screw'],'objects':d['tool_related_objects'],'hand_work_constraint':d['hand_work_constraint']},indent=2));bpy.ops.wm.quit_blender()
