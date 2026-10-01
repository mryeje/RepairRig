"""GUI test: native external assets in a fresh file, followed by local demo authoring."""
import bpy,json,traceback,sys
from pathlib import Path
sys.path.insert(0,'E:/RepairRig/scripts')
from stage6_demo_common import build_demo,curves,update
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library')
manifest=json.loads((LIB/'Docs/Library_Manifest.json').read_text());report={'steps':[],'pose_assets':{}}
# Start from a factory file; remove only its in-memory starter objects.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
library=bpy.context.preferences.filepaths.asset_libraries.new(name='RepairRig',directory=str(LIB))
report['library_preference']={'name':library.name,'path':library.path}
browser=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES');browser.type='FILE_BROWSER';browser.ui_type='ASSETS'
view=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
def region(a):return next(r for r in a.regions if r.type=='WINDOW')
def finish():
 (OUT/'asset_browser_new_project.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.quit_blender()
def append_asset(a):
 # Native File > Append is the documented deterministic Collection import path.
 return bpy.ops.wm.append(directory=a.full_library_path+'/Collection/',filename=a.name,instance_collections=False,do_reuse_local_id=True)
def execute():
 try:
  with bpy.context.temp_override(area=browser,region=region(browser)):
   bpy.ops.file.select_all(action='SELECT');assets={a.name:a for a in bpy.context.selected_assets}
  report['discovered']=sorted(assets);report['catalogs']={a.name:a.metadata.catalog_id for a in assets.values()}
  assert set(assets)=={a['name'] for a in manifest['assets']},report['discovered']
  for name in ['RepairRig_Character_Production','RepairRig_Tool_Screwdriver','RepairRig_Tool_Pliers','RepairRig_Worksite_Demo']:
   result=append_asset(assets[name]);assert result=={'FINISHED'};report['steps'].append('Native library Append: '+name)
  r=bpy.data.objects['RepairRig'];bpy.context.view_layer.objects.active=r;r.select_set(True)
  text=r['repairrig_library_ui'];exec(compile(text.as_string(),text.name,'exec'),{'__name__':'__main__'})
  assert bpy.ops.repairrig.bind_library_tools()=={'FINISHED'};assert bpy.ops.repairrig.bind_worksite()=={'FINISHED'}
  assert bpy.ops.repairrig.bind_library_tools()=={'FINISHED'}
  report['steps'].append('Embedded UI registration and idempotent native constraint binding')
  # Standard File > Append Action plus Action Editor assignment. This works
  # independently of Blender's context-sensitive drag/drop action operator.
  for name,frame,owner in [('BODY_Kneel_L',49,r),('REACH_Forward_Low_R',33,r),('TOOL_Screwdriver_CW_R',1,bpy.data.objects['CONTACT_ScrewdriverRoll_R'])]:
   bpy.context.view_layer.objects.active=owner
   result=bpy.ops.wm.append(directory=assets[name].full_library_path+'/Action/',filename=name,do_reuse_local_id=True)
   owner.animation_data_create();owner.animation_data.action=bpy.data.actions[name];owner.animation_data.action_slot=bpy.data.actions[name].slots[0]
   assert result=={'FINISHED'} and owner.animation_data.action.name==name,(name,result)
   bpy.context.scene.frame_set(frame);update();report['steps'].append('Native library Action Append + Action Editor assignment: '+name)
  # Restore fully engaged reach after selecting the independent roll Action.
  bpy.context.scene.frame_set(33);update();bpy.context.view_layer.objects.active=r
  with bpy.context.temp_override(area=view,region=region(view)):bpy.ops.object.mode_set(mode='POSE')
  for p in r.pose.bones:p.select=any(f in p.name for f in ['f_index','f_middle','f_ring','f_pinky','thumb']) and not p.name.startswith(('DEF-','MCH-','ORG-'))
  for name in sorted(n for n in assets if n.startswith('POSE_')):
   a=assets[name]
   active_before=r.animation_data.action
   slot_before=r.animation_data.action_slot
   with bpy.context.temp_override(area=browser,region=region(browser),asset=a):
    status=bpy.ops.poselib.apply_pose_asset('INVOKE_DEFAULT',blend_factor=1)
   assert status=={'FINISHED'},(name,status)
   assert r.animation_data.action==active_before and r.animation_data.action_slot==slot_before
   # Capture before the comparison-only Append below: Apply Pose need not
   # persist an Action datablock and must not replace the timeline Action.
   retained_as_local_action=name in bpy.data.actions
   # The operator may keep its imported Action temporary: compare against a local appended library Action.
   if name not in bpy.data.actions:bpy.ops.wm.append(directory=a.full_library_path+'/Action/',filename=name,do_reuse_local_id=True)
   action=bpy.data.actions[name];errors=[]
   for fc in curves(action):
    value=r.path_resolve(fc.data_path);errors.append(abs((value if isinstance(value,(float,int,bool)) else value[fc.array_index])-fc.evaluate(1)))
   error=max(errors);assert error<1e-5,(name,error)
   report['pose_assets'][name]={'result':list(status),'max_channel_error':error,
    'timeline_action_unchanged':True,'active_action':active_before.name,
    'local_action_after_apply_before_comparison_append':retained_as_local_action}
  report['contacts']={};report['states']={}
  for short,state,ref in [('Screwdriver',1,'REF_ScrewdriverTip'),('Pliers',2,'REF_PliersContact')]:
   name='POSE_Grip_'+short+'_R_Production';a=assets[name]
   with bpy.context.temp_override(area=browser,region=region(browser),asset=a):
    bpy.ops.poselib.apply_pose_asset('INVOKE_DEFAULT',blend_factor=1)
   assert bpy.ops.repairrig.select_tool(tool=state)=={'FINISHED'};update()
   report['contacts'][short]=(bpy.data.objects[ref].matrix_world.translation-bpy.data.objects['CONTACT_ScrewdriverRoll_R'].matrix_world.translation).length
   assert report['contacts'][short]<1e-5
  for state in [0,1,2,0]:
   bpy.ops.repairrig.select_tool(tool=state);update();report['states'][str(state)]=[bpy.data.objects[n].constraints[0].influence for n in ['TOOL_Screwdriver','TOOL_Pliers']]
  assert report['states']=={'0':[0.,0.],'1':[1.,0.],'2':[0.,1.]}
  report['rig_count']=sum(o.type=='ARMATURE' for o in bpy.data.objects);assert report['rig_count']==1
  if '--validate-only' in sys.argv:report['demo']='Existing demo independently checked by saved-file validation; not overwritten by this fresh import test.'
  else:report['demo']=build_demo()
  report['pass']=True
 except:report['error']=traceback.format_exc()
 finish()
def setup():
 try:browser.spaces.active.params.asset_library_reference=library.name;bpy.app.timers.register(execute,first_interval=8)
 except:report['error']=traceback.format_exc();finish()
bpy.app.timers.register(setup,first_interval=2)
