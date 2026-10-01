import sys,copy
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
r,m=load();prep=prepare(m)
changes=json.loads((OUT/'weight_changes_right.json').read_text());accepted={}
for vid,ws in changes.items():
 # The middle-finger trial introduced six new local crossings: reject that region.
 if prep[2][int(vid)]=='f_middle':continue
 total=sum(v['after'] for n,v in ws.items() if n in r.data.bones and r.data.bones[n].use_deform)
 for n,v in ws.items():
  if n in r.data.bones and r.data.bones[n].use_deform:v['after']/=total
  m.vertex_groups[n].add([int(vid)],v['after'],'REPLACE')
 accepted[vid]=ws
m.data.update();update();(OUT/'accepted_weights_right.json').write_text(json.dumps(accepted,indent=2))
params={}
for short in POSES:
 pose(short);params[short]={}
 for f in F:
  e=[r.pose.bones[f+'.%02d.R'%j].rotation_quaternion.to_euler('XYZ') for j in (1,2,3)]
  params[short][f]=[math.degrees(e[0].x),math.degrees(e[1].x),math.degrees(e[2].x),math.degrees(e[0].z),math.degrees(e[0].y)]
original=copy.deepcopy(params)
def apply(p):
 for f,vals in p.items():
  for j in (1,2,3):r.pose.bones[f+'.%02d.R'%j].rotation_quaternion=Euler(tuple(math.radians(v) for v in ([vals[0],vals[4],vals[3]] if j==1 else [vals[j-1],0,0])),'XYZ').to_quaternion()
 update()
def self_score():
 d=inspect_pose(r,m,prep);return sum(v for k,v in d['intersection_categories'].items() if k!='palm/palm'),d
log=[]
# Redistribute curl at the problem joints, rather than relaxing all fingers.
for short in ('Fist','Point','HoldSmallPart'):
 pose(short);p=params[short]
 for f in (['f_index','f_ring'] if short!='Point' else ['f_ring']):
  start=copy.deepcopy(p);choices=[]
  for shift in (0,3,6,9,12):
   c=copy.deepcopy(start);c[f][0]+=shift;c[f][1]-=shift;apply(c);score,d=self_score()
   choices.append((score+shift*.015,c,d,shift))
  best=min(choices,key=lambda x:x[0]);p=best[1];log.append({'pose':short,'finger':f,'pip_to_mcp_degrees':best[3],'self':best[2]})
 params[short]=p
 print('JOINT_REBALANCE',short,self_score()[0],flush=True)
pose('Grip_Pliers');p=params['Grip_Pliers'];base=copy.deepcopy(p)
def evaluate(p,f):
 apply(p);score,d=self_score();c=contact_metrics(m,prep,['Pliers_Handle_-1','Pliers_Handle_1'])
 gaps={ff:min(x['regions'][ff]['min_surface_gap'] for x in c.values()) for ff in F}
 depth=max(v['max_depth'] for x in c.values() for v in x['regions'].values());cross=sum(x['surface_intersections'] for x in c.values())
 # Do not purchase clearance by lifting pads away from the handles.
 gap_pen=sum(max(0,g-.001)**2 for g in gaps.values())*2000
 regular=sum(abs(p[ff][i]-base[ff][i]) for ff in F for i in range(5))*.000008
 return score*.0006+cross*.00015+depth*40+gap_pen+sum(gaps.values())*.1+regular,{'self':d,'contact':c,'gaps':gaps,'score':score,'crossings':cross},p
best=evaluate(p,'thumb');log.append({'pliers_before':best[1]})
for round in range(2):
 for f in ('thumb','f_index','f_middle','f_ring','f_pinky'):
  for axis in ((4,3,0,1,2) if f=='thumb' else (0,1,2,3)):
   start=copy.deepcopy(p);choices=[]
   for delta in (-6,-3,0,3,6):
    candidate=copy.deepcopy(start);candidate[f][axis]+=delta
    if abs(candidate[f][axis]-base[f][axis])>12:continue
    choices.append(evaluate(candidate,f))
   best=min(choices,key=lambda x:x[0]);p=best[2]
  print('PLIER_FIT',round,f,best[0],best[1]['crossings'],flush=True)
params['Grip_Pliers']=p;apply(p);log.append({'pliers_after':best[1]})
report={'original_angles':original,'refined_angles':params,'log':log,'poses':{}}
for short in POSES:
 pose(short);apply(params[short]);report['poses'][short]=metrics(r,m,prep)
 if short.startswith('Grip_'):report['poses'][short]['contact']=contact_metrics(m,prep,['Screwdriver_Handle'] if short=='Grip_Screwdriver' else ['Pliers_Handle_-1','Pliers_Handle_1'])
 for view in ('palm','side'):render_hand(r,m,prep,'after_trial_'+short,'Pliers_' if short=='Grip_Pliers' else 'Screwdriver_' if short=='Grip_Screwdriver' else None,view)
(OUT/'pose_refinement.json').write_text(json.dumps(report,indent=2));print('REFINEMENT_COMPLETE',flush=True)
