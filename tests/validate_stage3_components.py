import bpy,json,math
from pathlib import Path
r=bpy.data.objects['RepairRig']; s=bpy.context.scene; roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R']; out={}
def update(f): s.frame_set(f); r.update_tag(); bpy.context.view_layer.update()
def bone(n): return r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones[n]
# Actual NLA repetition, then mute the tool layer while preserving body and brace.
update(170); p0=roll.matrix_world.copy(); body=bone('torso').matrix.copy(); brace=bone('DEF-hand.L').matrix.copy()
update(206); p1=roll.matrix_world.copy()
out['repeat_transform_error']=max(abs(p0[i][j]-p1[i][j]) for i in range(4) for j in range(4))
update(174); moving=roll.matrix_world.copy(); out['unmuted_stroke_motion']=p0.to_quaternion().rotation_difference(moving.to_quaternion()).angle
update(170); roll.animation_data.nla_tracks[0].mute=True; update(174)
out['muting_tool_rotation_delta']=p0.to_quaternion().rotation_difference(roll.matrix_world.to_quaternion()).angle
out['body_unchanged_when_tool_muted']=max(abs(body[i][j]-bone('torso').matrix[i][j]) for i in range(4) for j in range(4))
out['brace_unchanged_when_tool_muted']=max(abs(brace[i][j]-bone('DEF-hand.L').matrix[i][j]) for i in range(4) for j in range(4))
roll.animation_data.nla_tracks[0].mute=False
# Single-frame pose Action round-trip on the correct object slot.
asset=bpy.data.actions['POSE_Grip_Screwdriver_R']; griptrack=r.animation_data.nla_tracks['GRIP_Close_Screwdriver_R']; griptrack.mute=True
for finger in ('f_index','f_middle','f_ring','f_pinky','thumb'): r.pose.bones[finger+'.01_master.R'].scale=(1,1,1)
r.animation_data.action=asset; r.animation_data.action_slot=asset.slots[0]; update(170)
out['pose_asset_values']={f:r.pose.bones[f+'.01_master.R'].scale.y for f in ('f_index','f_middle','f_ring','f_pinky','thumb')}
out['pose_asset_marked']=bool(asset.asset_data); out['pose_asset_slots']=len(asset.slots)
r.animation_data.action=None; griptrack.mute=False; update(170)
# Every rig Action owns disjoint F-curve channels. Slots identify the rig object,
# not a body-part mask. Fail on accidental ownership overlap.
owned={}; overlap=[]
for tr in r.animation_data.nla_tracks:
 for st in tr.strips:
  for fc in st.action.layers[0].strips[0].channelbag(st.action_slot).fcurves:
   k=(fc.data_path,fc.array_index)
   if k in owned: overlap.append([owned[k],tr.name,str(k)])
   owned[k]=tr.name
out['overlapping_rig_channels']=overlap
out['pass']=out['repeat_transform_error']<1e-5 and out['muting_tool_rotation_delta']<1e-5 and out['unmuted_stroke_motion']>.01 and out['body_unchanged_when_tool_muted']<1e-5 and out['brace_unchanged_when_tool_muted']<1e-5 and not overlap and out['pose_asset_marked'] and all(v<.8 for v in out['pose_asset_values'].values())
Path('E:/RepairRig/tests/stage3_component_validation.json').write_text(json.dumps(out,indent=2))
assert out['pass'],out

