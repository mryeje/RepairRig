# Stage 4 evidence

The delivered file is `../../blend/RepairRig_04_ActionLibrary.blend`.

Authoring proceeded in groups A, B, C, D, then the NLA demo. Group `.blend` files
are intermediate test checkpoints, not the final library. `group_*_channels.json`
records channel ownership. `group_*_validation.json` records tests at each stage.

Final evidence:

- `presave_validation.json` and `reopen_validation.json`: all 485 demo frames,
  Action/slot ownership, original rig architecture, contact/support measurements,
  repeated screwdriver motion and unchanged earlier checkpoint hashes.
- `additional_validation.json`: three actual NLA repeats of all four declared
  loops; body/brace isolation when the tool track is muted; body variant support
  and stationary-hold checks.
- `pose_application_validation.json`: native Asset Browser Apply Pose for all six
  poses, selected-finger application, half blending, switch to open, jaw drivers.
- `pliers_attachment_validation.json`: fitted Child Of matches the hand socket
  at open, squeezed, and returned frames.
- `finish.json`: delivered file checksum and library counts.
- `demo_*refined.png`, `demo_final_contact.png`: revised staggered foot support.
- `POSE_*.png`: individual hand-pose closeups.
- `pliers_final_open.png`, `pliers_final_closed.png`: attached pliers review.

Earlier `error_*.txt` files are diagnostic history, not current acceptance status.
Group B initially found an unreachable mid target, the first pose test lacked an
Asset Browser context, and the refined transfer briefly overextended the resting
left arm. Each was corrected and tested again. Early `demo_stand.png` predates the
staggered-foot correction; use the refined render and final saved file instead.

Run `validate_library.py` from Blender's Text Editor with the final file open to
write `manual_validation.json`. It changes the current frame but does not save
or rewrite the library. `25_stage4_reopen.py` runs this check in a fresh Blender
process. The authoring scripts are offline helpers, not runtime requirements.

The original Stage 3 rig remains the source; no rig generation was performed.
Quality review is on the segmented proxy, not production skin or a final character.
