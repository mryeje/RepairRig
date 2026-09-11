"""Production-only roll correction using standard Rigify manual X finger settings.
Run Blender --background --factory-startup --python this.py -- --preview (or --save).
Canonical and source production files are only read. No Action curves are edited.
"""
import bpy, addon_utils, json, math, hashlib, sys, re
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/hand_transfer'; OUT.mkdir(exist_ok=True)
SRC=ROOT/'blend/RepairRig_05_ProductionCharacter_Test.blend'
CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
DST=ROOT/'blend/RepairRig_05_ProductionCharacter_HandFixed.blend'
F=['f_index','f_middle','f_ring','f_pinky','thumb']
SAVE='--save' in sys.argv
if SAVE and DST.exists():
 prior=json.loads((OUT/'reopen_validation.json').read_text())['hashes_before'][str(DST)]
 assert hashlib.sha256(DST.read_bytes()).hexdigest()==prior, 'Corrected output has external changes; refusing overwrite'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SRC,CAN]}
addon_utils.enable('rigify',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(CAN),use_scripts=False)
cr=bpy.data.objects['RepairRig']
canonical={n:cr.data.bones[n].matrix_local.copy() for n in cr.data.bones.keys()}
asset=bpy.data.actions['POSE_Grip_Screwdriver_R'].asset_data
assetmeta={'description':asset.description,'author':asset.author,'catalog_id':asset.catalog_id,'tags':[t.name for t in asset.tags]}
bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
r=bpy.data.objects['RepairRig'];meta=bpy.data.objects['RepairRig_Metarig'];s=bpy.context.scene

