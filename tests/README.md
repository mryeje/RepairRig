# Test evidence

Stages 1-2 outcome records:

- `environment.json`: Blender 5.0.1 and API inventory.
- `base_validation.json`: 26 evaluated checks, all passed.
- `final_validation.json`: neutral checkpoint and pole/driver checks.
- `reopen_validation.json`: base-file reopen and live IK/blink/driver checks.
- `RepairRig_PoseValidation.blend`: base rig test pose for manual inspection.

Stage 3 outcome records:

- `stage3_validation.json`: original successful 288-frame interaction, nearby
  target translation, grip, contact, release and driver measurements.
- `stage3_component_validation.json`: NLA repeat/isolation, disjoint channel
  ownership and native grip Pose Asset application; rerun on the saved scene.
- `stage3_persistence.json`: base-file SHA-256, preserved armature architecture,
  final committed source scripts and pre-save Action keys/handles.
- `stage3_reopen_validation.json`: both deliverables reopened, all 288 frames
  compared to original evidence, unchanged Action data, reach/contact/release,
  109 drivers and registered Rigify UI properties.
- `stage3_fresh_session.json`: fresh-session verification and rendered review.
- `RepairRig_03_TargetB.blend`: saved nearby target translation trial. The main
  scene is `blend/RepairRig_03_InteractionTest.blend`.

To verify existing Stage 3 deliverables without authoring them again:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --factory-startup --python 'E:\RepairRig\scripts\14_stage3_verify.py'
```

This uses a separate Blender process, enables bundled Rigify for that session,
checks both files, reruns the component tests, renders `renders/stage3_reopened.jpg`
and exits. It does not save changes to either deliverable or user preferences.

Other diagnostic JSON/TXT files retain earlier errors and are not current
failures. Dedicated outcome records above are authoritative. Stage 3 establishes
nearby target translation on the original proxy only; cross-character transfer,
rotated-appliance transfer and production skinning remain untested.
