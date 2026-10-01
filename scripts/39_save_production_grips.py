"""Create six character-specific static assets; preserve original library and rig."""
import sys,json,hashlib,struct,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from production_grip_common import *
DST=ROOT/'blend/RepairRig_05C_ProductionCharacter_GripRefined.blend';CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def curves(a):return [fc for l in a.layers for st in l.strips for sl in a.slots if (b:=st.channelbag(sl)) for fc in b.fcurves]
def payload():return {a.name:[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for fc in curves(a)] for a in bpy.data.actions}
def rest():return {o.name:{b.name:[list(row) for row in b.matrix_local] for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}
def mesh_hash():
 h=hashlib.sha256();o=bpy.data.objects['Chris-Low-poly']
 for v in o.data.vertices:
  h.update(struct.pack('3f',*v.co))
  for g in v.groups:h.update(struct.pack('If',g.group,g.weight))
 for p in o.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
def assign(r,name,frame):
 a=bpy.data.actions[name];r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(frame);update(r)
try:
 assert not DST.exists(),'Refusing to overwrite an existing checkpoint'
 p=json.loads((OUT/'final_parameters.json').read_text());report={'inputs':{str(x):sha(x) for x in [SRC,CAN]},'parameters':p['poses'],'variants':[]}
 bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False);r=bpy.data.objects['RepairRig'];before_actions=payload();before_rest=rest();before_mesh=mesh_hash()
 # Establish a reachable work posture before fitting the sockets to the real wrist frame.
 assign(r,'BODY_Kneel_L',49);assign(r,'REACH_Forward_Low_R',33)
 ik=r.matrix_world@r.pose.bones['hand_ik.R'].matrix
 sock=bpy.data.objects['ATTACH_Screwdriver_R'];old=ik.inverted()@sock.matrix_world;new=Matrix(p['screwdriver_socket_in_hand'])
 report['socket_changes']={};report['contact_offset_changes']={}
 # Preserve the tool's engaged work/pickup transform while changing its hand-relative fit.
 for name in ['CONTACT_WorkWrist_R','CONTACT_PickupWrist_R']:
  o=bpy.data.objects[name];before=o.matrix_world.copy();after=before@old@new.inverted();o.matrix_world=after
  report['contact_offset_changes'][name]={'before':[list(row) for row in before],'after':[list(row) for row in after]}
 # Avoid a dependency-graph update until the matching socket transform has been set.
 before=sock.matrix_basis.copy();sock.matrix_world=ik@new;report['socket_changes'][sock.name]={'basis_before':[list(row) for row in before],'basis_after':[list(row) for row in sock.matrix_basis]}
 # Other attachment uses the same unchanged native hand reference.
 ps=bpy.data.objects['ATTACH_Pliers_R'];before=ps.matrix_basis.copy();ps.matrix_world=ik@Matrix(p['pliers_socket_in_hand']);report['socket_changes'][ps.name]={'basis_before':[list(row) for row in before],'basis_after':[list(row) for row in ps.matrix_basis]}
 update(r)
 # Each asset fully specifies only the 20 right finger controls, including reset channels.
 r.animation_data.action=None
 for short,pose in p['poses'].items():
  name='POSE_'+short+'_R_Production';a=bpy.data.actions.new(name);a.use_fake_user=True;a.slots.new(id_type='OBJECT',name=r.name);r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];apply(r,pose)
  for n in CONTROLS:
   control=r.pose.bones[n]
   for channel in ['location','rotation_quaternion','scale']:control.keyframe_insert(channel,frame=1,group=n)
  a.asset_mark();a.asset_data.description='Production Chris hand: '+short+'. Apply all 20 right finger controls. Preserves wrist. '+('Relaxed closure; tight fist limited by current joint/skin fit.' if short=='Fist' else '')
  a.asset_data.author='RepairRig';a.asset_data.tags.new('Production Hand');a.asset_data.tags.new('Right Hand');a['source_pose']='POSE_'+short+'_R';a['character']='Chris-Low-poly';a['scope']='20 right finger controls; no arm/wrist channels';a['required_controls']=json.dumps(CONTROLS)
  source=bpy.data.actions.get('POSE_'+short+'_R')
  if source and source.asset_data:a.asset_data.catalog_id=source.asset_data.catalog_id
  report['variants'].append(name)
 # Open the checkpoint at a useful, reachable screwdriver inspection pose.
 assign(r,'BODY_Kneel_L',49);assign(r,'REACH_Forward_Low_R',33);apply(r,p['poses']['Grip_Screwdriver'])
 bpy.data.objects['TOOL_Pliers'].constraints[0].influence=0
 report['preservation']={'original_actions_identical':all(payload()[n]==v for n,v in before_actions.items()),'all_rest_matrices_identical':rest()==before_rest,'mesh_topology_weights_identical':mesh_hash()==before_mesh}
 assert all(report['preservation'].values()),report['preservation']
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DST))
 bpy.ops.wm.open_mainfile(filepath=str(DST),use_scripts=False)
 report['reopen']={'original_actions_identical':all(payload()[n]==v for n,v in before_actions.items()),'all_rest_matrices_identical':rest()==before_rest,'mesh_topology_weights_identical':mesh_hash()==before_mesh,'six_assets':all(bpy.data.actions[n].asset_data for n in report['variants']),'inputs_unchanged':all(sha(Path(n))==v for n,v in report['inputs'].items())}
 assert all(report['reopen'].values()),report['reopen'];report['output']=str(DST);report['sha256']=sha(DST)
 (OUT/'saved_checkpoint.json').write_text(json.dumps(report,indent=2));print('SAVED',report['output'],report['reopen'],flush=True)
except:
 (OUT/'save_error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
bpy.ops.wm.quit_blender()
