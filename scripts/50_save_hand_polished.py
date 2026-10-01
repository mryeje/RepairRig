import sys,hashlib,struct,copy
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
from mathutils.kdtree import KDTree
CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload():return {a.name:[(f.data_path,f.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in f.keyframe_points]) for f in curves(a)] for a in bpy.data.actions}
def rest():return {o.name:{b.name:[list(row) for row in b.matrix_local] for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}
def geom(m):
 h=hashlib.sha256()
 for v in m.data.vertices:h.update(struct.pack('3f',*v.co))
 for p in m.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
def transforms():return {o.name:[list(row) for row in o.matrix_basis] for o in bpy.data.objects if o.name.startswith(('TOOL_','CONTACT_','ATTACH_','REF_','TARGET_','SCREW_'))}
assert not DST.exists(),'Refusing to overwrite checkpoint'
r,m=load();prep=prepare(m);before_actions=payload();before_rest=rest();before_geo=geom(m);before_trans=transforms();before_ui=bpy.data.texts['RepairRig_Tools_UI.py'].as_string();hashes={str(p):sha(p) for p in (SRC,CAN)}
original={v.index:{m.vertex_groups[g.group].name:g.weight for g in v.groups} for v in m.data.vertices}
changes=json.loads((OUT/'accepted_weights_right.json').read_text());tree=KDTree(len(m.data.vertices))
for v in m.data.vertices:tree.insert(r.matrix_world.inverted()@m.matrix_world@v.co,v.index)
tree.balance();mirrored={};unmatched=[]
for vid,ws in list(changes.items()):
 p=r.matrix_world.inverted()@m.matrix_world@m.data.vertices[int(vid)].co;p.x=-p.x
 co,idx,dist=tree.find(p)
 if dist>5e-5:unmatched.append([int(vid),dist]);continue
 target={n.replace('.R','.L'):dict(v) for n,v in ws.items()}
 # Apply the same normalized redistribution delta, not unrelated right-side weights.
 old=original[idx];new=dict(old)
 for rn,v in ws.items():
  ln=rn.replace('.R','.L');new[ln]=max(0,old.get(ln,0)+v['after']-v['before'])
 deform=[n for n in new if n in r.data.bones and r.data.bones[n].use_deform];total=sum(new[n] for n in deform)
 for n in deform:new[n]/=total
 mirrored[str(idx)]={n:{'before':old.get(n,0),'after':w} for n,w in new.items()}
changes.update(mirrored)
for vid,ws in changes.items():
 for n,v in ws.items():m.vertex_groups[n].add([int(vid)],v['after'],'REPLACE')
m.data.update();update()
fit=json.loads((OUT/'pose_refinement.json').read_text());params=fit['refined_angles'];ring_scan=[]
# Additional local test: preserve total curl, move excessive PIP bend into MCP.
for short in ('Fist','Point'):
 pose(short);orig=fit['original_angles'][short]['f_ring'];choices=[]
 for shift in (12,15,18,21,24):
  vals=list(orig);vals[0]+=shift;vals[1]-=shift
  for j in (1,2,3):r.pose.bones['f_ring.%02d.R'%j].rotation_quaternion=Euler(tuple(math.radians(v) for v in ([vals[0],vals[4],vals[3]] if j==1 else [vals[j-1],0,0]))).to_quaternion()
  update();d=inspect_pose(r,m,prep);score=sum(v for k,v in d['intersection_categories'].items() if k!='palm/palm');choices.append((score+shift*.015,vals,d,shift))
 best=min(choices,key=lambda x:x[0]);params[short]['f_ring']=best[1];ring_scan.append({'pose':short,'shift':best[3],'geometry':best[2]})
changed_actions=[]
for short in ('Fist','Point','Grip_Pliers'):
 a=bpy.data.actions['POSE_'+short+'_R_Production'];changed_actions.append(a.name)
 for f in F:
  vals=params[short][f]
  if short!='Grip_Pliers' and f!='f_ring':continue
  for j in (1,2,3):
   q=Euler(tuple(math.radians(v) for v in ([vals[0],vals[4],vals[3]] if j==1 else [vals[j-1],0,0])),'XYZ').to_quaternion();path='pose.bones["'+f+'.%02d.R'%j+'"].rotation_quaternion'
   for fc in curves(a):
    if fc.data_path==path:
     for k in fc.keyframe_points:
      delta=q[fc.array_index]-k.co.y;k.co.y+=delta;k.handle_left.y+=delta;k.handle_right.y+=delta
     fc.update()
pose('Grip_Pliers')
assert all(payload()[n]==v for n,v in before_actions.items() if n not in changed_actions)
assert rest()==before_rest and geom(m)==before_geo and transforms()==before_trans
assert bpy.data.texts['RepairRig_Tools_UI.py'].as_string()==before_ui
assert all(abs(sum(g.weight for g in m.data.vertices[int(i)].groups if m.vertex_groups[g.group].name in r.data.bones and r.data.bones[m.vertex_groups[g.group].name].use_deform)-1)<1e-5 for i in changes)
report={'input_hashes':hashes,'output':str(DST),'changed_actions':changed_actions,'weights_right':len(changes)-len(mirrored),'weights_left':len(mirrored),'unmatched_mirror':unmatched,'ring_scan':ring_scan,'original_angles':fit['original_angles'],'final_angles':params,'original_actions':before_actions,'rest':before_rest,'geometry_hash':before_geo,'tool_transforms':before_trans,'ui_sha256':hashlib.sha256(before_ui.encode()).hexdigest(),'weight_changes':changes}
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DST));report['output_sha256']=sha(DST)
(OUT/'checkpoint.json').write_text(json.dumps(report,indent=2));print('SAVED_STAGE5F',len(changes),'weights',[(x['pose'],x['shift'],x['geometry']['self_intersection_triangle_pairs']) for x in ring_scan],flush=True)
