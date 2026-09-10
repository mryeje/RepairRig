# Test evidence

Authoritative successful outcome records:

- environment.json — visible Blender 5.0.1 and API inventory.
- base_validation.json — 26 evaluated checks, all passed.
- final_validation.json — final neutral checkpoint and supplemental pole/driver checks.
- reopen_validation.json — saved-file reopen, live IK/blink/driver checks.
- RepairRig_PoseValidation.blend — inspect the test pose manually.

Other diagnostic JSON/TXT files retain earlier errors and are not current
failures. Early job status logs were shared by two development sessions, so
the dedicated outcome records above are authoritative. No cross-character
animation transfer, production skinning quality or Stage 3 interaction is
claimed tested. Temporary API Actions/assets were deleted from the scene after
measurement; their test source remains in validate_base.py.
