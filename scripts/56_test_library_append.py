"""Fresh project using only native library Append, no development blend access."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Vector
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library')
bpy.ops.wm.read_factory_settings(use_empty=True)
report={}
def append(file,kind,name):
 return bpy.ops.wm.append(directory=str(LIB/file)+'/'+kind+'/',filename=name,link=False,instance_collections=False,do_reuse_local_id=True)
def update():bpy.data.objects['RepairRig'].update_tag();bpy.context.view_layer.update()
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def assign(o,name,f):
 a=bpy.data.actions[name];o.animation_data_create();o.animation_data.action=a;o.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(f);update()
def pose(r,name):
 for fc in curves(bpy.data.actions[name]):r.path_resolve(fc.data_path)[fc.array_index]=fc.evaluate(1)
 update()
try:
 for file,name in [('Character/RepairRig_Production.blend','RepairRig_Character_Production'),('Tools/RepairRig_Screwdriver.blend','RepairRig_Tool_Screwdriver'),('Tools/RepairRig_Pliers.blend','RepairRig_Tool_Pliers'),('Tools/RepairRig_Worksite.blend','RepairRig_Worksite_Demo')]:
  report[name]=list(append(file,'Collection',name))
 r=bpy.data.objects['RepairRig'];bpy.context.view_layer.objects.active=r;r.select_set(True)
 report['texts']=[t.name for t in bpy.data.texts];report['rig_count']=len([o for o in bpy.data.objects if o.type=='ARMATURE'])
 t=r['repairrig_library_ui'];exec(compile(t.as_string(),t.name,'exec'),{'__name__':'__main__'})
 report['bind']=list(bpy.ops.repairrig.bind_library_tools());report['worksite']=list(bpy.ops.repairrig.bind_worksite())
 for name in ['BODY_Kneel_L','REACH_Forward_Low_R','TOOL_Screwdriver_CW_R']:append('Actions/RepairRig_Motion.blend','Action',name)
 for name in ['POSE_Grip_Screwdriver_R_Production','POSE_Grip_Pliers_R_Production']:append('Poses/RepairRig_HandPoses_Production.blend','Action',name)
 assign(r,'BODY_Kneel_L',49);assign(r,'REACH_Forward_Low_R',33)
 report['contacts']={}
 for name,state,ref in [('Screwdriver',1,'REF_ScrewdriverTip'),('Pliers',2,'REF_PliersContact')]:
  pose(r,'POSE_Grip_'+name+'_R_Production');bpy.ops.repairrig.select_tool(tool=state);update()
  report['contacts'][name]=(bpy.data.objects[ref].matrix_world.translation-bpy.data.objects['CONTACT_ScrewdriverRoll_R'].matrix_world.translation).length
 report['states']={}
 for state in [0,1,2,0]:
  bpy.ops.repairrig.select_tool(tool=state);update();report['states'][str(state)]=[bpy.data.objects[n].constraints[0].influence for n in ['TOOL_Screwdriver','TOOL_Pliers']]
 report['invalid_drivers']=[(o.name,f.data_path) for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
 report['object_names']=[o.name for o in bpy.data.objects];report['linked_files']=[l.filepath for l in bpy.data.libraries]
 report['api']={}
 for group,name in [('asset','assign_action'),('object','collection_external_asset_drop'),('poselib','apply_pose_asset')]:
  try:report['api'][group+'.'+name]=[(p.identifier,p.description) for p in getattr(getattr(bpy.ops,group),name).get_rna_type().properties]
  except Exception as e:report['api'][group+'.'+name]=str(e)
 assert report['rig_count']==1 and not report['invalid_drivers']
 assert all(v<1e-5 for v in report['contacts'].values()),report['contacts']
 assert report['states']=={'0':[0.,0.],'1':[1.,0.],'2':[0.,1.]}
 report['pass']=True
except:report['error']=traceback.format_exc();print(report['error'],flush=True)
(OUT/'append_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['object_names','api']},indent=2),flush=True)
