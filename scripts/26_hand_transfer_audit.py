"""Offline, non-saving hand audit. Run on copies in isolated Blender sessions.

--python scripts/26_hand_transfer_audit.py -- --label canonical
Does not edit rest bones, regenerate, change weights, or save a .blend.
"""
import bpy, addon_utils, json, hashlib, argparse, sys, traceback
from pathlib import Path
from mathutils import Matrix
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/hand_transfer'; OUT.mkdir(exist_ok=True)
args=argparse.ArgumentParser(); args.add_argument('--label',default='audit'); args.add_argument('--source')
opts=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
def serial(v):
 if isinstance(v,(str,int,float,bool)) or v is None: return v
 if isinstance(v,bpy.types.ID): return {'id':v.name,'type':v.bl_rna.identifier}
 try: return [serial(x) for x in v]
 except: return str(v)
def mat(m): return [list(row) for row in m]
def hand(n): return any(x in n for x in ['f_index','f_middle','f_ring','f_pinky','thumb','palm','hand'])
def fcurves(a): return [fc for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
def update(o): o.update_tag(); bpy.context.view_layer.update()
try:
 addon_utils.enable('rigify',default_set=True,persistent=True)
 if opts.source: bpy.ops.wm.open_mainfile(filepath=opts.source,use_scripts=False)
 out={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'version':bpy.app.version_string,'armatures':{},'pose_assets':{},'meshes':{}}
 for o in bpy.data.objects:
  if o.type=='MESH':
   out['meshes'][o.name]={'vertices':len(o.data.vertices),'armatures':[m.object.name if m.object else None for m in o.modifiers if m.type=='ARMATURE']}
  if o.type!='ARMATURE': continue
  entry={'matrix_world':mat(o.matrix_world),'data':o.data.name,'properties':{k:serial(v) for k,v in o.data.items()},'bones':{},'drivers':[],'samples':{}}
  out['armatures'][o.name]=entry
  for p in o.pose.bones:
   if not hand(p.name): continue
   b=p.bone; hname=next((n for n in ['ORG-hand'+p.name[-2:],'hand'+p.name[-2:],'hand_fk'+p.name[-2:]] if n in o.data.bones),None)
   palm=o.data.bones[hname].matrix_local if hname else Matrix.Identity(4)
   params={}
   for k in ['primary_rotation_axis','rotation_axis','make_extra_ik_control','ik_local_location','bbones','palm_both_sides']:
    if hasattr(p.rigify_parameters,k): params[k]=serial(getattr(p.rigify_parameters,k))
   cons=[]
   for c in p.constraints:
    vals={}
    for pr in c.bl_rna.properties:
     if pr.identifier=='rna_type' or pr.type=='COLLECTION': continue
     try: vals[pr.identifier]=serial(getattr(c,pr.identifier))
     except: pass
    cons.append(vals)
   entry['bones'][p.name]={'parent':b.parent.name if b.parent else None,'connected':b.use_connect,'deform':b.use_deform,'length':b.length,'head':list(b.head_local),'tail':list(b.tail_local),'rest_matrix':mat(b.matrix_local),'palm_reference':hname,'rest_in_palm':mat(palm.inverted_safe()@b.matrix_local),'rotation_mode':p.rotation_mode,'basis':mat(p.matrix_basis),'inherit_scale':b.inherit_scale,'rigify_type':p.rigify_type,'rigify_parameters':params,'properties':{k:serial(v) for k,v in p.items()},'constraints':cons}
  if o.animation_data:
   for fc in o.animation_data.drivers:
    if hand(fc.data_path): entry['drivers'].append({'path':fc.data_path,'index':fc.array_index,'expression':fc.driver.expression,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path,'bone':t.bone_target,'transform_type':t.transform_type,'transform_space':t.transform_space} for t in v.targets]} for v in fc.driver.variables]})
 # Inspect exact asset payload, not just pose names or authoring intentions.
 for a in bpy.data.actions:
  if a.name.startswith('POSE_'):
   out['pose_assets'][a.name]={'is_asset':bool(a.asset_data),'slots':[sl.identifier for sl in a.slots],'curves':[{'path':fc.data_path,'index':fc.array_index,'keys':[list(k.co) for k in fc.keyframe_points]} for fc in fcurves(a)]}
 # Evaluation-only experiment: same scalar input, measured rest-relative tip response.
 for o in bpy.data.objects:
  if o.type!='ARMATURE' or 'f_index.01_master.R' not in o.pose.bones: continue
  if o.animation_data:
   o.animation_data.action=None
   for tr in o.animation_data.nla_tracks: tr.mute=True
  for p in o.pose.bones:
   if hand(p.name) and not p.name.startswith(('DEF-','ORG-','MCH-')):
    p.matrix_basis=Matrix.Identity(4)
    if 'FK_IK' in p: p['FK_IK']=0
  for finger in ['f_index','f_middle','f_ring','f_pinky','thumb']:
   name=finger+'.01_master.R'
   if name not in o.pose.bones: continue
   entry=out['armatures'][o.name]['samples'][finger]={}
   for scale in [1,.95,.78,.70,.58,.48]:
    o.pose.bones[name].scale.y=scale; update(o)
    ep=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
    hp=next((ep[n].matrix for n in ['DEF-hand.R','ORG-hand.R','hand_fk.R'] if n in ep),Matrix.Identity(4))
    entry[str(scale)]={n:{'head_in_hand':list(hp.inverted_safe()@ep[n].head),'tail_in_hand':list(hp.inverted_safe()@ep[n].tail),'matrix_in_hand':mat(hp.inverted_safe()@ep[n].matrix)} for n in [f'DEF-{finger}.{i:02}.R' for i in [1,2,3]] if n in ep}
   o.pose.bones[name].scale.y=1; update(o)
 out['status']='audit_complete_no_correction'
 (OUT/(opts.label+'.json')).write_text(json.dumps(out,indent=2))
except: (OUT/(opts.label+'_error.txt')).write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
