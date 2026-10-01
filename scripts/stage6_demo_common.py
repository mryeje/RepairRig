"""Offline authoring of the distributable demo; playback requires only Blender."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
LIB=Path('E:/BlenderAssets/RepairRig')
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def update():bpy.data.objects['RepairRig'].update_tag();bpy.context.view_layer.update()
def apply_values(r,name):
 for fc in curves(bpy.data.actions[name]):r.path_resolve(fc.data_path)[fc.array_index]=fc.evaluate(1)
 update()
def track(o,a,start,name,hold='HOLD_FORWARD'):
 o.animation_data_create();t=o.animation_data.nla_tracks.new();t.name=name;st=t.strips.new(a.name,start,a);st.action_slot=a.slots[0];st.blend_type='REPLACE';st.extrapolation=hold;return st
def build_demo():
 r=bpy.data.objects['RepairRig'];s=bpy.context.scene
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 r.animation_data.action=None
 for t in list(r.animation_data.nla_tracks):r.animation_data.nla_tracks.remove(t)
 r.animation_data.use_nla=False
 # Shot-specific grip channel sequence; reusable assets remain unedited.
 grip=bpy.data.actions.new('DEMO_HandPoseSequence');grip.slots.new(id_type='OBJECT',name=r.name);r.animation_data.action=grip;r.animation_data.action_slot=grip.slots[0]
 controls=[f+'.01_master.R' for f in ['f_index','f_middle','f_ring','f_pinky','thumb']]+[f+'.%02d.R'%j for f in ['f_index','f_middle','f_ring','f_pinky','thumb'] for j in (1,2,3)]
 for frame,short in [(1,'OpenHand'),(49,'OpenHand'),(65,'Grip_Screwdriver'),(149,'Grip_Screwdriver'),(165,'OpenHand'),(180,'Grip_Pliers'),(240,'Grip_Pliers'),(249,'OpenHand'),(260,'OpenHand')]:
  apply_values(r,'POSE_'+short+'_R_Production')
  for n in controls:
   for ch in ['location','rotation_quaternion','scale']:r.pose.bones[n].keyframe_insert(ch,frame=frame,group=n)
 r.animation_data.action=None
 selector=bpy.data.actions.new('DEMO_ToolSelection');selector.slots.new(id_type='OBJECT',name=r.name);r.animation_data.action=selector;r.animation_data.action_slot=selector.slots[0]
 for frame,value in [(1,0),(65,1),(149,0),(181,2),(241,0),(260,0)]:r['repairrig_tool']=value;r.keyframe_insert(data_path='["repairrig_tool"]',frame=frame,group='Tool selector')
 for fc in curves(selector):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 r.animation_data.action=None;r.animation_data.use_nla=True
 track(r,bpy.data.actions['BODY_Kneel_L'],1,'01 | Body — kneel and hold','HOLD')
 track(r,bpy.data.actions['REACH_Forward_Low_R'],65,'02 | Right hand — work reach','HOLD')
 track(r,grip,1,'03 | Production hand poses','HOLD')
 track(r,selector,1,'04 | Tool pickup / release (Constant)','HOLD')
 roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R'];roll.animation_data_create();roll.animation_data.action=None
 for t in list(roll.animation_data.nla_tracks):roll.animation_data.nla_tracks.remove(t)
 roll.animation_data.use_nla=True;roll.location=(0,0,0);roll.rotation_euler=(0,0,0)
 track(roll,bpy.data.actions['TOOL_Screwdriver_CW_R'],101,'Screwdriver | CW operation','NOTHING')
 # Native, shot-specific screw response: match work-roll rotation and withdrawal.
 screw=bpy.data.objects['SCREW_Visible'];screw.animation_data_clear()
 for path,index in [('rotation_euler',2),('location',2)]:
  base=getattr(screw,path)[index];fc=screw.driver_add(path,index);d=fc.driver;v=d.variables.new();v.name='work';v.type='SINGLE_PROP';v.targets[0].id=roll;v.targets[0].data_path=path+'[2]';d.expression=repr(base)+' + work'
 s.frame_start=1;s.frame_end=260;s.render.fps=24
 for frame,label in [(1,'Kneel'),(65,'Attach screwdriver + reach'),(97,'Screwdriver contact'),(101,'Screwdriver operation'),(149,'Release screwdriver'),(180,'Pliers grip'),(181,'Attach pliers — aligned work'),(241,'Release pliers')]:s.timeline_markers.new(label,frame=frame)
 cam=bpy.data.objects.new('Demo_Camera',bpy.data.cameras.new('Demo_Camera'));s.collection.objects.link(cam);cam.location=(3.1,-4.2,2.4);center=Vector((0,-.25,.9));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.7;s.camera=cam
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=100
 s.render.filepath='//RepairRig_Demo_';s.frame_set(117);update()
 for area in bpy.context.screen.areas if bpy.context.screen else []:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 # Demo-local copies must not duplicate the library's assets in search results.
 for collection in [bpy.data.actions,bpy.data.collections,bpy.data.objects]:
  for id in collection:
   if id.asset_data:id.asset_clear()
 bpy.context.view_layer.objects.active=r
 for o in bpy.context.selected_objects:o.select_set(False)
 r.select_set(True)
 t=bpy.data.texts.new('READ_ME_Demo.txt');t.write('RepairRig Stage 6 independent new-project demo. All content was imported from the reusable library, not a development checkpoint.\nPlay frames 1–260; timeline markers explain each stage. N-panel > RepairRig > RepairRig Tools.\nTool selector has Constant keys on its own NLA track: buttons change current values, while scrubbing restores authored keys. Mute that track for manual tool testing.\nUse trusted embedded scripts to restore UI after reopening. No external Python dependency is required.\nSee ../Docs for library setup, compatibility, and limitations.\n')
 bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
 path=LIB/'Demo/RepairRig_NewProject_Validated.blend'
 assert not path.exists(),'Refusing to overwrite existing demo'
 bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=True,compress=True)
 return str(path)
