"""Run in visible Blender after 04_mannequin. Measures evaluated outcomes.
Temporary Actions are removed; the final checkpoint remains unanimated.
"""
import bpy, json, math
from mathutils import Vector, Quaternion
from pathlib import Path
ROOT=Path('E:/RepairRig'); rig=bpy.data.objects['RepairRig']; scene=bpy.context.scene
results={}
def update():
    rig.update_tag(); bpy.context.view_layer.update(); scene.frame_set(scene.frame_current)
def point(name):
    return rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones[name].head.copy()
def rotate(name,axis,angle):
    p=rig.pose.bones[name]
    if p.rotation_mode=='QUATERNION': p.rotation_quaternion=Quaternion(axis,angle)
    else: p.rotation_euler=Quaternion(axis,angle).to_euler(p.rotation_mode)
def move_world(name,delta):
    p=rig.pose.bones[name]; m=p.matrix.copy(); m.translation+=Vector(delta); p.matrix=m; update()
def mesh_points(name):
    obj=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=obj.to_mesh(); pts=[obj.matrix_world@v.co for v in mesh.vertices]; obj.to_mesh_clear(); return pts
saved={p.name:p.matrix_basis.copy() for p in rig.pose.bones}
props={p.name:{k:p[k] for k in p.keys()} for p in rig.pose.bones}
def reset():
    for p in rig.pose.bones:
        p.matrix_basis=saved[p.name]
        for k,value in props[p.name].items(): p[k]=value
    update()
def check(name,value,passed):
    results[name]={'value':value,'pass':bool(passed)}
    (ROOT/'tests/base_validation.json').write_text(json.dumps(results,indent=2))
    assert passed, f'{name}: {value}'
update()
required=['root','torso','hips','chest','neck','head']
for side in ('L','R'):
    required += [n+'.'+side for n in ('hand_ik','foot_ik','upper_arm_ik_target','thigh_ik_target','upper_arm_fk','forearm_fk','hand_fk','thigh_fk','shin_fk','foot_fk')]
check('required_controls',required,all(n in rig.pose.bones for n in required))
check('hidden_internal_collections',[c.name for c in rig.data.collections_all if c.name in ('DEF','ORG','MCH') and not c.is_visible],all(not rig.data.collections_all[n].is_visible for n in ('DEF','ORG','MCH')))
meshes=list(bpy.data.collections['Character | Proxy'].objects)
invalid=[]
for obj in meshes:
    for vert in obj.data.vertices:
        weights=[g.weight for g in vert.groups if rig.data.bones.get(obj.vertex_groups[g.group].name) and rig.data.bones[obj.vertex_groups[g.group].name].use_deform]
        if abs(sum(weights)-1)>1e-5: invalid.append([obj.name,vert.index])
check('normalized_DEF_weights',len(invalid),not invalid)
for side in ('L','R'):
    reset(); before=mesh_points('Proxy_ElbowBlend.'+side)
    move_world('hand_ik.'+side,(-.12 if side=='L' else .12,-.16,.04))
    error=(point('DEF-hand.'+side)-point('hand_ik.'+side)).length
    check('hand_IK_error_'+side,error,error<.002)
    displacement=max((a-b).length for a,b in zip(before,mesh_points('Proxy_ElbowBlend.'+side)))
    check('elbow_skin_deforms_'+side,displacement,displacement>.01)
    reset(); feet={s:point('DEF-foot.'+s) for s in ('L','R')}
    move_world('torso',(0,0,-.14))
    error=max((point('DEF-foot.'+s)-feet[s]).length for s in feet)
    check('planted_feet_torso_lower_'+side,error,error<.002)
    knee=point('DEF-shin.'+side)
    move_world('thigh_ik_target.'+side,(.15,0,0))
    delta=(point('DEF-shin.'+side)-knee).length
    check('knee_pole_response_'+side,delta,delta>.005)
    reset(); rig.pose.bones['upper_arm_parent.'+side]['IK_FK']=1.; update()
    before=point('DEF-hand.'+side); rotate('forearm_fk.'+side,(1,0,0),.55); update()
    delta=(point('DEF-hand.'+side)-before).length
    check('arm_FK_response_'+side,delta,delta>.03)
    reset(); rig.pose.bones['thigh_parent.'+side]['IK_FK']=1.; update()
    before=point('DEF-foot.'+side); rotate('shin_fk.'+side,(1,0,0),.5); update()
    delta=(point('DEF-foot.'+side)-before).length
    check('leg_FK_response_'+side,delta,delta>.03)
    reset(); before=point('DEF-f_index.03.'+side)
    rig.pose.bones['f_index.01_master.'+side].scale.y=.55; update()
    delta=(point('DEF-f_index.03.'+side)-before).length
    check('finger_master_curl_'+side,delta,delta>.005)
    reset(); before=mesh_points('Proxy_Lid.'+side)
    rig.pose.bones['lid.'+side]['blink']=1.; update()
    key=bpy.data.objects['Proxy_Lid.'+side].data.shape_keys.key_blocks['Blink'].value
    delta=max((a-b).length for a,b in zip(before,mesh_points('Proxy_Lid.'+side)))
    check('blink_driver_'+side,{'value':key,'motion':delta},key>.99 and delta>.02)
