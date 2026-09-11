"""Read-only structural and evaluated-scene validation, usable from Blender Text Editor."""
import sys,re
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
def validate(label):
 names=json.loads((OUT/'expected_actions.json').read_text()); poses=json.loads((OUT/'pose_values.json').read_text()); checks={}; detail={}
 checks['15_actions']=len(names)==15 and all(n in bpy.data.actions for n in names)
 checks['six_pose_assets']=len(poses)==6 and all(n in bpy.data.actions and bpy.data.actions[n].asset_data for n in poses)
 for name in names:
  a=bpy.data.actions[name]; fs=curves(a)
  if name.startswith('BODY_'): allowed=set(BODY)
  elif name=='TOOL_Pliers_Squeeze_R': allowed={f+'.01_master.R' for f in FINGERS}
  elif name.startswith('TOOL_'): allowed=set()
  else:
   side='L' if name.endswith('_L') else 'R'; allowed={'hand_ik.'+side,'upper_arm_ik_target.'+side,'upper_arm_parent.'+side}
  keyed=set(); paths_valid=True
  owner=bpy.data.objects[a['owner']]
  for fc in fs:
   m=re.match(r'pose.bones\["([^"]+)"\]',fc.data_path)
   if m: keyed.add(m[1])
   else: paths_valid &= owner.name=='CONTACT_ScrewdriverRoll_R' and (fc.data_path,fc.array_index) in [('rotation_euler',2),('location',2)]
   try: owner.path_resolve(fc.data_path)
   except: paths_valid=False
  checks[name]=bool(fs) and len(a.slots)==1 and keyed<=allowed and paths_valid and all(len(fc.keyframe_points)>1 for fc in fs)
  if a['loopable']: checks[name+'_seam']=max(abs(fc.evaluate(a.frame_range[0])-fc.evaluate(a.frame_range[1])) for fc in fs)<1e-6
  detail[name]={'range':list(a.frame_range),'owner':owner.name,'keyed_bones':sorted(keyed),'channels':len(fs)}
 for name in poses:
  a=bpy.data.actions[name]; fs=curves(a)
  checks[name]=all(any('"'+f+'.01_master.R"' in fc.data_path for f in FINGERS) for fc in fs) and bool(fs)
 old=json.loads((OUT/'architecture.json').read_text()); now=json.loads(json.dumps(structure()))
 checks['rest_skeleton_unchanged']=now['bones']==old['bones']; checks['rigify_drivers_unchanged']=now['drivers']==old['drivers'] and len(r.animation_data.drivers)==109
 checks['contact_hierarchy_unchanged']=now['hierarchy']==old['hierarchy']
 checks['existing_constraints_retained']=all(all(c in now['contacts'][n] for c in cs) for n,cs in old['contacts'].items())
 nla=[]
 for o in bpy.data.objects:
  if o.animation_data:
   for tr in o.animation_data.nla_tracks:
    for st in tr.strips:
     assert st.action and st.action_slot and st.action_slot in st.action.slots[:]
     nla.append({'owner':o.name,'track':tr.name,'action':st.action.name,'slot':st.action_slot.identifier,'start':st.frame_start,'end':st.frame_end,'repeat':st.repeat,'reverse':st.use_reverse})
 checks['nla_valid']=bool(nla) and r.animation_data.action is None
 worst_hand=[]; handerr=tiperr=griperr=legerr=0.; samples={}; feet={}; support={}
 for f in range(1,486):
  update(f); dg=bpy.context.evaluated_depsgraph_get(); p=r.evaluated_get(dg).pose.bones
  for side in ['L','R']:
   err=(p['DEF-hand.'+side].head-p['hand_ik.'+side].head).length
   if err>handerr: worst_hand=[f,side,err]
   handerr=max(handerr,err)
   legerr=max(legerr,(p['DEF-foot.'+side].head-p['foot_ik.'+side].head).length)
  if 113<=f<=269: feet[f]=[list(p['DEF-foot.'+side].head) for side in ['L','R']]
  if 65<=f<=113 or 325<=f<=373: support[f]=min(abs(p['foot_ik.'+side].head.z-.0852) for side in ['L','R'])
  def mat(n): return bpy.data.objects[n].evaluated_get(dg).matrix_world
  grip=(r.matrix_world@p['DEF-hand.R'].matrix@bpy.data.objects['ATTACH_Screwdriver_R'].matrix_basis).translation
  griperr=max(griperr,(grip-mat('TOOL_Screwdriver').translation).length)
  if 161<=f<269:
   samples[f]=[list(row) for row in mat('CONTACT_ScrewdriverRoll_R')]
   if (f-161)%36<=21: tiperr=max(tiperr,(mat('REF_ScrewdriverTip').translation-mat('TARGET_Screw').translation).length)
 repeaterr=max(abs(samples[f][i][j]-samples[f+36][i][j]) for f in range(161,233) for i in range(4) for j in range(4))
 drift=max((Vector(feet[f][i])-Vector(feet[113][i])).length for f in feet for i in [0,1])
 checks['actual_hand_reaches']=handerr<.003; checks['actual_tool_grip']=griperr<.003; checks['engaged_tip_alignment']=tiperr<.0001; checks['nla_three_cycles']=repeaterr<1e-6
 checks['stationary_kneel_feet']=drift<.0001; checks['one_support_foot_during_transfers']=max(support.values())<.0001; checks['leg_ik_reach']=legerr<.003
 checks['drivers_valid']=all(fc.driver.is_valid for fc in r.animation_data.drivers)
 hashes=json.loads((OUT/'source_hashes.json').read_text()); checks['earlier_checkpoints_unchanged']=all(hashlib.sha256((ROOT/'blend'/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
 report={'pass':all(checks.values()),'checks':checks,'actions':detail,'nla':nla,'measurements_metres':{'max_hand_ik_error':handerr,'max_leg_ik_error':legerr,'max_actual_grip_error':griperr,'max_engaged_tip_error':tiperr,'stationary_foot_drift':drift,'max_nearest_support_foot_height_error':max(support.values())},'worst_hand':worst_hand,'repeat_matrix_error':repeaterr,'version':bpy.app.version_string}
 (OUT/(label+'.json')).write_text(json.dumps(report,indent=2)); update(179)
 assert report['pass'],{k:v for k,v in checks.items() if not v}
 return report
if __name__=='__main__': validate('manual_validation')
