# Production hand-grip refinement

Checkpoint: `E:/RepairRig/blend/RepairRig_05C_ProductionCharacter_GripRefined.blend`.

Input: `E:/RepairRig/blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend`.
Reference: `E:/RepairRig/blend/RepairRig_04_ActionLibrary.blend`.
Both inputs remain unchanged. Blender files and generated validation images/JSON remain local and ignored by Git.

## What made the grip awkward

The inherited poses primarily drove five master Y scales. This distributes curl through the generated finger mechanisms but does not fit separate joints, thumb opposition, or the actual handle contact surface. Matching Rigify control names was not sufficient to transfer the proxy's grasp to this character.

The production hand has materially different segment proportions. Examples, in Blender units:

| Segment | Proxy | Production | Difference |
|---|---:|---:|---:|
| Ring proximal | 0.044817 | 0.033902 | 24% shorter |
| Ring distal | 0.018550 | 0.007356 | 60% shorter |
| Pinky proximal | 0.027876 | 0.039092 | 40% longer |
| Pinky distal | 0.015018 | 0.027416 | 83% longer |
| Thumb middle | 0.033446 | 0.042635 | 27% longer |
| Thumb distal | 0.020791 | 0.031811 | 53% longer |

Uniform master curl therefore produced different fingertip paths and excessive joint folds. Thumb opposition was not fitted to the grip. The proxy's hand-relative tool placement also put the screwdriver through portions of the production palm/fingers while leaving the index and thumb separated from the handle. The primary remedy here is character-specific poses plus character-specific socket placement, not another rig rebuild or global changes to the canonical library.

## What changed

Six new single-frame native Pose Assets were created:

- `POSE_Grip_Screwdriver_R_Production`
- `POSE_Grip_Pliers_R_Production`
- `POSE_HoldSmallPart_R_Production`
- `POSE_OpenHand_R_Production`
- `POSE_Fist_R_Production`
- `POSE_Point_R_Production`

Each asset keys only 20 right finger controls: the five `.01_master.R` controls and the fifteen `.01.R`, `.02.R`, `.03.R` FK controls. It includes location, quaternion and scale reset channels so switching between these variants clears the previous refinement. The master transforms are neutral; independent native FK rotations supply the curls, splay, and thumb opposition. No wrist or arm channels are included.

The screwdriver variant uses individually fitted index/middle/ring/pinky bends and an opposed thumb. A second fitting pass checked the evaluated skin against the handle, rather than accepting a bone-centerline fit as evidence of clearance. The handle is seated near the palm, with finger pads close to its surface. Wrist orientation is unchanged.

The two existing production tool sockets, `ATTACH_Screwdriver_R` and `ATTACH_Pliers_R`, received static positional fitting. Tool dimensions and orientation were preserved. The screwdriver handle center is approximately (-0.043, 0.130, 0.020) in hand coordinates. `CONTACT_WorkWrist_R` and `CONTACT_PickupWrist_R` received the corresponding positional offset update so the socket change does not displace the engaged screwdriver in world space. No target hierarchy, constraint type, constraint ordering, driver, or Action was redesigned.

The checkpoint opens in a kneeling screwdriver inspection pose, with `REACH_Forward_Low_R` active at frame 33 and the refined screwdriver fingers applied. This is a saved review posture, not a new full-body Action or NLA sequence.

## Preservation

All original Actions, including the original six hand assets, retain identical F-curves, key values, handles and interpolation. All armature rest matrices, mesh vertex coordinates, topology and weights match the input exactly after save/reopen. The previous finger-axis calibration and production-specific rest proportions are retained. No rig regeneration, corrective shape key, mesh edit, or runtime fitting script was introduced.

The Stage 4 file was read only. Its architecture and poses were not changed. The new variants are character-specific additions for the six requested poses; no motion clips were added.

## Reopened validation

A separate Blender process reopened 05C and tested all six variants through slotted Action evaluation. Another disposable GUI session applied all six through the native Asset Browser: every operation returned FINISHED and every keyed channel matched exactly. Rig drivers remained valid.

The source and refined grips were also compared in a reachable kneeling work posture:

| Check | Source | Refined |
|---|---:|---:|
| Screwdriver/hand intersecting triangle pairs | 347 | 0 |
| Screwdriver maximum sampled penetration | 0.016410 units | 0 |
| Pliers handles, total intersecting triangle pairs | 186 | 66 |
| Pliers sampled hand vertices inside either handle | 158 | 0 |
| Pliers maximum sampled vertex penetration | 0.007469 units | 0 |

