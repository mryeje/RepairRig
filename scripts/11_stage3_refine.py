import bpy,math,json
from pathlib import Path
ROOT=Path('E:/RepairRig'); s=bpy.context.scene; r=bpy.data.objects['RepairRig']; col=bpy.data.collections['Stage 3 | Appliance and interaction']
# Fit the pickup rest to the handle underside; the proxy now stands on the floor.
o=bpy.data.objects['TOOL_RestStand']; o.location.z=.19; o.dimensions=(.18,.22,.38)
# The advancing right foot has a brief lift, rather than sliding on the floor.
a=bpy.data.actions['BODY_Kneel_L']; bag=a.layers[0].strips[0].channelbag(a.slots[0])
for fc in bag.fcurves:
 if fc.data_path=='pose.bones["foot_ik.R"].location' and fc.array_index==2:
  for k in fc.keyframe_points:
   if round(k.co.x)==38: k.co.y+=.08
  fc.update()
# A cross recess makes the quarter-turn return strokes reseat on equivalent axes.
slot=bpy.data.objects['SCREW_Slot']; copy=slot.copy(); copy.data=slot.data.copy(); col.objects.link(copy); copy.name='SCREW_Slot_Cross'; copy.rotation_euler.z=math.pi/2
blade=bpy.data.objects['Screwdriver_Blade']; copy=blade.copy(); copy.data=blade.data.copy(); col.objects.link(copy); copy.name='Screwdriver_Blade_Cross'; copy.rotation_euler.z=math.pi/2
# Visible screw follows the engaged 90-degree strokes, holds during withdrawal.
screw=bpy.data.objects['SCREW_Visible']; screw.rotation_mode='XYZ'
for f,deg in [(1,-35),(152,-35),(157,-35),(173,55),(188,55),(193,55),(209,145),(224,145),(229,145),(245,235),(288,235)]:
 screw.rotation_euler.z=math.radians(deg); screw.keyframe_insert('rotation_euler',index=2,frame=f)
a=screw.animation_data.action; a.name='SHOT_Screw_QuarterTurns'; a.use_fake_user=True
for fc in a.layers[0].strips[0].channelbag(a.slots[0]).fcurves:
 for k in fc.keyframe_points: k.handle_left_type='AUTO_CLAMPED'; k.handle_right_type='AUTO_CLAMPED'
# Exact bookmark for the documented alternate position; no animation or dependency.
ref=bpy.data.objects.new('REF_Screw_Location_B',None); col.objects.link(ref); ref.empty_display_type='CIRCLE'; ref.empty_display_size=.025; ref.matrix_world=bpy.data.objects['TARGET_Screw'].matrix_world.copy(); ref.location.x+=.06; ref.location.z+=.04; ref['Purpose']='Tested second location. Copy location to TARGET_Screw. Not a constraint target.'
for name in ['Targets | appliance','References | hand and tool sockets','Tool | screwdriver','Appliance | proxy','Review | cameras']:
 c=bpy.data.collections.new(name); col.children.link(c)
for o in list(col.objects):
 if o.name.startswith('TARGET_') or o.name=='REF_Screw_Location_B': name='Targets | appliance'
 elif o.type=='EMPTY' and o.name!='TOOL_Screwdriver': name='References | hand and tool sockets'
 elif o.name.startswith(('TOOL_Screwdriver','Screwdriver_')): name='Tool | screwdriver'
 elif o.type=='CAMERA': name='Review | cameras'
 else: name='Appliance | proxy'
 col.objects.unlink(o); bpy.data.collections[name].objects.link(o)
s.frame_set(170); r.update_tag(); bpy.context.view_layer.update()
