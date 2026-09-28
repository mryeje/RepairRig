# Production reach and saved-wrist correction

Delivered checkpoint: `E:/RepairRig/blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend`.

Input: `E:/RepairRig/blend/RepairRig_05_ProductionCharacter_HandFixed.blend`.
Canonical reference: `E:/RepairRig/blend/RepairRig_04_ActionLibrary.blend`.
Both inputs remain byte-identical. The generated rig is `RepairRig`, armature data `RIG-RepairRig_Metarig`.

## Restored architecture

All five constraints are native Copy Transforms, WORLD owner and target spaces, REPLACE mix, no subtarget, unmuted, and without target-shear removal. Other writable constraint settings were copied and compared with the canonical file. Existing target objects were reused. Ordering below matches canonical, including Work before Mid on the right.

| Control | Constraint, in stack order | Target |
|---|---|---|
| hand_ik.R | Pickup \| TARGET_ToolGrip | CONTACT_PickupWrist_R |
| hand_ik.R | Work \| TARGET_Screw | CONTACT_WorkWrist_R |
| hand_ik.R | Reach \| Mid_R | TARGET_Reach_Mid_R |
| hand_ik.L | Brace \| TARGET_Brace_L | TARGET_Brace_L |
| hand_ik.L | Reach \| Low_L | TARGET_Reach_Low_L |

Saved influences are all zero, matching the canonical demonstration at frame 1. Its saved frame 179 has Work and Brace engaged; those animated values are not neutral defaults. Existing reach Actions now resolve every F-curve and animate these influences normally. Their OBRepairRig slots remain valid. No Action was rebuilt or edited.

Both upper_arm_parent controls now use canonical `pole_vector=1` and `IK_Stretch=0`, instead of production values 0 and 1. These settings belong to the established workflow: its arm Actions key elbow-pole transforms and Stage 4 uses unstretched IK. IK_FK remains 0. Parent selections and other custom properties were retained.

## Exact saved-pose correction

Production metarig and generated wrist rest frames were already mirror-symmetric. The left saved hand IK quaternion contained an extra 180-degree local-Y rotation relative to the mirrored right quaternion. The measured residual axis was approximately (0,-1,0), angle 179.999991 degrees.

Quaternion order is W,X,Y,Z:

- Left before: `(0.121922798, 0.450626552, 0.884329200, 0.005701492)`.
- Left after: `(0.884329140, 0.005701506, -0.121922821, -0.450626612)`.
- Right retained: `(0.884329081, 0.005701501, 0.121922828, 0.450626612)`.

Only hand_ik.L rotation_quaternion was corrected. Both hand locations and scales were retained. No rest roll, compensating bone transform, target transform, Action rotation, or mesh change was introduced. All armature rest matrices compare exactly equal before and after saving/reopening, including the metarig and finger calibration.

The production-specific hand axes (about 36 degrees from canonical due to the fitted chain direction), dimensions, weights, and prior finger-axis calibration remain intact. Saved body/action/frame selection is retained: BODY_Stand_From_Kneel_L, frame 68. Existing asymmetric hand positions and right finger grip are retained; wrist orientation symmetry is corrected.

Saved-state mirrored wrist orientation error is zero at reported precision. A disposable neutral-pose check also reports zero, with visually consistent left/right anatomy. BODY_Kneel_L at frames 1,25,49 retains mirrored wrist orientation. See saved_pose.png and neutral_pose.png in tests/reach_fixed.

## Behavioral validation

The new file was reopened independently for each motion. All four arm clips were tested at frames 1,17,33. The following endpoint displacement is measured on the actual DEF-hand bone using the checkpoint's saved body posture; mesh hand-region centroids also moved.

| Action | Hand displacement, Blender units | Weighted hand-region displacement |
|---|---:|---:|
| REACH_Forward_Low_R | 0.353944 | 0.354737 |
| REACH_Forward_Mid_R | 0.335776 | 0.335150 |
| REACH_Forward_Low_L | 0.322855 | 0.345932 |
| BRACE_Forward_L | 0.375106 | 0.404965 |

BODY_Kneel_L changes the torso and evaluated mesh. All sampled rig drivers remain valid and all evaluated mesh coordinates are finite. Mesh topology, vertex coordinates and weights have identical hashes. These checks verify deformation follows animation, not a full skin-quality approval.

Additional tests use the documented body pairing: Kneel_L for low reaches and brace, Bend_Forward for Mid_R. At frame 33 all four DEF-hand/hand-IK position errors are below 0.000021 Blender units. At frame 17 all four are below 0.000003 units.

Remaining fit limit: at frame 1 of the kneeling low reaches/brace, inherited wrist start positions exceed the unstretched arm range by about 0.145 units on the right and 0.157 units on the left. Simply playing low reaches from standing can also exceed arm reach. The Actions now function, but their starting arm carriage needs future character/shot fitting. No target, Action, or body retiming was added to hide that limitation.

TOOL_Screwdriver_CW_R was assigned to its correct owner, CONTACT_ScrewdriverRoll_R, with the low right reach engaged and Kneel_L applied. Frames 1,17,33,37 show rotation, withdrawal, and return. Tool/socket position error stays below 0.000000081 units; orientation error is zero at reported precision. DEF-hand/hand-IK error stays below 0.0000056 units.

The screwdriver remains positioned in the grip and follows the socket. Visual evidence: tests/reach_fixed/screwdriver_grip.png. Existing finger/handle intersections remain; this is not a collision-free production grasp. Socket alignment passed, skin-contact quality remains limited as previously documented.

All six existing hand Pose Assets retain asset metadata and apply through native slotted Action evaluation with matching keyed values: OpenHand, Fist, Point, HoldSmallPart, Grip_Pliers, and Grip_Screwdriver. Existing curled-joint intersection counts are unchanged in five poses. OpenHand changes from zero to two detected near-contact triangle pairs under the changed evaluated arm pose; this small diagnostic difference is not treated as a collision-free pass. No pose payload was altered.

## Preservation and evidence

Reopened structural checks pass: all restored constraint properties/order match canonical frame 1; arm settings match; all Action curves/keys/handles/interpolation and all armature rest matrices remain identical to input; mesh/weight hash matches; both input files are unchanged. The validation process also leaves the new checkpoint byte-identical.

- `tests/reach_fixed/correction.json`: exact settings, pose transforms, hashes, save/reopen preservation checks.
- `tests/reach_fixed/validation.json`: motion samples, mesh response, pose assets, tool cycle, neutral check.
- `tests/reach_fixed/pairings.json`: reach accuracy in intended body postures.
- `scripts/32_restore_production_reach.py`: targeted correction and save/reopen checks.
- `scripts/33_validate_production_reach.py` and `34_validate_reach_pairings.py`: disposable validation without scene saves.

The base rig was not rebuilt, the canonical Stage 4 file was not modified, and the animation library was not expanded. No production NLA demonstration was assembled as part of these corrections; the working combined demonstration remains in Stage 4.