For the refined screwdriver, nearest sampled surface gaps are approximately 0.214–0.287 mm for the five fingers/thumb and 1.841 mm for the palm, interpreting one Blender unit as one meter. These are surface samples, not a pressure/contact simulation. The palm clearance is visually small but is not mathematically zero contact.

The screwdriver's world transform during the existing CW cycle was compared at frames 1,17,33,37. Maximum matrix-element difference from 05B was 1.79e-7; wrist orientation difference was zero at reported precision. The fitted socket thus preserves the established work motion and natural wrist angle.

## Remaining limits

This is a better testing checkpoint, not an assertion that every hand pose is fully production-approved.

- The screwdriver has no detected hand/handle intersections in the reopened work test. Its remaining 32 hand self-intersection pairs are all classified palm/palm; no cross-finger intersections were detected in that pose.
- The pliers still have 66 surface-triangle intersections despite no sampled vertices lying inside the handles. Triangle crossings can occur between vertex samples. Its skin also has a few ring/palm and palm/thumb intersections. It needs a final visual contact pass for the intended shot; it is not certified collision-free.
- The Fist variant is deliberately a relaxed closure. A tight closure on the current joint/weight fitting reintroduces folds, particularly at the unusually short ring distal segment. No weights or joint positions were altered to hide this limitation.
- Point preserves an extended index and a restrained curled remainder. OpenHand resets all 20 controls. HoldSmallPart improves thumb/index opposition but was not fitted around a specified small-part prop and is not a verified precision pinch.
- Self-contact depends on the arm/wrist pose. In the reopened work posture, self-intersection counts are 32 screwdriver, 38 pliers, 52 relaxed fist, 50 point, 36 open, and 33 small-part. Many remaining pairs involve the palm/wrist region; these counts must not be conflated with prop penetration. The corresponding source counts were 273,60,526,344,58,75.
- The pliers pose was tested with the proxy jaws at their open driver limit. The old master-scale squeeze Action is preserved, but combining it with these additional FK offsets has not been contact-fitted through a squeeze cycle.

## Animator use

Open 05C, select `RepairRig`, enter Pose Mode, and use Asset Browser > Current File. Choose the assets ending `_Production` (tagged Production Hand). Select all 20 right finger controls when applying the full pose. Native Asset Browser application was tested with that selection.

Use `POSE_OpenHand_R_Production` to clear production FK offsets before returning to an original master-only pose. Original assets do not contain reset curves for all the additional FK controls and therefore cannot clear those offsets themselves. For animation, key the selected finger controls; a pose application by itself is an unkeyed hand state. Keep wrist positioning in the separate reach/arm workflow.

## Recommended workflow for future characters

1. Validate the fitted rest hand and skin before transferring grips. Check segment ratios, joint centers, thumb base/opposition, and deformation under moderate curl.
2. Preserve the canonical assets as references. Create character-specific copies when proportions differ materially.
3. Fit the prop socket in a reachable body/arm pose. Place the handle near the palm before curling fingers. Preserve the tool's work/pickup reference relationship if the socket changes.
4. Fit MCP/PIP/DIP bends separately, then thumb opposition and pad placement. Use master curl as a starting point, not the sole contact control.
5. Check the actual skin from palm, side and back views. Measure both hand self-contact and hand/prop intersection; neither bone positions nor sampled vertices alone prove a clean grasp.
6. Check open, relaxed fist, point, both grips, and transitions. Fit a precision pinch against the actual small-part dimensions.
7. Save explicit reset channels, reopen, apply through the native Asset Browser, and test the work motion. Validate a squeeze cycle separately if required.

Future production characters should receive their own grip-pose and socket fitting. Canonical motion architecture can remain shared; precise grasps are geometry-dependent.

## Evidence and reproduction

`tests/grip_refined/saved_checkpoint.json` records input/output hashes and preservation checks. `reopen_validation.json` contains saved-file measurements; `asset_browser_validation.json` records actual pose-operator application. `final_parameters.json` records final joint rotations and fitted socket matrices. Review images include `surface_Grip_Screwdriver_palm.png`, `saved_Grip_Screwdriver_side.png`, and the `saved_*` pose views.

Scripts 35–38 perform inspection/fitting, 39 saves the checkpoint, 40 validates the reopened scene, and 41 tests native Asset Browser application. `production_grip_common.py` and `grip_contact_validation.py` are offline helpers. SciPy/NumPy used for fitting live in ignored temp storage and are not required to open or animate the delivered .blend.
