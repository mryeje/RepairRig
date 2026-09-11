Latest result: [production correction and validation report](HandTransfer_Correction_Report.md).

# Hand Pose Asset transfer investigation

Historical baseline status (superseded by [production comparison](hand_pose_production_comparison.md)): canonical baseline audited; production comparison and correction pending
access to the production scene. No rig, mesh, weight, Action, or .blend was changed.

The saved Stage 4 file still has SHA-256
`4e93e612330797e826ec39a6bcdacd637db91c20d78025849c10428b0b2a4f08`,
matching the original deliverable. At inspection time, the open Blender window
showed unsaved changes under that filename. The production scene was not found
as a separate saved file in either workspace. Unsaved edits are not represented
by the on-disk canonical checkpoint and must not be overwritten by a diagnostic
session.

## Established canonical facts

- The hand topology originates from stock Rigify human metarig fingers, each
  using `limbs.super_finger` with three phalanges.
- Right-hand masters are `f_index.01_master.R`, `f_middle.01_master.R`,
  `f_ring.01_master.R`, `f_pinky.01_master.R`, and `thumb.01_master.R`.
- The metarig uses Automatic primary rotation axis, 10 B-Bone segments, and no
  extra finger IK controls.
- Generated finger bend drivers convert master Y scale into local X rotation
  using `(1-sy)*pi`. That scalar response depends on the generated bend-bone
  orientation and axis sign, not simply on matching master names.
- All six assets store 120 native curves: location, quaternion, scale and B-Bone
  properties on the five masters. Their quaternion values are identity and
  locations zero. Their meaningful curl differences are master Y-scale values.
  They do not store compensating rotations or an independently authored thumb
  opposition adjustment.

The installed Blender 5.0.1 Rigify implementation shows that Automatic mode
aligns chain X axes during generation. Manual signed-axis settings change which
local axis receives the bend and its sign. See the official
[Rigify finger implementation](https://github.com/blender/blender-addons/blob/main/rigify/rigs/limbs/super_finger.py)
and [limb rig documentation](https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/rig_types/limbs.html).
The local installed source, rather than a different Blender release, was used
for the actual code inspection.

These facts do not establish the production root cause. Possible differences
still to test include generation-time bend plane, explicit axis/sign, chain
topology, rest thumb opposition, extra finger IK, and posed master offsets that
the assets reset. Body transfer succeeding does not distinguish those causes.

## Audit evidence and next comparison

`tests/hand_transfer/canonical.json` records exact hand bone names, parents,
rest matrices in armature and hand-relative coordinates, Rigify parameters,
constraints, driver expressions/targets, and exact asset payloads. It also
measures each finger's deform-chain heads/tails and orientations in hand space
at master scales 1, 0.95, 0.78, 0.70, 0.58, and 0.48. These are diagnostic curl
samples, not proof of production fingertip direction or thumb opposition.

`scripts/26_hand_transfer_audit.py` runs in an isolated Blender session without
saving the scene. Register Rigify before loading to read parameter defaults:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --factory-startup --python 'E:/RepairRig/scripts/26_hand_transfer_audit.py' -- --label production --source 'PATH_TO_SAVED_PRODUCTION.blend'
```

Compare actual generated and metarig hand-relative bases, signed bend axes,
joint positions and scalar curl responses. A changed rest finger direction is
not automatically a roll error: use the chain direction and hand-relative bend
normal together. Do not copy arbitrary Euler rolls or regenerate the whole rig
without understanding the deformation/animation consequences.

Only after this comparison should a minimum correction be selected. Validate
screwdriver, pliers, fist, open hand and point on the production mesh, including
thumb opposition, fingertip direction, unchanged body/tool behavior, and a saved
file reopen. No production correction or validation has been claimed yet.

