# Production hand-transfer correction

Saved and reopened: `E:/RepairRig/blend/RepairRig_05_ProductionCharacter_HandFixed.blend`.

**Status: rig transfer correction completed; contact-quality validation did not fully pass.** All six native hand Actions evaluate with unchanged channels. The corrected mesh still has curled-joint self-intersections and tool-fit problems. This is a production test checkpoint, not a contact-ready character.

## Exact root cause

The fitted production metarig changed the geometric plane of the finger chains. Stock Rigify 0.6.10 in Blender 5.0.1 computes Automatic X from the cross product of the first segment's direction and the vector from the first joint to the final fingertip. It uses the original roll only for an almost-straight chain. None of the ten production chains used that fallback.

Replaying that calculation on the saved production metarig reproduces the generated axes: the independent mathematical comparison reports 0 degrees at the recorded float precision, and the separate Edit Mode helper replay agrees within 0.020 degrees. Heads and tails match. The generated setup is therefore consistent with the fitted metarig; there is no evidence of a stale generated rig or a wrong driver formula.

The large index/ring/pinky differences originate in metarig fitting and the resulting automatically selected local axes. They appear as generated bone-roll differences, but simply changing metarig roll while leaving Automatic enabled would not correct them. Right-hand master residual X differences after accounting for chain aim were index 136.53, middle 14.27, ring 102.60, pinky 87.83, thumb 49.39 degrees. These are comparisons, not Euler angles to copy.

No extra production finger rotations or translations were present. Saved master scales represented the screwdriver grip. All six source pose payloads match Stage 4. The screwdriver's missing asset flag was an independent metadata issue.

Implementation evidence is the installed `rigify/rigs/limbs/super_finger.py` (`prepare_bones`, `axis_options`, `rig_mch_bend_bone`) and `rigify/utils/bones.py` (`compute_chain_x_axis`, lines 661–681). The live `Bone.x_axis` property is parent-relative; diagnostics use `matrix_local` columns to compare armature-space axes. The saved diagnostic reports include the corrected coordinate-space handling.

## Exact correction

1. Read canonical rest bases without saving Stage 4. Map each canonical finger X axis into hand space, apply the shortest rotation from canonical segment Y to fitted production segment Y, and map it into production armature space.
2. Roll all 170 generated finger bones across both hands to the resulting frames: ORG, DEF, bend mechanisms, stretch mechanisms, FK controls, masters and locked tip controls. The tip controls preserve the flipped tip convention. No joint head/tail, length, parent, name, driver expression, or constraint is intentionally changed.
3. Apply matching rolls to the 30 metarig finger segments and set the ten `limbs.super_finger` roots to **Primary Rotation Axis: X (manual)**. This is a standard Rigify option; no custom deformation driver, per-asset compensation, or runtime script was introduced. Whole-body regeneration was avoided.
4. Fit the thumb bend plane once for the character: add +55 degrees about segment Y on the right and mirrored -55 degrees on the left (opposite sign for flipped tip controls). This is relative to the transported canonical frame, not a universal thumb roll. A 35–75 degree sweep at 5-degree intervals found 55 to be the first sampled offset with no thumb-to-palm or thumb-to-finger triangle intersections in all six right-hand poses. It is a shared static rig calibration, not an Action edit. It improves clearance but does not establish precision pinch/tool contact.
5. Restore `POSE_Grip_Screwdriver_R` as an asset, including canonical description, author, catalog and tags. All Action F-curves, key positions, handles and interpolation remain identical to the production input.

Exact old/new roll values for each edited bone are in `tests/hand_transfer/correction.json`. The saved metarig and generated ORG finger matrices agree within 6.41e-7. Existing hand constraints compare exactly equal. This verifies frame consistency for the manual-X setup; a destructive full-rig regeneration was not performed.

## Preservation and reopen tests

- All Action payloads, including body animation and six hand poses: identical.
- Mesh vertices, topology and weights: identical hash.
- Driver definitions, bone names/parents, object transforms and parenting: identical.
- All six assets are present after reopening; native slotted Action evaluation reproduces all master scales and `(1-sy)*pi` bend angles. All audited rig drivers are valid.
- Non-finger rest matrices differ by at most 3.22e-6 from Blender Edit Mode float normalization. Body Actions sampled at start/mid/end have maximum non-finger evaluated matrix-element difference 2.48e-5, within the declared 1e-4 regression tolerance. This is numerical preservation, not a claim of bit-identical matrices or exhaustive frame-by-frame body validation.
- Original production frame 68 and active `BODY_Stand_From_Kneel_L` are retained in the new file. Diagnostic pose, tool, camera and render changes are not saved.
- The six assets are right-hand assets. Detailed mesh/contact tests cover the right hand; the left receives mirrored frame calibration and structural checks, not a separate six-pose visual validation.

