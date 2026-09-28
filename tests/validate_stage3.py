import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/RepairRig'); s=bpy.context.scene; r=bpy.data.objects['RepairRig']
def update(f): s.frame_set(f); r.update_tag(); bpy.context.view_layer.update()
def pp(n): return r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones[n]
def wp(n): return bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
def mat(n): return bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
def curves(a): return [fc for l in a.layers for st in l.strips for sl in a.slots if (b:=st.channelbag(sl)) for fc in b.fcurves]
def signature(): return {a.name:[[fc.data_path,fc.array_index,[[float(k.co.x),float(k.co.y)] for k in fc.keyframe_points]] for fc in curves(a)] for a in bpy.data.actions}
results={'background':bpy.app.background,'version':bpy.app.version_string,'samples':{}}
for f in range(1,289):
 update(f)
 data={'hand_error_R':(pp('DEF-hand.R').head-pp('hand_ik.R').head).length,'hand_error_L':(pp('DEF-hand.L').head-pp('hand_ik.L').head).length,'tip_error':(wp('REF_ScrewdriverTip')-wp('TARGET_Screw')).length,'socket_error':(wp('TOOL_Screwdriver')-wp('ATTACH_Screwdriver_R')).length,'knee_L':list(pp('DEF-shin.L').head),'foot_R':list(pp('DEF-foot.R').head),'foot_L':list(pp('DEF-foot.L').head)}
 data['actual_grip_error']=((r.matrix_world @ pp('DEF-hand.R').matrix @ bpy.data.objects['ATTACH_Screwdriver_R'].matrix_basis).translation-wp('TOOL_Screwdriver')).length
 results['samples'][str(f)]=data
results['max_hand_error_R']=max(x['hand_error_R'] for x in results['samples'].values())
results['max_hand_error_L']=max(x['hand_error_L'] for x in results['samples'].values())
results['max_attached_socket_error']=max(x['socket_error'] for f,x in results['samples'].items() if int(f)>=112)
contact_frames=[f for f in range(152,260) if (f-152)%36<=21]
results['max_engaged_tip_error']=max(results['samples'][str(f)]['tip_error'] for f in contact_frames)
# Reuse trial: physically move one screw Empty, evaluate the entire contact animation,
# and compare every Action key to prove no rebuild or animation edit occurred.
target=bpy.data.objects['TARGET_Screw']; original=target.location.copy(); before=signature(); target.location+=Vector((.06,0,.04))
results['reuse']={'original':list(original),'second':list(target.location),'changed_only':'TARGET_Screw.location','frames':{}}
for f in range(1,289):
 update(f); results['reuse']['frames'][str(f)]={'hand_error':(pp('DEF-hand.R').head-pp('hand_ik.R').head).length,'tip_error':(wp('REF_ScrewdriverTip')-wp('TARGET_Screw')).length}
results['reuse']['actions_identical']=signature()==before
results['reuse']['max_hand_error']=max(x['hand_error'] for x in results['reuse']['frames'].values())
results['reuse']['max_engaged_tip_error']=max(results['reuse']['frames'][str(f)]['tip_error'] for f in contact_frames)
s.render.image_settings.file_format='JPEG'; s.render.image_settings.quality=85; s.render.resolution_percentage=75
update(170); s.render.filepath=str(ROOT/'renders/stage3_second_location.jpg'); bpy.ops.render.render(write_still=True)
target.location=original; update(170)
# Release experiment: preserve visual matrix while disabling Child Of, then move
# the hand through another stroke. Restore the original scene animation afterward.
tool=bpy.data.objects['TOOL_Screwdriver']; c=tool.constraints['Attach / release | right hand socket']; action=tool.animation_data.action; slot=tool.animation_data.action_slot; basis=tool.matrix_basis.copy(); visual=mat(tool.name); tool.animation_data.action=None; c.influence=0; tool.matrix_world=visual; bpy.context.view_layer.update()
release0=mat(tool.name); update(181); release1=mat(tool.name)
results['release']={'preserved_world_error':max(abs(visual[i][j]-release0[i][j]) for i in range(4) for j in range(4)),'drift_after_hand_moves':(release1.translation-release0.translation).length}
tool.matrix_basis=basis; tool.animation_data.action=action; tool.animation_data.action_slot=slot; update(170)
results['rigify_invalid_drivers']=[fc.data_path for fc in r.animation_data.drivers if not fc.driver.is_valid]
results['rigify_driver_count']=len(r.animation_data.drivers)
results['nla']={o.name:[{'track':t.name,'strips':[{'action':st.action.name,'slot':st.action_slot.identifier,'repeat':st.repeat,'start':st.frame_start,'end':st.frame_end,'blend':st.blend_type} for st in t.strips]} for t in o.animation_data.nla_tracks] for o in (r,bpy.data.objects['CONTACT_ScrewdriverRoll_R'])}
results['max_actual_grip_error']=max(x['actual_grip_error'] for f,x in results['samples'].items() if int(f)>=112)
results['pass']=results['max_hand_error_R']<.002 and results['max_hand_error_L']<.002 and results['max_actual_grip_error']<.002 and results['max_attached_socket_error']<.0001 and results['max_engaged_tip_error']<.0001 and results['reuse']['actions_identical'] and results['reuse']['max_hand_error']<.002 and results['reuse']['max_engaged_tip_error']<.0001 and results['release']['drift_after_hand_moves']<.0001 and not results['rigify_invalid_drivers']
(ROOT/'tests/stage3_validation.json').write_text(json.dumps(results,indent=2))
assert results['pass'], 'See stage3_validation.json'
# Review essential poses and the grip using actual rendered geometry.
for f in (1,38,64,104,112,146,170,184,246):
 update(f); s.render.filepath=str(ROOT/f'renders/stage3_frame_{f:03}.jpg'); bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_Grip_Detail']; update(170); s.render.filepath=str(ROOT/'renders/stage3_grip_detail.jpg'); bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM_Interaction_Overview']; update(170)

