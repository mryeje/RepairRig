"""Offline native-control fitting. Writes parameter evidence, never a .blend."""
import sys,math,json
sys.path.insert(0,'E:/RepairRig/temp/grip-numerics');sys.path.insert(0,'E:/RepairRig/scripts')
import numpy as np
from scipy.optimize import least_squares
from production_grip_common import *
from hand_mesh_validation import prepare,inspect_pose
r=load();reset(r);mesh=bpy.data.objects['Chris-Low-poly'];prepared=prepare(mesh)
# A production-only socket fit: handle sits at the palm rather than distal finger creases.
center=np.array([-.043,.130,.020]);radius=.020
socket=bpy.data.objects['ATTACH_Screwdriver_R'];h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix
old=(h.inverted()@socket.matrix_world).copy();new=old.copy();new.translation=Vector(center)+Vector((0,0,.015))
socket.matrix_world=h@new;update(r)
result={'screwdriver_socket_in_hand':[list(row) for row in new],'poses':{},'scores':{}}
neutral={f:[0,0,0,0,0] for f in F}
pose={f:[35,60,40,0,0] for f in F}
def fit(f,target,initial,limits,kind='cylinder'):
 def residual(v):
  set_finger(r,f,v);update(r);points=np.array([list(p) for p in bones(r,f)])
  res=list((points[-1]-target)*150)
  if kind=='cylinder':
   for i in [0,1,2]:
    for t in [.25,.5,.75,1]:
     p=points[i]*(1-t)+points[i+1]*t
     # Finger centerline stays outside the handle by its approximate padded radius.
     dist=np.linalg.norm(p[:2]-center[:2]);gap=dist-radius-(.008 if f!='thumb' else .011)
     if abs(p[2]-center[2])<.065:res.append(min(gap,0)*350)
     else:res.append(0.)
   res+=list((points[1:,-1]-target[2])*12)
  res+=list((np.array(v)-initial)*.003)
  return np.array(res)
 sol=least_squares(residual,initial,bounds=limits,diff_step=.02,max_nfev=100,ftol=1e-5,xtol=1e-4,gtol=1e-4)
 set_finger(r,f,sol.x);update(r);print('FIT',f,sol.x.tolist(),float(np.linalg.norm(residual(sol.x))),flush=True)
 result['last_cost']=float(np.linalg.norm(residual(sol.x)))
 return sol.x.tolist()
for f in F[:-1]:
 z={'f_index':.063,'f_middle':.033,'f_ring':.003,'f_pinky':-.024}[f]
 target=np.array([center[0]-.027,center[1]-.001,z])
 pose[f]=fit(f,target,[30,65,40,1,1],([0,5,0,-30,-25],[85,100,80,30,25]))
 if f=='f_pinky':
  candidates=[(result['last_cost'],pose[f])]
  for initial in [[1,75,65,1,1],[5,45,75,1,1],[15,85,55,1,1]]:
   candidate=fit(f,target,initial,([-10,5,0,-20,-25],[70,110,85,20,25]));candidates.append((result['last_cost'],candidate))
  pose[f]=min(candidates,key=lambda x:x[0])[1]
# Thumb crosses the palm onto the opposite/upper handle face near the index.
pose['thumb']=fit('thumb',np.array([center[0]-.020,center[1]-.015,.064]),[20,25,20,-15,20],([-60,-15,-10,-90,-90],[85,85,75,90,90]),'thumb')
apply(r,pose);result['poses']['Grip_Screwdriver']=pose;result['scores']['Grip_Screwdriver']=inspect_pose(r,mesh,prepared)
for view in ['palm','side','back']:render(r,'fitted_screwdriver','Screwdriver_',view)
# Fist and point use restrained, independently distributed joint bends.
fist={f:list(v) for f,v in pose.items()}
apply(r,fist)
for f in F[:-1]:
 base=np.array(list(bones(r,f)[0]));target=np.array([-.040,base[1]-.006,base[2]])
 options=[]
 for initial in [pose[f],[10,75,65,1,1]]:
  candidate=fit(f,target,initial,([-10,0,0,-30,-35],[90,110,90,30,35]),'free');options.append((result['last_cost'],candidate))
 fist[f]=min(options,key=lambda v:v[0])[1]
