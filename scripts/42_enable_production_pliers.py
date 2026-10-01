"""Select pliers using the existing Child Of workflow; no Action or rig redesign."""
import bpy,json,hashlib,traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/pliers_attach';SRC=ROOT/'blend/RepairRig_05C_ProductionCharacter_GripRefined.blend';DST=ROOT/'blend/RepairRig_05D_ProductionCharacter_PliersAttach.blend';CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mat(m):return [list(row) for row in m]
def err(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def update():
 for n in ['RepairRig','TOOL_Pliers','TOOL_Screwdriver']:bpy.data.objects[n].update_tag()
 bpy.context.view_layer.update()
def world(o):return o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
def curves(a):return [fc for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for fc in b.fcurves]
def actions():return {a.name:[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for fc in curves(a)] for a in bpy.data.actions}
def assign(r,name,frame):
 a=bpy.data.actions[name];r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(frame);update()
try:
 assert not DST.exists(),'Refusing to overwrite existing checkpoint'
 hashes={str(p):sha(p) for p in [SRC,CAN]};bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
 r=bpy.data.objects['RepairRig'];pl=bpy.data.objects['TOOL_Pliers'];sd=bpy.data.objects['TOOL_Screwdriver'];pc=pl.constraints['Attach / release | pliers right socket'];sc=sd.constraints['Attach / release | right hand socket']
 before_actions=actions();source_sd=world(sd);source_parked=world(pl);old_action=r.animation_data.action;old_slot=r.animation_data.action_slot;old_frame=bpy.context.scene.frame_current
 before_rest={o.name:{b.name:mat(b.matrix_local) for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}
 report={'source':str(SRC),'inputs':hashes,'changes':{'TOOL_Pliers.constraint.influence':[pc.influence,1.0],'TOOL_Screwdriver.constraint.influence':[sc.influence,0.0]},'source_parked_pliers':mat(source_parked)}
 pc.influence=1;sc.influence=0;update()
 socket=world(pc.target);attached=world(pl);offset=socket.inverted()@attached
 report['attached_socket_relative_matrix']=mat(offset);report['movement_from_parked']=(attached.translation-source_parked.translation).length
 assert report['movement_from_parked']>.01
 # Apply existing pose values as an unkeyed state, preserving the active reach Action.
 pose=bpy.data.actions['POSE_Grip_Pliers_R_Production']
 for fc in curves(pose):
  value=r.path_resolve(fc.data_path);value[fc.array_index]=fc.evaluate(1)
 update()
 report['applied_existing_pose']=pose.name
 bpy.context.view_layer.objects.active=r
 assert actions()==before_actions
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DST))
 bpy.ops.wm.open_mainfile(filepath=str(DST),use_scripts=False)
 r=bpy.data.objects['RepairRig'];pl=bpy.data.objects['TOOL_Pliers'];sd=bpy.data.objects['TOOL_Screwdriver'];pc=pl.constraints['Attach / release | pliers right socket'];sc=sd.constraints['Attach / release | right hand socket']
 checks={'pliers_enabled':pc.influence==1,'screwdriver_disabled_only_for_saved_tool_selection':sc.influence==0,'all_actions_identical':actions()==before_actions,'rest_matrices_identical':before_rest=={o.name:{b.name:mat(b.matrix_local) for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}}
 samples={}
 for f in [1,17,33]:
  bpy.context.scene.frame_set(f);update();actual=world(pl);target=world(pc.target)
  samples[str(f)]={'position':list(actual.translation),'relative_error':err(target.inverted()@actual,offset)}
 checks['pliers_follow_moving_hand']=max(v['relative_error'] for v in samples.values())<1e-4 and (Vector(samples['1']['position'])-Vector(samples['33']['position'])).length>.01
 bpy.context.scene.frame_set(old_frame);update();pc.influence=0;update();checks['detach_returns_to_parked_transform']=err(world(pl),source_parked)<1e-5
 pc.influence=1;update();checks['reattach_restores_grip']=err(world(pc.target).inverted()@world(pl),offset)<1e-4
 pc.influence=0;sc.influence=1;update();checks['screwdriver_can_be_reenabled']=err(world(sd),source_sd)<1e-5
 checks['inputs_unchanged']=all(sha(Path(n))==h for n,h in hashes.items())
 report['motion_samples']=samples;report['checks']=checks;assert all(checks.values()),checks
 report['output']=str(DST);report['sha256']=sha(DST);report['pass']=True
 (OUT/'correction_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
except:
 (OUT/'error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
bpy.ops.wm.quit_blender()
