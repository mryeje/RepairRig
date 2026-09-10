"""Stage 3 authoring only. Run in visible Blender using the existing runner.
The saved scene needs no runner, callbacks, or custom animation runtime.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
ROOT=Path('E:/RepairRig')
assert not bpy.data.collections.get('Stage 3 | Appliance and interaction'), 'Reload Stage 2 in a separate runner job first.'
rig=bpy.data.objects['RepairRig']; scene=bpy.context.scene
bpy.context.view_layer.objects.active=rig
if rig.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
scene.frame_start=1; scene.frame_end=288; scene.render.fps=24
rest={p.name:p.matrix.copy() for p in rig.pose.bones}
col=bpy.data.collections.new('Stage 3 | Appliance and interaction'); scene.collection.children.link(col)
def link(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj); return obj
def mat(name,color,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.35
    return m
enamel=mat('Appliance | porcelain',(.69,.75,.77)); trim=mat('Appliance | dark trim',(.035,.065,.085)); metal=mat('Tool | steel',(.47,.55,.61),.8); rubber=mat('Tool | amber grip',(.95,.28,.045)); floor_mat=mat('Floor | slate',(.16,.20,.23))
def cube(name,loc,size,material,bevel=.01,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=link(bpy.context.object); o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel: m=o.modifiers.new('Soft proxy edges','BEVEL'); m.width=bevel; m.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o
def empty(name,loc=(0,0,0),parent=None,size=.07):
    o=bpy.data.objects.new(name,None); col.objects.link(o); o.empty_display_type='ARROWS'; o.empty_display_size=size; o.parent=parent; o.location=loc; o.show_in_front=True; return o
def cylinder(name,radius,depth,loc,material,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc); o=link(bpy.context.object); o.name=name; o.data.materials.append(material)
    if parent: o.parent=parent
    m=o.modifiers.new('Edge highlight','BEVEL'); m.width=.002; m.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
def update(): rig.update_tag(); bpy.context.view_layer.update()
def key_pose(name,frame,loc=None,rot=None):
    p=rig.pose.bones[name]; p.rotation_mode='QUATERNION'
    m=rest[name].copy()
    if rot is not None: m=rot.to_matrix().to_4x4(); m.translation=rest[name].translation
    if loc is not None: m.translation=loc
    p.matrix=m; update()
    for path in ('location','rotation_quaternion','scale'): p.keyframe_insert(path,frame=frame,group=name)
def start_action(): rig.animation_data.action=None
def finish_action(name):
    a=rig.animation_data.action; a.name=name; a.use_fake_user=True; a['Stage']='3 | interaction POC'; rig.animation_data.action=None
    tr=rig.animation_data.nla_tracks.new(); tr.name=name; st=tr.strips.new(name,int(a.frame_range[0]),a); st.action_slot=a.slots[0]; st.blend_type='REPLACE'; st.extrapolation='HOLD_FORWARD'; return a
def action_curves(a):
    return [fc for layer in a.layers for s in layer.strips for slot in a.slots if (bag:=s.channelbag(slot)) for fc in bag.fcurves]
def smooth(a):
    for fc in action_curves(a):
        for k in fc.keyframe_points: k.handle_left_type='AUTO_CLAMPED'; k.handle_right_type='AUTO_CLAMPED'
def influence(c,keys):
    for f,v in keys: c.influence=v; c.keyframe_insert('influence',frame=f)
cab=cube('APPLIANCE_Washer_Proxy',(0,-1.03,.57),(1.03,.64,1.14),enamel,.035)
cube('APPLIANCE_LowerServicePanel',(0,-.700,.30),(.95,.022,.50),trim,.012)
cube('APPLIANCE_ControlPanel',(0,-.697,1.035),(.91,.028,.13),trim)
door=cylinder('APPLIANCE_Door',.285,.035,(0,-.69,.67),trim); door.rotation_euler.x=math.pi/2
glass=cylinder('APPLIANCE_DoorGlass',.235,.045,(0,-.663,.67),metal); glass.rotation_euler.x=math.pi/2
cube('GROUND',(0,-.25,-.045),(4.6,4,.06),floor_mat)
cube('KNEEL_Pad_L',(.13,-.045,.011),(.25,.30,.022),trim,.02)
# Tool coordinates: local +Z goes from grip to tip, toward the appliance.
tool_q=Vector((0,-1,0)).to_track_quat('Z','Y')
screw=empty('TARGET_Screw',(-.24,-.674,.48)); screw.rotation_mode='QUATERNION'; screw.rotation_quaternion=tool_q
screw['Purpose']='Move this Empty to adapt the engaged right hand, tool and look. +Z points into the appliance.'
head=cylinder('SCREW_Visible',.017,.01,(0,0,0),metal,screw)
cube('SCREW_Slot',(0,0,-.006),(.023,.004,.003),trim,.0005,head)
look=empty('TARGET_Look',(0,0,0),screw)
brace=empty('TARGET_Brace_L',(.27,-.642,.75))
# Orient the right fist vertically; shaft crosses the fist along hand local X.
hand_q=Matrix(((-1,0,0),(0,0,-1),(0,-1,0))).to_quaternion()
grip_local=Vector((-.027,.122,0))
grip_from_hand=Matrix.Translation(grip_local) @ (hand_q.inverted() @ tool_q).to_matrix().to_4x4()
tool=empty('TOOL_Screwdriver',size=.035); tool['Grip_reference']='Object origin is grip centre. +Z is shaft/tip; tip is +0.235 m.'
cylinder('Screwdriver_Handle',.020,.115,(0,0,-.015),rubber,tool)
cylinder('Screwdriver_Collar',.023,.013,(0,0,.048),trim,tool)
cylinder('Screwdriver_Shaft',.004,.167,(0,0,.135),metal,tool)
cube('Screwdriver_Blade',(0,0,.226),(.012,.003,.018),metal,.001,tool)
cube('Screwdriver_RotationStripe',(.020,0,-.015),(.004,.009,.087),trim,.001,tool)
tip=empty('REF_ScrewdriverTip',(0,0,.235),tool,.018)
pick=empty('TARGET_ToolGrip',(-.38,-.32,.40)); pick.rotation_mode='QUATERNION'; pick.rotation_quaternion=tool_q
pick['Purpose']='Independent pickup socket. Move before authoring pickup; never constrain it to the attached tool.'
cube('TOOL_RestStand',(-.38,-.32,.28),(.20,.24,.10),trim,.015)
tool.matrix_world=pick.matrix_world.copy(); update()
# Grip references are standard Copy Transforms + static local offset, no dependency cycle.
hand_ref=empty('REF_Hand_R',size=.035); c=hand_ref.constraints.new('COPY_TRANSFORMS'); c.target=rig; c.subtarget='hand_ik.R'
socket=empty('ATTACH_Screwdriver_R',parent=hand_ref,size=.03); socket.matrix_basis=grip_from_hand
pickup_wrist=empty('CONTACT_PickupWrist_R',parent=pick,size=.045); pickup_wrist.matrix_basis=grip_from_hand.inverted()
roll=empty('CONTACT_ScrewdriverRoll_R',parent=screw,size=.04)
work_grip=empty('CONTACT_WorkGrip_R',(0,0,-.235),roll,size=.025)
work_wrist=empty('CONTACT_WorkWrist_R',parent=work_grip,size=.045); work_wrist.matrix_basis=grip_from_hand.inverted()
brace.rotation_mode='QUATERNION'; brace.rotation_quaternion=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_quaternion()
# Body keys own only torso, chest, feet and knee poles.
start_action()
body_frames=[(1,0),(16,0),(38,.30),(64,1),(288,1)]
for f,t in body_frames:
    key_pose('torso',f,rest['torso'].translation+Vector((0,.06*t,-.50*t)),Quaternion((1,0,0),.55*t))
    p=rig.pose.bones['chest']; p.rotation_mode='QUATERNION'; p.location=(0,0,0); p.rotation_quaternion=Quaternion((1,0,0),.25*t); p.keyframe_insert('rotation_quaternion',frame=f,group='chest')
    for side in ('L','R'):
        end=Vector((.13,.39,.20)) if side=='L' else Vector((-.16,-.40,.0852))
        pos=rest['foot_ik.'+side].translation.lerp(end,t)
        if side=='L': pos.z+=.09*math.sin(math.pi*t)
        key_pose('foot_ik.'+side,f,pos,Quaternion((1,0,0),math.radians(65)*t if side=='L' else 0) @ rest['foot_ik.'+side].to_quaternion())
        key_pose('thigh_ik_target.'+side,f,(.14 if side=='L' else -.18,-1.05,.22 if side=='L' else .65))
body=finish_action('BODY_Kneel_L'); smooth(body)
# Free hand trajectories remain on Rigify IK controls; contact constraints take over later.
for side in ('R','L'):
    start_action()
    for f,pos in [(1,(-.27 if side=='R' else .27,-.04,1.065)),(16,(-.27 if side=='R' else .27,-.04,1.065)),(38,(-.31 if side=='R' else .32,-.07,.91)),(64,(-.32 if side=='R' else .34,-.12,.60)),(82,(-.33 if side=='R' else .29,-.28,.55))]:
        scene.frame_set(f); update(); key_pose('hand_ik.'+side,f,pos,hand_q if side=='R' else hand_q @ Quaternion((0,1,0),math.pi))
        key_pose('upper_arm_ik_target.'+side,f,(-.72 if side=='R' else .72,.15,.75 if f>=64 else 1.20))
    p=rig.pose.bones['hand_ik.'+side]
    if side=='R':
        c=p.constraints.new('COPY_TRANSFORMS'); c.name='Pickup | TARGET_ToolGrip'; c.target=pickup_wrist; c.owner_space='WORLD'; c.target_space='WORLD'
        influence(c,[(1,0),(82,0),(104,1),(118,1),(146,0),(288,0)])
        c=p.constraints.new('COPY_TRANSFORMS'); c.name='Work | TARGET_Screw'; c.target=work_wrist; c.owner_space='WORLD'; c.target_space='WORLD'
        influence(c,[(1,0),(118,0),(146,1),(288,1)])
        a=finish_action('REACH_Forward_Low_R')
    else:
        c=p.constraints.new('COPY_TRANSFORMS'); c.name='Brace | TARGET_Brace_L'; c.target=brace; c.owner_space='WORLD'; c.target_space='WORLD'
        influence(c,[(1,0),(64,0),(94,1),(288,1)])
        a=finish_action('LEFT_Brace')
    smooth(a)
# Grip is a narrowly keyed transition plus a native single-frame Pose Asset.
start_action()
fingers=['f_index','f_middle','f_ring','f_pinky','thumb']
for f,t in [(1,0),(101,0),(112,1),(288,1)]:
    for finger in fingers:
        p=rig.pose.bones[finger+'.01_master.R']; p.scale.y=1-(.42 if finger!='thumb' else .30)*t; p.keyframe_insert('scale',frame=f,group=p.name)
grip=finish_action('GRIP_Close_Screwdriver_R'); smooth(grip)
scene.frame_set(112); update()
bpy.context.view_layer.objects.active=rig; bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.ops.object.mode_set(mode='POSE')
for p in rig.pose.bones: p.select=p.name in [x+'.01_master.R' for x in fingers]
rig.data.bones.active=rig.data.bones['f_index.01_master.R']
bpy.ops.poselib.create_pose_asset(pose_name='POSE_Grip_Screwdriver_R',asset_library_reference='LOCAL')
asset=bpy.data.actions['POSE_Grip_Screwdriver_R']; asset.use_fake_user=True; asset.asset_data.description='Right finger masters only. Fit thumb and handle offset when changing tool size. Authored for Stage 3 screwdriver.'
rig.animation_data.action=None; bpy.ops.object.mode_set(mode='OBJECT')
# Head rotation is targeted without touching generated MCH/DEF constraints.
start_action(); c=rig.pose.bones['head'].constraints.new('DAMPED_TRACK'); c.name='Look | TARGET_Look'; c.target=look; c.track_axis='TRACK_Z'
influence(c,[(1,0),(48,.1),(90,.78),(288,.78)]); a=finish_action('HEAD_Look_Target'); smooth(a)
# Standard Child Of: inverse cancels the tool's pickup transform at activation.
scene.frame_set(112); update(); tool.matrix_world=pick.matrix_world.copy(); update()
attach=tool.constraints.new('CHILD_OF'); attach.name='Attach / release | right hand socket'; attach.target=socket
attach.inverse_matrix=socket.matrix_world.inverted(); attach.influence=0
influence(attach,[(1,0),(111,0),(112,1),(288,1)])
tool.animation_data.action.name='TOOL_AttachRelease_R'
for fc in action_curves(tool.animation_data.action):
    for k in fc.keyframe_points: k.interpolation='CONSTANT'
# Three short forward twist / disengage / return / reseat cycles via one repeated NLA strip.
roll.rotation_mode='XYZ'
for f,deg,lift in [(1,-35,0),(6,-35,0),(22,55,0),(25,55,-.022),(33,-35,-.022),(37,-35,0)]:
    roll.rotation_euler.z=math.radians(deg); roll.location.z=lift
    roll.keyframe_insert('rotation_euler',index=2,frame=f); roll.keyframe_insert('location',index=2,frame=f)
a=roll.animation_data.action; a.name='TOOL_Screwdriver_CW_R'; a.use_fake_user=True; smooth(a); roll.animation_data.action=None
tr=roll.animation_data.nla_tracks.new(); tr.name='Repeat 3 tightening strokes'; st=tr.strips.new(a.name,152,a); st.action_slot=a.slots[0]; st.repeat=3; st.extrapolation='HOLD'; st.blend_type='REPLACE'
# Render/review setup; leave standard viewport accessible.
for o in list(bpy.data.objects):
    if o.type in ('CAMERA','LIGHT'): bpy.data.objects.remove(o,do_unlink=True)
def camera(name,pos,target,ortho):
    data=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,data); col.objects.link(o); o.location=pos; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); data.type='ORTHO'; data.ortho_scale=ortho; return o
scene.camera=camera('CAM_Interaction_Overview',(-3.3,2.0,2.25),(0,-.38,.86),2.8)
camera('CAM_Grip_Detail',(-1.55,.18,.98),(-.24,-.49,.48),.62)
scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1200; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
sh=scene.display.shading; sh.light='STUDIO'; sh.studiolight_rotate_z=.4; sh.color_type='MATERIAL'; sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_object_outline=True; sh.background_type='WORLD'; scene.world.color=(.10,.13,.16)
for f,label in [(1,'01 Standing'),(16,'02 Lower to left knee'),(64,'03 Kneel'),(94,'04 Left brace'),(104,'05 Pickup'),(112,'06 Grip + attach'),(146,'07 Screw contact'),(152,'08 Three CW strokes'),(260,'09 Hold / retarget review')]: scene.timeline_markers.new(label,frame=f)
scene['Stage 3']='Native Rigify interaction proof of concept. See Stage3_Interaction.md and How_to_set_up_a_new_appliance_repair_shot.md.'
scene.frame_set(170); update()
bpy.context.view_layer.objects.active=rig; bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        s=area.spaces.active; s.region_3d.view_perspective='CAMERA'; s.overlay.show_overlays=False; s.shading.color_type='MATERIAL'
scene.render.filepath=str(ROOT/'renders/stage3_initial.png'); bpy.ops.render.render(write_still=True)
(ROOT/'tests/stage3_build_inventory.json').write_text(json.dumps({'actions':[a.name for a in bpy.data.actions],'bones':{n:list(rig.pose.bones[n].head) for n in ['DEF-shin.L','DEF-shin.R','DEF-foot.L','DEF-foot.R','DEF-hand.R','hand_ik.R']},'grip_fingers_local':{n:list(rig.pose.bones['DEF-hand.R'].matrix.inverted() @ rig.pose.bones[n].head) for n in [f'DEF-{x}.{i:02}.R' for x in fingers for i in (1,2,3)]}},indent=2))




