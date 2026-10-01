import sys
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
r,m=load();prep=prepare(m);names={g.index:g.name for g in m.vertex_groups}
report={'modifiers':[{p:getattr(mod,p,None) for p in ('name','type','use_deform_preserve_volume','levels','render_levels')} for mod in m.modifiers],'mesh':{'vertices':len(m.data.vertices),'faces':len(m.data.polygons),'hand_triangles':len(prep[0])},'bones':{},'weights':{},'poses':{}}
for f in F:
 for j in (1,2,3):
  n='DEF-'+f+'.%02d.R'%j;b=r.data.bones[n];report['bones'][n]={'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length,'matrix':[list(row) for row in b.matrix_local]}
for f in F+['palm']:
 ids=[v.index for v in m.data.vertices if prep[2][v.index]==f];cross=[];un=[];dominant=[]
 for i in ids:
  gs={names[g.group]:g.weight for g in m.data.vertices[i].groups if g.weight>1e-5};total=sum(w for n,w in gs.items() if n in r.data.bones and r.data.bones[n].use_deform)
  if abs(total-1)>.001:un.append([i,total])
  other=sum(w for n,w in gs.items() if any(ff in n for ff in F if ff!=f))
  if other>.01:cross.append([i,other,gs])
  dominant.append(max(gs.values(),default=0))
 report['weights'][f]={'vertices':len(ids),'cross_finger_over_001':len(cross),'cross_samples':cross[:12],'unnormalized':un[:30],'rigid_over_098':sum(w>.98 for w in dominant)}
for short in POSES:
 pose(short);report['poses'][short]=metrics(r,m,prep)
 for view in ('palm','side'):render_hand(r,m,prep,'before_'+short,'Pliers_' if short=='Grip_Pliers' else 'Screwdriver_' if short=='Grip_Screwdriver' else None,view)
 print(short,report['poses'][short]['self_intersection_triangle_pairs'],flush=True)
# A controlled amplitude test distinguishes skin limitations from pose-specific contact.
pose('OpenHand')
for f in F:
 for j,angle in ((1,65),(2,80),(3,45)):
  r.pose.bones[f+'.%02d.R'%j].rotation_quaternion=Euler((math.radians(angle),0,0)).to_quaternion()
update();report['tight_curl_stress']=metrics(r,m,prep);render_hand(r,m,prep,'before_stress',None,'side')
(OUT/'diagnosis.json').write_text(json.dumps(report,indent=2));print('DIAGNOSIS_SAVED',flush=True)
