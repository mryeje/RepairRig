"""Read-only library regression: native Append, instance realization, slots and NLA.

Run with Blender --background --factory-startup --python this_file.
Only disposable tests/library outputs are written; no library/source is saved.
"""
import hashlib
import json
import traceback
from pathlib import Path

import bpy

LIB = Path('E:/BlenderAssets/RepairRig')
OUT = Path('E:/RepairRig/tests/library')
REPORT = {'routes': {}, 'blender': bpy.app.version_string}


def curves(action):
    return [f for layer in action.layers for strip in layer.strips
            for slot in action.slots if (bag := strip.channelbag(slot))
            for f in bag.fcurves]


def append(file, kind, name, instance=False):
    assert bpy.ops.wm.append(directory=str(LIB / file) + '/' + kind + '/',
                             filename=name, instance_collections=instance,
                             do_reuse_local_id=True) == {'FINISHED'}


def update(frame):
    bpy.context.scene.frame_set(frame)
    for obj in bpy.context.scene.objects:
        obj.update_tag()
    bpy.context.view_layer.update()


def sample(rig):
    evaluated = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return {name: list((evaluated.matrix_world @ evaluated.pose.bones[name].matrix).translation)
            for name in ('hand_ik.R', 'hand_ik.L', 'DEF-hand.R', 'DEF-hand.L')}


def test_route(instance):
    bpy.ops.wm.read_factory_settings(use_empty=False)
    append('Character/RepairRig_Production.blend', 'Collection',
           'RepairRig_Character_Production', instance)
    if instance:
        instances = [o for o in bpy.context.scene.objects if o.instance_collection]
        assert len(instances) == 1
        bpy.ops.object.select_all(action='DESELECT')
        instances[0].select_set(True)
        bpy.context.view_layer.objects.active = instances[0]
        assert bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True) == {'FINISHED'}
    rigs = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    assert len(rigs) == 1, [o.name for o in rigs]
    rig = rigs[0]
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    result = {'rig': rig.name, 'actions': {}, 'constraint_targets': {}}
    for bone in ('hand_ik.R', 'hand_ik.L'):
        for constraint in rig.pose.bones[bone].constraints:
            if constraint.type == 'COPY_TRANSFORMS':
                result['constraint_targets'][constraint.name] = constraint.target.name
                assert constraint.target.name in bpy.context.scene.objects
    mesh = next(o for o in bpy.context.scene.objects if o.name.startswith('Chris-Low-poly'))
    assert all(m.object == rig for m in mesh.modifiers if m.type == 'ARMATURE')
    for obj in bpy.context.scene.objects:
        if obj.animation_data:
            obj.animation_data.action = None
            for track in obj.animation_data.nla_tracks:
                track.mute = True
    baseline = {p.name: p.matrix_basis.copy() for p in rig.pose.bones}
    influences = {(p.name, c.name): c.influence for p in rig.pose.bones for c in p.constraints}
    roll = rig['repairrig_work_roll']
    # Realization should remap rig-owned helper pointers as well as bone constraints.
    assert roll.name in bpy.context.scene.objects
    roll_basis = roll.matrix_basis.copy()
    names = ['REACH_Forward_Mid_R', 'REACH_Forward_Low_R', 'REACH_Forward_Low_L',
             'BRACE_Forward_L', 'BODY_Kneel_L', 'TOOL_Screwdriver_CW_R',
             'GESTURE_Talk_OneHand_R']
    for name in names:
        for obj in (rig, roll):
            if obj.animation_data:
                obj.animation_data.action = None
        for p in rig.pose.bones:
            p.matrix_basis = baseline[p.name]
            for c in p.constraints:
                c.influence = influences[p.name, c.name]
        roll.matrix_basis = roll_basis
        append('Actions/RepairRig_Motion.blend', 'Action', name)
        action = bpy.data.actions[name]
        owner = roll if name.startswith('TOOL_Screwdriver') else rig
        owner.animation_data_create()
        owner.animation_data.action = action
        owner.animation_data.action_slot = action.slots[0]
        fcurves = curves(action)
        for fc in fcurves:
            owner.path_resolve(fc.data_path)
        samples = []
        for frame in (1, 17, 33):
            update(frame)
            values = []
            for fc in fcurves:
                value = owner.path_resolve(fc.data_path)
                value = value if isinstance(value, (float, int, bool)) else value[fc.array_index]
                assert abs(value - fc.evaluate(frame)) < 1e-4, (name, fc.data_path, frame, value)
                values.append(value)
            samples.append({'frame': frame, 'hands': sample(rig), 'values': values})
        assert samples[0]['values'] != samples[-1]['values'], name
        if name.startswith(('REACH_', 'BRACE_')):
            side = 'L' if name.endswith('_L') else 'R'
            assert samples[0]['hands']['DEF-hand.' + side] != samples[-1]['hands']['DEF-hand.' + side]
        result['actions'][name] = {'slot': action.slots[0].identifier,
                                  'frame_range': list(action.frame_range),
                                  'curves': len(fcurves), 'samples': samples}
    # Direct Action versus native NLA evaluation must agree at all three samples.
    action = bpy.data.actions['REACH_Forward_Mid_R']
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    direct = []
    for frame in (1, 17, 33):
        update(frame)
        direct.append(sample(rig))
    track = rig.animation_data.nla_tracks.new()
    track.name = 'Validated appended reach'
    strip = track.strips.new(action.name, 1, action)
    strip.action_slot = action.slots[0]
    rig.animation_data.action = None
    rig.animation_data.use_nla = True
    for i, frame in enumerate((1, 17, 33)):
        update(frame)
        assert sample(rig) == direct[i]
    result['nla_matches_action'] = True
    saved = OUT / ('motion_import_instance.blend' if instance else 'motion_import_append.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(saved), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(saved), use_scripts=False)
    rig = bpy.data.objects[result['rig']]
    for i, frame in enumerate((1, 17, 33)):
        update(frame)
        assert sample(rig) == direct[i]
    result['reopen_pass'] = True
    return result


try:
    OUT.mkdir(parents=True, exist_ok=True)
    motion = LIB / 'Actions/RepairRig_Motion.blend'
    REPORT['motion_sha256_before'] = hashlib.sha256(motion.read_bytes()).hexdigest()
    with bpy.data.libraries.load(str(motion)) as (source, destination):
        REPORT['motion_inventory'] = {'actions': list(source.actions), 'objects': list(source.objects)}
    assert len(REPORT['motion_inventory']['actions']) == 15
    assert not REPORT['motion_inventory']['objects']
    for instance in (False, True):
        REPORT['routes']['instance_real' if instance else 'direct_append'] = test_route(instance)
    REPORT['motion_sha256_after'] = hashlib.sha256(motion.read_bytes()).hexdigest()
    assert REPORT['motion_sha256_before'] == REPORT['motion_sha256_after']
    REPORT['pass'] = True
except Exception:
    REPORT['error'] = traceback.format_exc()
finally:
    (OUT / 'motion_import_validation.json').write_text(json.dumps(REPORT, indent=2))
    print(json.dumps(REPORT, indent=2), flush=True)