reset()
for control,mesh,axis,angle in [('jaw','Proxy_Jaw',(1,0,0),.3),('eye.L','Proxy_Pupil.L',(0,0,1),.3),('head','Proxy_Head',(0,0,1),.2)]:
    before=mesh_points(mesh); rotate(control,axis,angle); update()
    delta=max((a-b).length for a,b in zip(before,mesh_points(mesh)))
    check('face_'+control,delta,delta>.001); reset()
# Native slotted Action / NLA channel composition, isolated from the rig.
obj=bpy.data.objects.new('TEST_Action_API',None); scene.collection.objects.link(obj)
created=[]
for axis,label in [(0,'X'),(1,'Y')]:
    obj.animation_data_clear(); obj.location=(0,0,0)
    obj.keyframe_insert('location',index=axis,frame=1)
    obj.location[axis]=2.; obj.keyframe_insert('location',index=axis,frame=11)
    action=obj.animation_data.action; action.name='TEST_API_'+label; created.append(action)
    slot=obj.animation_data.action_slot
    bag=action.layers[0].strips[0].channelbag(slot)
    for fc in bag.fcurves:
        for key in fc.keyframe_points: key.interpolation='LINEAR'
    check('Action_slot_'+label,{'slots':len(action.slots),'curves':len(bag.fcurves)},len(action.slots)==1 and len(bag.fcurves)==1)
obj.animation_data_clear(); obj.animation_data_create(); obj.location=(0,0,0)
for action in created:
    track=obj.animation_data.nla_tracks.new(); strip=track.strips.new(action.name,1,action)
    strip.action_slot=action.slots[0]; strip.blend_type='REPLACE'
scene.frame_set(6); bpy.context.view_layer.update()
check('NLA_disjoint_channel_composition',list(obj.location),abs(obj.location.x-1)<1e-5 and abs(obj.location.y-1)<1e-5)
bpy.data.objects.remove(obj,do_unlink=True)
for a in created: bpy.data.actions.remove(a)
scene.frame_set(1); reset()
# Native pose-asset operator on one selected finger, then remove the test asset.
before=set(bpy.data.actions)
for b in rig.pose.bones: b.select=False
rig.pose.bones['f_index.01_master.R'].select=True
rig.data.bones.active=rig.data.bones['f_index.01_master.R']
bpy.context.view_layer.objects.active=rig
if rig.mode!='POSE': bpy.ops.object.mode_set(mode='POSE')
bpy.ops.poselib.create_pose_asset(pose_name='TEST_PoseAsset',asset_library_reference='LOCAL')
assets=[a for a in bpy.data.actions if a not in before]
check('native_pose_asset_creation',[{'name':a.name,'slots':len(a.slots),'asset':bool(a.asset_data)} for a in assets],bool(assets) and all(a.asset_data and len(a.slots)==1 for a in assets))
rig.animation_data.action=None
for a in assets: bpy.data.actions.remove(a)
reset()
# Keep a reviewable pose test in tests/, not an animation library Action.
move_world('torso',(0,0,-.14))
move_world('hand_ik.R',(.18,-.20,.03))
for finger in ('f_index','f_middle','f_ring','f_pinky','thumb'):
    rig.pose.bones[f'{finger}.01_master.R'].scale.y=.65
update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tests/RepairRig_PoseValidation.blend'))
# Leave the pose visible for inspection. Finalization restores the saved neutral bases.
(ROOT/'tests/neutral_bases.json').write_text(json.dumps({n:[list(row) for row in m] for n,m in saved.items()}))