## Pose and contact validation

The table counts intersecting non-adjacent hand triangles, excluding shared vertices and coincident seam points. Counts are diagnostic surface-pair counts, not penetration volumes. All final cross-finger and thumb/palm categories are zero; remaining pairs are within individual fingers/thumb. Joint-region folding remains visible in close views. Small counts near degeneracies warrant manual review.

| Pose | Source self-intersection pairs | Corrected pairs | Thumb/index bone-tip gap (Blender units) |
| --- | ---: | ---: | ---: |
| POSE_Grip_Screwdriver_R | 347 | 215 | 0.0579 |
| POSE_Grip_Pliers_R | 0 | 2 | 0.0819 |
| POSE_HoldSmallPart_R | 92 | 17 | 0.1134 |
| POSE_OpenHand_R | 1 | 0 | 0.1227 |
| POSE_Fist_R | 572 | 468 | 0.0670 |
| POSE_Point_R | 400 | 286 | 0.1272 |

Finger curl and distal direction now follow the canonical hand-space bend convention, while fitted segment lengths and rest spread are preserved. Open Hand has no detected self-intersection; Point retains the extended index. Thumb motion is no longer through the palm, but a fingertip gap is not a surface-pad contact measurement. Hold Small Part is not a successful precision pinch and no small-part prop contact is claimed.

Screwdriver attachment follows the unchanged socket (matrix agreement at float tolerance), but the handle still intersects palm/middle/pinky geometry. The final handle test reports 349 surface triangle intersections and sampled penetration up to approximately 0.0164 Blender units. The thumb's closest surface remains about 0.0081 units away and index about 0.0069. This is not an acceptable production grip.

Pliers were temporarily attached to their existing socket for validation. One handle reports 186 surface triangle intersections, with sampled palm penetration about 0.0076 units; the other reports none. This also fails contact readiness. Tool interior tests use three-ray majority parity independent of imported face winding, plus nearest-surface distance. They do not constitute a full scene-wide collision simulation.

No per-pose edits were used to conceal these problems. Resolving the remaining joint folds and contact requires production hand joint/weight fitting and calibrated tool sockets/proportions. A roll-only compatibility correction cannot establish collision-free skinning and identical prop contact for a differently proportioned mesh.

## Standard for future production metarigs

A canonical finger-fitting standard is required for repeatable asset transfer. Matching bone names is insufficient.

- Keep the canonical three-segment topology, master channel semantics, control rotation modes and positive-X curl sign. Fit joint centers and segment ratios deliberately, including the thumb metacarpal/opposition geometry.
- Establish axes in hand space, not global Euler roll values. Transport the canonical bend normal onto each fitted chain direction and use explicit manual X so small fitting edits do not make Automatic derive a different plane.
- Keep metarig and generated finger frames synchronized. Fit and verify the metarig before generation; do not correct only generated bone rolls and then regenerate from an unchanged Automatic metarig.
- Treat thumb opposition as a character-level fitting decision shared by all poses. The 55-degree calibration here is specific to this character and is not a template default.
- Validate neutral/open, fist, point, both tool grips and small-part pinch on the actual weighted mesh before approving a character. Check joint folds, fingertip/pad direction, palm clearance and each prop's dimensions/socket. Canonical channel compatibility is not a guarantee of geometric contact.
- Keep existing body Actions and custom contact constraints under regression checks when regenerating. This correction deliberately updates finger frames without replacing the generated body rig.

## Reproducible evidence

- `scripts/29_fix_production_hand.py`: correction; `--preview` does not save; `--save` writes only HandFixed and refuses to replace externally changed output.
- `scripts/30_validate_hand_fixed.py`: independent source/fixed reopen, native pose evaluation, data preservation, collision and contact checks; no scene saves.
- `scripts/hand_mesh_validation.py`: evaluated hand surface checks.
- `tests/hand_transfer/correction.json`, `reopen_validation.json`, `manual_generation_consistency.json`, `root_cause_detail.json`, `thumb_scan.json`, `thumb_refined_scan.json`, and `fixed.json` contain detailed measurements.
- `tests/hand_transfer/final_pose_contact_sheet.png` and `tool_contact_comparison.png` show the final saved-file validation views.

## SHA-256

- `RepairRig_04_ActionLibrary.blend`: `4e93e612330797e826ec39a6bcdacd637db91c20d78025849c10428b0b2a4f08`
- `RepairRig_05_ProductionCharacter_Test.blend`: `4574051f7e338543c23a5b1ac1f8cc1b643898fc47156f945f92bdc82d6730d9`
- `RepairRig_05_ProductionCharacter_HandFixed.blend`: `0ae0449ac67792c9818322801113bc1214377435d7d8c2fc3cc86ae9e38945cb`

Both Stage 4 and the original production file remain unchanged.
