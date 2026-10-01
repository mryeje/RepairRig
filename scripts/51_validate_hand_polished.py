import sys,hashlib,struct
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
saved=json.loads((OUT/'checkpoint.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mat(m):return [list(row) for row in m]
def err(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def assign(obj,name,frame):
 a=bpy.data.actions[name];obj.animation_data_create();obj.animation_data.action=a;obj.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(frame);update()
def world(n):return bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
def weights(m):return {str(v.index):{m.vertex_groups[g.group].name:g.weight for g in v.groups} for v in m.data.vertices}
def actions():return {a.name:[[f.data_path,f.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]] for f in curves(a)] for a in bpy.data.actions}
def geom(m):
 h=hashlib.sha256()
 for v in m.data.vertices:h.update(struct.pack('3f',*v.co))
 for p in m.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
report={'poses':{},'motion':{}};sourceweights=None;neutral={}
for label,path in (('before',SRC),('after',DST)):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=True);update();r=bpy.data.objects['RepairRig'];m=bpy.data.objects['Chris-Low-poly'];prep=prepare(m)
 if label=='before':sourceweights=weights(m)
 else:
  current=weights(m);changed=[i for i,w in current.items() if w!=sourceweights[i]]
  report['weight_validation']={'changed_vertices':len(changed),'exact_scope':set(changed)==set(saved['weight_changes']),'all_normalized':all(abs(sum(w for n,w in current[i].items() if n in r.data.bones and r.data.bones[n].use_deform)-1)<1e-5 for i in changed),'geometry_unchanged':geom(m)==saved['geometry_hash']}
  report['preservation']={'other_actions_unchanged':all(actions()[n]==v for n,v in saved['original_actions'].items() if n not in saved['changed_actions']),'rest_unchanged':{o.name:{b.name:mat(b.matrix_local) for b in o.data.bones} for o in bpy.data.objects if o.type=='ARMATURE'}==saved['rest'],'tool_transforms_unchanged':{n:mat(bpy.data.objects[n].matrix_basis) for n in saved['tool_transforms']}==saved['tool_transforms'],'ui_text_unchanged':hashlib.sha256(bpy.data.texts['RepairRig_Tools_UI.py'].as_string().encode()).hexdigest()==saved['ui_sha256'],'panel_registered':hasattr(bpy.types,'REPAIRRIG_PT_tools')}
 report['poses'][label]={}
 for short in POSES:
  pose(short);item=metrics(r,m,prep)
  if short=='OpenHand':neutral[label]=evaluated(m)
  if short.startswith('Grip_'):item['contact']=contact_metrics(m,prep,['Screwdriver_Handle'] if short=='Grip_Screwdriver' else ['Pliers_Handle_-1','Pliers_Handle_1'])
  # Use the native slotted Action evaluator, checking every asset channel.
  old=r.animation_data.action;slot=r.animation_data.action_slot;frame=bpy.context.scene.frame_current
  assign(r,'POSE_'+short+'_R_Production',1)
  item['asset_channel_error']=max(abs(r.path_resolve(fc.data_path)[fc.array_index]-fc.evaluate(1)) for fc in curves(r.animation_data.action));item['asset_marked']=bool(r.animation_data.action.asset_data)
  r.animation_data.action=old;r.animation_data.action_slot=slot;bpy.context.scene.frame_set(frame);pose(short)
  report['poses'][label][short]=item
  if label=='after':
   for view in ('palm','side'):render_hand(r,m,prep,'saved_'+short,'Pliers_' if short=='Grip_Pliers' else 'Screwdriver_' if short=='Grip_Screwdriver' else None,view)
  print(label,short,item['self_intersection_triangle_pairs'],flush=True)
 states={}
 for state in (0,1,2,0,2):
  assert bpy.ops.repairrig.select_tool(tool=state)=={'FINISHED'};update();states[str(state)]=[bpy.data.objects[n].constraints[c].influence for n,c in [('TOOL_Screwdriver','Attach / release | right hand socket'),('TOOL_Pliers','Attach / release | pliers right socket')]]
 report['motion'][label]={'states':states,'samples':{}}
 for short,state in (('Grip_Screwdriver',1),('Grip_Pliers',2)):
  pose(short);assign(bpy.data.objects['CONTACT_ScrewdriverRoll_R'],'TOOL_Screwdriver_CW_R',1)
  for f in (1,17,33,37):
   bpy.context.scene.frame_set(f);update();key=short+str(f)
   report['motion'][label]['samples'][key]={n:mat(world(n)) for n in ('TOOL_Screwdriver','TOOL_Pliers','SCREW_Visible','REF_PliersContact','REF_ScrewdriverTip','CONTACT_ScrewdriverRoll_R')}
 for name in ('BODY_Kneel_L','REACH_Forward_Low_R','REACH_Forward_Mid_R','REACH_Forward_Low_L','BRACE_Forward_L'):
  for f in (1,17,33):
   assign(r,name,f);report['motion'][label]['samples'][name+str(f)]={n:mat(r.pose.bones[n].matrix) for n in ('hand_ik.R','hand_ik.L','torso')}
report['neutral_max_vertex_difference']=max((a-b).length for a,b in zip(neutral['before'],neutral['after']))
report['motion_max_matrix_error']=max(err(a,report['motion']['after']['samples'][key][n]) for key,s in report['motion']['before']['samples'].items() for n,a in s.items())
checks={**report['preservation'],**{k:v for k,v in report['weight_validation'].items() if isinstance(v,bool)},'motion_preserved':report['motion_max_matrix_error']<1e-5,'neutral_preserved':report['neutral_max_vertex_difference']<1e-5,'tool_buttons':report['motion']['after']['states']=={'0':[0.,0.],'1':[1.,0.],'2':[0.,1.]},'all_assets':all(v['asset_marked'] and v['asset_channel_error']<1e-5 for v in report['poses']['after'].values()),'inputs_unchanged':all(sha(Path(p))==h for p,h in saved['input_hashes'].items()),'saved_file_unchanged_by_tests':sha(DST)==saved['output_sha256']}
for short in ('Grip_Screwdriver','Grip_Pliers'):
 checks[short+'_no_tool_crossings']=sum(c['surface_intersections'] for c in report['poses']['after'][short]['contact'].values())==0
for short in POSES:checks[short+'_self_not_worse']=report['poses']['after'][short]['self_intersection_triangle_pairs']<=report['poses']['before'][short]['self_intersection_triangle_pairs']
for short,ref in (('Grip_Pliers','REF_PliersContact'),('Grip_Screwdriver','REF_ScrewdriverTip')):
 s=report['motion']['after']['samples'][short+'33'];checks[short+'_work_contact']=sum((s[ref][i][3]-s['CONTACT_ScrewdriverRoll_R'][i][3])**2 for i in range(3))**.5<1e-5
report['checks']=checks;report['pass']=all(checks.values());(OUT/'reopen_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(checks,indent=2),flush=True);assert report['pass'],checks
