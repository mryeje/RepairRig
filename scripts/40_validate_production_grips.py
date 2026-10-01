"""Independent saved-file validation; never saves scenes."""
import sys,json,hashlib,traceback
sys.path.insert(0,'E:/RepairRig/scripts')
from production_grip_common import *
from hand_mesh_validation import prepare,inspect_pose
from grip_contact_validation import contact_metrics
DST=ROOT/'blend/RepairRig_05C_ProductionCharacter_GripRefined.blend'
def assign(r,name,f):
 a=bpy.data.actions[name];r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(f);update(r)
def matrix_error(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def work(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);r=bpy.data.objects['RepairRig'];r.animation_data.use_nla=False;assign(r,'BODY_Kneel_L',49);assign(r,'REACH_Forward_Low_R',33);return r
report={'path':str(DST),'sha256_before':hashlib.sha256(DST.read_bytes()).hexdigest(),'poses':{},'source_poses':{}}
try:
 tool_samples={};wrist_samples={}
 for label,path in [('source',SRC),('refined',DST)]:
  r=work(path);r.animation_data.action=None;roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R'];a=bpy.data.actions['TOOL_Screwdriver_CW_R'];roll.animation_data.use_nla=False;roll.animation_data.action=a;roll.animation_data.action_slot=a.slots[0];samples={};wrists={}
  for f in [1,17,33,37]:
   bpy.context.scene.frame_set(f);update(r);samples[f]=bpy.data.objects['TOOL_Screwdriver'].matrix_world.copy();wrists[f]=r.pose.bones['hand_ik.R'].matrix.to_quaternion().copy()
  tool_samples[label]=samples;wrist_samples[label]=wrists
 report['tool_cycle_world_matrix_error']=max(matrix_error(tool_samples['source'][f],tool_samples['refined'][f]) for f in tool_samples['source'])
 report['work_wrist_orientation_error_degrees']=max(math.degrees(wrist_samples['source'][f].rotation_difference(wrist_samples['refined'][f]).angle) for f in wrist_samples['source'])
 assert report['tool_cycle_world_matrix_error']<1e-4,report['tool_cycle_world_matrix_error']
 for label,path in [('source',SRC),('refined',DST)]:
  r=work(path);mesh=bpy.data.objects['Chris-Low-poly'];prepared=prepare(mesh)
  for short in ['Grip_Screwdriver','Grip_Pliers','Fist','Point','OpenHand','HoldSmallPart']:
   name='POSE_'+short+'_R'+('_Production' if label=='refined' else '')
   reset(r);assign(r,name,1);a=bpy.data.actions[name];assert a.asset_data
   errors=[];paths=[]
   for l in a.layers:
    for st in l.strips:
     bag=st.channelbag(a.slots[0])
     for fc in bag.fcurves:
      value=r.path_resolve(fc.data_path);actual=value if isinstance(value,(float,int)) else value[fc.array_index];errors.append(abs(actual-fc.evaluate(1)));paths.append(fc.data_path)
   assert max(errors)<1e-5,(name,max(errors))
   if label=='refined':assert all(any('"'+n+'"' in path for n in CONTROLS) for path in paths)
   item={'slot':a.slots[0].identifier,'max_channel_error':max(errors),'asset':bool(a.asset_data),'geometry':inspect_pose(r,mesh,prepared),'drivers_valid':all(fc.driver.is_valid for fc in r.animation_data.drivers)}
   assert item['drivers_valid']
   if short in ['Grip_Screwdriver','Grip_Pliers']:
    bpy.data.objects['TOOL_Pliers'].constraints[0].influence=int(short=='Grip_Pliers');update(r)
    item['tool_contact']=contact_metrics(mesh,prepared,['Screwdriver_Handle'] if short=='Grip_Screwdriver' else ['Pliers_Handle_-1','Pliers_Handle_1'])
   report['poses' if label=='refined' else 'source_poses'][short]=item
   if label=='refined':
    for view in ['palm','side']:render(r,'saved_'+short,('Screwdriver_' if short=='Grip_Screwdriver' else 'Pliers_' if short=='Grip_Pliers' else None),view)
   print('VALIDATED',label,short,item['geometry']['self_intersection_triangle_pairs'],flush=True)
 report['sha256_after']=hashlib.sha256(DST.read_bytes()).hexdigest();assert report['sha256_before']==report['sha256_after'];report['pass']=True
except:report['error']=traceback.format_exc();print(report['error'],flush=True)
(OUT/'reopen_validation.json').write_text(json.dumps(report,indent=2));print('COMPLETE',report.get('pass'),flush=True);bpy.ops.wm.quit_blender()
