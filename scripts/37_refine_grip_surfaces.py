"""Refine native joint rotations against actual evaluated hand surfaces."""
import sys,json,math
sys.path.insert(0,'E:/RepairRig/temp/grip-numerics');sys.path.insert(0,'E:/RepairRig/scripts')
import numpy as np
from scipy.optimize import least_squares
from production_grip_common import *
from hand_mesh_validation import prepare,inspect_pose
from grip_contact_validation import contact_metrics
params=json.loads((OUT/'fit_parameters.json').read_text());r=load();mesh=bpy.data.objects['Chris-Low-poly'];prep=prepare(mesh)
h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix
for n,k in [('ATTACH_Screwdriver_R','screwdriver_socket_in_hand'),('ATTACH_Pliers_R','pliers_socket_in_hand')]:bpy.data.objects[n].matrix_world=h@Matrix(params[k])
regions={f:np.array([i for i,v in enumerate(prep[2]) if v==f],dtype=int) for f in F}
world=np.array(mesh.matrix_world);history={}
for name,objects in [('Grip_Screwdriver',['Screwdriver_Handle']),('Grip_Pliers',['Pliers_Handle_-1','Pliers_Handle_1'])]:
 pose=params['poses'][name];apply(r,pose);bpy.data.objects['TOOL_Pliers'].constraints[0].influence=int(name=='Grip_Pliers');update(r)
 tooldata=[]
 for n in objects:
  o=bpy.data.objects[n];m=o.matrix_world;rot=m.to_3x3().normalized();bounds=np.array([list(x) for x in o.bound_box]);mid=(bounds.max(0)+bounds.min(0))/2;half=(bounds.max(0)-bounds.min(0))/2;scale=np.array([m.to_3x3().col[i].length for i in range(3)])
  tooldata.append((np.array(rot),np.array(m@Vector(mid)),half*scale))
 def distances(v):
  allsd=[]
  for rot,pos,half in tooldata:
   local=(v-pos)@rot
   if name=='Grip_Screwdriver':q=np.column_stack((np.linalg.norm(local[:,:2],axis=1)-min(half[:2]),np.abs(local[:,2])-half[2]))
   else:q=np.abs(local)-half
   allsd.append(np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.max(q,axis=1),0))
  return np.min(np.array(allsd),axis=0)
 for f in F:
  start=np.array(pose[f]);tip=np.array(list(bones(r,f)[-1]));ids=regions[f]
  def residual(v):
   set_finger(r,f,v);update(r);ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();coords=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)[ids];ev.to_mesh_clear();coords=coords@world[:3,:3].T+world[:3,3];sd=distances(coords)
   penetration=np.maximum(.00025-sd,0)*700
   contact=np.sort(np.maximum(sd,0))[:12]*50
   target=(np.array(list(bones(r,f)[-1]))-tip)*20
   return np.concatenate([penetration,contact,target,(v-start)*.004])
  lo=np.maximum(start-22,[-20,-15,-10,-45,-45]);hi=np.minimum(start+22,[95,110,95,45,45])
  sol=least_squares(residual,start,bounds=(lo,hi),diff_step=.015,max_nfev=70,ftol=2e-4,xtol=2e-4,gtol=1e-4)
  pose[f]=sol.x.tolist();set_finger(r,f,pose[f]);update(r);print('SURFACE',name,f,pose[f],flush=True)
 apply(r,pose);params['poses'][name]=pose;params['scores'][name]=inspect_pose(r,mesh,prep);history[name]=contact_metrics(mesh,prep,objects)
 for view in ['palm','side']:render(r,'surface_'+name,'Screwdriver_' if name=='Grip_Screwdriver' else 'Pliers_',view)
params['surface_contacts']=history
(OUT/'surface_fit_parameters.json').write_text(json.dumps(params,indent=2));print('DONE',json.dumps(history),flush=True);bpy.ops.wm.quit_blender()
