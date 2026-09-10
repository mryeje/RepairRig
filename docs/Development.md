# Development and verification

All project artifacts live under E:/RepairRig. Blender was launched visibly,
without --background. No animation control system or custom animator UI was
installed. `visible_runner.py` is only a development file queue executing bpy
scripts on Blender's main thread. It is not needed to open, pose or animate the
saved rig. It starts only when explicitly launched, and is not embedded in .blend.

## Scripts and checkpoints

- 01_probe.py: runtime version, Rigify and animation API inventory.
- 02_metarig.py: human metarig with simplified native face components.
- 03_generate.py: stock Rigify generation and bone/control inventory.
- 04_mannequin.py: bound segmented proxy and facial shape keys.
- 05_refresh_face_drivers.py: driver refresh after proxy construction, then tests.
- tests/validate_base.py: evaluated posing and animation API tests.
- 06_finalize.py: neutral final checkpoint and persisted metarig defaults.

Checkpoints 01 and 02 are the public milestones. The 02a and 02b files retain
intermediate generation and mannequin work. tests/RepairRig_PoseValidation.blend
retains a crouched, raised-hand, curled-finger test pose for inspection; it is
not a reusable repair Action.

For a repeat build use a separate Blender session with --factory-startup and
run milestones one at a time via the Text Editor, or launch the local runner.
Output existence assertions deliberately prevent overwriting checkpoints.
Example for continuing from checkpoint 01:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --factory-startup 'E:\RepairRig\blend\RepairRig_01_RigifySetup.blend' --python 'E:\RepairRig\scripts\start_clean.py'
```

The runner reads scripts/job.json. Set an intended script and a unique job id
before launching. Only run one runner against that queue. For ordinary manual
use, simply open the final .blend without --python.

## Findings

The runtime is Blender 5.0.1, bundled Rigify 0.6.10. An initial session exposed
a Python/RNA Rigify class identity mismatch (module class unregistered while the
bone property pointed to another class). Re-registering parameters or toggling
the add-on there did not resolve it. A clean --factory-startup session with
Rigify enabled using default_set=True succeeded. User preferences were not
saved or modified on disk. The exact trigger for the original mismatch is
not established; do not label this a general Blender or Rigify defect.

The first eyelid driver became invalid during incremental proxy construction.
Recreating both native drivers after the geometry existed resolved this; the
test measures both shape-key value and evaluated vertex displacement.

Blender 5 selection uses PoseBone.select; Bone.select is removed. See the
[official Python API release notes](https://developer.blender.org/docs/release_notes/5.0/python_api/).
Slotted Actions use layers -> keyframe strips -> channelbag(slot) -> fcurves.
NLA strips expose action_slot. Do not rely on legacy Action.fcurves examples.

Runtime test records are JSON in tests/. Earlier job logs and diagnostic files
are retained as debugging history; base_validation.json and final_validation.json
are the outcome records. Diagnostic runner sessions remained open because
automatic approval review rejected a process-cleanup request. The original
unrelated user Blender document was not modified by this work.
