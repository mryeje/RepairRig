"""Reopen both deliverables and compare their evaluated motion to saved evidence."""
import bpy
import addon_utils
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reference = json.loads((ROOT / 'tests/stage3_validation.json').read_text())
persisted = json.loads((ROOT / 'tests/stage3_persistence.json').read_text())
addon_utils.enable('rigify', default_set=True, persistent=True)
out = {'version': bpy.app.version_string, 'files': {}}


def signature():
    return {
        a.name: [[fc.data_path, fc.array_index,
                  [[list(k.co), list(k.handle_left), list(k.handle_right),
                    k.interpolation] for k in fc.keyframe_points]]
                 for layer in a.layers for strip in layer.strips
                 for slot in a.slots if (bag := strip.channelbag(slot))
                 for fc in bag.fcurves]
        for a in bpy.data.actions
    }


for label, relative in [('A', 'blend/RepairRig_03_InteractionTest.blend'),
                        ('B', 'tests/RepairRig_03_TargetB.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / relative), use_scripts=True)
    scene = bpy.context.scene
    rig = bpy.data.objects['RepairRig']
    saved_frame = scene.frame_current
    expected_target = reference['reuse']['original' if label == 'A' else 'second']
    target_error = max(abs(a-b) for a, b in zip(bpy.data.objects['TARGET_Screw'].location, expected_target))
    errors = {'hand_R': 0., 'hand_L': 0., 'tip_engaged': 0., 'socket': 0., 'actual_grip': 0.}
    historical_delta = 0.
    for frame in range(1, 289):
        scene.frame_set(frame)
        rig.update_tag()
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        p = rig.evaluated_get(dg).pose.bones
        def matrix(name):
            return bpy.data.objects[name].evaluated_get(dg).matrix_world
        right = (p['DEF-hand.R'].head-p['hand_ik.R'].head).length
        left = (p['DEF-hand.L'].head-p['hand_ik.L'].head).length
        tip = (matrix('REF_ScrewdriverTip').translation-matrix('TARGET_Screw').translation).length
        errors['hand_R'] = max(errors['hand_R'], right)
        errors['hand_L'] = max(errors['hand_L'], left)
        if frame >= 112:
            errors['socket'] = max(errors['socket'], (matrix('TOOL_Screwdriver').translation-matrix('ATTACH_Screwdriver_R').translation).length)
            grip = (rig.matrix_world @ p['DEF-hand.R'].matrix @ bpy.data.objects['ATTACH_Screwdriver_R'].matrix_basis).translation
            errors['actual_grip'] = max(errors['actual_grip'], (grip-matrix('TOOL_Screwdriver').translation).length)
        if 152 <= frame < 260 and (frame-152) % 36 <= 21:
            errors['tip_engaged'] = max(errors['tip_engaged'], tip)
        old = reference['samples'][str(frame)] if label == 'A' else reference['reuse']['frames'][str(frame)]
        historical_delta = max(historical_delta, abs(right-old['hand_error_R' if label == 'A' else 'hand_error']), abs(tip-old['tip_error']))
    invalid = [fc.data_path for fc in rig.animation_data.drivers if not fc.driver.is_valid]
    checks = {
        'saved_working_frame': saved_frame == 170,
        'timeline': (scene.frame_start, scene.frame_end, scene.render.fps) == (1, 288, 24),
        'target_location': target_error < 1e-6,
        'actions_survive_save': signature() == persisted['action_signature'],
        'rig_active_action_unlinked': rig.animation_data.action is None,
        'rig_tracks_enabled': len(rig.animation_data.nla_tracks) == 5 and all(not t.mute for t in rig.animation_data.nla_tracks),
        'drivers': len(rig.animation_data.drivers) == 109 and not invalid,
        'rig_ui': any('rig_ui' in t.name for t in bpy.data.texts),
        'rigify_ui_properties_registered': all(hasattr(c, 'rigify_ui_row') for c in rig.data.collections_all),
        'pose_asset': bool(bpy.data.actions['POSE_Grip_Screwdriver_R'].asset_data),
        'historical_motion_matches': historical_delta < 1e-5,
        'reach': max(errors['hand_R'], errors['hand_L'], errors['actual_grip']) < .002,
        'contact': max(errors['socket'], errors['tip_engaged']) < .0001,
    }
    # Prove release still preserves the whole world matrix after reopening.
    scene.frame_set(170); rig.update_tag(); bpy.context.view_layer.update()
    tool = bpy.data.objects['TOOL_Screwdriver']
    visual = tool.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
    tool.animation_data.action = None
    tool.constraints['Attach / release | right hand socket'].influence = 0
    tool.matrix_world = visual
    bpy.context.view_layer.update()
    release_error = 0.
    for frame in (170, 181):
        scene.frame_set(frame); rig.update_tag(); bpy.context.view_layer.update()
        actual = tool.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
        release_error = max(release_error, max(abs(actual[i][j]-visual[i][j]) for i in range(4) for j in range(4)))
    checks['release_preserves_transform'] = release_error < .0001
    out['files'][label] = {'path': relative, 'sha256': hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),
                            'checks': checks, 'max_errors_metres': errors,
                            'historical_max_delta': historical_delta,
                            'release_matrix_error': release_error, 'pass': all(checks.values())}

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_03_InteractionTest.blend'), use_scripts=True)
out['base_checkpoint_unchanged'] = hashlib.sha256((ROOT/'blend/RepairRig_02_ControlRig.blend').read_bytes()).hexdigest() == persisted['base_sha256']
out['pass'] = out['base_checkpoint_unchanged'] and all(f['pass'] for f in out['files'].values())
(ROOT/'tests/stage3_reopen_validation.json').write_text(json.dumps(out, indent=2))
assert out['pass'], out