def finger(n):return any(f in n for f in F)
def mats(m):return [list(row) for row in m]
def err(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def update():r.update_tag();bpy.context.view_layer.update()
def curves(a):return [fc for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
def payload():
 return {a.name:[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for fc in curves(a)] for a in bpy.data.actions}
def body_samples():
 ad=r.animation_data;act=ad.action;slot=ad.action_slot;frame=s.frame_current;result={}
 for a in [a for a in bpy.data.actions if a.name.startswith('BODY_')]:
  ad.action=a;ad.action_slot=a.slots[0]
  for f in sorted(set([int(a.frame_range[0]),int(sum(a.frame_range)/2),int(a.frame_range[1])])):
   s.frame_set(f);update();ep=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
   result[a.name+':'+str(f)]={p.name:p.matrix.copy() for p in ep if not finger(p.name)}
 ad.action=act
 if act:ad.action_slot=slot
 s.frame_set(frame);update();return result
visibility={o.name:o.hide_get() for o in bpy.data.objects}
before_payload=payload();before_bones={b.name:b.matrix_local.copy() for b in r.data.bones};before_heads={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in r.data.bones}
before_body=body_samples()
report={'inputs':hashes,'method':'manual_X_canonical_transport_roll_only','changes':{},'root_cause':{},'checks':{}}
# Independent mathematical replay of stock compute_chain_x_axis on the saved metarig.
for side in ['R','L']:
 for f in F:
  names=[f+'.%02d.'%i+side for i in [1,2,3]];b=meta.data.bones[names[0]]
  normal=b.matrix_local.to_3x3().col[1].cross(meta.data.bones[names[-1]].tail_local-b.head_local)
  fallback=normal.length<b.length/100
  if fallback:normal=b.matrix_local.to_3x3().col[0].copy()
  normal.normalize();rows=[]
  for n in names:
   mb=meta.data.bones[n];g=r.data.bones['ORG-'+n];my=mb.matrix_local.to_3x3().col[1];projected=(normal-my*normal.dot(my)).normalized()
   rows.append({'bone':n,'automatic_vs_generated_degrees':math.degrees(projected.angle(g.matrix_local.to_3x3().col[0])),
                'metarig_head_error':(mb.head_local-g.head_local).length,'metarig_tail_error':(mb.tail_local-g.tail_local).length})
  report['root_cause'][f+'.'+side]={'automatic_roll_fallback':fallback,'segments':rows}
# Define target X from canonical hand-relative basis, transported to fitted bone Y.
targets={}
for b in r.data.bones:
 if not finger(b.name):continue
 match=re.search(r'\.([LR])(?:\.\d+)?$',b.name);side=match[1] if match else None
 if side not in ['R','L']:continue
 ch=canonical['ORG-hand.'+side].to_3x3();ph=r.data.bones['ORG-hand.'+side].matrix_local.to_3x3()
 cb=canonical[b.name].to_3x3();cx=ch.inverted()@cb.col[0];cy=ch.inverted()@cb.col[1]
 py=ph.inverted()@b.matrix_local.to_3x3().col[1]
 targets[b.name]=ph@(cy.rotation_difference(py)@cx)

# One character-level thumb opposition calibration, shared by every Action.
# 55 degrees is the first passing sample in the 5-degree refined collision sweep.
if '--scan-thumb' not in sys.argv:
 from mathutils import Quaternion
 for n,x in list(targets.items()):
  if 'thumb' not in n:continue
  side=re.search(r'\.([LR])(?:\.\d+)?$',n)[1];sign=1 if side=='R' else -1
  if '.001' in n:sign*=-1
  y=r.data.bones[n].matrix_local.to_3x3().col[1]
  targets[n]=Quaternion(y,math.radians(55*sign))@x
 report['thumb_calibration_degrees']={'R':55,'L':-55}
def edit_rolls(obj, values):
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.object.mode_set(mode='EDIT')
 changes={}
 for n,x in values.items():
  b=obj.data.edit_bones[n];old=b.roll;head=b.head.copy();tail=b.tail.copy()
  # Blender align_roll takes target Z; X cross Y gives the corresponding Z.
  z=x.cross(b.y_axis).normalized();b.align_roll(z)
  assert (b.head-head).length<1e-7 and (b.tail-tail).length<1e-7
  changes[n]={'old_roll':old,'new_roll':b.roll,'x_error_degrees':math.degrees(b.x_axis.angle(x))}
 bpy.ops.object.mode_set(mode='OBJECT');return changes
report['changes']['generated']=edit_rolls(r,targets)
mt={n.removeprefix('ORG-'):x for n,x in targets.items() if n.startswith('ORG-')}
report['changes']['metarig']=edit_rolls(meta,mt)
for side in ['R','L']:
 for f in F:meta.pose.bones[f+'.01.'+side].rigify_parameters.primary_rotation_axis='X'
a=bpy.data.actions['POSE_Grip_Screwdriver_R'];a.asset_mark()
for k in ['description','author','catalog_id']:setattr(a.asset_data,k,assetmeta[k])
for tag in assetmeta['tags']:
 if tag not in a.asset_data.tags:a.asset_data.tags.new(tag)
update();after_body=body_samples()
report['checks']['all_action_payloads_unchanged']=before_payload==payload()
report['checks']['nonfinger_rest_matrices_unchanged']=max(err(before_bones[b.name],b.matrix_local) for b in r.data.bones if not finger(b.name))<1e-5
report['checks']['all_joint_positions_unchanged']=max(max((before_heads[b.name][0]-b.head_local).length,(before_heads[b.name][1]-b.tail_local).length) for b in r.data.bones)<1e-6
report['body_max_matrix_error']=max(err(mat,after_body[k][n]) for k,v in before_body.items() for n,mat in v.items())
report['checks']['body_animation_unchanged']=report['body_max_matrix_error']<1e-4
report['checks']['six_assets']=all(a.asset_data for a in bpy.data.actions if a.name.startswith('POSE_'))
report['checks']['target_axes_aligned']=max(v['x_error_degrees'] for v in report['changes']['generated'].values())<.1
report['nonfinger_rest_errors']={b.name:err(before_bones[b.name],b.matrix_local) for b in r.data.bones if not finger(b.name) and err(before_bones[b.name],b.matrix_local)>1e-7}
(OUT/'correction.json').write_text(json.dumps(report,indent=2))
assert all(report['checks'].values()),report['checks']
if '--scan-thumb' in sys.argv:
 sys.path.insert(0,str(ROOT/'scripts'))
 from hand_mesh_validation import prepare,inspect_pose
 mesh=bpy.data.objects['Chris-Low-poly'];prepared=prepare(mesh);scan={}
 base={n:r.data.bones[n].matrix_local.copy() for n in targets if 'thumb' in n}
 r.animation_data.action=None
 for p in r.pose.bones:
  if finger(p.name) and not p.name.startswith(('ORG-','DEF-','MCH-')):p.matrix_basis=Matrix.Identity(4)
 from mathutils import Quaternion
 for degrees in range(35,76,5):
  new={}
  for n,matrix in base.items():
   sign=-1 if '.001' in n else 1
   new[n]=Quaternion(matrix.to_3x3().col[1],math.radians(degrees*sign))@matrix.to_3x3().col[0]
  edit_rolls(r,new);update();scan[str(degrees)]={}
  for name in [a.name for a in bpy.data.actions if a.name.startswith('POSE_')]:
   a=bpy.data.actions[name];r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];s.frame_set(1);update()
   scan[str(degrees)][name]=inspect_pose(r,mesh,prepared)
  print('THUMB_SCAN',degrees,flush=True)
 (OUT/'thumb_refined_scan.json').write_text(json.dumps(scan,indent=2))
 bpy.ops.wm.quit_blender()
 raise SystemExit
# Save before disposable rendering changes, retaining source Action, frame and control values.
if SAVE:
 for name,hidden in visibility.items():bpy.data.objects[name].hide_set(hidden)
 bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(DST))
 report['saved_file']=str(DST)
(OUT/'correction.json').write_text(json.dumps(report,indent=2))
# Render all poses on the corrected production mesh, no additional scene saves.
ad=r.animation_data;ad.action=None
for tr in ad.nla_tracks:tr.mute=True
for p in r.pose.bones:
 if finger(p.name) and not p.name.startswith(('ORG-','DEF-','MCH-')):p.matrix_basis=Matrix.Identity(4)
update();mesh=bpy.data.objects['Chris-Low-poly']
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=(o!=mesh)
mesh.hide_render=False
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.65,.7,.8);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.08,.08,.08)
s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
cam=bpy.data.objects.new('AUDIT_Camera',bpy.data.cameras.new('AUDIT_Camera'));bpy.context.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.32
hp=r.pose.bones['DEF-hand.R'].matrix.copy();center=r.matrix_world@(hp@Vector((0,.105,0)))
for a in [a for a in bpy.data.actions if a.name.startswith('POSE_')]:
 ad.action=a;ad.action_slot=a.slots[0];s.frame_set(1);update()
 for label,v in [('palm',(1,0,0)),('oblique',(1,0,1)),('side',(0,0,1))]:
  cam.location=center+hp.to_3x3()@Vector(v).normalized()*.6;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('fixed_'+a.name+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
for p,h in hashes.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
bpy.ops.wm.quit_blender()







