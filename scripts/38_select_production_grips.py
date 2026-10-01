"""Select a pliers refinement without accepting folded/crossed fingers."""
import sys,json
sys.path.insert(0,'E:/RepairRig/scripts')
from production_grip_common import *
from hand_mesh_validation import prepare,inspect_pose
from grip_contact_validation import contact_metrics
p=json.loads((OUT/'surface_fit_parameters.json').read_text());r=load();mesh=bpy.data.objects['Chris-Low-poly'];prep=prepare(mesh);h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix
bpy.data.objects['ATTACH_Pliers_R'].matrix_world=h@Matrix(p['pliers_socket_in_hand']);bpy.data.objects['TOOL_Pliers'].constraints[0].influence=1
base=p['poses']['Grip_Screwdriver'];target=p['poses']['Grip_Pliers'];scan=[];candidates=[]
for t in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]:
 pose={f:[a*(1-t)+b*t for a,b in zip(base[f],target[f])] for f in F};apply(r,pose);m=inspect_pose(r,mesh,prep)
 item={'blend':t,'self':m}
 if m['self_intersection_triangle_pairs']<=25:
  contacts=contact_metrics(mesh,prep,['Pliers_Handle_-1','Pliers_Handle_1']);item['contacts']=contacts
  depth=max(v['max_depth'] for c in contacts.values() for v in c['regions'].values());gap=sum(min(c['regions'][f]['min_surface_gap'] for c in contacts.values()) for f in F)
  score=depth*15+gap;candidates.append((score,pose,m,contacts,t))
 scan.append(item);print('PLIER_SCAN',t,m['self_intersection_triangle_pairs'],flush=True)
score,pose,m,contacts,t=min(candidates,key=lambda v:v[0]);p['pliers_selection']={'blend':t,'score':score};p['pliers_scan']=scan
for f in ['thumb','f_index','f_middle','f_ring','f_pinky']:
 choices=[];start=list(pose[f])
 for blend in [0,.25,.5,.75,1]:
  candidate={n:list(v) for n,v in pose.items()};candidate[f]=[a*(1-blend)+b*blend for a,b in zip(start,target[f])];apply(r,candidate);m=inspect_pose(r,mesh,prep)
  if m['self_intersection_triangle_pairs']>25:continue
  c=contact_metrics(mesh,prep,['Pliers_Handle_-1','Pliers_Handle_1']);depth=max(v['regions'][f]['max_depth'] for v in c.values());gap=min(v['regions'][f]['min_surface_gap'] for v in c.values());choices.append((depth*15+gap,candidate,m,c,blend))
 _,pose,m,contacts,blend=min(choices,key=lambda v:v[0]);print('FINGER_SELECTED',f,blend,flush=True)
for axis in [0,2,3]:
 choices=[];start=list(pose['f_pinky'])
 for delta in [-12,-8,-4,0,4,8,12]:
  candidate={n:list(v) for n,v in pose.items()};candidate['f_pinky'][axis]=start[axis]+delta;apply(r,candidate);m=inspect_pose(r,mesh,prep)
  if m['self_intersection_triangle_pairs']>25:continue
  c=contact_metrics(mesh,prep,['Pliers_Handle_-1','Pliers_Handle_1']);depth=max(v['regions']['f_pinky']['max_depth'] for v in c.values());gap=min(v['regions']['f_pinky']['min_surface_gap'] for v in c.values());choices.append((depth*20+gap,candidate,m,c,delta))
 _,pose,m,contacts,delta=min(choices,key=lambda v:v[0]);print('PINKY_CLEARANCE',axis,delta,flush=True)
p['poses']['Grip_Pliers']=pose;p['scores']['Grip_Pliers']=m;p['surface_contacts']['Grip_Pliers']=contacts
apply(r,pose);render(r,'selected_pliers','Pliers_','palm');render(r,'selected_pliers','Pliers_','side')
(OUT/'final_parameters.json').write_text(json.dumps(p,indent=2));print('SELECTED',t,contacts,flush=True);bpy.ops.wm.quit_blender()
