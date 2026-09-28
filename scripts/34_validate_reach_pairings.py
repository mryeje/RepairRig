import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/reach_fixed';DST=ROOT/'blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend'
def assign(r,name,f):
 a=bpy.data.actions[name];r.animation_data.use_nla=False;r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];bpy.context.scene.frame_set(f);r.update_tag();bpy.context.view_layer.update()
result={}
for name,body,frame in [('REACH_Forward_Low_R','BODY_Kneel_L',49),('REACH_Forward_Mid_R','BODY_Bend_Forward',33),('REACH_Forward_Low_L','BODY_Kneel_L',49),('BRACE_Forward_L','BODY_Kneel_L',49)]:
 bpy.ops.wm.open_mainfile(filepath=str(DST),use_scripts=False);r=bpy.data.objects['RepairRig'];assign(r,body,frame);samples={}
 for f in [1,17,33]:
  assign(r,name,f);ep=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones;side=name[-1]
  samples[str(f)]={'ik_def_distance':(ep['hand_ik.'+side].head-ep['DEF-hand.'+side].head).length,'hand_head':list(ep['DEF-hand.'+side].head)}
 result[name]={'body':body,'samples':samples}
 print(name,result[name],flush=True)
 if name=='REACH_Forward_Low_R':
  # Existing screwdriver grip is preserved as saved; display actual evaluated hand/tool together.
  s=bpy.context.scene;center=r.matrix_world@ep['DEF-hand.R'].head
  for o in bpy.data.objects:
   if o.type=='MESH':o.hide_render=o.name!='Chris-Low-poly' and not o.name.startswith('Screwdriver_')
  cam=bpy.data.objects.new('ValidationCamera',bpy.data.cameras.new('ValidationCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.45;cam.location=center+Vector((.6,-1,.5));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
  s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';bpy.data.objects['Chris-Low-poly'].color=(.65,.68,.72,1)
  for o in bpy.data.objects:
   if o.name.startswith('Screwdriver_'):o.color=(.95,.3,.08,1)
  s.display.shading.show_cavity=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'screwdriver_grip.png');bpy.ops.render.render(write_still=True)
(OUT/'pairings.json').write_text(json.dumps(result,indent=2));bpy.ops.wm.quit_blender()