apply(r,fist)
fist['thumb']=list(pose['thumb'])
# Choose the firmest closure that the current fitted/weighted skin can support without folding.
closed=fist;chosen={f:list(v) for f,v in pose.items()};scan=[]
for t in [0,.2,.4,.6,.8,1]:
 candidate={f:[(1-t)*a+t*b for a,b in zip(pose[f],closed[f])] for f in F};apply(r,candidate);m=inspect_pose(r,mesh,prepared);scan.append({'blend':t,'pairs':m['self_intersection_triangle_pairs'],'categories':m['intersection_categories']})
 if m['self_intersection_triangle_pairs']<=25 and not any(a!=b for a,b in (k.split('/') for k in m['intersection_categories'])):chosen=candidate
fist=chosen;result['fist_closure_scan']=scan
apply(r,fist);result['poses']['Fist']=fist;result['scores']['Fist']=inspect_pose(r,mesh,prepared)
render(r,'fitted_fist',None,'palm');render(r,'fitted_fist',None,'side')
point={f:list(v) for f,v in fist.items()};point['f_index']=[0,3,2,0,0]
apply(r,point);result['poses']['Point']=point;result['scores']['Point']=inspect_pose(r,mesh,prepared);render(r,'fitted_point',None,'palm')
opened={f:[0,0,0,0,0] for f in F};apply(r,opened);result['poses']['OpenHand']=opened;result['scores']['OpenHand']=inspect_pose(r,mesh,prepared);render(r,'fitted_open',None,'palm')
small={f:[10,20,10,0,0] for f in F};apply(r,small)
small['f_index']=fit('f_index',np.array([-.065,.143,.070]),[30,45,35,1,1],([0,0,0,-25,-25],[80,100,80,25,25]),'free');small['thumb']=list(pose['thumb'])
apply(r,small);result['poses']['HoldSmallPart']=small;result['scores']['HoldSmallPart']=inspect_pose(r,mesh,prepared);render(r,'fitted_smallpart',None,'palm')
# Pliers are evaluated at their existing attachment before choosing a character fit.
pliers={f:list(v) for f,v in pose.items()}
apply(r,pliers);bpy.data.objects['TOOL_Pliers'].constraints[0].influence=1;update(r)
hp=(r.matrix_world@r.pose.bones['DEF-hand.R'].matrix).inverted()
handle_centers=[hp@bpy.data.objects['Pliers_Handle_'+str(i)].matrix_world.translation for i in [-1,1]]
print('PLIER_HANDLE_CENTERS',[list(x) for x in handle_centers],flush=True)
ps=bpy.data.objects['ATTACH_Pliers_R'];pm=hp@ps.matrix_world;pm.translation+=Vector((-.043,.130,.020))-(handle_centers[0]+handle_centers[1])*.5
ps.matrix_world=hp.inverted()@pm;update(r);result['pliers_socket_in_hand']=[list(row) for row in pm]
result['poses']['Grip_Pliers']=pliers;result['scores']['Grip_Pliers']=inspect_pose(r,mesh,prepared)
render(r,'fitted_pliers','Pliers_','palm');render(r,'fitted_pliers','Pliers_','side')
for o in bpy.data.objects:
 if o.name.startswith('Pliers_JawPivot'):
  print('PLIER_DRIVER',o.name,[(fc.driver.expression,[(v.name,[(t.data_path) for t in v.targets]) for v in fc.driver.variables]) for fc in o.animation_data.drivers],flush=True)
(OUT/'fit_parameters.json').write_text(json.dumps(result,indent=2));bpy.ops.wm.quit_blender()
