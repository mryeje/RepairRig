"""Persist the committed Stage 3 interaction on the existing Stage 2 checkpoint.
Run in a separate Blender UI process with --python; never in an unrelated scene.
No generation, mannequin construction, or pose-fitting scripts are replayed.
"""
import bpy
import addon_utils
import hashlib
import json
import runpy
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'blend/RepairRig_03_InteractionTest.blend'
SECOND = ROOT / 'tests/RepairRig_03_TargetB.blend'


def architecture():
    return {
        name: [(b.name, b.parent.name if b.parent else None,
                [list(row) for row in b.matrix_local], b.use_deform)
               for b in bpy.data.objects[name].data.bones]
        for name in ('RepairRig', 'RepairRig_Metarig')
    }


def action_signature():
    return {
        a.name: [(fc.data_path, fc.array_index,
                  [(list(k.co), list(k.handle_left), list(k.handle_right),
                    k.interpolation) for k in fc.keyframe_points])
                 for layer in a.layers for strip in layer.strips
                 for slot in a.slots if (bag := strip.channelbag(slot))
                 for fc in bag.fcurves]
        for a in bpy.data.actions
    }


def main():
    assert not MAIN.exists() and not SECOND.exists(), 'Deliverables exist; reopen/validate them instead.'
    base = ROOT / 'blend/RepairRig_02_ControlRig.blend'
    base_hash = hashlib.sha256(base.read_bytes()).hexdigest()
    assert Path(bpy.data.filepath).resolve() == base.resolve(), 'Launch with the Stage 2 checkpoint'
    addon_utils.enable('rigify', default_set=True, persistent=True)
    before = architecture()
    # These two committed scripts already contain the final fitted values.
    for script in ('09_stage3_build.py', '11_stage3_refine.py'):
        runpy.run_path(str(ROOT / 'scripts' / script), run_name='__main__')
    assert architecture() == before, 'Base armature/rest architecture changed'
    assert hashlib.sha256(base.read_bytes()).hexdigest() == base_hash
    scene = bpy.context.scene
    scene.camera = bpy.data.objects['CAM_Interaction_Overview']
    scene.frame_set(170)
    bpy.context.view_layer.update()
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 85
    scene.render.resolution_percentage = 75
    scene.render.filepath = str(ROOT / 'renders/stage3_frame_170.jpg')
    scene['Stage 3'] = 'Native Rigify interaction proof of concept. See docs/Stage3_Interaction.md.'
    notes = bpy.data.texts.get('Stage3_Interaction.md') or bpy.data.texts.new('Stage3_Interaction.md')
    notes.clear()
    notes.write((ROOT / 'docs/Stage3_Interaction.md').read_text())
    signatures = action_signature()
    bpy.ops.wm.save_as_mainfile(filepath=str(MAIN), compress=True)
    target = bpy.data.objects['TARGET_Screw']
    target.location = bpy.data.objects['REF_Screw_Location_B'].location.copy()
    scene.frame_set(170)
    bpy.context.view_layer.update()
    assert action_signature() == signatures
    bpy.ops.wm.save_as_mainfile(filepath=str(SECOND), compress=True, copy=True)
    report = {'base_sha256': base_hash, 'base_architecture_preserved': True,
              'source_scripts': ['scripts/09_stage3_build.py', 'scripts/11_stage3_refine.py'],
              'action_signature': signatures}
    (ROOT / 'tests/stage3_persistence.json').write_text(json.dumps(report, indent=2))
    runpy.run_path(str(ROOT / 'tests/validate_stage3_reopen.py'), run_name='__main__')


def execute():
    try:
        main()
        result = {'pass': True}
    except Exception:
        result = {'pass': False, 'traceback': traceback.format_exc()}
    (ROOT / 'tests/stage3_finalize_status.json').write_text(json.dumps(result, indent=2))
    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=1)

bpy.app.timers.register(execute, first_interval=2)


