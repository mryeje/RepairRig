"""Targeted native-constraint and saved wrist-pose repair; immutable input files."""
import bpy, json, hashlib, math, traceback
from pathlib import Path
from mathutils import Matrix
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/reach_fixed'; OUT.mkdir(exist_ok=True)
CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
SRC=ROOT/'blend/RepairRig_05_ProductionCharacter_HandFixed.blend'
DST=ROOT/'blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend'
REQUIRED={'R':['Pickup | TARGET_ToolGrip','Work | TARGET_Screw','Reach | Mid_R'], 'L':['Brace | TARGET_Brace_L','Reach | Low_L']}
def mat(m):return [list(row) for row in m]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def curves(a):return [fc for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
def payload():return {a.name:[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for fc in curves(a)] for a in bpy.data.actions}
def constraint(c):
 props={}
 for p in c.bl_rna.properties:
  n=p.identifier
  if n in ['rna_type','type'] or p.is_readonly:continue
  v=getattr(c,n)
  if p.type=='POINTER':props[n]={'object':v.name} if v else None
  elif isinstance(v,Matrix):props[n]={'matrix':mat(v)}
  elif getattr(p,'is_array',False):props[n]=list(v)
  elif isinstance(v,(str,int,float,bool)):props[n]=v
 return {'name':c.name,'type':c.type,'properties':props}
def rest():return {o.name:{b.name:mat(b.matrix_local) for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}
def mesh_hash():
 import struct
 h=hashlib.sha256();o=bpy.data.objects['Chris-Low-poly']
 for v in o.data.vertices:
  h.update(struct.pack('3f',*v.co))
  for g in v.groups:h.update(struct.pack('If',g.group,g.weight))
 for p in o.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
try:
 if DST.exists():
  prior=json.loads((OUT/'correction.json').read_text())
  assert digest(DST)==prior['output_sha256'],'Output changed externally; refusing overwrite'
 report={'input_hashes':{str(p):digest(p) for p in [CAN,SRC]}}
 bpy.ops.wm.open_mainfile(filepath=str(CAN),use_scripts=False)
 # Capture the workflow's idle defaults, not frame 179's animated engaged contact state.
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 report['canonical_defaults_frame']=1
 r=bpy.data.objects['RepairRig'];canonical={};settings={}
 for side,names in REQUIRED.items():
  canonical[side]=[constraint(c) for c in r.pose.bones['hand_ik.'+side].constraints if c.name in names]
  assert set(c['name'] for c in canonical[side])==set(names)
  settings[side]={k:r.pose.bones['upper_arm_parent.'+side][k] for k in ['pole_vector','IK_Stretch']}
 report['canonical_constraints']=canonical;report['canonical_arm_settings']=settings
 bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
 r=bpy.data.objects['RepairRig'];before_rest=rest();before_actions=payload();before_mesh=mesh_hash()
 report['saved_frame']=bpy.context.scene.frame_current;report['pose_before']={side:{'location':list(r.pose.bones['hand_ik.'+side].location),'rotation_mode':r.pose.bones['hand_ik.'+side].rotation_mode,'quaternion':list(r.pose.bones['hand_ik.'+side].rotation_quaternion),'scale':list(r.pose.bones['hand_ik.'+side].scale),'basis':mat(r.pose.bones['hand_ik.'+side].matrix_basis)} for side in ['L','R']}
 report['arm_settings_before']={side:{k:r.pose.bones['upper_arm_parent.'+side][k] for k in settings[side]} for side in settings}
 for side,items in canonical.items():
  p=r.pose.bones['hand_ik.'+side];assert len(p.constraints)==0
  for item in items:
   c=p.constraints.new(item['type'])
   for n,v in item['properties'].items():
    if isinstance(v,dict) and 'object' in v:
     assert v['object'] in bpy.data.objects, 'Missing existing target '+v['object']
     v=bpy.data.objects[v['object']]
    elif isinstance(v,dict) and 'matrix' in v:v=Matrix(v['matrix'])
    setattr(c,n,v)
  for k,v in settings[side].items():r.pose.bones['upper_arm_parent.'+side][k]=v
 # Both fitted rest bases are exact mirrors. Remove only the left's extra local-Y half-turn.
 left=r.pose.bones['hand_ik.L'];right=r.pose.bones['hand_ik.R'];S=Matrix.Diagonal((-1,1,1))
 desired=S@right.rotation_quaternion.to_matrix()@S
 delta=desired.inverted()@left.rotation_quaternion.to_matrix()
 report['left_extra_rotation']={'angle_degrees':math.degrees(delta.to_quaternion().angle),'axis':list(delta.to_quaternion().axis),'matrix':mat(delta)}
 assert abs(math.degrees(delta.to_quaternion().angle)-180)<.01
 assert abs(abs(delta.to_quaternion().axis.y)-1)<1e-5
 left.rotation_quaternion=desired.to_quaternion()
 r.update_tag();bpy.context.view_layer.update()
 report['pose_after']={side:{'location':list(r.pose.bones['hand_ik.'+side].location),'quaternion':list(r.pose.bones['hand_ik.'+side].rotation_quaternion),'scale':list(r.pose.bones['hand_ik.'+side].scale)} for side in ['L','R']}
 report['checks']={'rest_matrices_unchanged':rest()==before_rest,'actions_unchanged':payload()==before_actions,'mesh_topology_weights_unchanged':mesh_hash()==before_mesh,'constraints_match_canonical':all([constraint(c) for c in r.pose.bones['hand_ik.'+side].constraints]==canonical[side] for side in canonical)}
 assert all(report['checks'].values()),report['checks']
 report['invalid_action_paths']=[]
 for name in ['REACH_Forward_Low_R','REACH_Forward_Mid_R','REACH_Forward_Low_L','BRACE_Forward_L']:
  for fc in curves(bpy.data.actions[name]):
   try:r.path_resolve(fc.data_path)
   except:report['invalid_action_paths'].append([name,fc.data_path])
 assert not report['invalid_action_paths']
 bpy.ops.wm.save_as_mainfile(filepath=str(DST))
 bpy.ops.wm.open_mainfile(filepath=str(DST),use_scripts=False)
 r=bpy.data.objects['RepairRig']
 report['reopen_checks']={'rest_matrices_unchanged':rest()==before_rest,'actions_unchanged':payload()==before_actions,'mesh_topology_weights_unchanged':mesh_hash()==before_mesh,'constraints_match_canonical':all([constraint(c) for c in r.pose.bones['hand_ik.'+side].constraints]==canonical[side] for side in canonical),'arm_settings_match':all(r.pose.bones['upper_arm_parent.'+side][k]==v for side in settings for k,v in settings[side].items()),'inputs_unchanged':all(digest(Path(p))==h for p,h in report['input_hashes'].items())}
 assert all(report['reopen_checks'].values()),report['reopen_checks']
 report['output']=str(DST);report['output_sha256']=digest(DST)
 (OUT/'correction.json').write_text(json.dumps(report,indent=2))
 print('CORRECTION_SAVED_AND_REOPENED',report['reopen_checks'],flush=True)
except:
 (OUT/'correction_error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
bpy.ops.wm.quit_blender()
